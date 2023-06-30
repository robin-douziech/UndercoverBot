import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys
import json
import random

from UnderCoverBot import *

load_dotenv()

bot = UnderCoverBot(players_file, vars_file)

@bot.event
async def on_ready() :

	bot.bot_guild = bot.get_guild(bot_guild_id)
	bot.bot_txt_channel = bot.bot_guild.get_channel(bot_txt_channel_id)

	#============================#
	# RÉCUPÉRATION DES VARIABLES #
	#============================#

	with open(bot.players_file, "rt") as f :
		bot.players = json.load(f)
	with open(bot.vars_file, "rt") as f :
		bot.vars = json.load(f)

	bot.stop_game()

	print(f"players_file : {bot.players_file}")

@bot.command(name="play")
async def play_ucb(ctx, play=None) :

	dm_channel = ctx.author.dm_channel
	if dm_channel == None :
		dm_channel = await ctx.author.create_dm()

	author_name = f"{ctx.author.name}#{ctx.author.discriminator}"

	if bot.dm_command(ctx) :

		if not(bot.vars['game_started']) :

			if play in ['True', 'true', 'Yes', 'yes', 'T', 't', 'Y', 'y', '1'] :
				if author_name in bot.players :
					await dm_channel.send(f"Tu es déjà inscrit(e) à la partie")
				else :
					bot.players[author_name] = {
						"alive": False,
						"role" : "",
						"vote" : ""
					}
					await dm_channel.send(f"C'est bon, tu es inscrit(e) à la partie")
					await bot.bot_txt_channel.send(f"{author_name} joue avec nous")

			elif play in ['False', 'false', 'No', 'no', 'F', 'f', 'N', 'n', '0'] :
				if author_name in bot.players :
					bot.players.pop(author_name)
					await dm_channel.send("C'est bon, tu es désinscrit(e) de la partie")
					await bot.bot_txt_channel.send(f"{author_name} ne joue plus avec nous")
				else :
					await dm_channel.send(f"Tu n'es pas inscrit(e) à la partie")

			else :
				await dm_channel.send(f"Commande incorrecte")

			bot.write_json(bot.players, bot.players_file)

		else :
			await dm_channel.send(f"Une partie est déjà en cours")

@bot.command(name="game")
async def game_ucb(ctx, action=None) :

	dm_channel = ctx.author.dm_channel
	if dm_channel == None :
		dm_channel = await ctx.author.create_dm()

	author_name = f"{ctx.author.name}#{ctx.author.discriminator}"

	if bot.dm_command(ctx) and ctx.author.id == bot_owner_id :

		if action == "start" :

			if not(bot.vars['game_started']) :

				bot.vars['game_started'] = True
				for player in bot.players :
					bot.players[player]['alive'] = True
				players_list = list(bot.players.keys())
				bot.vars['compo'] = bot.vars['def_compos'][str(len(players_list))]

				# choix des mots
				with open(words_file, "rt") as f :
					wordlist = f.readlines()
					num_line = random.randint(0,len(wordlist)-1)
					invert = random.randint(0,1)
					if invert == 0 :
						bot.vars['civils_word'] = wordlist[num_line].split('\n')[0].split(';')[0]
						bot.vars['undercovers_word'] = wordlist[num_line].split('\n')[0].split(';')[1]
					else :
						bot.vars['civils_word'] = wordlist[num_line].split('\n')[0].split(';')[1]
						bot.vars['undercovers_word'] = wordlist[num_line].split('\n')[0].split(';')[0]
					bot.write_json(bot.vars, bot.vars_file)

				# distribution des rôles
				for i in range(bot.vars['compo']['mr.white']) :
					player = random.choice(players_list)
					bot.players[player]['role'] = "mr.white"
					bot.players[player]['guess'] = ""
					players_list.remove(player)
				first_player = randomt.choice(players_list)
				for i in range(bot.vars['compo']['undercover']) :
					player = random.choice(players_list)
					bot.players[player]['role'] = "undercover"
					players_list.remove(player)
				for player in players_list :
					bot.players[player]['role'] = "civil"

				bot.write_json(bot.players, bot.players_file)
				bot.write_json(bot.vars, bot.vars_file)

				for player in bot.players :
					dm_channel_tmp = bot.fetch_member(player).dm_channel
					if dm_channel_tmp == None :
						dm_channel_tmp = await bot.fetch_member(player).create_dm()
					if bot.players[player]['role'] == "mr.white" :
						await dm_channel_tmp.send(f"Tu es mr.white")
					elif bot.players[player]['role'] == "civil" :
						await dm_channel.send(f"Ton mot est {bot.vars['civils_word']}")
					else :
						await dm_channel.send(f"Ton mot est {bot.vars['undercovers_word']}")

				await bot.bot_txt_channel.send(f"{first_player} commence à dire son mot")
				
			else :

				await ctx.channel.send(f"Une partie est déjà en cours")

		elif action == "stop" :

			if bot.vars['game_started'] :

				bot.stop_game()

			else :

				await ctx.channel.send(f"Aucune partie en cours")

		else :

			await ctx.channel.send(f"Commande incorrecte")


