import json
from case_selector import CaseSelector
from datetime import datetime

def main():
    """
    主函数：从错误答案数据集中自动选择具有代表性的few-shot案例
    """
    # 初始化案例选择器
    selector = CaseSelector()
    
    # 读取wrong_answers.jsonl文件
    data_path = "../wrong_answers.jsonl"
    
    # 直接从数据集中选择具有代表性的案例
    selected_cases, stats = selector.select_representative_cases(data_path, top_k=5)
    
    # 将统计信息保存到单独的文件
    stats_output_path = "selection_stats.json"
    with open(stats_output_path, 'w', encoding='utf-8') as f:
        stats_output = {
            "type": "statistics",
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "总处理数据量": stats["total_processed"],
                "案例分布特征": stats["case_distribution"],
                "特征统计": stats["feature_statistics"]
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