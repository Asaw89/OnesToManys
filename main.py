from fastapi import FastAPI #source venv/bin/activate
import sqlite3
from pydantic import BaseModel #FastAPI uses pydantic models
from typing import Optional
import json

app = FastAPI()
    #http://127.0.0.1:8000/docs
    #uvicorn main:app --reload
    #curl -s http://localhost:8000/musicians | jq
    #source venv/bin/activate

#all of the albums are associated with this musician

@app.get("/musicians")
def get_musicians():
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT*FROM musicians")
    rows = cursor.fetchall()
    musicians = []
    connection.close()
    for row in rows:
        musicians.append({
            "id": row[0],
            "musician_name": row[1],
            "genre": row[2],
            "year_formed": row[3],
            "origin": row[4]
        })
    return{"musicians":musicians} #return json list of musicians


@app.get("/albums")
def get_albums():
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT*FROM albums")
    rows = cursor.fetchall()
    connection.close()
    albums = []
    for row in rows:
        albums.append({
            "id": row[0],
            "musician_id": row[1],
            "title": row[2],
            "number_of_tracks": row[3],
            "label": row[4],
            "description": row[5]
        })
    return {"albums": albums} #return json list of albums

@app.get("/musicians/search/{name}")
def get_musician(name:str):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM musicians WHERE LOWER(musician_name) = LOWER(?)",(name, ))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("SELECT * FROM musicians ORDER BY RANDOM() LIMIT 1")
        suggestion = cursor.fetchone()
        connection.close()
        return {"error": "Musician not found", "suggestion": suggestion}
    connection.close()

    musician = {
        "id": row[0],
        "musician_name": row[1],
        "genre": row[2],
        "year_formed": row[3],
        "origin": row[4]
    }
    return {"musician": musician}

@app.get("/musicians/{musician_id}")
def get_musician_by_id(musician_id: int):
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM musicians WHERE id = ?", (musician_id,))
    row = cursor.fetchone()
    connection.close()

    if row is None:
        return {"error": "Musician not found"}

    musician = {
        "id": row[0],
        "musician_name": row[1],
        "genre": row[2],
        "year_formed": row[3],
        "origin": row[4]
    }
    return {"musician": musician}

@app.get("/musicians/{musician_id}/albums")
def get_all_musician_albums_by_ID(musician_id: int):
    connection = sqlite3.connect("music.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM musicians WHERE id = ?", (musician_id,))
    musician = cursor.fetchone()

    if musician is None:
        connection.close()
        return {"error": "Musician not found"}

    cursor.execute("SELECT * FROM albums WHERE musician_id = ?", (musician_id,))
    rows = cursor.fetchall()
    connection.close()

    if rows == []:
        return {"No albums found"}

    albums = []
    for row in rows:
        albums.append({
            "id": row[0],
            "musician_id": row[1],
            "title": row[2],
            "number_of_tracks": row[3],
            "label": row[4],
            "description": row[5]
        })
    return {"albums": albums}

@app.get("/musicians/search/{name}/albums")
def get_all_musician_albums(name: str):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()

    cursor.execute("SELECT * FROM musicians WHERE LOWER(musician_name) = LOWER(?)", (name,))
    musician = cursor.fetchone()
    if musician is None:
        connection.close()
        return {"Musician not found"}
    musician_id = musician[0]

    cursor.execute("SELECT * FROM albums WHERE musician_id = ?", (musician_id,))
    rows=cursor.fetchall()
    connection.close()

    if rows == []:
        return {'Albums not found'}

    albums = []
    for row in rows:
        albums.append({
            "id": row[0],
            "musician_id": row[1],
            "title": row[2],
            "number_of_tracks": row[3],
            "label": row[4],
            "description": row[5]
        })
    return {"albums": albums}

@app.get("/albums/search/title/{title}")
def get_album(title:str):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM albums WHERE LOWER(title) = LOWER(?)",(title, ))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("SELECT * FROM albums ORDER BY RANDOM() LIMIT 1")
        suggestion = cursor.fetchone()
        connection.close()
        return {"error": "Album not found", "suggestion": suggestion}
    connection.close()

    album =({
            "id": row[0],
            "musician_id": row[1],
            "title": row[2],
            "number_of_tracks": row[3],
            "label": row[4],
            "description": row[5]
        })
    return {"album": album}

@app.get("/albums/search/{album_id}")
def get_album_by_id(album_id:int):
    connection=sqlite3.connect("music.db")
    cursor=connection.cursor()
    cursor.execute("SELECT * FROM albums WHERE id = ?", (album_id,))
    row=cursor.fetchone()
    if row is None:
        cursor.execute("SELECT * FROM albums ORDER BY RANDOM() LIMIT 1")
        suggestion = cursor.fetchone()
        connection.close()
        return {"error": "Album not found", "suggestion": suggestion}
    connection.close()
    album =({
            "id": row[0],
            "musician_id": row[1],
            "title": row[2],
            "number_of_tracks": row[3],
            "label": row[4],
            "description": row[5]
        })
    return {"album": album}


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
    cursor.execute("SELECT * FROM musicians WHERE LOWER(musician_name) = LOWER(?)", (musician.musician_name,))
    existing = cursor.fetchone()

    if existing:
        connection.close()
        return {"error": "This musician already exists", "musician": existing}

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
    cursor.execute("SELECT * FROM albums WHERE LOWER(title) = LOWER(?)", (album.title,))
    existing = cursor.fetchone()

    if existing:
        connection.close()
        return {"error": "This album already exists", "album": existing}

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

@app.get("/dump")
def dump_data():
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