@bot.command(name="vote")
async def vote_ucb(ctx, action=None) :

	dm_channel = ctx.author.dm_channel
	if dm_channel == None :
		dm_channel = await ctx.author.create_dm()

	author_name = f"{ctx.author.name}#{ctx.author.discriminator}"

	if bot.dm_command(ctx) :

		if action in bot.players and action != author_name and bot.players[action]['alive'] :

			bot.players[author_name]['vote'] = action
			bot.write_json(bot.players, bot.players_file)
			await dm_channel.send(f"C'est noté ! Tu as voté pour {action}")

		elif action == "done" and ctx.author.id == bot_owner_id and not(bot.vars['wait_mr.white']) :

			everyone_voted = True
			for player in bot.players :
				if bot.players[player]['vote'] == "" :
					everyone_voted = False

			if everyone_voted :

				msg = f"Liste des votes :\n"
				for player in [p for p in bot.players if bot.players[p]['alive']] :
					msg += f"{player} ===> {bot.players[player]['vote']}\n"
				await bot.bot_txt_channel.send(msg)

				vote_count = {player:0 for player in bot.players if bot.players[player]['alive']}
				for player in [p for p in bot.players if bot.players[p]['alive']] :
					vote_count[bot.players[player]['vote']] += 1

				max_vote = 0
				for player in vote_count :
					if vote_count[player] > max_vote :
						max_vote = vote_count[player]

				max_vote_players = []
				for player in vote_count :
					if vote_count[player] == max_vote :
						max_vote_players.append(player)

				if len(max_vote_players) > 1 :
					await bot.bot_txt_channel.send(f"Égalité ! Il faut revoter !")
				else :
					await bot.player_death(max_vote_players[0])

				for player in bot.players :
					bot.players[player]['vote'] = ""
					bot.write_json(bot.players, bot.players_file)

			else :

				await dm_channel.send(f"Tous les joueurs n'ont pas voté")

		else :

			await dm_channel.send("Commande incorrecte")



@bot.command(name="guess")
async def guess_ucb(ctx, word) :

	dm_channel = ctx.author.dm_channel
	if dm_channel == None :
		dm_channel = await ctx.author.create_dm()

	author_name = f"{ctx.author.name}#{ctx.author.discriminator}"

	if bot.dm_command(ctx) :

		if bot.vars['game_started'] and bot.players[author_name]['role'] == "mr.white" :

			if word == "Null" :
				bot.players[author_name]['guess'] = ""
			else :
				bot.players[author_name]['guess'] = word

			bot.write_json(bot.players, bot.players_file)

			if bot.vars['wait_mr.white'] and bot.players[author_name]['guess'] != "" :

				bot.vars['wait_mr.white'] = False
				bot.players[author_name]['alive'] = False
				bot.write_json(bot.players, bot.players_file)
				bot.write_json(bot.vars, bot.vars_file)
				bot.death()








@bot.command(name="kill")
async def kill_ucb(ctx) :
	if ctx.author.id == bot_owner_id :
		sys.exit()

bot.run(os.getenv("TOKEN"))