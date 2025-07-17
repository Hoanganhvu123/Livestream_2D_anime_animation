# Streaming Utilities

This folder contains helper scripts for livestreaming to multiple platforms.

## multistream.py

Use `multistream.py` to forward a single video input to multiple RTMP
endpoints using `ffmpeg`. This can be used to save resources when streaming to
several services simultaneously.

### Example

```bash
python multistream.py video.mp4 --rtmp rtmp://a.example/live/streamkey \
    rtmp://b.example/app/key
```

`ffmpeg` must be installed and available on your `PATH`.

## headless_multistream.py

`headless_multistream.py` launches a virtual display using `Xvfb`, opens a web page with a Live2D character in a browser, and streams that headless session to multiple RTMP endpoints.

### Example

```bash
python headless_multistream.py https://example.com/character \
    --rtmp rtmp://a.example/live/key rtmp://b.example/app/key
```

Both `ffmpeg` and `Xvfb` must be installed.

## canvas_multistream.py

`canvas_multistream.py` uses the Chrome DevTools protocol via `pyppeteer` to
capture the canvas from a web page and stream it directly to multiple RTMP
destinations.

### Example

```bash
python canvas_multistream.py https://example.com/character \
    --rtmp rtmp://a.example/live/key rtmp://b.example/app/key
```

`ffmpeg` and `pyppeteer` are required.
