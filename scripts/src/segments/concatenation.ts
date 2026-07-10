import Ffmpeg from "fluent-ffmpeg";
import { writeFileSync } from "fs";
import path from "path";

export async function mergeFiles(
  allAudioFiles: string[],
  outputChapter: string,
) {
  await new Promise<void>((resolve, reject) => {
    const txtFilePath = "../outputAudios/tmp/filelist.txt";

    // 1. Create the text file
    const fileListContent = allAudioFiles
      .map((f) => `file '${path.resolve(f)}'`)
      .join("\n");
    writeFileSync(txtFilePath, fileListContent);

    console.log("Merging audio files into:", outputChapter);
    // 2. Run FFmpeg using the concat demuxer
    Ffmpeg()
      .input(txtFilePath)
      .inputOptions(["-f concat", "-safe 0"])
      .outputOptions("-c copy")
      .on("error", (err) => {
        console.error("ffmpeg concat error:", err);
        reject(err);
      })
      .on("end", () => {
        console.log(`Saved chapter audio safely to ${outputChapter}`);
        resolve();
      })
      .save(outputChapter);
  });
}
