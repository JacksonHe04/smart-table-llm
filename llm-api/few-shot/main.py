import json
from case_selector import CaseSelector
from datetime import datetime

def main():
    """
    主函数：演示如何使用CaseSelector选择few-shot案例
    """
    # 初始化案例选择器
    selector = CaseSelector()
    
    # 读取wrong_answers.jsonl文件
    data_path = "../wrong_answers.jsonl"
    
    # 假设我们要为新的查询问题选择案例
    query = {
        "question": "your new question here",
        "table": [["column1", "value1"], ["column2", "value2"]]
    }
    
    # 选择最合适的案例并获取统计信息
    selected_cases, stats = selector.select_cases(data_path, query, top_k=5)
    
    # 将统计信息保存到单独的文件
    stats_output_path = "selection_stats.json"
    with open(stats_output_path, 'w', encoding='utf-8') as f:
        stats_output = {
            "type": "statistics",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "总处理数据量": stats["total_processed"],
                "长度过滤后数据量": stats["length_filtered"],
                "筛选比例": f"{(stats['length_filtered']/stats['total_processed']*100):.2f}%",
                "相似度排名": [
                    {
                        "问题": item["question"],
                        "相似度得分": item["similarity_score"]
                    } for item in stats["top_similarities"]
                ],
                "查询问题本体分布": {
                    k: round(v, 4) for k, v in stats["ontology_distribution"].items()
                }
            }
        }
        json.dump(stats_output, f, ensure_ascii=False, indent=2)
    
    # 将选中的案例保存到单独的文件
    cases_output_path = "selected_cases.jsonl"
    with open(cases_output_path, 'w', encoding='utf-8') as f:
        for case in selected_cases:
            json.dump(case, f, ensure_ascii=False)
            f.write('\n')

if __name__ == "__main__":
    main()