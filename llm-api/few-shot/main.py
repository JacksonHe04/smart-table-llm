import json
from case_selector import CaseSelector

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
    
    # 选择最合适的3个案例
    selected_cases = selector.select_cases(data_path, query, top_k=5)
    
    # 将选中的案例保存到文件
    output_path = "selected_cases.jsonl"
    with open(output_path, 'w', encoding='utf-8') as f:
        for case in selected_cases:
            json.dump(case, f, ensure_ascii=False)
            f.write('\n')

if __name__ == "__main__":
    main()