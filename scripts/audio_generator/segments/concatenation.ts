import Ffmpeg from "fluent-ffmpeg";
import { writeFileSync } from "fs";
import path from "path";
import { configDotenv } from "dotenv";

configDotenv();

export async function mergeFiles(allAudioFiles: string[], outputChapter: string) {
  await new Promise<void>((resolve, reject) => {
    const temDir = `../../../outputAudios/tmp`;
    const txtFilePath = path.join(import.meta.dirname, temDir, `file_list.txt`);

    // 1. Create the text file
    const fileListContent = allAudioFiles
      .map((f) => `file '${path.resolve(f)}'`)
      .join("\n");
    writeFileSync(txtFilePath, fileListContent);

    console.log("\nMerging audio files into:", outputChapter);
    // 2. Run FFmpeg using the concat demuxer
    Ffmpeg()
      .input(txtFilePath)
      .inputOptions(["-f concat", "-safe 0"])
      .outputOptions("-c copy")
      .on("error", (err) => {
        console.error("\nffmpeg concat error:", err);
        reject(err);
      })
      .on("end", () => {
        console.log(`\nSaved chapter audio safely to ${outputChapter}`);
        resolve();
      })
      .save(outputChapter);
  });
}
