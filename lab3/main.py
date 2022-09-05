## uvicorn main:app --reload --port 7007
from fastapi import FastAPI, Response
from typing import Optional
import sqlite3
import hashlib
from pydantic import BaseModel
from starlette.responses import PlainTextResponse
import json

app = FastAPI()

connect = sqlite3.connect("movies.sqlite", check_same_thread=False)
sql = connect.cursor()

def make_json(keys, data):
    ret = []
    for d in data:
        ret.append(dict(zip(keys, d)))
    return ret


def hash(plaintext):
	return hashlib.sha256(plaintext.encode('utf-8')).hexdigest()

###MODELS-----------------------------

class User(BaseModel):
	username: str
	fullName: str
	pwd: str

class Movie(BaseModel):
	imdbKey: str
	title: str
	year: int

class Performance(BaseModel):
	imdbKey: str
	theater: str
	date: str
	time: str

class Ticket(BaseModel):
	username: str
	pwd: str
	performanceId: str

##GET---------------------------------

@app.get("/")
def read_root():
    return {"Welcome to": "root"}

@app.get("/ping", response_class=PlainTextResponse)
def ping(response: Response):
	response.status_code = 200
	return "pong"

@app.get("/movies")
def getMovies(title: str = "", year: int = -1):
	query = """
	SELECT imdb_id, movie_title, movie_year
	FROM movies
	WHERE 1 = 1
	"""
	params = []
	if title != "":
		query += " AND movie_title LIKE ? "
		params.append(title)
	if year != -1:
		query += " AND movie_year = ? "
		params.append(year)
	sql.execute(query, params)
	return { "data" : make_json(("imdbKey", "title", "year"), sql.fetchall())}

@app.get("/movies/{imdb_key}")
def getImdb(imdb_key):
	query = """
	SELECT imdb_id, movie_title, movie_year
	FROM movies
	WHERE imdb_id = ?
	"""
	sql.execute(query, (imdb_key,))
	return { "data" : make_json(("imdbKey", "title", "year"), sql.fetchall())}

@app.get("/theaters")
def getTheaters():
	query = """
	SELECT theater_name, capacity
	FROM theaters
	"""
	sql.execute(query)
	return { "data" : make_json(("theater_name", "capacity"), sql.fetchall())}

@app.get("/performances")
def performances(response: Response):
	query = """
		SELECT screening_id, screening_date, start_time, movie_title, movie_year, theater_name, (capacity - count(ticket_id)) AS remainingSeats
		FROM screenings
		LEFT OUTER JOIN movies USING (imdb_id)
		LEFT OUTER JOIN theaters USING (theater_name)
		LEFT OUTER JOIN tickets USING (screening_id)
		GROUP BY screening_id
	"""
	sql.execute(query)
	response.status_code = 201
	return { "data": make_json(("performanceId", "date", "startTime", "title", "year", "theater", "remainingSeats"), sql.fetchall()) }

##POST---------------------------------

@app.post("/users", response_class=PlainTextResponse)
def add_user(user: User, response: Response):
	query = """
		INSERT INTO customers(username, fullname, password)
		VALUES (?, ?, ?)
	"""
	params = [user.username, user.fullName, hash(user.pwd)]
	try: 
		sql.execute(query, params)
		connect.commit()
	except sqlite3.IntegrityError:  
		response.status_code = 400
		return ""
	response.status_code = 201
	return "/users/" + user.username

@app.post("/movies", response_class=PlainTextResponse)
def users(movie: Movie, response: Response):
	query = """
		INSERT INTO movies(imdb_id, movie_title, movie_year)
		VALUES (?, ?, ?)
	"""
	params = [movie.imdbKey, movie.title, movie.year]
	try:
		sql.execute(query, params)
		connect.commit()
	except sqlite3.IntegrityError:  
		response.status_code = 400
		return ""
	response.status_code = 201
	return "/movies/" + movie.imdbKey

