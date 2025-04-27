import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url';

// 获取 ES modules 中的 __dirname 等价物
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * 将原始的 SFT 数据集转换为测试格式
 * @param {string} inputPath - 输入文件路径
 * @param {string} outputPath - 输出文件路径
 */
function convertSFTToTest(inputPath, outputPath) {
    // 读取输入文件
    const input = fs.readFileSync(inputPath, 'utf-8');
    
    // 按行分割
    const lines = input.trim().split('\n');
    
    // 转换每一行
    const converted = lines.map(line => {
        const data = JSON.parse(line);
        const messages = data.messages;
        
        // 提取系统消息、用户提示和助手回答
        const systemMsg = messages[0].content;
        const userMsg = messages[1].content;
        const assistantMsg = messages[2].content;
        
        // 返回新格式
        return JSON.stringify({
            system: systemMsg,
            prompt: userMsg,
            answer: assistantMsg
        });
    });
    
    // 写入输出文件
    fs.writeFileSync(outputPath, converted.join('\n'));
}

// 获取命令行参数中的输入和输出文件路径
const inputPath = process.argv[2] || path.join(__dirname, '../datasets/sft_test_lower.jsonl');
const outputPath = process.argv[3] || path.join(__dirname, '../datasets/sft_test_converted.jsonl');

// 执行转换
try {
    convertSFTToTest(inputPath, outputPath);
    console.log('转换完成！');
} catch (error) {
    console.error('转换过程中发生错误:', error);
}