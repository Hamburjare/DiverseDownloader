from typing import Union
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse
from fastapi.responses import PlainTextResponse
import yt_dlp
import random
import os
import time

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

def remove_file(path: str):
    time.sleep(120)
    os.remove(path)

@app.get('/robots.txt', response_class=PlainTextResponse, include_in_schema=False)
def robots():
    data = """User-agent: *\nDisallow: /"""
    return data

@app.get("/download")
async def download(background_tasks: BackgroundTasks, url: str):
    random.seed()
    random_hash = random.getrandbits(128)
    filename = f"downloads/{random_hash}.mp4"
    ydl_opts = {
        "format": "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/best[height<=?720][ext=mp4]",
        "audio-quality": 0,
        "outtmpl": filename,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    background_tasks.add_task(remove_file, filename)
    
    response = FileResponse(filename, media_type='video/mp4')

    return response
