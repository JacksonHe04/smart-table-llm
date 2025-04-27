import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { isCorrect } from './utils/isCorrect.js';

export class Evaluator {
  constructor(openai, prompt) {
    this.openai = openai;
    this.prompt = prompt;
  }

  async evaluateSamples(selectedData, testData, args, startIndex, datasetType) {
    const startTime = Date.now();
    let correctCount = 0;
    const totalSamples = selectedData.length;

    this.printTestInfo(selectedData, testData, args, startIndex, totalSamples);

    for (let i = 0; i < selectedData.length; i++) {
      const item = selectedData[i];
      const result = await this.evaluateSingle(item, i, totalSamples, testData, args, startIndex);
      if (result.isCorrect) {
        correctCount++;
      }
    }

    this.printFinalStats(startTime, correctCount, totalSamples);
    this.logResults(startTime, correctCount, totalSamples, datasetType);
    return {
      totalSamples,
      correctCount,
      accuracy: ((correctCount / totalSamples) * 100).toFixed(2)
    };
  }

  logResults(startTime, correctCount, totalSamples, datasetType) {
    const endTime = Date.now();
    const totalTimeSeconds = ((endTime - startTime) / 1000).toFixed(2);
    const accuracy = ((correctCount / totalSamples) * 100).toFixed(2);
    const timestamp = new Date().toISOString();
    const logMessage = `Timestamp: ${timestamp}\nDataset: ${datasetType}\nTotal Samples: ${totalSamples}\nCorrect Count: ${correctCount}\nAccuracy: ${accuracy}%\nTotal Time: ${totalTimeSeconds} seconds\n\n`;

    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    const logFilePath = path.join(__dirname, 'logs', `${datasetType}-log.txt`);
    fs.appendFileSync(logFilePath, logMessage, 'utf8');
  }

  printTestInfo(selectedData, testData, args, startIndex, totalSamples) {
    console.log(`\n测试范围信息：`);
    console.log(`- 数据集总样本数：${testData.length}`);
    if (args.length === 0 || args.length === 1) {
      const indices = Array.from(selectedData.keys()).map(i => {
        const index = testData.indexOf(selectedData[i]) + 1;
        return `${index}`;
      }).sort((a, b) => parseInt(a) - parseInt(b));
      console.log(`- 本次随机测试样本位置：${indices.join(', ')}`);
    } else {
      console.log(`- 本次测试范围：第 ${startIndex + 1} 个到第 ${startIndex + selectedData.length} 个`);
    }
    console.log(`- 本次测试样本数：${totalSamples}\n`);
  }

  async evaluateSingle(item, index, totalSamples, testData, args, startIndex) {
    const currentProgress = ((index + 1) / totalSamples * 100).toFixed(1);
    
    console.log('\n' + '='.repeat(50) + '\n');
    
    console.log(`测试进度：${index + 1}/${totalSamples} (${currentProgress}%)`);
    if (args.length === 0 || args.length === 1) {
      console.log(`数据集位置：第 ${testData.indexOf(item) + 1} 个`);
    } else {
      console.log(`数据集位置：第 ${startIndex + index + 1} 个`);
    }
    
    const userPrompt = this.prompt.generateUserPrompt(item.table_text, item.statement);
    const systemPrompt = this.prompt.system;
    
    const stream = await this.openai.chat.completions.create({
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      // model: 'doubao-1-5-pro-32k-250115',
      // model: 'doubao-1-5-pro-256k-250115',
      model: 'doubao-1-5-vision-pro-32k-250115',
      stream: true,
    });

    let modelAnswer = '';
    for await (const part of stream) {
      modelAnswer += part.choices[0]?.delta?.content || '';
    }

    const isAnswerCorrect = isCorrect(modelAnswer, item.answer);
    
    console.log(`问题: ${item.statement}`);
    // console.log(`表格内容: ${item.table_text}`);
    console.log(`预期答案: ${item.answer}`);
    console.log(`模型答案: ${modelAnswer.trim()}`);
    console.log(`是否正确: ${isAnswerCorrect}`);

    return { modelAnswer, expectedAnswer: item.answer, isCorrect: isAnswerCorrect };
  }

  printFinalStats(startTime, correctCount, totalSamples) {
    const endTime = Date.now();
    const totalTimeSeconds = ((endTime - startTime) / 1000).toFixed(2);
    const accuracy = ((correctCount / totalSamples) * 100).toFixed(2);

    console.log('\n测试统计信息如下');
    console.log(`总样本数: ${totalSamples}`);
    console.log(`正确数量: ${correctCount}`);
    console.log(`ACC: ${accuracy}%`);
    console.log(`总耗时: ${totalTimeSeconds}秒`);
  }
}