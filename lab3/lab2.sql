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