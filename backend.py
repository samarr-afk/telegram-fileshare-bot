from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import requests
import os
import sqlite3

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")

def get_file(file_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    r = requests.get(url)
    return r.json()["result"]["file_path"]

def stream_file(url):
    r = requests.get(url, stream=True)
    for chunk in r.iter_content(chunk_size=1024*1024):
        yield chunk

@app.get("/download/{share_code}")
def download_file(share_code: str):
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT file_id, file_name FROM files WHERE share_code=?", (share_code,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_id, file_name = row
    file_path = get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return StreamingResponse(stream_file(file_url), headers={"Content-Disposition": f"attachment; filename={file_name}"})
