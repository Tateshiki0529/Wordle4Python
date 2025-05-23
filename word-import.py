import sqlite3, csv

dbname = "words.db"
word_file = "general-words.csv"

conn = sqlite3.connect(database=dbname)

cursor = conn.cursor()

with open(file=word_file, mode="r", newline="", encoding="utf-8") as fp:
	reader = csv.DictReader(f=fp)
	data = [r for r in reader]

for row in data:
	print("Adding %s..." % row["word"] ,end="")
	try:
		cursor.execute('INSERT INTO "general-words"("word","count","CEFR","meaning","example","example-jp") VALUES (?, ?, ?, ?, ?, ?);', (row['word'], len(row['word']), row['CEFR'], row['Japanese'], row['Example'], row['Example_JP']))
		print(" [Complete]")
	except sqlite3.IntegrityError:
		print(" [Passed]")

conn.commit()
conn.close()