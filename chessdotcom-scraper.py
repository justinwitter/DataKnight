# Chess.com Scraper (DataKnight)
# Justin Witter Aug-Sep 2023

import pandas as pd
import asyncio
from tqdm import tqdm
from random import sample
from chessdotcom.aio import ChessDotComError, get_country_players, get_country_clubs, get_club_members, get_player_games_by_month

"""
This is a script to scrape online chess games from chess.com's public API (chess.com/news/view/published-data-api#pubapi-endpoint-country-players). 
The chess.com Python Wrapper (https://chesscom.readthedocs.io/_/downloads/en/latest/pdf/) is used to leverage pre-built methods that can access 
all endpoints provided by the API. Asynchronous requests are made to gather relevant information such as lists of chess.com users by country, 
stats related to each user, and their monthly games played. The file "raw_data.csv" is created in main() to export the retrieved data.
"""

async def get_players(country):
    """
    This function returns a list of users that identify themselves as being in the given country. The chess.com API does not currently 
    support pagination, therefore only the first 10,000 usernames (alphabetical order) are provided.
    """
    players = await asyncio.gather(get_country_players(country))
    return list(players[0].json.values())[0]

async def get_club_players(country):
    """
    This function returns a list of members from all clubs that are located in or are associated with the given country.
    """
    # get clubs from country
    clubs = await asyncio.gather(get_country_clubs(country))
    clubs = [x.split('club/')[1] for x in list(clubs[0].json.values())[0]]

    # extract members from each club
    club_players = []
    for club in clubs:
      club_dict = await asyncio.gather(get_club_members(club))
      club_dict = list(club_dict[0].json.values())[0]
      for activity_level in club_dict:
        club_players.extend([x['username'] for x in club_dict[activity_level]])

      return club_players

async def get_games(all_players, month, year):
    """
    This function returns a list of all games that players have completed in the given month/year.
    """
    games = []

    # extract games for each player
    for player in tqdm(all_players, desc='Getting games'):
      try:
        data = await asyncio.gather(get_player_games_by_month(username=player, year=year, month=month))
        games.extend(list(data[0].json.values())[0])
      except ChessDotComError:
        continue

    return games

def parse_games(games):
    """
    This functions converts a list of games into a pandas DataFrame.
    """
    games_df = []

    # extract attributes for each game
    for game in tqdm(games, desc='Parsing games'):
      game_id = game['url'].split('/')[-1]
      white_rating = game['white']['rating']
      black_rating = game['black']['rating']
      white_result = game['white']['result']
      black_result = game['black']['result']
      time_class = game['time_class']
      time_control = game['time_control']
      rated = game['rated']
      rules = game['rules']

      # include opening/pgn if a move has been played
      try:
        pgn = game['pgn']
        eco = game['pgn'].split('ECO "')[1].split('"')[0]

        eco_path = '/content/eco_codes.csv'
        openings = pd.read_csv(eco_path)

        opening_pgn = openings[openings['eco']==eco]['pgn'].values[0]
        opening = openings[openings['eco']==eco]['name'].values[0]

      except (KeyError, IndexError):
        eco = None
        pgn = None
        opening = None
        opening_pgn = None

      # create row in df
      games_df.append({'game_id':game_id, 'eco':eco, 'opening':opening, 'white_rating':white_rating, 'black_rating':black_rating, 
                       'white_result':white_result, 'black_result':black_result, 'time_class':time_class, 
                       'time_control':time_control, 'rated':rated, 'rules':rules, 'opening_pgn':opening_pgn,'pgn':pgn})
      
    return pd.DataFrame.from_records(games_df)

async def main():
    all_players = []

    # get list of countries (2-character iso 3166 codes)
    iso_path = '/content/iso_3166_codes.csv'
    countries = pd.read_csv(iso_path)['alpha-2']

    # get players from each country
    for country in tqdm(countries, desc='Getting players'):
      try :
        all_players.extend(await get_players(country))
        # uncomment below to include more players **significantly increases runtime**
        #all_players.extend(await get_club_players(country))
      except ChessDotComError:
        pass

    # remove duplicate players
    all_players = list(set(all_players))

    # randomize players and limit sample if needed
    player_limit = 1000
    random_players = sample(all_players, player_limit) if player_limit < len(all_players) else all_players

    # get monthly games for each player
    all_games = await get_games(random_players, month = '08', year = '2023')

    # randomize games and limit sample if needed
    game_limit = 10000
    random_games = sample(all_games, game_limit) if game_limit < len(all_games) else all_games

    # convert games into df
    games_df = parse_games(random_games)

    # output csv
    games_df.to_csv('raw_data.csv')

# Run Scraper
await main()
