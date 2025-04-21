import fs from 'fs';

export function readJSONL(filePath) {
  const data = fs.readFileSync(filePath, 'utf-8');
  return data.split('\n').filter(line => line.trim()).map(line => JSON.parse(line));
}

export function logWrongAnswer(item, modelAnswer) {
  const logEntry = {
    question: item.statement,
    table: item.table_text,
    expected: item.answer,
    model_answer: modelAnswer,
    timestamp: new Date().toISOString()
  };
  
  fs.appendFileSync('wrong_answers.jsonl', JSON.stringify(logEntry) + '\n');
}