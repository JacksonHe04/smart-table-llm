# 何锦诚的工作内容学术报告

在本项目的研究进程中，本人（何锦诚）主要负责基于大模型 API 开展数据集的批量处理工作，并通过提示词工程对模型在数据集上的表现进行优化提升。具体工作内容如下：

## 一、Zero Shot 相关工作

首先，本人编写了 Zero-shot 的系统提示词，该提示词的具体内容存储于 [zero-shot-prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/zero-shot-prompt.js) 文件中。其核心内容为：“You are an accurate table Q\&A assistant. Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process. "table\_text":table content; "statement": question. Please give the answer directly.” 在代码实现层面，采用如下 JavaScript 代码进行定义：



```
const prompt = {

&#x20; get system() {

&#x20;   return "You are an accurate table Q\&A assistant.";

&#x20; },

&#x20; generateUserPrompt: (tableText, statement) =>

&#x20;   \`Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.\n\nTable Content: \${tableText}\n\nQuestion：\${statement}\n\nPlease give the answer directly.\`,

};

export default prompt;
```

随后，本人与郑宇榕、李凯文基于测试集的同一个随机子集 [test\_100.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/datasets/test_100.jsonl) 分别展开测试工作。将上述提示词应用到 doubao-1-5-pro-256k 模型上，经测试，该模型在该测试集上的准确率（ACC）达到 57%，此结果为本后续工作奠定了重要基础。

在针对训练集的工作中，为了更好地优化模型性能，本人设计了将模型在批量处理训练集时回答错误的问题及其内容存储到 [wrong\_answers.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/wrong_answers.jsonl) 文件的机制。

### （一）基于训练集的错误案例编写规则提示词

通过对训练集 [train\_lower.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/datasets/train_lower.jsonl) 进行多次随机抽取批量测试，从 [to\_train\_rules.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/to_train_rules.jsonl) 文件中精心选取了 39 个回答错误的案例。针对这些案例的错误原因展开深入分析，在此基础上，为提示词新增了 15 条规则，并将添加规则后的提示词命名为 jincheng-prompt，其在项目文件中的存储路径为 [simple-prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/simple-prompt.js)。

基于 [simple-prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/simple-prompt.js) 提示词，在 doubao-1.5-pro-32k 模型上，对 [test\_100.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/datasets/test_100.jsonl) 测试集进行测试，结果显示准确率（ACC）达到 62%，相较于 Zero-shot 提示词的 57%，提升了 5 个百分点。进一步将规则从中文转换为英文后，准确率（ACC）提升至 63%，较中文规则提示词又提高了 1 个百分点。对应的 JavaScript 代码如下：



```
const prompt = {

&#x20; rules: \[

&#x20;   "Only output the final answer, without any explanation",

&#x20;   "The answer must be in exactly the same format as required by the question",

&#x20;   "If it is a country name, use the full country name instead of the abbreviation",

&#x20;   "If the quantity is asked, the count must be accurate",

&#x20;   "If the answer is a number, output the number without any units",

&#x20;   "If there are multiple possible answers, only output the one that best meets the requirements of the question",

&#x20;   "The answer must be based on the data in the table and do not use external knowledge",

&#x20;   "If calculations are involved, they must be accurately calculated without estimation",

&#x20;   "Keep the case of the answer consistent with what is required by the question",

&#x20;   "For dates and times, keep the original format",

&#x20;   "If there are null or missing values in the table, exclude these values during calculations",

&#x20;   "For the content within quotation marks, the original format must be maintained, including the quotation marks themselves",

&#x20;   "Carefully check all cases that meet the criteria when counting",

&#x20;   "For sorting and comparison, consider the data in all relevant columns",

&#x20;   "If the answer involves specific text content, it must exactly match the original text, including case and punctuation marks",

&#x20; ],

&#x20; get system() {

&#x20;   return (

&#x20;     "You are an accurate table Q\&A assistant.\n" +

&#x20;     this.rules.map((rule, index) => \`\${index + 1}. \${rule}\`).join("\n")

&#x20;   );

&#x20; },

&#x20; generateUserPrompt: (tableText, statement) =>

&#x20;   \`Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.\n\nTable Content: \${tableText}\n\nQuestion：\${statement}\n\nPlease give the answer directly.\`,

};

export default prompt;
```

