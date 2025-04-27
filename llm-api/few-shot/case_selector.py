import json
import numpy as np
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModel
import torch
from collections import defaultdict

class CaseSelector:
    """
    基于ConsistNER框架思想的Few-shot案例选择器
    用于从表格数据中选择最合适的案例用于few-shot提示
    """
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        初始化案例选择器
        Args:
            model_name: 使用的预训练语言模型名称
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.ontology_types = {
            "time": ["year", "date", "week", "month", "season"],
            "location": ["town", "city", "country", "venue", "location", "place"],
            "person": ["artist", "director", "author", "player", "name"],
            "event": ["competition", "tournament", "match", "concert", "show"],
            "number": ["count", "amount", "total", "number", "score"],
            "attribute": ["type", "category", "class", "style", "genre"]
        }
        
    def _extract_ontologies(self, headers: List[str]) -> Dict[str, List[str]]:
        """
        从表格头部提取本体类型
        Args:
            headers: 表格的列名列表
        Returns:
            每个本体类型对应的列名字典
        """
        ontology_map = defaultdict(list)
        for header in headers:
            header_lower = header.lower()
            for onto_type, keywords in self.ontology_types.items():
                if any(keyword in header_lower for keyword in keywords):
                    ontology_map[onto_type].append(header)
        return ontology_map
    
    def _calculate_ontology_distribution(self, row: List[List[str]], ontology_map: Dict[str, List[str]]) -> Dict[str, float]:
        """
        计算表格行的本体分布
        Args:
            row: 表格行数据，格式为 [[header1, value1, value2, ...], [header2, value1, value2, ...], ...]
            ontology_map: 本体映射字典
        Returns:
            本体分布字典
        """
        distribution = defaultdict(float)
        total_fields = len(row)
        
        # 创建表头到值的映射
        row_dict = {}
        for column in row:
            if len(column) > 0:  # 确保列不为空
                row_dict[column[0]] = column[1:]  # 第一个元素为表头，其余为值
        
        for onto_type, headers in ontology_map.items():
            # 计算每个本体类型的字段数量
            onto_count = sum(1 for header in headers if header in row_dict and any(row_dict[header]))
            if total_fields > 0:
                distribution[onto_type] = onto_count / total_fields
        
        return distribution
    
    def _get_contextual_embedding(self, text: str) -> torch.Tensor:
        """
        获取文本的上下文嵌入表示
        Args:
            text: 输入文本
        Returns:
            文本的嵌入向量
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze()
    
    def _calculate_similarity(self, case: Dict, query: Dict, ontology_map: Dict[str, List[str]]) -> float:
        """
        计算案例与查询的综合相似度
        Args:
            case: 候选案例
            query: 查询问题
            ontology_map: 本体映射字典
        Returns:
            综合相似度分数
        """
        # 计算本体分布相似度
        case_od = self._calculate_ontology_distribution(case["table"], ontology_map)
        query_od = self._calculate_ontology_distribution(query["table"], ontology_map)
        
        od_sim = sum(min(case_od[k], query_od[k]) for k in set(case_od) | set(query_od))
        
        # 计算上下文语义相似度
        case_emb = self._get_contextual_embedding(case["question"])
        query_emb = self._get_contextual_embedding(query["question"])
        
        context_sim = torch.cosine_similarity(case_emb, query_emb, dim=0).item()
        
        # 综合相似度（可调整权重）
        return 0.5 * od_sim + 0.5 * context_sim
    
    def _calculate_case_length(self, case: Dict) -> int:
        """
        计算案例的总长度
        Args:
            case: 候选案例
        Returns:
            案例的字符总长度
        """
        # 计算问题长度
        question_length = len(case["question"])
        
        # 计算表格内容长度
        table_length = sum(len(str(item)) for row in case["table"] for item in row)
        
        return question_length + table_length
    
    def select_cases(self, data_path: str, query: Dict, top_k: int = 3, max_length: int = 500) -> List[Dict]:
        """
        选择最合适的few-shot案例
        Args:
            data_path: 数据文件路径
            query: 查询问题
            top_k: 选择的案例数量
            max_length: 每个案例的最大长度限制
        Returns:
            选中的案例列表
        """
        cases = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                case = json.loads(line.strip())
                # 只添加长度在限制范围内的案例
                if self._calculate_case_length(case) <= max_length:
                    cases.append(case)
        
        if not cases:
            raise ValueError(f"没有找到长度在 {max_length} 字符以内的案例")
        
        # 提取表格头部并建立本体映射
        headers = [col[0] for col in cases[0]["table"]]
        ontology_map = self._extract_ontologies(headers)
        
        # 计算每个案例与查询的相似度
        similarities = []
        for case in cases:
            sim = self._calculate_similarity(case, query, ontology_map)
            similarities.append((case, sim))
        
        # 选择相似度最高的k个案例
        selected_cases = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
        return [case for case, _ in selected_cases]