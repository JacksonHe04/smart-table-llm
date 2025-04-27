import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// 指定数据集目录
const DATASETS_DIR = "../datasets";

/**
 * 将原始的表格问答数据转换为SFT训练格式
 * @param {string} inputPath - 输入文件路径
 * @param {string} outputPath - 输出文件路径
 */
function convertFormat(inputPath, outputPath) {
  // 读取输入文件
  const data = fs.readFileSync(inputPath, "utf-8");
  const lines = data.split("\n").filter((line) => line.trim());

  // 转换每一行数据
  const convertedLines = lines.map((line) => {
    const item = JSON.parse(line);

    // 构建system prompt
    const systemPrompt =
      "You are an accurate table Q&A assistant. Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process. Please give the answer directly.";

    // 构建user prompt，直接使用table_text而不是再次stringify
    const userPrompt = `Table Content: ${item.table_text}\n\nQuestion：${item.statement}\n\n`;

    // 构建assistant response
    const assistantResponse = Array.isArray(item.answer)
      ? item.answer.join(", ")
      : item.answer;

    // 构建SFT格式的数据
    const sftFormat = {
      messages: [
        {
          role: "system",
          content: systemPrompt,
        },
        {
          role: "user",
          content: userPrompt,
        },
        {
          role: "assistant",
          content: assistantResponse,
        },
      ],
    };

    // 移除格式化参数，确保每个JSON对象都在一行
    return JSON.stringify(sftFormat);
  });

  // 写入输出文件
  fs.writeFileSync(outputPath, convertedLines.join("\n"));
}

/**
 * 获取输出文件路径
 * @param {string} filename - 输入文件名
 * @returns {string} - 输出文件路径
 */
function getOutputPath(filename) {
  return path.join(DATASETS_DIR, `sft_${filename}`);
}

/**
 * 获取完整的输入文件路径
 * @param {string} filename - 输入文件名
 * @returns {string} - 完整的输入文件路径
 */
function getInputPath(filename) {
  return path.join(DATASETS_DIR, filename);
}

// 主函数：处理命令行参数并执行转换
function main() {
  // 获取命令行参数
  const args = process.argv.slice(2);
  
  if (args.length !== 1) {
    console.error('使用方法: node format-conversion.js <输入文件名>');
    process.exit(1);
  }
  
  const filename = args[0];
  const inputPath = getInputPath(filename);
  
  // 检查输入文件是否存在
  if (!fs.existsSync(inputPath)) {
    console.error(`错误：输入文件 "${inputPath}" 不存在`);
    process.exit(1);
  }
  
  // 生成输出文件路径
  const outputPath = getOutputPath(filename);
  
  try {
    // 执行转换
    convertFormat(inputPath, outputPath);
    console.log(`转换完成！输出文件：${outputPath}`);
  } catch (error) {
    console.error('转换过程中发生错误：', error);
    process.exit(1);
  }
}

// 如果是直接运行此文件（而不是作为模块导入），则执行main函数
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}

export default convertFormat;
