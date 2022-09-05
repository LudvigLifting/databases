--DROP TABLES THAT ALREADY EXISTS
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS theaters;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS screenings;
DROP TABLE IF EXISTS tickets;

--CREATE TABLES
PRAGMA foreign_keys = ON;

CREATE TABLE movies (
  IMDB_key TEXT, 
  title TEXT,
  prod_year DATE,
  running_time INT,
  PRIMARY KEY (IMDB_key)
);

CREATE TABLE theaters (
  name TEXT,
  capacity INT,
  PRIMARY KEY (name)
);

CREATE TABLE customers (
  username TEXT,
  password TEXT,
  full_name TEXT,
  PRIMARY KEY (username)
);

CREATE TABLE screenings (
  start_time TIME,
  start_date DATE,
  n_seats INT,
  name TEXT,
  IMDB_key TEXT,
  PRIMARY KEY (start_time, start_date),
  FOREIGN KEY (IMDB_key) REFERENCES movies(IMDB_key),
  FOREIGN KEY (name) REFERENCES theaters(name)
);

CREATE TABLE tickets (
  ticket_id TEXT  DEFAULT (lower(hex(randomblob(16)))),
  username TEXT,
  name TEXT,
  start_time TIME,
  start_date DATE,
  PRIMARY KEY (ticket_id),
  FOREIGN KEY (username) REFERENCES customers(username),
  FOREIGN KEY (name) REFERENCES theaters(name),
  FOREIGN KEY (start_time, start_date) REFERENCES screenings(start_time, start_date)
);

--INSERT DATA
INSERT INTO movies (IMDB_key, title, prod_year, running_time)
VALUES 
('tt0111161', 'The Shawshank Redemption', 1995, 142),
('tt1687901', 'The Awakening', 2011, 102),
('tt0080402', 'The Awakening', 1980, 105),
('tt0468569', 'The Dark Knight', 2008, 152),
('tt0068646', 'The Godfather', 1972, 1756);

INSERT INTO theaters (name, capacity)
VALUES 
('Filmstaden', 300),
('Kino', 220),
('Folkets Bio i Lund Södran', 110);

INSERT INTO customers (username, password, full_name)
VALUES 
('Kalle15', 'Katt', 'Karl Erik'),
('Hasse64', 'Hund', 'Hasse Björk'),
('Knugen3', 'Silvia', 'Carl XVI Gustaf');

INSERT INTO screenings (start_time, start_date, n_seats, name, IMDB_key)
VALUES 
('08:15:00', '2011-11-11', 8, 'Kino', 'tt0080402'),
('13:15:00', '2001-01-01', 8, 'Filmstaden', 'tt0468569'),
('15:15:15', '2001-01-01', 8, 'Kino', 'tt0111161'),
('23:59:59', '2001-02-02', 8, 'Folkets Bio i Lund Södran', 'tt0068646'),
('11:11:11', '2001-02-02', 8, 'Filmstaden', 'tt1687901');

INSERT INTO tickets(username, name, start_time, start_date)
VALUES ('Kalle15', 'Kino', '15:15:15', '2001-01-01');