@app.post("/performances", response_class=PlainTextResponse)
def users(pref: Performance, response: Response):
	query = """
		INSERT INTO screenings(theater_name, screening_date, start_time, imdb_id)
		VALUES (?, ?, ?, ?)
	"""
	params = [pref.theater, pref.date, pref.time, pref.imdbKey]
	try:
		sql.execute(query, params)
		connect.commit()
	except sqlite3.IntegrityError:  	
		response.status_code = 400
		return ""
	sql.execute("SELECT screening_id FROM screenings WHERE rowid = last_insert_rowid()")
	screenid = sql.fetchone()[0]
	response.status_code = 201
	return "/performances/" + screenid

@app.post("/tickets", response_class=PlainTextResponse)
def tickets(ticket: Ticket, response: Response):
	query = """
		SELECT EXISTS (
			SELECT * FROM customers WHERE username = ? AND password = ?
		)
	"""
	params = [ticket.username, hash(ticket.pwd)]
	sql.execute(query, params)
	if sql.fetchall()[0]:
		query = """
		SELECT EXISTS (
			SELECT (capacity-count(ticket_id)) AS remainingSeats 
			FROM screenings
			LEFT OUTER JOIN tickets USING (screening_id)
			LEFT OUTER JOIN theaters USING (theater_name)
			WHERE screening_id = ? AND remainingSeats > 0
		)
		"""
		params = [ticket.performanceId]
		sql.execute(query, params)
		if sql.fetchall()[0]:
			query = """
			INSERT INTO tickets(username, screening_id)
			VALUES (?, ?)
			"""
			params = [ticket.username, ticket.performanceId]
			try:
				sql.execute(query, params)
				connect.commit()
				response.status_code = 201
				return "/tickets/" + sql.execute("SELECT ticket_id FROM tickets WHERE rowid = last_insert_rowid()").fetchone()[0]
			except sqlite3.IntegrityError:
				response.status_code = 400
				return "Error"
		response.status_code = 400
		return "No tickets left"
	response.status_code = 401
	return "Wrong user credentials"


@app.post("/reset")
def reset():
	query = """
	PRAGMA foreign_keys=OFF;

	DROP TABLE IF EXISTS movies;
	DROP TABLE IF EXISTS theaters;
	DROP TABLE IF EXISTS screenings;
	DROP TABLE IF EXISTS customers;
	DROP TABLE IF EXISTS tickets;

	PRAGMA foreign_keys=ON;

	CREATE TABLE movies (
		movie_title TEXT,
		movie_year INT,
		imdb_id TEXT,
		runtime INT,
		PRIMARY KEY (imdb_id)
	);

	CREATE TABLE theaters (
		theater_name TEXT,
		capacity INT,
		PRIMARY KEY (theater_name)
	);

	CREATE TABLE screenings (
		screening_id TEXT DEFAULT (lower(hex(randomblob(16)))),
		imdb_id TEXT,
		theater_name TEXT,
		screening_date DATE,
		start_time TIME,
		PRIMARY KEY (screening_id),
		FOREIGN KEY (imdb_id) REFERENCES movies (imdb_id),
		FOREIGN KEY (theater_name) REFERENCES theaters (theater_name)
	);

	CREATE TABLE customers (
		username TEXT,
		fullname TEXT,
		password TEXT,
		PRIMARY KEY (username)
	);

	CREATE TABLE tickets (
		ticket_id TEXT DEFAULT (lower(hex(randomblob(16)))),
		username TEXT,
		screening_id TEXT,
		PRIMARY KEY (ticket_id),
		FOREIGN KEY (username) REFERENCES customers (username),
		FOREIGN KEY (screening_id) REFERENCES screenings (screening_id)
	);

	INSERT INTO theaters (theater_name, capacity) VALUES
	("Kino", 10),
	("Regal", 16),
	("Skandia", 100);

	DROP TRIGGER IF EXISTS avail_tickets;
	CREATE TRIGGER avail_tickets
	BEFORE INSERT
	ON tickets
	WHEN
	(
		select count()
		from tickets
		where screening_id = NEW.screening_id
	) >= (
		select capacity
		from theaters
		where theater_name =
		(
			select theater_name
			from screenings
			where screening_id = NEW.screening_id
		)
	)
	BEGIN
		SELECT RAISE (ABORT, "no tickets available");
	END;
		"""

	sql.executescript(query)
	return "Reset succesful!"
