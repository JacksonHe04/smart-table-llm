/**
 * 判断模型回答是否正确
 * @param {string} modelAnswer - 模型的回答
 * @param {string|string[]} expectedAnswer - 预期的答案，可以是字符串或字符串数组
 * @returns {boolean} - 返回判断结果
 */
export function isCorrect(modelAnswer, expectedAnswer) {
  // 处理预期答案为数组的情况
  const answer = Array.isArray(expectedAnswer) ? expectedAnswer.join(',') : expectedAnswer;
  
  // 清理函数：去除所有空格和符号，并标准化特殊字符
  const cleanText = (text) => {
    return text
      .toLowerCase()
      .normalize('NFKD')                // 将特殊字符分解为基本字符和变音符号
      .replace(/\([^)]*\)/g, '')        // 移除英文括号及其中的内容
      .replace(/[\u0300-\u036f]/g, '') // 移除所有变音符号
      .replace(/\s+/g, '')             // 去除所有空白字符（空格、制表符、换行等）
      .replace(/[^\u4e00-\u9fa5a-z0-9]/g, '');  // 只保留中文、英文字母和数字
  };

  // 对比清理后的文本
  console.log('cleanText(answer)', cleanText(answer));
  console.log('cleanText(modelAnswer)', cleanText(modelAnswer));
  return cleanText(modelAnswer) === cleanText(answer);
}