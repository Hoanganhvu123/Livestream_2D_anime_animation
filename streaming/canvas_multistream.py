import argparse
import asyncio
import base64
import subprocess
from typing import List

from pyppeteer import launch


async def start_canvas_stream(url: str, rtmp_urls: List[str], fps: int) -> None:
    """Capture canvas rendering from a web page and stream to multiple RTMP endpoints."""
    if not rtmp_urls:
        raise ValueError("No RTMP URLs provided")

    outputs = "|".join(f"[f=flv]{u}" for u in rtmp_urls)
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "image2pipe",
        "-vcodec",
        "mjpeg",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-f",
        "tee",
        outputs,
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.goto(url)

    client = await page.target.createCDPSession()
    await client.send("Page.startScreencast", {"format": "jpeg", "quality": 80})
    try:
        while True:
            msg = await client.recv()
            if msg.get("method") == "Page.screencastFrame":
                data = base64.b64decode(msg["params"]["data"])
                proc.stdin.write(data)
                proc.stdin.flush()
                await client.send(
                    "Page.screencastFrameAck",
                    {"sessionId": msg["params"]["sessionId"]},
                )
    finally:
        await browser.close()
        proc.stdin.close()
        proc.wait()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture canvas render and livestream to multiple platforms"
    )
    parser.add_argument("url", help="URL of the page containing the canvas")
    parser.add_argument("--rtmp", nargs="+", required=True, help="RTMP URLs")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.get_event_loop().run_until_complete(
        start_canvas_stream(args.url, args.rtmp, args.fps)
    )
