import argparse
import os
import subprocess
from typing import List


def start_headless_stream(url: str, rtmp_urls: List[str], resolution: str, display: str, fps: int) -> None:
    """Launch a headless browser in a virtual display and stream it via ffmpeg."""
    if not rtmp_urls:
        raise ValueError("No RTMP URLs provided")

    # Start Xvfb virtual display
    xvfb_cmd = ["Xvfb", display, "-screen", "0", f"{resolution}x24", "-ac"]
    xvfb_proc = subprocess.Popen(xvfb_cmd)

    env = os.environ.copy()
    env["DISPLAY"] = display

    try:
        # Launch browser within the virtual display
        browser_cmd = ["chromium-browser", url]
        browser_proc = subprocess.Popen(browser_cmd, env=env)

        outputs = "|".join(f"[f=flv]{u}" for u in rtmp_urls)
        ffmpeg_cmd = [
            "ffmpeg",
            "-f",
            "x11grab",
            "-video_size",
            resolution,
            "-i",
            f"{display}.0",
            "-r",
            str(fps),
            "-f",
            "tee",
            outputs,
        ]
        subprocess.run(ffmpeg_cmd, check=True, env=env)
    finally:
        browser_proc.terminate()
        xvfb_proc.terminate()
        browser_proc.wait()
        xvfb_proc.wait()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Headless multi-platform streaming")
    parser.add_argument("url", help="URL of the page to render")
    parser.add_argument("--rtmp", nargs="+", required=True, help="RTMP URLs")
    parser.add_argument("--resolution", default="1280x720", help="Video resolution WxH")
    parser.add_argument("--display", default=":99", help="X11 display number for Xvfb")
    parser.add_argument("--fps", type=int, default=30, help="Output frames per second")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    start_headless_stream(args.url, args.rtmp, args.resolution, args.display, args.fps)
