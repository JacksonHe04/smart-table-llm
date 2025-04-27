const prompt = {
    get system() {
      return "You are an accurate table Q&A assistant."
    },
    generateUserPrompt: (tableText, statement) =>
      `Please carefully analyze the following table and answer the questions accurately. Note: Only output the answers, do not explain the process.

Example:
Question: who was the first cyclist to finish?
Table Content: rank,cyclist,team,time,uci protour\npoints,1,alejandro valverde (esp),caisse d'epargne,5h 29' 10",40,2,alexandr kolobnev (rus),team csc saxo bank,s.t.,30,3,davide rebellin (ita),gerolsteiner,s.t.,25,4,paolo bettini (ita),quick step,s.t.,20,5,franco pellizotti (ita),liquigas,s.t.,15,6,denis menchov (rus),rabobank,s.t.,11,7,samuel sánchez (esp),euskaltel-euskadi,s.t.,7,8,stéphane goubert (fra),ag2r-la mondiale,+ 2",5,9,haimar zubeldia (esp),euskaltel-euskadi,+ 2",3,10,david moncoutié (fra),cofidis,+ 2",1
Answer: Alejandro Valverde

Now, please answer the following question:
Table Content: ${tableText}
Question: ${statement}

Please give the answer directly.`,
  };
  
  export default prompt;