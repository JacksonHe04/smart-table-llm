const fs = require('fs');
const readline = require('readline');
const path = require('path');

/**
 * 从源文件随机抽取指定数量的行到目标文件
 * @param {string} sourcePath - 源文件路径
 * @param {string} targetPath - 目标文件路径
 * @param {number} sampleSize - 需要抽取的行数
 */
async function randomSample(sourcePath, targetPath, sampleSize) {
    // 读取所有行
    const lines = [];
    const fileStream = fs.createReadStream(sourcePath);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    // 将每行数据存入数组
    for await (const line of rl) {
        if (line.trim()) {  // 忽略空行
            lines.push(line);
        }
    }

    // 如果请求的样本大小大于总行数，则调整样本大小
    const actualSampleSize = Math.min(sampleSize, lines.length);
    
    // Fisher-Yates 洗牌算法随机抽取
    for (let i = lines.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [lines[i], lines[j]] = [lines[j], lines[i]];
    }

    // 取前 sampleSize 行写入目标文件
    const selectedLines = lines.slice(0, actualSampleSize);
    fs.writeFileSync(targetPath, selectedLines.join('\n'));

    console.log(`成功从 ${sourcePath} 随机抽取 ${actualSampleSize} 行数据到 ${targetPath}`);
}

// 定义文件路径
const sourcePath = path.join(__dirname, 'valid_lower.jsonl');
const targetPath = path.join(__dirname, 'valid_20.jsonl');

// 执行随机抽样
randomSample(sourcePath, targetPath, 20).catch(console.error);