import 'dotenv/config';
import { Evaluator } from './evaluator.js';
import { openai } from './utils/openai-client.js';
import { readJSONL } from './utils/jsonl-utils.js';
import { selectData } from './utils/data-selector.js';

async function main() {
  const args = process.argv.slice(2);
  
  // 获取 prompt 文件名，默认使用 simple-prompt
  let promptFile = 'simple-prompt';
  if (args[0] && args[0].startsWith('--prompt=')) {
    promptFile = args[0].split('=')[1];
    args.shift(); // 移除 prompt 参数
  }

  // 获取数据集文件名，默认使用 test_lower.jsonl
  let datasetFile = 'test_lower.jsonl';
  if (args[0] && args[0].startsWith('--dataset=')) {
    datasetFile = args[0].split('=')[1];
    args.shift(); // 移除 dataset 参数
  }
  
  // 动态导入 prompt 文件
  const prompt = (await import(`./prompts/${promptFile}.js`)).default;
  
  const testData = readJSONL(`../datasets/${datasetFile}`);
  const { selectedData, startIndex } = selectData(testData, args);

  const evaluator = new Evaluator(openai, prompt);
  await evaluator.evaluateSamples(selectedData, testData, args, startIndex, 'test');
}

main().catch(console.error);