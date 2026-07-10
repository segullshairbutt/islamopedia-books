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

const bookChapter = process.env.BOOK_CHAPTER;
const chapterNo = parseInt(process.env.CHAPTER_NO || "1", 10);
console.log("Processing book chapter:", bookChapter, "Chapter number:", chapterNo);

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
    const inputText = readFileSync(`./inputFiles/${bookChapter}`, "utf-8");
    const chunks = createChunks(inputText);

    const allAudioFiles: string[] = [];

    console.log("Total chunks created:", chunks.length);

    for (const [i, chunk] of chunks.entries()) {
      // writeFileSync(`./outputTextFiles/chunk_${i + 1}.txt`, chunk, {
      //   encoding: "utf-8",
      // });

      if (i === 1) break;

      const chunkWithEmotion = await parseTextAndEmotions(chunk);
      if (!chunkWithEmotion) {
        console.error(
          "Failed to parse text and emotions for the chunk.",
          i + 1,
        );
        continue;
      }

      if (!existsSync(`./emotionTextFiles/chapter${chapterNo}`)) {
        mkdirSync(`./emotionTextFiles/chapter${chapterNo}`, {
          recursive: true,
        });
      }

      writeFileSync(
        `./emotionTextFiles/chapter${chapterNo}/chunk_${i + 5}.txt`,
        chunkWithEmotion,
        {
          encoding: "utf-8",
        },
      );

      console.log(`Processing chunk ${i + 1} with emotion:`, chunkWithEmotion);

      if (!existsSync(`./outputAudios/tmp/chapter${chapterNo}`)) {
        mkdirSync(`./outputAudios/tmp/chapter${chapterNo}`, {
          recursive: true,
        });
      }

      const tempFilePath = `./outputAudios/tmp/chapter${chapterNo}/out_${i + 1}.wav`;
      try {
        const audioBuffer = await changeTextToAudio(chunkWithEmotion);

        if (audioBuffer) {
          // 1. Write the buffer to your Thinkpad's disk right here
          await saveWaveFile(tempFilePath, audioBuffer);

          // 2. Push the FILE PATH string into the array for FFmpeg
          allAudioFiles.push(tempFilePath);
        }
      } catch (error: any) {
        console.error("--- DEBUGGING API ERROR ---");

        // 1. Print out the raw underlying status codes
        console.log("Status Code:", error.statusCode);

        // 2. Look inside the raw request structure if available
        if (error.error?.httpMeta?.request) {
          console.log("Request URL:", error.error.httpMeta.request.url);
          console.log("Request Headers:", error.error.httpMeta.request.headers);
        }

        // 3. Print the raw error body string directly
        console.log("Raw Error Body:", error);
        console.error("---------------------------");
        continue;
      }

      await new Promise((r) => setTimeout(r, 200));
    }
    console.log(
      "Creating chapter audio by concatenating all sentence audios. Total files:",
      allAudioFiles.length,
    );

    if (allAudioFiles.length === 0) {
      console.error("No audio files to concatenate.");
      return;
    }

    if (!existsSync(`./outputAudios/outputChapters`)) {
      mkdirSync(`./outputAudios/outputChapters`, { recursive: true });
    }

    const outputChapter = `./outputAudios/outputChapters/chapter${chapterNo}.wav`;
 
    if (allAudioFiles.length === 1) {
      copyFileSync(allAudioFiles[0], outputChapter);
      console.log(`Saved chapter audio to ${outputChapter}`);
      return;
    }

    mergeFiles(allAudioFiles, outputChapter);
  } catch (error) {
    throw new Error("Error: " + error);
  }
}

await main();
