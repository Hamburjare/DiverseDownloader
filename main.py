from typing import Union
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse, PlainTextResponse
import yt_dlp
import os
import asyncio
import logging
import uuid
from starlette.responses import Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

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

async def remove_file(path: str):
    await asyncio.sleep(120)
    if os.path.exists(path):
        os.remove(path)
        logging.info(f"Removed file {path}")
    else:
        logging.info(f"File {path} not found")

@app.get('/robots.txt', response_class=PlainTextResponse, include_in_schema=False)
def robots():
    data = """User-agent: *\nDisallow: /"""
    return data

@app.get("/download")
async def download(background_tasks: BackgroundTasks, url: str):
    if not url:
        return Response(content="URL is required", status_code=HTTP_400_BAD_REQUEST)

    filename = f"downloads/{uuid.uuid4()}.mp4"
    ydl_opts = {
        "format": "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=?1080][ext=mp4]",
        "audio-quality": 0,
        "outtmpl": filename,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logging.info(f"Starting download for {url}")
            ydl.download([url])
            logging.info(f"Download finished for {url}")
    except yt_dlp.DownloadError as e:
        logging.error(f"Error downloading video: {e}")
        return Response(content="Error downloading video", status_code=HTTP_400_BAD_REQUEST)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return Response(content="Unexpected error", status_code=HTTP_500_INTERNAL_SERVER_ERROR)

    background_tasks.add_task(remove_file, filename)
    
    response = FileResponse(filename, media_type='video/mp4')

    return response