import fs from 'fs';
import path from 'path';

/**
 * 将大型JSONL文件分割成多个小文件
 * @param {string} inputPath - 输入文件路径
 * @param {string} outputDir - 输出目录路径
 * @param {number} chunkSize - 每个文件包含的记录数，默认1000
 */
function splitJsonlFile(inputPath, outputDir, chunkSize = 1000) {
    // 确保输出目录存在
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    // 读取输入文件
    const data = fs.readFileSync(inputPath, 'utf8');
    const lines = data.split('\n').filter(line => line.trim() !== '');

    // 计算需要分割的文件数量
    const fileCount = Math.ceil(lines.length / chunkSize);
    
    // 获取输入文件名（不含扩展名）
    const inputFileName = path.basename(inputPath, path.extname(inputPath));

    // 分割文件
    for (let i = 0; i < fileCount; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, lines.length);
        const chunk = lines.slice(start, end).join('\n');

        // 生成输出文件名
        const outputPath = path.join(
            outputDir, 
            `${inputFileName}_part${i + 1}.jsonl`
        );

        // 写入文件
        fs.writeFileSync(outputPath, chunk);
        console.log(`已写入文件: ${outputPath}`);
    }

    console.log(`分割完成，共生成 ${fileCount} 个文件`);
}

// 使用示例
const inputFile = '/Users/jackson/Terms/25-1-Junior-II/nlp-practice/llm-api/sft/datasets/sft_test_converted.jsonl';
const outputDir = '/Users/jackson/Terms/25-1-Junior-II/nlp-practice/llm-api/sft/datasets/split';

// 执行分割
splitJsonlFile(inputFile, outputDir);