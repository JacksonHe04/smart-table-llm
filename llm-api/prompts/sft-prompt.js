const prompt = {
    get system() {
      return "You are an accurate table Q&A assistant. Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process. Please give the answer directly."
    },
    generateUserPrompt: (tableText, statement) =>
      `Table Content: ${tableText}\n\nQuestion：${statement}\n\n`,
  };
  
  export default prompt;