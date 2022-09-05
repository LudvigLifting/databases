uml:
	dot -T png uml.dot -o er-model.png

html: uml
	pandoc README.md -o readme.html

db:
	rm krusty.db || echo "no db"
	sqlite3 krusty.db < create-schema.sql
	sqlite3 krusty.db < initial-data.sql

start:
	uvicorn krusty-api:app --reload

test:
	python3 check-krusty.py
