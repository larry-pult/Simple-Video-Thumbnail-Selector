from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import generator
import base64


app = FastAPI()


class VideoLink(BaseModel):
    link: str


@app.get("/")
def index():
    return {
        "message": "the api is working!"
    }


@app.post("/get_thumbnail")
def get_thumbnail(video_link: VideoLink):
    link = video_link.link

    is_valid, error_message = generator.is_valid_video_link(link)
    
    if not is_valid:
        return JSONResponse(
            status_code=400,
            content={
                "message": error_message
            }
        )
    
    print("parsing the video...")
    key_frames = generator.select_key_frames(link)

    print("generaing thumbnails...")
    thumbnail = generator.generate_thumbnail_from_key_frames(key_frames)
    
    return JSONResponse(
        status_code=200,
        content={
            "thumbnail": base64.b64encode(thumbnail).decode("utf-8")
        }
    )