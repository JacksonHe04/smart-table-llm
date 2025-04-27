const prompt = {
    get system() {
      return "You are an accurate table Q&A assistant."
    },
    generateUserPrompt: (tableText, statement) =>
      `Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.\n\nTable Content: ${tableText}\n\nQuestion：${statement}\n\nPlease give the answer directly.`,
  };
  
  export default prompt;