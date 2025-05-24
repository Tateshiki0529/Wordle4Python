from discord import (
	Cog, Bot, ApplicationContext, Message, DMChannel, Interaction
)
from discord import option
from discord.ext.commands import slash_command as command
from datetime import datetime as dt, timezone as tz, timedelta as td
from math import floor
from json import load, dump

from os import getcwd
import sys, random, re

sys.path.append(getcwd()+'/../')

from wordle4python import Wordle4Python

from utils.functions import log
from utils.autocomplete import AutoComplete

class Wordle(Cog):
	def __init__(self, bot: Bot) -> None:
		log('[Wordle] Loading extension \'Wordle\'...')
		super().__init__()
		self.bot: Bot = bot
		self.w4p: dict[str, Wordle4Python] = {}
		self.interactions: dict[str, Interaction] = {}
		self.progresses: dict[str, list[str]] = {}
		log('[Wordle] Extension \'Wordle\' loaded.')
		return
	
	@command(
		name = 'wordle',
		description = '新規Wordleを開始します [Extension: Wordle]'
	)
	@option(
		name = 'words_count',
		type = int,
		description = '単語の文字数',
		required = False,
		default = 5
	)
	@option(
		name = 'guess_count',
		type = int,
		description = 'チャレンジ回数',
		required = False,
		default = 6
	)
	@option(
		name = 'seed',
		type = int,
		description = 'シード値',
		required = False
	)
	@option(
		name = 'words_table',
		type = str,
		description = '使用するワードテーブル名',
		required = False,
		default = "general-words"
	)
	async def __wordle(self, ctx: ApplicationContext, words_count: int = 5, guess_count: int = 6, seed: int = random.randint(0, 65535), words_table: str = "general-words") -> None:
		if ctx.author.name in self.w4p.keys():
			await ctx.respond('Error: 既にゲームを開始しています！')
			return
		self.w4p[ctx.author.name] = Wordle4Python(
			words_table=words_table,
			word_count=words_count,
			guess_count=guess_count,
			seed=seed
		)
		text = ['%s is playing: (%s)' % (ctx.author.mention, self.w4p[ctx.author.name].word['word']), '']
		for h in range(0, guess_count):
			text.append('<:wordle_empty:1375635744483180735>' * words_count)
		
		self.interactions[ctx.author.name] = await ctx.respond('\n'.join(text))
		self.progresses[ctx.author.name] = text
	
	@Cog.listener()
	async def on_message(self, msg: Message) -> None:
		if isinstance(msg.channel, DMChannel):
			if msg.author.name in self.w4p.keys():
				word = ''
				for w in list(msg.content):
					if len(re.findall('[a-zA-Z]', w)) == 0:
						await msg.reply('Error: 使えない文字が入っています！(半角英文字のみ)')
						return
					word += w
				if len(word) != self.w4p[msg.author.name].words_count:
					await msg.reply('Error: %d文字で入力してください！' % self.w4p[msg.author.name].words_count)
					return
				result = self.w4p[msg.author.name].guess(word=word)
				line = ''
				if result == True:
					line = '<:wordle_match:1375636434211442870>' * self.w4p[msg.author.name].words_count
				else:
					for c in result:
						if c['match'] == True:
							line += '<:wordle_match:1375636434211442870>'
						elif c['match'] == False and c['include'] == True:
							line += '<:wordle_include:1375636265172598966>'
						else:
							line += '<:wordle_incorrect:1375636083525550080>'
				print(self.w4p[msg.author.name].guess_count + 2)
				self.progresses[msg.author.name][self.w4p[msg.author.name].guess_count + 1] = line
				self.interactions[msg.author.name] = await self.interactions[msg.author.name].edit(content='\n'.join(self.progresses[msg.author.name]))
				if result == True:
					await msg.reply('正解！')
					del self.progresses[msg.author.name]
					del self.interactions[msg.author.name]
					del self.w4p[msg.author.name]
					return
				if self.w4p[msg.author.name].max_guess_count == self.w4p[msg.author.name].guess_count:
					await msg.reply('チャレンジ回数をオーバーしました…')
					del self.progresses[msg.author.name]
					del self.interactions[msg.author.name]
					del self.w4p[msg.author.name]
					return

def setup(bot: Bot):
	bot.add_cog(Wordle(bot=bot))