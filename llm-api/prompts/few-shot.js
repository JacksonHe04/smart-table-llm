const prompt = {
    get system() {
      return "You are an accurate table Q&A assistant."
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