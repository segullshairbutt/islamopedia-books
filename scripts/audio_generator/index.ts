import wav from "wav";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "fs";
import createChunks from "./segments/divideIntoChunks.ts";
import { parseTextAndEmotions } from "./segments/parseTextWithEmotions.ts";
import { changeTextToAudio } from "./segments/textToSpeech.ts";
import { mergeFiles } from "./segments/concatenation.ts";
import { configDotenv } from "dotenv";

configDotenv();

const chapterNo = parseInt(process.env.CHAPTER_NO || "1");
const bookChapter = `chap_${chapterNo}.rtl.md`;
const temDir = `../../outputAudios`;

console.log(
  "Processing book chapter:",
  bookChapter,
  "Chapter number:",
  chapterNo,
);

async function saveWaveFile(
  filename: string,
  pcmData: Buffer,
  channels = 1,
  rate = 24000,
  sampleWidth = 2,
) {
  return new Promise((resolve, reject) => {
    const writer = new wav.FileWriter(filename, {
      channels,
      sampleRate: rate,
      bitDepth: sampleWidth * 8,
    }) as any;

    writer.on("finish", resolve);
    writer.on("error", reject);

    writer.write(pcmData);
    console.log(`Saved audio to ${filename}`);
    writer.end();
  });
}

async function main() {
  try {
    const inputText = readFileSync(`../../inputFiles/${bookChapter}`, "utf-8");
    if (inputText.trim() === "") {
      console.error("Input text file is empty. Please provide valid text.");
      return;
    }

    if (!existsSync(`../../emotionTextFiles/chapter${chapterNo}`)) {
      mkdirSync(`../../emotionTextFiles/chapter${chapterNo}`, {
        recursive: true,
      });
    }

    if (!existsSync(`${temDir}/tmp/chapter${chapterNo}`)) {
      mkdirSync(`${temDir}/tmp/chapter${chapterNo}`, {
        recursive: true,
      });
    }

    const chunks = createChunks(inputText, 10);

    const allAudioFiles: string[] = [];

    console.log("\nTotal chunks created:", chunks.length);

    for (const [i, chunk] of chunks.entries()) {
      try {
        const chunkWithEmotion = parseTextAndEmotions(chunk);

        if (!chunkWithEmotion) {
          console.log(
            "Failed to parse text and emotions for the chunk.",
            i + 1,
          );
          continue;
        }

        writeFileSync(
          `../../emotionTextFiles/chapter${chapterNo}/chunk_${i + 5}.txt`,
          String(chunkWithEmotion),
          {
            encoding: "utf-8",
          },
        );

        const tempFilePath = `${temDir}/tmp/chapter${chapterNo}/out_${i + 1}.wav`;
        const audioBuffer: any = changeTextToAudio(String(chunkWithEmotion));

        if (audioBuffer) {
          await saveWaveFile(tempFilePath, audioBuffer);
          allAudioFiles.push(tempFilePath);
        }
        
        await new Promise((r) => setTimeout(r, 200));
      } catch (error: any) {
        console.error("\n--- DEBUGGING AUDIO PARSING API ERROR ---");
        console.log(
          `\nRaw Error Body for the chunk ${i + 1}:`,
          error.message,
          "\n",
        );
        console.error("---------------------------");
        continue;
      }
    }

    console.log(
      "\nConcatenating all sentence audios. Total files:",
      allAudioFiles.length,
    );

    if (allAudioFiles.length === 0) {
      console.error("No audio files to concatenate.");
      return;
    }

    if (!existsSync(`${temDir}/outputChapters`)) {
      mkdirSync(`${temDir}/outputChapters`, { recursive: true });
    }

    const outputChapter = `${temDir}/outputChapters/chapter${chapterNo}.wav`;

    if (allAudioFiles.length === 1) {
      copyFileSync(allAudioFiles[0], outputChapter);
      console.log(`\nSaved chapter audio to ${outputChapter}`);
      return;
    }

    mergeFiles(allAudioFiles, outputChapter);
  } catch (error: any) {
    console.error("\n--- DEBUGGING MAIN METHOD ERROR ---");
    console.error("\nAn error occurred in the main function:", error.message);
    console.error("\n---------------------------");
  }
}

await main();
