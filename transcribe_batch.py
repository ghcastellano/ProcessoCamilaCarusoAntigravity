import glob
import json
import os
import sys
import traceback
from faster_whisper import WhisperModel

print("Starting transcription script...", flush=True)

opus_files = sorted(glob.glob("*.opus"))
print(f"Total opus files found: {len(opus_files)}", flush=True)

cache_file = "transcriptions.json"
transcriptions = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            transcriptions = json.load(f)
        print(f"Loaded {len(transcriptions)} existing transcriptions", flush=True)
    except Exception as e:
        print(f"Error loading cache: {e}", flush=True)

remaining = [f for f in opus_files if f not in transcriptions]
print(f"Remaining to process: {len(remaining)}", flush=True)

if not remaining:
    print("All files already transcribed!", flush=True)
    sys.exit(0)

try:
    print("Loading Whisper model 'base'...", flush=True)
    model = WhisperModel("base", device="cpu", compute_type="int8", cpu_threads=4)
    print("Model loaded successfully.", flush=True)
except Exception as e:
    print(f"Failed to load Whisper model: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

for idx, f in enumerate(remaining, 1):
    try:
        segments, info = model.transcribe(f, language="pt", beam_size=1)
        text = " ".join([s.text for s in segments]).strip()
        transcriptions[f] = {
            "text": text,
            "duration": info.duration
        }
        print(f"[{idx}/{len(remaining)}] {f} ({info.duration:.1f}s): {text[:80]}", flush=True)
        # save every file
        with open(cache_file, "w", encoding="utf-8") as out:
            json.dump(transcriptions, out, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error processing {f}: {e}", flush=True)
        traceback.print_exc()

print("Transcription batch finished successfully!", flush=True)
