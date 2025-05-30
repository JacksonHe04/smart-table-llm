# 基于大模型的智能表格问答

一个基于豆包大模型的智能表格问答系统，能够根据输入的表格数据和自然语言问题生成准确的答案。支持多种提示词工程方法（Zero-shot、One-shot、Few-shot）和模型微调（SFT + Lora），在测试集上达到71.29%的准确率。

## 问题定义
- 输入：一个表格数据（csv/excel），一个自然语言问题。
- 输出：根据表格数据，自然语言问题对应的答案。
- 示例：
    - 问题：how many people stayed at least 3 years in office?
    - 表格数据：
    ``` 
    [["","name","took office","left office","party","notes/events"],["11","william mccreery","march 4, 1803","march 3, 1809","democratic republican",""],["12","alexander mckim","march 4, 1809","march 3, 1815","democratic republican",""],["13","william pinkney","march 4, 1815","april 18, 1816","democratic republican","resigned to accept position as minister plenipotentiary to russia"],["14","peter little","september 2, 1816","march 3, 1823","democratic republican",""],["14","peter little","march 4, 1823","march 3, 1825","jacksonian dr",""],["14","peter little","march 4, 1825","march 3, 1829","adams",""],["15","benjamin c. howard","march 4, 1829","march 3, 1833","jacksonian",""]]
    ```
    - 答案：4
    - 评价指标：ACC

我在项目中负责的工作是通过大模型 API 调用来批量处理数据集的问题，并通过提示词工程进一步优化模型在数据集上的表现。测试的日志为 [test-log.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-log.txt)

## Zero Shot

我首先编写了 Zero-shot 的系统提示词 [zero-shot-prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/zero-shot-prompt.js)：

```
You are an accurate table Q&A assistant. Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.
"table_text":table content;
"statement": question.
Please give the answer directly.
```

在代码中是：

```javascript
const prompt = {
  get system() {
    return "You are an accurate table Q&A assistant.";
  },
  generateUserPrompt: (tableText, statement) =>
    `Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.\n\nTable Content: ${tableText}\n\nQuestion：${statement}\n\nPlease give the answer directly.`,
};

export default prompt;
```

我（何锦诚）、郑宇榕、李凯文基于测试集的同一个随机子集[test_100.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/datasets/test_100.jsonl)分别展开了测试。

## Doubao 1.5 Pro

我将该提示词应用到 doubao-1-5-pro-256k 模型上，ACC 是 57%，这是我的工作的基础。

在针对训练集的工作中，我让模型在批量处理训练集时将回答错误的问题及其内容存储到一个名为 [wrong_answers.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/wrong_answers.jsonl) 的文件中。

### 基于训练集的错误案例编写规则提示词

在经历了多次基于训练集 [train_lower.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/datasets/train_lower.jsonl) 的随机抽取批量测试，我在 [to_train_rules.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/to_train_rules.jsonl) 文件中选取了 39 个回答错误的案例，针对这些案例的错误原因进行分析，并据此为提示词增加了 15 条规则。

我把添加了规则的提示词称为 jincheng-prompt，在项目文件中是 [simple-prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/simple-prompt.js)。

基于 [simple-prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/simple-prompt.js)，doubao-1.5-pro-32k 在 [test_100.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/datasets/test_100.jsonl) 上的 ACC 是 62%，相比于 [Zero-shot](<(https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/zero-shot-prompt.js)>) 的 57% 提高了 5%。

我把规则从中文换成了英文后，ACC 达到了 63%，提高了 1%。

```javascript
const prompt = {
  rules: [
    "Only output the final answer, without any explanation",
    "The answer must be in exactly the same format as required by the question",
    "If it is a country name, use the full country name instead of the abbreviation",
    "If the quantity is asked, the count must be accurate",
    "If the answer is a number, output the number without any units",
    "If there are multiple possible answers, only output the one that best meets the requirements of the question",
    "The answer must be based on the data in the table and do not use external knowledge",
    "If calculations are involved, they must be accurately calculated without estimation",
    "Keep the case of the answer consistent with what is required by the question",
    "For dates and times, keep the original format",
    "If there are null or missing values in the table, exclude these values during calculations",
    "For the content within quotation marks, the original format must be maintained, including the quotation marks themselves",
    "Carefully check all cases that meet the criteria when counting",
    "For sorting and comparison, consider the data in all relevant columns",
    "If the answer involves specific text content, it must exactly match the original text, including case and punctuation marks",
  ],
  get system() {
    return (
      "You are an accurate table Q&A assistant.\n" +
      this.rules.map((rule, index) => `${index + 1}. ${rule}`).join("\n")
    );
  },
  generateUserPrompt: (tableText, statement) =>
    `Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.\n\nTable Content: ${tableText}\n\nQuestion：${statement}\n\nPlease give the answer directly.`,
};

export default prompt;
```

