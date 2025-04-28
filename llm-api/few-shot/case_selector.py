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
    
    def select_cases(self, data_path: str, query: Dict, top_k: int = 3, max_length: int = 500) -> Tuple[List[Dict], Dict]:
        """
        选择最合适的few-shot案例
        Args:
            data_path: 数据文件路径
            query: 查询问题
            top_k: 选择的案例数量
            max_length: 每个案例的最大长度限制
        Returns:
            选中的案例列表和统计信息字典
        """
        cases = []
        total_cases = 0
        filtered_cases = 0
        
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                total_cases += 1
                case = json.loads(line.strip())
                # 只添加长度在限制范围内的案例
                if self._calculate_case_length(case) <= max_length:
                    cases.append(case)
                    filtered_cases += 1
        
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
        
        # 按相似度排序
        sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        selected_cases = sorted_similarities[:top_k]
        
        # 生成统计信息
        stats = {
            "total_processed": total_cases,
            "length_filtered": filtered_cases,
            "top_similarities": [
                {
                    "question": case["question"],
                    "similarity_score": round(score, 4)
                } for case, score in sorted_similarities[:top_k]
            ],
            "ontology_distribution": self._calculate_ontology_distribution(query["table"], ontology_map)
        }
        
        return [case for case, _ in selected_cases], stats
    
    def select_representative_cases(self, data_path: str, top_k: int = 5, max_length: int = 500) -> Tuple[List[Dict], Dict]:
        """
        直接从数据集中选择具有代表性的案例
        
        Args:
            data_path (str): 数据集文件路径
            top_k (int): 要选择的案例数量
            max_length (int): 每个案例的最大长度限制
            
        Returns:
            Tuple[List[Dict], Dict]: 选中的案例列表和统计信息
        """
        cases = []
        total_cases = 0
        filtered_cases = 0
        
        # 读取所有案例
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                total_cases += 1
                case = json.loads(line.strip())
                # 只添加长度在限制范围内的案例
                if self._calculate_case_length(case) <= max_length:
                    cases.append(case)
                    filtered_cases += 1
        
        if not cases:
            raise ValueError(f"没有找到长度在 {max_length} 字符以内的案例")
        
        # 提取表格头部并建立本体映射
        headers = [col[0] for col in cases[0]["table"]]
        ontology_map = self._extract_ontologies(headers)
        
        # 计算每个案例的特征向量
        case_features = []
        for case in cases:
            # 获取问题的语义嵌入
            question_embedding = self._get_contextual_embedding(case["question"])
            # 获取本体分布
            ontology_dist = self._calculate_ontology_distribution(case["table"], ontology_map)
            case_features.append({
                "case": case,
                "embedding": question_embedding,
                "ontology_dist": ontology_dist
            })
        
        # 使用聚类选择代表性案例
        selected_indices = []
        remaining_indices = list(range(len(cases)))
        
        # 选择第一个案例（最长的问题）
        first_case_idx = max(remaining_indices, 
                            key=lambda i: len(cases[i]["question"]))
        selected_indices.append(first_case_idx)
        remaining_indices.remove(first_case_idx)
        
        # 贪心选择剩余案例
        while len(selected_indices) < top_k and remaining_indices:
            max_min_dist = -1
            next_idx = -1
            
            for i in remaining_indices:
                min_dist = float('inf')
                curr_embedding = case_features[i]["embedding"]
                curr_dist = case_features[i]["ontology_dist"]
                
                # 计算与已选案例的最小距离
                for j in selected_indices:
                    selected_embedding = case_features[j]["embedding"]
                    selected_dist = case_features[j]["ontology_dist"]
                    
                    # 综合距离（语义 + 本体）
                    semantic_dist = 1 - torch.cosine_similarity(
                        curr_embedding, selected_embedding, dim=0).item()
                    ontology_dist = sum(abs(curr_dist[k] - selected_dist[k]) 
                                  for k in set(curr_dist) | set(selected_dist))
                    
                    dist = 0.5 * semantic_dist + 0.5 * ontology_dist
                    min_dist = min(min_dist, dist)
                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    next_idx = i
            
            selected_indices.append(next_idx)
            remaining_indices.remove(next_idx)
        
        selected_cases = [cases[i] for i in selected_indices]
        
        # 生成统计信息
        stats = {
            "total_processed": total_cases,
            "length_filtered": filtered_cases,
            "case_distribution": {
                "问题类型分布": self._analyze_question_types(selected_cases),
                "本体类型分布": {
                    case["question"]: case_features[i]["ontology_dist"]
                    for i, case in zip(selected_indices, selected_cases)
                }
            },
            "feature_statistics": {
                "平均问题长度": sum(len(case["question"]) 
                          for case in selected_cases) / len(selected_cases),
                "平均表格行数": sum(len(case["table"]) 
                          for case in selected_cases) / len(selected_cases)
            }
        }
        
        return selected_cases, stats
    
    def _analyze_question_types(self, cases: List[Dict]) -> Dict[str, int]:
        """
        分析问题类型分布
        
        Args:
            cases: 案例列表
            
        Returns:
            Dict[str, int]: 问题类型及其数量
        """
        type_count = defaultdict(int)
        for case in cases:
            question = case["question"].lower()
            if "how many" in question:
                type_count["计数类"] += 1
            elif "what" in question:
                type_count["查找类"] += 1
            elif "when" in question:
                type_count["时间类"] += 1
            elif "where" in question:
                type_count["地点类"] += 1
            elif "who" in question:
                type_count["人物类"] += 1
            else:
                type_count["其他"] += 1
        return dict(type_count)