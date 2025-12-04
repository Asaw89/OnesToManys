from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel #FastAPI uses pydantic models
from typing import Optional
import json

app = FastAPI() #http://127.0.0.1:8000/docs
    #uvicorn main:app --reload

@app.get("/")
def home():
    return {"message": "Hello World"}


@app.get("/musicians")
def get_musicians():
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT*FROM musicians")
    results = cursor.fetchall()
    connection.close()
    return{"musicians":results}


@app.get("/albums")
def get_albums():
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT*FROM albums")
    results = cursor.fetchall()
    connection.close()
    return{"albums":results}

@app.get("/musicians/{musician_id}")
def get_musician(musician_id: int):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM musicians WHERE id = ?", (musician_id,))
    results = cursor.fetchone()
    connection.close()
    return{"musician":results}

@app.get("/albums/{album_id}")
def get_album(album_id:int):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM albums WHERE id = ?", (album_id,))
    results = cursor.fetchone()
    connection.close()
    return{"album":results}


class MusicianCreate(BaseModel):
    musician_name: str
    genre: str
    year_formed: int
    origin: str

class AlbumCreate(BaseModel):
    musician_id: int
    title: str
    number_of_tracks: int
    label: str
    description:str

class MusicianUpdate(BaseModel):
    musician_name: str
    genre: Optional[str] = None
    year_formed: Optional[int] = None
    origin: Optional[str] = None

class AlbumUpdate(BaseModel):
    musician_id: int
    title: str
    number_of_tracks: int
    label: str
    description: str


@app.post("/musicians")
def add_musician(musician: MusicianCreate):
    connection = sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute(
        "Insert Into musicians(musician_name,genre,year_formed,origin) VALUES(?, ?, ? ,?)",
        (musician.musician_name,musician.genre,musician.year_formed,musician.origin)
    )
    connection.commit()
    connection.close()
    return{"Musician successfully added"}

@app.post("/albums")
def add_album(album: AlbumCreate):
    connection = sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute(
        "Insert Into albums(musician_id,title,number_of_tracks,label,description) VALUES(?, ?, ? ,?,?)",
        (album.musician_id,album.title,album.number_of_tracks,album.label,album.description)
    )
    connection.commit()
    connection.close()
    return{"Album successfully added"}

@app.delete("/albums/{album_id}")
def delete_album(album_id:int):
    connection = sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("DELETE FROM albums WHERE id = ?",(album_id,))
    connection.commit()
    connection.close()
    return{"Album successfully deleted"}

@app.delete("/musicians/{musician_id}")
def delete_musician(musician_id: int):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("DELETE FROM musicians WHERE id = ?",(musician_id,))
    connection.commit()
    connection.close()
    return{"Musician successfully deleted"}

@app.put("/musicians/{musician_id}")
def update_musician(musician_id: int, data: MusicianUpdate):
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE musicians
        SET musician_name = ?, genre = ?, year_formed = ?, origin = ?
        WHERE id = ?
    """, (data.musician_name, data.genre, data.year_formed, data.origin, musician_id))
    connection.commit()
    cursor.execute("SELECT * FROM musicians WHERE id = ?", (musician_id,))
    updated = cursor.fetchone()
    connection.close()
    return {"musician successfully": updated}

@app.put("/albums/{album_id}")
def update_album(album_id: int, data: AlbumUpdate):
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE albums
        SET musician_id = ?, title = ?, number_of_tracks = ?, label = ?, description = ?
        WHERE id = ?
    """, (data.musician_id, data.title, data.number_of_tracks, data.label, data.description,album_id))
    connection.commit()
    cursor.execute("SELECT * FROM albums WHERE id = ?", (album_id,))
    updated = cursor.fetchone()
    connection.close()
    return {"album successfully": updated}

@app.get("/musicians/{musician_id}/albums")
def get_all_musician_albums(musician_id: int):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM albums WHERE musician_id = ?", (musician_id,))
    results = cursor.fetchall()
    connection.close()
    return{"albums":results}

@app.get("/dump")
def dump_data(file):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM musicians")
    musicians = cursor.fetchall()
    cursor.execute ("SELECT * FROM albums")
    albums = cursor.fetchall()
    connection.close()

    data = {
        "musicians":musicians,
        "albums":albums
    }

    with open("backup.json", "w") as file:
        json.dump(data, file,indent=2)
    return {"Data has been Exported to backup.json"}

@app.post("/load")
def load_data():
    with open("backup.json", "r") as file:
        data = json.load(file)
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    for musician in data["musicians"]:
        cursor.execute(
        "Insert Into musicians(id,musician_name,genre,year_formed,origin) VALUES(?, ?, ? ,?, ?)",
        musician
    )
    for album in data["albums"]:
        cursor.execute(
        "Insert Into albums(id,musician_id,title,number_of_tracks,label,description) VALUES(?, ?, ? ,?,?,?)",
        album
    )
    connection.commit()
    connection.close()

    return{"Data has been imported"}


