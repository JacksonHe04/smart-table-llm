export function selectData(testData, args) {
  const totalDataLength = testData.length;
  let selectedData;
  let startIndex;
  let count;
  
  if (args.length === 0) {
    count = 10;
    const indices = new Set();
    while (indices.size < count) {
      indices.add(Math.floor(Math.random() * totalDataLength));
    }
    selectedData = Array.from(indices).map(index => testData[index]);
    startIndex = Math.min(...indices);
  } else if (args[0].toLowerCase() === 'all') {
    startIndex = 0;
    count = totalDataLength;
    selectedData = testData;
  } else if (args.length === 1) {
    count = parseInt(args[0]) || 10;
    const indices = new Set();
    while (indices.size < count) {
      indices.add(Math.floor(Math.random() * totalDataLength));
    }
    selectedData = Array.from(indices).map(index => testData[index]);
    startIndex = Math.min(...indices);
  } else {
    startIndex = parseInt(args[0]) || 0;
    count = parseInt(args[1]) || 10;
    selectedData = testData.slice(startIndex, startIndex + count);
  }
  
  return { selectedData, startIndex, count };
}