我在测试集上进行了独立的 5 次测试，每次随机抽取 100 个案例，ACC 的平均值是 61.60%。

测试日志为 [test-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-1.txt)、[test-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-2.txt)、[test-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-3.txt)、[test-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-4.txt)、[test-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-5.txt)。

### 更复杂的规则提示词

根据[谷歌提示工程指南](https://ai.google.dev/gemini-api/docs/prompting-strategies#few-shot)，我重新深度优化了提示词，新增了多条规则，并给出了具体执行的步骤，于[prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/prompt.js)中，随机测试了 100 个案例，ACC 反而降低到 59%。

提示词复杂化导致准确率下降的原因主要有以下几点：

1. 认知负载增加：更复杂的提示词包含了更多的规则和步骤，这增加了模型的认知负载。当模型需要同时处理和遵循多个复杂规则时，可能会影响其对核心任务（表格问答）的注意力分配。

2. 规则冲突：随着规则数量的增加，不同规则之间可能产生潜在的冲突或模糊性，导致模型在决策时出现犹豫或错误。

3. 过度约束：过多的具体执行步骤可能限制了模型的灵活性，使其无法充分利用自身在表格理解和问答方面的能力。

4. 输出格式干扰：复杂的提示词可能导致模型过分关注输出格式的规范性，而不是答案的准确性。

## One Shot

我从训练集中选取了 1 个案例作为 one-shot 的例子，在 [one-shot.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/one-shot.js) 中（不包含规则）。

同样在 doubao-1.5-pro-32k 上进行了独立的 5 次测试，每次随机抽取 100 个案例，ACC 的平均值是 63%。

测试日志为 [one-shot-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-1.txt)、[one-shot-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-2.txt)、[one-shot-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-3.txt)、[one-shot-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-4.txt)、[one-shot-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-5.txt)。

## Few Shot

one-shot 学习仅为模型提供单个示例用于学习和预测，数据极度稀缺，模型需从这唯一示例中快速捕捉关键特征并作出判断。few-shot 学习则提供少量（通常 2-10 个）示例，为模型提供更多参考信息，减轻学习负担。在文本分类任务里，给模型提供 3-5 个不同类别的文本示例，帮助其对新文本分类。

我阅读了 [ConsistNER: Towards Instructive NER Demonstrations for LLMs with the Consistency of Ontology and Context](https://ojs.aaai.org/index.php/AAAI/article/view/29892#:~:text=To%20address%20this%20issue%2C%20we%20propose%20ConsistNER%2C%20a,incorporates%20ontological%20and%20contextual%20information%20for%20low-resource%20NER.) 这篇论文，决定基于该论文的思想，实现一个案例选择器。该选择器通过计算本体分布相似度和上下文语义相似度来为每个新的查询选择最合适的 few-shot 案例。具体来说：

1. 本体分布相似度：通过预定义的本体类型（如时间、地点、人物、事件、数字、属性等）对表格列进行分类，计算不同案例间本体分布的相似程度。

2. 上下文语义相似度：使用 BERT 模型提取问题的语义表示，计算不同问题之间的余弦相似度。

3. 综合评分：将本体分布相似度和上下文语义相似度按照 0.5 的权重进行加权平均，得到案例与查询问题的综合相似度分数。

于是我先使用 one-shot 的提示词对训练集进行了测试，随机选取了 300 个案例，ACC 是 67%，详细日志在[one-shot-train.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-train.txt)

我把失败的案例存储到了 [wrong_answers_train.jsonl]( [wrong_answers_train.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/wrong_answers_train.jsonl) 文件中，一共积累了 99 个案例。

对于积累的 99 个失败案例，我们使用论文中的本体一致性和上下文一致性方法，对每个新的查询问题，通过计算本体分布相似度和语义相似度来选择最相似的案例。这种方法不仅考虑了问题的语义相似性，还考虑了表格结构的相似性，能够更准确地找到与当前问题相关的示例。具体实现在 [case_selector.py](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/few-shot/case_selector.py) 中。

我使用此方法从这 99 个失败案例中选取了 3 个案例作为 few-shot 的例子，在 [few-shot.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/few-shot.js) 中（不包含规则提示词）。

## Doubao 1.5 Vision Pro 32k

因为不管是通过训练集优化规则提示词，还是通过 few-shot 来优化提示词，模型的表现都没有明显的提升，所以我尝试了 doubao-1.5-vision-pro-32k 模型，该模型的表现相比于 doubao-1.5-pro-32k 显著提升。

```javascript
const stream = await this.openai.chat.completions.create({
  messages: [
    { role: "system", content: systemPrompt },
    { role: "user", content: userPrompt },
  ],
  // model: 'doubao-1-5-pro-32k-250115',
  // model: 'doubao-1-5-pro-256k-250115',
  model: "doubao-1-5-vision-pro-32k-250115",
  stream: true,
});
```
使用 Zero-shot 的提示词，在测试集上进行了独立的 5 次测试，每次随机抽取 100 个案例，ACC 的平均值是 69.20%。

测试日志为  [vision-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-1.txt)、[vision-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-2.txt)、[vision-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-3.txt)、 [vision-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-4.txt)、[vision-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-5.txt)。

使用我们的规则提示词，在测试集上进行了独立的 5 次测试，每次随机抽取 100 个案例，ACC 的平均值是 70.40%，是我首次在测试集上突破了 70% 的 ACC。

测试日志为: [vision-pro-simple-prompt-1.txt](htURL_ADDRESS.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-1.txt)、[vision-pro-simple-prompt-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-2.txt)、[vision-pro-simple-prompt-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-3.txt)、[vision-pro-simple-prompt-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-4.txt)、[vision-pro-simple-prompt-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-5.txt)。

采用视觉模型后性能显著提升的原因可以从以下几个方面分析：

1. 结构感知能力：视觉模型通过预训练已经具备了强大的图像结构识别能力，这种能力可以自然地迁移到表格结构的理解上。表格本质上是一种二维结构，与图像数据具有相似的空间关系。

2. 多模态理解：视觉模型在处理表格时，不仅能够理解文本内容，还能够感知单元格的位置关系、表格的布局等视觉特征，这种多模态理解能力有助于更准确地解答问题。

3. 上下文关联：视觉模型可以更好地捕捉表格中的全局信息，理解单元格之间的空间关联关系，这对于需要关联多个列或行的问题尤其有帮助。

4. 预训练优势：视觉模型在预训练阶段接触了大量的结构化视觉数据，这种经验可能有助于其更好地理解和处理表格这种结构化数据。

## Doubao 1.5 Vision Pro 32k + Few Shot

最后我尝试了在 doubao-1.5-vision-pro-32k 模型上使用 few-shot 来优化提示词。
在测试集上进行了独立的 5 次测试，每次随机抽取 100 个案例，ACC 的平均值是 71.20%，是我目前在测试集上的最高分。

```javascript
const prompt = {
  get system() {
    return "You are an accurate table Q&A assistant.";
  },
  generateUserPrompt: (tableText, statement) =>
    `Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.

Example 1:
Question: who was the first cyclist to finish?
Table Content: rank,cyclist,team,time,uci protour\npoints,1,alejandro valverde (esp),caisse d'epargne,5h 29' 10",40,2,alexandr kolobnev (rus),team csc saxo bank,s.t.,30,3,davide rebellin (ita),gerolsteiner,s.t.,25,4,paolo bettini (ita),quick step,s.t.,20,5,franco pellizotti (ita),liquigas,s.t.,15,6,denis menchov (rus),rabobank,s.t.,11,7,samuel sánchez (esp),euskaltel-euskadi,s.t.,7,8,stéphane goubert (fra),ag2r-la mondiale,+ 2",5,9,haimar zubeldia (esp),euskaltel-euskadi,+ 2",3,10,david moncoutié (fra),cofidis,+ 2",1
Answer: Alejandro Valverde

Example 2:
Question: what show was he in before running man
Table Content: [["year","title","hangul","network","further info"],["2008","pretty boys: a wrong situation","꽃미남 아롱사태","mnet",""],["2009","let's go dream team! season 2","출발 드림팀2","kbs2","variety show"],["2009-10","music bank","뮤직뱅크","kbs2","music show, as mc"],["2010-11","running man","런닝맨","sbs","variety show"],["2011","i'm real: song joong-ki","i'm real 송중기","qtv",""],["2011","everyone dramatic","에브리원 드라마틱","mbc",""],["2011","made in u","메이드 인 유","jtbc","audition show, as mc"],["2011-12","tears of the antarctic","남극의 눈물","mbc","documentary, as narrator"]]
Answer: Music Bank

Example 3:
Question: how many athletes finished race 1?
Table Content: [["athlete","event","race 1\\ntime","race 2\\ntime","total\\ntime","total\\nrank"],["jóhann haraldsson","giant slalom","1:19.10","dnf","dnf","–"],["kristinn magnússon","giant slalom","1:17.50","1:16.29","2:33.79","42"],["björgvin björgvinsson","giant slalom","1:15.86","dnf","dnf","–"],["kristinn magnússon","slalom","dnf","–","dnf","–"],["björgvin björgvinsson","slalom","dnf","–","dnf","–"],["jóhann haraldsson","slalom","56.98","1:00.19","1:57.17","28"],["kristinn björnsson","slalom","53.05","56.76","1:49.81","21"]]
Answer: 4

Now, please answer the following question:
Table Content: ${tableText}
Question: ${statement}

Please give the answer directly.`,
};

export default prompt;
```

测试日志为：[vision-pro-few-shot-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-few-shot-1.txt)、[vision-pro-few-shot-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-few-shot-2.txt)、[vision-pro-few-shot-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-few-shot-3.txt)、[vision-pro-few-shot-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-few-shot-4.txt)、[vision-pro-few-shot-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-few-shot-5.txt)。

测试结果表明，在表格数据上，doubao-1.5-vision-pro-32k 模型在处理表格数据时表现良好，能够正确地识别表格结构并生成有效的答案。

few-shot 提示词的效果也很明显，在测试集上的表现优于规则提示词。

将 few-shot 提示词应用到 doubao-1.5-vision-pro-32k 模型上，可以得到更好的结果。

确定之后，我在整个测试集上进行了测试，测试集共有 4344 个测试样本，测试次数为 1，正确数为 3097，用时 4420.90s，ACC 是 71.29%。

测试日志为：[vision-pro-few-shot-all.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-few-shot-all.txt)

## SFT + Lora
## 使用 200 个训练集样本 + 20 个验证集样本微调
我开始尝试使用 SFT 来优化模型，基于字节跳动的火山方舟平台对 doubao-lite-32k 进行 SFT + Lora 的模型精调。

但是我把整个训练集放入火山方舟的微调任务时，被告知要花费数百元的费用，所以只能选择 200 个训练样本和 20 个验证样本。

于是尝试使用 200 个训练样本和 20 个验证样本进行微调。

经过 15 分 27 秒的训练，训练完成后导出模型。
我在测试集上进行了 5 次测试（仅有系统提示词），每次随机抽取 100 个案例，ACC 的平均值是 36.4%。原因是训练样本太少，模型的泛化能力很差。

测试日志为：[sft-2-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/sft-2-1.txt)、[sft-2-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/sft-2-2.txt)、[sft-2-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/sft-2-3.txt)、[sft-2-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/sft-2-4.txt)、[sft-2-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/sft-2-5.txt)。

## 测试结果表格
<!-- TODO -->
| 模型 | 方法 | ACC | 测试样本数 | 测试次数 | 备注 |
|------|------------|-----|------------|----------|------|
| doubao-1.5-pro-256k | Zero-shot | 57% | 100 | 1 | 基础测试 |
| doubao-1.5-pro-32k | 规则提示词(中文) | 62% | 100 | 1 | 相比Zero-shot提升5% |
| doubao-1.5-pro-32k | 规则提示词(英文) | 63% | 100 | 5 | 平均值61.60% |
| doubao-1.5-pro-32k | 复杂规则提示词 | 59% | 100 | 1 | 性能反而下降 |
| doubao-1.5-pro-32k | One-shot | 63% | 100 | 5 | 平均值63% |
| doubao-1.5-pro-32k | One-shot (训练集) | 67% | 300 | 1 | 在训练集上的测试 |
| doubao-lite-32k | SFT + Lora | 36.4% | 100 | 5 | 由于训练样本较少，效果不理想 |
| doubao-1.5-vision-pro-32k | Zero-shot | 69.20% | 100 | 5 | 性能提升 |
| doubao-1.5-vision-pro-32k | 规则提示词 | 70.40% | 100 | 5 | 首次突破70% |
| doubao-1.5-vision-pro-32k | Few-shot | 71.20% | 100 | 5 | Vision + Few Shot |
| doubao-1.5-vision-pro-32k | Few-shot | 71.29% | 4344 | 1 | 在测试集全集上的测试 |