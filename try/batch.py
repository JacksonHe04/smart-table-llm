import asyncio
import json
import sys
from datetime import datetime
from env import ARK_API_KEY as api_key

import uvloop

from volcenginesdkarkruntime import AsyncArk

# Authentication
# 1.If you authorize your endpoint using an API key, you can set your api key to environment variable "ARK_API_KEY"
# or specify api key by Ark(api_key="${YOUR_API_KEY}").
# Note: If you use an API key, this API key will not be refreshed.
# To prevent the API from expiring and failing after some time, choose an API key with no expiration date.

# 2.If you authorize your endpoint with Volcengine Identity and Access Management（IAM), set your api key to environment variable "VOLC_ACCESSKEY", "VOLC_SECRETKEY"
# or specify ak&sk by Ark(ak="${YOUR_AK}", sk="${YOUR_SK}").
# To get your ak&sk, please refer to this document(https://www.volcengine.com/docs/6291/65568)
# For more information，please check this document（https://www.volcengine.com/docs/82379/1263279）

async def process_jsonl_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

async def worker(worker_id, data_batch, results):
    client = AsyncArk(api_key=api_key)  # 修改这里，显式传入 api_key
    print(f"Worker {worker_id} is starting.")
    
    for i, item in enumerate(data_batch):
        print(f"Worker {worker_id} task {i} is running.")
        try:
            # 构建提示词
            prompt = f"根据以下表格回答问题：\n表格：{item['table_text']}\n问题：{item['statement']}"
            
            completion = await client.batch_chat.completions.create(
                model="ep-bi-20250421172448-2szkg",
                messages=[
                    {"role": "system", "content": "你是一个专门解答表格问题的AI助手。请直接给出答案，不要解释过程。"}, 
                    {"role": "user", "content": prompt},
                ],
            )
            
            model_answer = completion.choices[0].message.content.strip()
            expected_answer = item['answer'][0] if isinstance(item['answer'], list) else item['answer']
            
            is_correct = model_answer == expected_answer
            if is_correct:
                results['correct'] += 1
                
            print(f"问题: {item['statement']}")
            print(f"预期答案: {expected_answer}")
            print(f"模型答案: {model_answer}")
            print(f"是否正确: {is_correct}\n")
            
        except Exception as e:
            print(f"Worker {worker_id} task {i} failed with error: {e}")
        else:
            print(f"Worker {worker_id} task {i} is completed.")
            
    print(f"Worker {worker_id} is completed.")


async def main():
    start = datetime.now()
    max_concurrent_tasks = 10  # 减少并发数以避免API限制
    
    # 读取测试数据
    test_data = await process_jsonl_data('test_mini.jsonl')
    total_samples = len(test_data)
    
    # 使用字典来存储结果
    results = {'correct': 0}
    
    # 将数据平均分配给workers
    batch_size = (total_samples + max_concurrent_tasks - 1) // max_concurrent_tasks
    data_batches = [test_data[i:i + batch_size] for i in range(0, total_samples, batch_size)]
    
    # 创建任务列表
    tasks = [worker(i, batch, results) for i, batch in enumerate(data_batches)]
    
    # 等待所有任务完成
    await asyncio.gather(*tasks)
    
    end = datetime.now()
    accuracy = (results['correct'] / total_samples) * 100
    
    print(f"\n测试结果统计:")
    print(f"总样本数: {total_samples}")
    print(f"正确数量: {results['correct']}")
    print(f"准确率: {accuracy:.2f}%")
    print(f"总耗时: {end - start}")



if __name__ == "__main__":
    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            runner.run(main())
    else:
        uvloop.install()
        asyncio.run(main())