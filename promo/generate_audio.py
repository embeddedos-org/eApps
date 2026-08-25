"""Generate per-segment narration using edge-tts (US English neural voice)."""
import asyncio
import json
import edge_tts
from mutagen.mp3 import MP3

VOICE = "en-US-GuyNeural"
RATE = "+0%"

SEGMENTS = [
    {"id": "intro", "text": "Introducing eApps. The unified marketplace and app store for EoS."},
    {"id": "f1", "text": "Feature one. 50 Apps Across 8 Platforms. Native apps, desktop apps, mobile, web PWAs, browser extensions, dev tools, CLI tools, and enterprise deployments — all in one monorepo."},
    {"id": "f2", "text": "Feature two. Automated Build and Delivery. CI/CD pipelines compile, test, and publish every app to 188 platform targets automatically."},
    {"id": "f3", "text": "Feature three. Live Marketplace. A hosted web storefront where users browse, search, and install EoS apps with one click."},
    {"id": "arch", "text": "Under the hood, eApps is built with C, TypeScript, React, and GitHub Actions. The architecture flows from App Source, to Build Matrix, to Test Suite, to Package Registry, to Marketplace."},
    {"id": "cta", "text": "eApps. Open source and ready to ship. Visit github dot com slash embeddedos-org slash eApps."}
]


async def generate():
    durations = {}
    audio_files = []

    for seg in SEGMENTS:
        filename = f"seg_{seg['id']}.mp3"
        communicate = edge_tts.Communicate(seg["text"], VOICE, rate=RATE)
        await communicate.save(filename)
        dur = MP3(filename).info.length
        durations[seg["id"]] = round(dur + 0.5, 1)
        audio_files.append(filename)
        print(f"  {seg['id']}: {dur:.1f}s -> padded {durations[seg['id']]}s")

    with open("durations.json", "w") as f:
        json.dump(durations, f, indent=2)

    import subprocess
    with open("concat_list.txt", "w") as f:
        for af in audio_files:
            f.write(f"file '{af}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", "concat_list.txt", "-c", "copy", "narration.mp3"
    ], check=True)

    total = sum(durations.values())
    print(f"\nVoice: {VOICE}")
    print(f"Total narration: {total:.1f}s")

asyncio.run(generate())
