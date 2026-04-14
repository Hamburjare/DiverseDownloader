from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
import yt_dlp
import os
import asyncio
import logging
import uuid
from urllib.parse import urlparse

os.makedirs("downloads", exist_ok=True)

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL must use http or https scheme")


def _run_download(ydl_opts: dict, url: str) -> None:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


async def remove_file(path: str) -> None:
    await asyncio.sleep(120)
    if os.path.exists(path):
        os.remove(path)
        logging.info(f"Removed file {path}")
    else:
        logging.info(f"File {path} not found")


@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
def robots():
    return "User-agent: *\nDisallow: /"


@app.get("/download")
async def download(background_tasks: BackgroundTasks, url: str):
    _validate_url(url)

    file_id = str(uuid.uuid4())
    filename = f"downloads/{file_id}.mp4"
    ydl_opts = {
        "format": "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]",
        "merge_output_format": "mp4",
        "outtmpl": f"downloads/{file_id}.%(ext)s",
    }

    try:
        logging.info(f"Starting video download for {url}")
        await asyncio.to_thread(_run_download, ydl_opts, url)
        logging.info(f"Video download finished for {url}")
    except yt_dlp.DownloadError as e:
        logging.error(f"Error downloading video: {e}")
        raise HTTPException(status_code=400, detail="Error downloading video")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")

    background_tasks.add_task(remove_file, filename)
    return FileResponse(filename, media_type="video/mp4")


@app.get("/download/audio")
async def download_audio(background_tasks: BackgroundTasks, url: str):
    _validate_url(url)

    file_id = str(uuid.uuid4())
    filename = f"downloads/{file_id}.mp3"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"downloads/{file_id}.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        logging.info(f"Starting audio download for {url}")
        await asyncio.to_thread(_run_download, ydl_opts, url)
        logging.info(f"Audio download finished for {url}")
    except yt_dlp.DownloadError as e:
        logging.error(f"Error downloading audio: {e}")
        raise HTTPException(status_code=400, detail="Error downloading audio")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error")

    background_tasks.add_task(remove_file, filename)
    return FileResponse(filename, media_type="audio/mpeg")