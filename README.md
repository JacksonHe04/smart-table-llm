# 基于大模型的智能表格问答
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