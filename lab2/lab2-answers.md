4. 
a) movies (title, year), customers (username), screenings (start_time, start_date, name).
b) Theater could change name.
c) screenings is a weak entry set.
d) It would be nice to have for screenings as it currently has two columns as primary key.

movies(_IMDB_key_, title, prod_year, running_time)
theaters(_name_, capacity, screenings)
customers(_username_, password, full_name)
screenings(_start_time_, _start_date_, n_seats, /_name_/, /_IMDB_key_/, /title/)
tickets(_ticket_id_, /_start_date_/, /_username_/, /_name_/, /_start_time_/)