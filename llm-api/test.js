import 'dotenv/config';
import prompt from './prompts/prompt.js';
import { Evaluator } from './evaluator.js';
import { openai } from './utils/openai-client.js';
import { readJSONL } from './utils/jsonl-utils.js';
import { selectData } from './utils/data-selector.js';

async function main() {
  const args = process.argv.slice(2);
  const testData = readJSONL('../datasets/test_lower.jsonl');
  const { selectedData, startIndex } = selectData(testData, args);

  const evaluator = new Evaluator(openai, prompt);
  await evaluator.evaluateSamples(selectedData, testData, args, startIndex, 'test');
}

main();