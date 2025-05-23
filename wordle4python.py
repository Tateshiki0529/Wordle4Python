from sqlite3 import connect
from os.path import isfile
import random

class Wordle4Python:
	def __init__(self, words_db: str = "words.db", words_table: str = "general-words", word_count: int = 5, guess_count: int = 6, CEFR: str = None, seed: int = random.randint(0, 65535)) -> None:
		if not isfile(path=words_db):
			raise Exception("指定されたデータベース \"%s\" は存在しません！" % words_db)
		self.conn = connect(database=words_db)
		self.cursor = self.conn.cursor()

		self.cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE TYPE = "table" AND NAME = "%s";' % words_table)
		if self.cursor.fetchone() == (0,):
			raise Exception("指定されたワードテーブル \"%s\" は存在しません！" % words_table)
		
		sql = 'SELECT * FROM "%s" WHERE count = ?' % words_table
		params = (word_count, )
		if CEFR:
			sql = sql + " AND CEFR = ?"
			params = params + CEFR
		sql = sql + ";"

		self.cursor.execute(sql, params)
		words = self.cursor.fetchall()
		self.words = []
		self.words_details = []

		for word in words:
			self.words_details.append({
				'word': word[0],
				'word_count': word[1],
				'CEFR': word[2],
				'meaning': word[3],
				'example': word[4],
				'example_japanese': word[5]
			})
			self.words.append(word[0])
		
		self.seed = seed
		random.seed(a=self.seed)
		self.word = random.choice(self.words_details)

		self.max_guess_count = guess_count
		self.words_count = word_count
		self.guess_count = 0

		return
	
	def guess(self, word: str) -> list|bool:
		if word not in self.words:
			raise Exception("入力された単語は単語リストにありません！")
		self.guess_count += 1
		if self.max_guess_count < self.guess_count:
			raise Exception("チャレンジ回数をオーバーしました！")
		
		char_list = list(self.word['word'])
		guess_char_list = list(word)

		index = 0
		match_count = 0
		output = []
		char_count = {}
		guess_char_count = {}
		for char in char_list:
			char_count[char] = char_count.get(char, 0) + 1
		for guess_char in guess_char_list:
			if char_list[index] == guess_char: # 場所まで一致
				guess_char_count[guess_char] = guess_char_count.get(guess_char, 0) + 1
				output.append({
					'char': guess_char,
					'match': True,
					'include': (guess_char_count[guess_char] <= char_count[guess_char])
				})
				match_count += 1
			elif guess_char in char_list and char_list[index] != guess_char: # 含む (場所は違う)
				guess_char_count[guess_char] = guess_char_count.get(guess_char, 0) + 1
				output.append({
					'char': guess_char,
					'match': False,
					'include': (guess_char_count[guess_char] <= char_count[guess_char])
				})
			else:
				output.append({
					'char': guess_char,
					'match': False,
					'include': False
				})
			index += 1

		if match_count == self.words_count:
			return True
		return output