此外，本人在测试集上进行了 5 次独立测试，每次随机抽取 100 个案例，经计算，准确率（ACC）的平均值为 61.60%，测试日志分别存储于 [test-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-1.txt)、[test-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-2.txt)、[test-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-3.txt)、[test-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-4.txt)、[test-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/test-5.txt) 文件中。

### （二）更复杂的规则提示词

参考 [谷歌提示工程指南](https://ai.google.dev/gemini-api/docs/prompting-strategies#few-shot)，本人对提示词进行重新深度优化，新增多条规则并详细给出具体执行步骤，优化后的提示词存储于 [prompt.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/prompt.js) 文件中。然而，在随机测试 100 个案例后发现，模型准确率（ACC）反而下降至 59%。经分析，提示词复杂化导致准确率下降的原因主要包括以下几个方面：

**认知负载增加**：更复杂的提示词包含了更多的规则和步骤，这显著增加了模型的认知负载。当模型需要同时处理和遵循多个复杂规则时，其对核心任务（表格问答）的注意力分配受到影响，进而导致性能下降。

**规则冲突**：随着规则数量的增多，不同规则之间可能产生潜在的冲突或模糊性，使得模型在决策过程中出现犹豫或错误判断。

**过度约束**：过多的具体执行步骤在一定程度上限制了模型的灵活性，使其无法充分发挥自身在表格理解和问答方面的能力。

**输出格式干扰**：复杂的提示词可能使模型过度关注输出格式的规范性，而忽视了答案本身的准确性。

## 二、One Shot 相关工作

本人从训练集中选取 1 个案例作为 one-shot 的示例，相关代码存储于 [one-shot.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/one-shot.js) 文件中（该提示词不包含规则）。同样在 doubao-1.5-pro-32k 模型上进行 5 次独立测试，每次随机抽取 100 个案例，经计算，准确率（ACC）的平均值为 63%，测试日志分别记录在 [one-shot-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-1.txt)、[one-shot-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-2.txt)、[one-shot-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-3.txt)、[one-shot-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-4.txt)、[one-shot-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-5.txt) 文件中。

## 三、Few Shot 相关工作

One-shot 学习仅为模型提供单个示例用于学习和预测，由于数据极度稀缺，模型需要从这唯一示例中快速捕捉关键特征并作出判断。而 few-shot 学习则为模型提供少量（通常 2 - 10 个）示例，能够为模型提供更多的参考信息，从而有效减轻模型的学习负担。以文本分类任务为例，为模型提供 3 - 5 个不同类别的文本示例，有助于模型对新文本进行准确分类。

本人在深入阅读 [ConsistNER: Towards Instructive NER Demonstrations for LLMs with the Consistency of Ontology and Context](https://ojs.aaai.org/index.php/AAAI/article/view/29892#:\~:text=To%20address%20this%20issue%2C%20we%20propose%20ConsistNER%2C%20a,incorporates%20ontological%20and%20contextual%20information%20for%20low-resource%20NER.) 这篇论文后，决定基于论文的思想，开发实现一个案例选择器。该案例选择器通过计算本体分布相似度和上下文语义相似度，为每个新的查询选择最合适的 few-shot 案例，具体实现方式如下：

**本体分布相似度**：通过预定义的本体类型（如时间、地点、人物、事件、数字、属性等）对表格列进行分类，在此基础上计算不同案例间本体分布的相似程度。

**上下文语义相似度**：运用 BERT 模型提取问题的语义表示，并通过计算余弦相似度来衡量不同问题之间的语义相似性。

**综合评分**：将本体分布相似度和上下文语义相似度按照 0.5 的权重进行加权平均，最终得到案例与查询问题的综合相似度分数。

基于上述方法，本人首先使用 one-shot 的提示词对训练集进行测试，随机选取 300 个案例，测试结果显示准确率（ACC）为 67%，详细测试日志存储于 [one-shot-train.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/one-shot-train.txt) 文件中。随后，将测试失败的案例存储到 [wrong\_answers\_train.jsonl](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/wrong_answers_train.jsonl) 文件中，共计积累 99 个案例。

针对这 99 个失败案例，运用论文中的本体一致性和上下文一致性方法，对每个新的查询问题，通过计算本体分布相似度和语义相似度来选择最相似的案例。该方法不仅充分考虑了问题的语义相似性，还兼顾了表格结构的相似性，能够更精准地找到与当前问题相关的示例，具体实现代码存储于 [case\_selector.py](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/few-shot/case_selector.py) 文件中。最终，从这 99 个失败案例中选取 3 个案例作为 few-shot 的示例，相关代码存储于 [few-shot.js](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/prompts/few-shot.js) 文件中（该提示词不包含规则提示词）。

## 四、Doubao 1.5 Vision Pro 32k 相关工作

鉴于通过训练集优化规则提示词以及采用 few-shot 方法优化提示词，模型表现均未实现明显提升，本人尝试使用 doubao-1.5-vision-pro-32k 模型。经测试发现，该模型的表现相较于 doubao-1.5-pro-32k 有显著提升，具体实现代码如下：



```
const stream = await this.openai.chat.completions.create({

&#x20; messages: \[

&#x20;   { role: "system", content: systemPrompt },

&#x20;   { role: "user", content: userPrompt },

&#x20; ],

&#x20; // model: 'doubao-1-5-pro-32k-250115',

&#x20; // model: 'doubao-1-5-pro-256k-250115',

&#x20; model: "doubao-1-5-vision-pro-32k-250115",

&#x20; stream: true,

});
```

使用 Zero-shot 的提示词，在测试集上进行 5 次独立测试，每次随机抽取 100 个案例，经计算，准确率（ACC）的平均值为 69.20%，测试日志分别存储于 [vision-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-1.txt)、[vision-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-2.txt)、[vision-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-3.txt)、[vision-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-4.txt)、[vision-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-5.txt) 文件中。

使用上述规则提示词，在测试集上再次进行 5 次独立测试，每次随机抽取 100 个案例，测试结果显示准确率（ACC）的平均值为 70.40%，这是本人首次在测试集上使准确率突破 70%，测试日志分别记录在 [vision-pro-simple-prompt-1.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-1.txt)、[vision-pro-simple-prompt-2.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-2.txt)、[vision-pro-simple-prompt-3.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-3.txt)、[vision-pro-simple-prompt-4.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-4.txt)、[vision-pro-simple-prompt-5.txt](https://github.com/JacksonHe04/smart-table-llm/blob/main/llm-api/logs/vision-pro-simple-prompt-5.txt) 文件中。

经分析，采用视觉模型后性能显著提升的原因主要体现在以下几个方面：

**结构感知能力**：视觉模型通过预训练，具备强大的图像结构识别能力，而表格本质上属于二维结构，与图像数据在空间关系上具有相似性，因此视觉模型的结构识别能力可自然迁移到表格结构理解上。

**多模态理解**：视觉模型在处理表格时，不仅能够理解文本内容，还能感知单元格的位置关系、表格的布局等视觉特征，这种多模态理解能力有助于模型更准确地解答问题。

**上下文关联**：视觉模型能够更好地捕捉表格中的全局信息，理解单元格之间的空间关联关系，这对于解答需要关联多个列或行的问题具有显著优势。

**预训练优势**：视觉模型在预训练阶段接触了大量的结构化视觉数据，这些经验有助于其更好地理解和处理表格这种结构化数据。

## 五、Doubao 1.5 Vision Pro 32k + Few Shot 相关工作

最后，本人尝试在 doubao-1.5-vision-pro-32k 模型上结合 few-shot 方法优化提示词。在测试集上进行 5 次独立测试，每次随机抽取 100 个案例，经计算，准确率（ACC）的平均值为 71.20%，这是目前在测试集上取得的最高分数，相关提示词代码如下：



```
const prompt = {

&#x20; get system() {
```