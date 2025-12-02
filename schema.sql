CREATE TABLE musicians(
    id INTEGER PRIMARY KEY,
    musician_name TEXT NOT NULL,
    genre TEXT,
    year_formed INTEGER,
    origin TEXT
);

CREATE TABLE albums(
    id INTEGER PRIMARY KEY,
    musician_id INTEGER NOT NULL,
    title TEXT,
    number_of_tracks INTEGER,
    label TEXT,
    description TEXT,
    FOREIGN KEY (musician_id) REFERENCES musicians(id)
);