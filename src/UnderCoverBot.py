import discord
from discord.ext import commands
import json

from variables import *

class UnderCoverBot(commands.Bot) :

	def __init__(self, players_file, vars_file) :
		super().__init__(command_prefix="!", intents=discord.Intents.all())

		self.players_file = players_file
		self.players = {}

		self.vars_file = vars_file
		self.vars = {}


	def write_json(self, dico, file) :

		""" Writes the content of the given dictionary in the givent file in JSON format.
		"""

		json_object = json.dumps(dico, indent=2)
		with open(file, "wt") as f :
			f.write(json_object)


	def fetch_member(self, pseudo) :

		""" Finds a member by his name.
		Parameters :
			- pseudo (str) : the pseudonym of a member of the guild (ex: M1k3y#8407)
		Returns :
			- member (discord.Member or None) : the corresponding discord.Member if this pseudo exists in the guild (None else)
		"""

		for member in self.bot_guild.members :
			if pseudo == f"{member.name}#{member.discriminator}" :
				return member
		return None


	def dm_command(self, ctx) :
		"""Is this command sent in a DM channel ?"""
		return ctx.channel == ctx.author.dm_channel


	def channel_command(self, ctx) :
		"""Is this command sent in the self.bot_txt_channel channel ?"""
		return ctx.channel == self.bot_txt_channel

	def stop_game(self) :

		self.vars['game_started'] = False
		self.vars['wait_mr.white'] = False
		self.vars['civils_word'] = ""
		self.vars['undercovers_word'] = ""
		self.vars['compo'] = {}
		self.write_json(self.vars, self.vars_file)

		for player in self.players :
			self.players[player] = {
				"alive": False,
				"role": "",
				"vote": ""
			}
		self.write_json(self.players, self.players_file)

	async def mr_white_death(self, player) :

		if self.players[player]['guess'] == "" :
			await self.bot_txt_channel.send(f"Mr.white n'a pas encore tenté de deviner le mot des civils, attendez qu'il fasse sa tentative...")
			self.vars['wait_mr.white'] = True
			self.write_json(self.vars, self.vars_file)
		elif self.players[player]['guess'] == self.vars['civils_word'] :
			await self.bot_txt_channel.send(f"Mr.white a deviné le mot des civils, il remporte la partie")
			self.stop_game()
		else :
			await self.bot_txt_channel.send(f"Mr.white n'a pas deviné le mot des civils")

	async def player_death(self, player) :

		await self.bot_txt_channel.send(f"{player} a été désigné(e) par le vote. Il/elle était {self.players[player]['role']}")

		if self.players[player]['role'] == "mr.white" :
			await self.mr_white_death(player)

		self.players[player]['alive'] = False
		self.write_json(self.players, self.players_file)

		if not(self.vars['wait_mr.white']) :
			await self.death()

	async def death(self) :

		alive_roles = {"civil":0, "undercover":0, "mr.white":0}
		for player in [p for p in self.players if self.players[p]['alive']] :
			alive_roles[self.players[player]['role']] += 1

		if alive_roles["mr.white"] == 0 :
			if alive_roles["undercover"] == 0 :
				await self.bot_txt_channel.send(f"Fin de la partie : les civils ont gagné")
			elif alive_roles["undercover"] >= alive_roles["civils"] :
				await self.bot_txt_channel.send(f"Fin de la partie : les undercover ont gagné")

		return end,winners