import { GoogleGenAI } from "@google/genai";
import { configDotenv } from "dotenv";

configDotenv();

const ai = new GoogleGenAI({
  apiKey: process.env.GOOGLE_GENAI_API_KEY,
});

export async function changeTextToAudio(input: string | undefined) {
  if (!input) {
    throw new Error("Input text is undefined or empty.");
  }
  const prompt = `TTS the following book text using multiple voices between Joe and Jane:\n${input}`;
  const interaction = await ai.interactions.create({
    model: "gemini-3.1-flash-tts-preview",
    input: prompt,
    response_format: { type: "audio" },
    generation_config: {
      speech_config: [
        { speaker: "Joe", voice: "Gacrux" },
        { speaker: "Jane", voice: "Despina" },
      ],
    },
  });

  console.log("Audio generation completed.");

  const audioData = interaction.output_audio?.data;
  if (!audioData) {
    throw new Error("No audio data returned from TTS interaction.");
  }
  const audioBuffer = Buffer.from(audioData, "base64");

  // await saveWaveFile(`./outputAudios/out_${index}.wav`, audioBuffer);
  return audioBuffer;
}
