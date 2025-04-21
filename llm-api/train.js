import 'dotenv/config';
import prompt from './prompt.js';
import { Evaluator } from './evaluator.js';
import { openai } from './utils/openai-client.js';
import { readJSONL, logWrongAnswer } from './utils/jsonl-utils.js';
import { selectData } from './utils/data-selector.js';

class LoggingEvaluator extends Evaluator {
  async evaluateSingle(item, index, totalSamples, testData, args, startIndex) {
    const result = await super.evaluateSingle(item, index, totalSamples, testData, args, startIndex);
    
    if (!result.isCorrect) {
      logWrongAnswer(item, result.modelAnswer);
    }
    
    return result;
  }
}

async function main() {
  const args = process.argv.slice(2);
  const testData = readJSONL('../datasets/train_lower.jsonl');
  const { selectedData, startIndex } = selectData(testData, args);

  const evaluator = new LoggingEvaluator(openai, prompt);
  await evaluator.evaluateSamples(selectedData, testData, args, startIndex);
}

main();