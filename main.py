from fastapi import FastAPI
import sqlite3

app = FastAPI()

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

