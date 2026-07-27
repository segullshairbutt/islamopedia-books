import { GoogleGenAI } from "@google/genai";
import type { Interactions } from "@google/genai";
import { configDotenv } from "dotenv";

configDotenv();

const ai = new GoogleGenAI({
  apiKey: process.env.GOOGLE_GENAI_API_KEY,
});

const tools: Interactions.Tool[] = [
  {
    type: "google_search",
  },
];

const generationConfig = {
  temperature: 1,
  max_output_tokens: 65536,
  top_p: 0.95,
  thinking_level: "low",
};

export async function parseTextAndEmotions(
  prompt: string,
): Promise<string | undefined> {
  const interaction = await ai.interactions.create({
    model: "models/gemini-3.5-flash",
    input: prompt,
    system_instruction: `Identifying Speakers:
   - "Jane": Narrates standard Urdu book descriptions, transition text, inline arabic short words and historical context/direct speech.
   - "Joe": Recites all native Arabic text, Quranic verses, Hadith text, and all Urdu translations of quotations.
2. Order & Boundaries:
   - If the raw text starts with Arabic, the first chunk MUST be assigned to "Joe".
   - If the raw text starts with standard narration text, inline short arabic words, the first chunk MUST be assigned to "Jane".
    - Every time it should start a new line whenever it switch the speaker 
 3. No Numbering: Use only the exact strings "Jane" or "Joe" as the keys. Never use numbers like "Jane_1" or "Joe_1".
4. Inline Audio Emotion Tags: Prepend an English tag inside \`[]\` brackets at the absolute beginning of the text value string:
   - For Jane (Narration): Use \`[calmly, steady narration pacing]\` or \`[with serious emphasis, clear historical presentation]\`.
   - For Joe (Arabic Recitation): Use \`[smooth, steady pace, continous flow]\`.
   - For Joe (Urdu Quotation): Use \`[powerful, authoritative tone]\` or \`[softly, with concern]\`.`,
    tools: tools,
    generation_config: generationConfig,
  });

  return interaction?.steps?.at(-1)?.content[0]?.text;
}
