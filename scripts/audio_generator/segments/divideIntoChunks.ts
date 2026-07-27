export default function createChunks(text: string, maxChars = 1500) {
  const paragraphs = text
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter(Boolean);

  const chunks = [];
  let currentChunk = "";

  for (const paragraph of paragraphs) {
    if (
      currentChunk.length > 0 &&
      currentChunk.length + paragraph.length > maxChars
    ) {
      chunks.push(currentChunk.trim());
      currentChunk = "";
    }

    currentChunk += paragraph + "\n\n";
  }

  if (currentChunk.trim()) {
    chunks.push(currentChunk.trim());
  }

  return chunks;
}
