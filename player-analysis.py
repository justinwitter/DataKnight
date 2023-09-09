# Player Analysis (DataKnight)
# Justin Witter Aug-Sep 2023

import streamlit as st

import pandas as pd
import numpy as np
import asyncio
from stqdm import stqdm
from random import sample
from chessdotcom.aio import ChessDotComError, get_player_profile, get_player_stats, get_player_games_by_month

import io
import time
import chess.svg
import chess.pgn

import base64

from collections import Counter


# Find more emojis here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="DataKnight - Player Analysis", page_icon=":chess_pawn:", layout='wide', initial_sidebar_state='collapsed')

# hide fullscreen option for images
hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''

st.markdown(hide_img_fs, unsafe_allow_html=True)


# This script generates a Streamlit web app that allows Chess.com players to get information on their openings.
# Link to deployed app: ()


async def get_games(player, start_month,start_year,end_month,end_year):
    """
    This function returns a list of all games that the player has completed in the given timeframe.
    """
    games = []

    # extract games for player
    month_list = pd.period_range(start=str(start_month)+"-"+str(start_year), end=str(end_month)+"-"+str(end_year), freq='M')
    for month in stqdm(month_list, ":runner: Getting games"):
        data = await asyncio.gather(get_player_games_by_month(username=player, year=str(month)[:4], month=str(month)[-2:]))
        games.extend(list(data[0].json.values())[0])
    
    return games


def parse_games(games):
    """
    This functions converts a list of games into a pandas DataFrame.
    """
    games_df = []

    # extract attributes for each game
    for game in stqdm(games, desc=':male-factory-worker: Parsing games'):
      game_id = game['url'].split('/')[-1]
      white_player = game['white']['username']
      black_player = game['black']['username']
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

        eco_path = "./data/eco_codes.csv"
        openings = pd.read_csv(eco_path)

        opening_pgn = openings[openings['eco']==eco]['pgn'].values[0]
        opening = openings[openings['eco']==eco]['name'].values[0]

      except (KeyError, IndexError):
        eco = None
        pgn = None
        opening = None
        opening_pgn = None

      # create row in df
      games_df.append({'game_id':game_id, 'eco':eco, 'opening':opening, 'white_player':white_player, 'black_player':black_player,
                       'white_rating':white_rating, 'black_rating':black_rating, 'white_result':white_result, 'black_result':black_result, 
                       'time_class':time_class, 'time_control':time_control, 'rated':rated, 'rules':rules, 'opening_pgn':opening_pgn,'pgn':pgn})
      
    return pd.DataFrame.from_records(games_df)

async def get_profile(player):
    info = await asyncio.gather(get_player_profile(username=player))
    try:
        avatar = list(info[0].json.values())[0]['avatar']
    except KeyError:
        avatar = None
    try:
        name = list(info[0].json.values())[0]['name']
    except KeyError:
        name = None
    try:
        league = list(info[0].json.values())[0]['league']
    except KeyError:
        league = None

    followers = list(info[0].json.values())[0]['followers']
    return {'avatar':avatar,'name':name,'followers':followers,'league':league}


async def show_stats(player, mode):
    info = await asyncio.gather(get_player_stats(username=player))
    info = list(info[0].json.values())[0]

    try:
        test = info[mode]
        wins = info[mode]['record']['win']
        losses = info[mode]['record']['loss']
        draws = info[mode]['record']['draw']
        current_rating = info[mode]['last']['rating']
    except KeyError:
        return {}
    
    try:
        best_game = info[mode]['best']['game']
        best_rating = info[mode]['best']['rating']
    except KeyError:
        best_game = None
        best_rating = None

    return {'wins':wins, 'losses':losses, 'draws':draws, 'best_game':best_game,'current_rating':current_rating,'best_rating':best_rating}

def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)

def get_fens(pgns):
    all_fens = []
    for i, pgn in enumerate(pgns):
        fens = []
        pgn_stringio = io.StringIO(pgn)
        
        if pgn is None:
            st.write(f'{pgns.count(None)} Nones in pgn list')
            st.write(f'{i} is None')
        
        game = chess.pgn.read_game(pgn_stringio)
        board = game.board()
        fens.append(game.board().fen().split(" ")[0])

        for move in game.mainline_moves():
            board.push(move)
            fens.append(board.fen().split(" ")[0])
        
        all_fens.append(fens)
        
    return all_fens

def check_fens(df, current_fen, is_white):
    results = []
    for i, fens in enumerate(df['fens']):
        if current_fen in fens:
            if is_white:
                results.append(df['white_result'][i])
            else:
                results.append(df['black_result'][i])

    return results

def delete_games():
    if 'games' in st.session_state:
        del st.session_state['games']

# fix multi button presses
# def disable():
#     st.session_state.disabled = True

# # Initialize disabled for form_submit_button to False
# if "disabled" not in st.session_state:
#     st.session_state.disabled = False

# with st.form("myform"):
#     # Assign a key to the widget so it's automatically in session state
#     name = st.text_input("Enter your name below:", key="name")
#     submit_button = st.form_submit_button(
#         "Submit", on_click=disable, disabled=st.session_state.disabled
#     )

#     if submit_button:
#         st.info("You have entered: " + st.session_state.name)

# # Initialize disabled for form_submit_button to False
# if "disabled" not in st.session_state:
# #     st.session_state.disabled = False
st.markdown("""
        <style>
               .block-container {
                    padding-top: 0.75rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

with st.sidebar:
    st.subheader(f':date: Date Range')
    date_cols = st.columns(2)
    years = range(2020, 2024)
    months = range(1, 13)
    
    with date_cols[0]:
        start_year = st.selectbox(f'**Start Year**', years, index=years.index(2023))
        end_year = st.selectbox(f'**End Year**', years, index=years.index(2023))
    with date_cols[1]:
        start_month = st.selectbox(f'**Start Month**', months, index=months.index(9))
        end_month = st.selectbox(f'**End Month**', months, index=months.index(9))

    new_dates = st.button(f':runner: **Get Data**')
    if new_dates:
        delete_games()


header_cols = st.columns(3)    
with header_cols[2]:
    colors = [':white_circle: White',':black_circle: Black']
    chosen_color = st.radio(f'**Color**', colors, index=colors.index(':white_circle: White'))

with header_cols[1]:
    username = st.text_input(f':chess_pawn: Enter your **Chess.com** username...', value="justinwitter")
    username = username.lower()
    try:
        profile = asyncio.run(get_profile(username))
        found = True
    except ChessDotComError:
        st.error('That username doesn\'t seem to exist...')
        found = False


tabs = st.tabs([":information_source: Profile", ":bar_chart: All-Time Stats", ":medal: Top Openings", ":open_book: Opening Analyzer"])

if found:
    # PROFILE SECTION
    with tabs[0]:
        st.write("---")
        if profile['avatar']:
            profile_cols = st.columns(4)
            with profile_cols[1]:
                st.image(profile['avatar'])

        else:
            profile_cols = st.columns(5)

        # add chess.com user link
        

        with profile_cols[2]:
            
            if profile['name']:
                st.write(f':id: **Name**: {profile["name"]}')
            else:
                st.write(f':id: **Username**: {username}')

            st.write(f':bald_man: **Followers**: {profile["followers"]}')
            if profile['league']:
                st.write(f':trident: **League**: {profile["league"]}')
        st.write("---")



    #STATS SECTION
    with tabs[1]:
        st.write("---")
        modes = ['Bullet', 'Blitz', 'Rapid', 'Daily']
        mode_dict = {'Bullet':'chess_bullet', 'Blitz':'chess_blitz', 'Rapid':'chess_rapid', 'Daily':'chess_daily'}
        stats_columns = st.columns(3)
        with stats_columns[0]:
            mode = st.radio(f':clock1: **Mode**', modes, index=modes.index('Rapid'))
            
        try: 
            stats = asyncio.run(show_stats(username,mode_dict[mode]))
        except:
            stats= {}
            st.error('Sorry, there\'s no data available for the specified mode.')
        st.write("---")
        if stats == {}:
            with stats_columns[1]:
                st.error('Sorry, there\'s no data available for the specified mode.')
        else:

            total = stats["wins"] + stats["losses"] + stats["draws"]
            with stats_columns[1]:
                st.write(f':trophy: **Wins**: :green[{stats["wins"]}] (:green[{100*stats["wins"]/total:0.1f}%])')
                st.write(f':x: **Losses**: :red[{stats["losses"]}] (:red[{100*stats["losses"]/total:0.1f}%])')
                st.write(f':heavy_minus_sign: **Draws**: :gray[{stats["draws"]}] (:gray[{100*stats["draws"]/total:0.1f}%])')

            with stats_columns[2]:
                st.write(f':chart: **Current Rating**: {stats["current_rating"]}')
                st.write(f':star: **Best Rating**: {stats["best_rating"]}')



    if "games" not in st.session_state or username != st.session_state.user:
        st.session_state.user = username
        st.session_state.games = asyncio.run(get_games(username,start_month=start_month,start_year=start_year,end_month=end_month,end_year=end_year))

    # TOP OPENINGS SECTION
    with tabs[2]:
        
        if st.session_state.games == []:
            st.error('Sorry, there\'s no data available for the specified time frame. Check if dates are valid.')
        else:
            games_df = parse_games(st.session_state.games)
            games_df = games_df[(games_df['rules']=='chess')]
            games_df = games_df.dropna(subset='pgn')
            games_df.reset_index(inplace=True)
            games_df['white_player'] = games_df['white_player'].str.lower()
            games_df['black_player'] = games_df['black_player'].str.lower()
            games_df['fens'] = get_fens(games_df['pgn'])
            
            st.write("---")

            analysis_cols = st.columns(3)
            with analysis_cols[0]:

                if chosen_color == ':white_circle: White':
                    white = True
                    analysis_df = games_df[games_df['white_player']==username]
                else:
                    white = False
                    analysis_df = games_df[games_df['black_player']==username]

                st.write(f'**Openings faced as {"White :white_circle:" if white else "Black :black_circle:"}**')
                openings_stats = pd.DataFrame()

                openings_stats['Opening'] = analysis_df['opening'].value_counts().index

                games_played = analysis_df["opening"].value_counts().values
                games_played_pct = 100.0*analysis_df["opening"].value_counts(normalize=True).values
                openings_stats['Games Played'] = [f'{value} ({pct:0.1f}%)' for value, pct in zip(games_played,games_played_pct)]

                totals = []
                for opening in openings_stats['Opening']:
                    
       
                    total = len(analysis_df[analysis_df["opening"]==opening])
                    totals.append(total)

                #openings_stats['totals'] = totals

                st.write(openings_stats)



            with analysis_cols[1]:
                st.write(f':star: **Best Opening**: {":construction_worker: Under Construction"}')
                st.write(f':x: **Worst Opening**: {":construction_worker: Under Construction"}')
                st.write(f':heartpulse: **Favorite Opening**: {openings_stats["Opening"][0]}')
            st.write("---")
                
            
    with tabs[3]:
        if st.session_state.games == []: 
            st.error('Sorry, there\'s no data available for the specified time frame. Check if dates are valid.')
        else: 
            # account for variation overlap
            st.write("---")

            board_cols = st.columns([0.4,0.2,0.3,0.1], gap = "large")
            with board_cols[1]:
                speed = st.slider("Time per Move (s)",min_value = 0.1, value=1.0, max_value = 3.0)
                st.write("---")
                play_button = st.button(f':arrow_forward: Play')
                pause_button = st.button(f':double_vertical_bar: Pause')
                next_button = st.button(f':black_right_pointing_double_triangle_with_vertical_bar: Next Move')
                prev_button = st.button(f':black_left_pointing_double_triangle_with_vertical_bar: Previous Move')
                stop_button = st.button(f':black_medium_square: End')
                

            with board_cols[2]:
                if white:
                    opening_df = games_df[games_df['white_player']==username]
                else:
                    opening_df = games_df[games_df['black_player']==username] 

                opening = st.selectbox('Select opening to analyze...', openings_stats['Opening'])
                analysis_df = opening_df[(opening_df['opening']==opening)]
                variations = np.unique(analysis_df['opening_pgn'].values)
                chosen_variations = st.multiselect("Variations", variations, default = variations)
                analysis_df = opening_df[(opening_df['opening_pgn'].isin(chosen_variations))]
             
                analysis_df.reset_index(inplace=True)
                games = []
                for i in stqdm(range(len(analysis_df)), "Collecting Data"):
                    game_id = analysis_df["game_id"].loc[i]
                    
                    if (white):
                        result = analysis_df["white_result"].loc[i] 
                        player_elo = analysis_df["white_rating"].loc[i]
                        opponent_elo = analysis_df["black_rating"].loc[i]
                        opponent = analysis_df["black_player"].loc[i]
                    else:
                        result = analysis_df["black_result"].loc[i] 
                        player_elo = analysis_df["black_rating"].loc[i]
                        opponent_elo = analysis_df["white_rating"].loc[i]
                        opponent = analysis_df["white_player"].loc[i]

                    games.append(f'{username} ({player_elo}) vs. {opponent} ({opponent_elo}) | {result} | ID: {game_id}')

                st.write("---")
            
            chosen_game = st.selectbox(f'Archive ({opening})', games)
            chosen_game_id = chosen_game.split("ID: ")[1]
            st.write("---")


            sides = {True:'white',False:'black'}

            pgn = analysis_df[analysis_df['game_id']==chosen_game_id]['pgn'].values[0]
            pgn_stringio = io.StringIO(pgn)

            if stop_button and 'existing_game' in st.session_state:
                del st.session_state['existing_game']

            # create new game after stop
            if ('existing_game' not in st.session_state) or (opening != st.session_state.opening) or (chosen_game != st.session_state.chosen_game):
                st.session_state['existing_game'] = True
                st.session_state.game = chess.pgn.read_game(pgn_stringio)
                st.session_state.board = st.session_state.game.board()
                st.session_state.prev_board = st.session_state.board.copy()
                st.session_state.move_num = -1
                st.session_state.moves = list(st.session_state.game.mainline_moves())
                st.session_state.opening = opening
                st.session_state.chosen_game = chosen_game
                st.session_state.next_move = chosen_game


            if next_button and st.session_state.move_num != len(st.session_state.moves)-1:
                st.session_state.move_num += 1
                move = st.session_state.moves[st.session_state.move_num]
                st.session_state.board.push(move)

            if prev_button and st.session_state.move_num != -1:
                st.session_state.move_num -= 1
                st.session_state.board.pop()
                
            # display board when stopped
            with board_cols[0]:
                # update board
                svg = chess.svg.board(st.session_state.board, size=500,flipped= not white)
                output = st.empty()
                with output.container():

                    #display updated board
                    render_svg(svg)

                    # display move description
                    if st.session_state.move_num != -1:
                        board = st.session_state.board.copy()
                        board.pop()
                        move = st.session_state.moves[st.session_state['move_num']]
                        side = sides[board.turn].capitalize()
                        fullmove_number = str(board.fullmove_number)
                        move_san = board.san(move)
                        
                        if st.session_state['move_num'] == len(st.session_state.moves)-1:
                            termination = pgn.split("Termination \"")[1].split("\"")[0]
                            st.write(f'**{side} played {fullmove_number}. {move_san} ({termination})**')
                        else:
                            st.write(f'**{side} played {fullmove_number}. {move_san}**')
                    else:
                        st.write("---")

            # display positional analysis
            with board_cols[2]:
                if st.session_state.move_num != -1:
                    outcome_display = st.empty()
                    with outcome_display.container():
                        if white:
                            col = 'white_player'
                        else:
                            col = 'black_player'
                            
                        results = check_fens(games_df[(games_df[col]==username)&(games_df['game_id']!=chosen_game_id)].reset_index(), st.session_state.board.fen().split(" ")[0], white)


                        if len(results) > 0 :
                            counts = Counter(results)
                            wins = counts["win"]
                            losses = counts["checkmated"]+counts["abandoned"]+counts["resigned"]+counts["timeout"]
                            draws = counts["agreed"]+counts["repetition"]+counts["stalemate"]+counts["timevsinsufficient"]+counts["insufficient"]+counts["50move"]
                            

                            win_pct = 100.0*wins/len(results)
                            lose_pct = 100.0*losses/len(results)
                            draw_pct = 100.0*draws/len(results)
                            
                            
                            
                            if win_pct > 60.0:
                                with st.chat_message(name='assistant',avatar='🏆'):
                                    st.write(f'**This is a :green[strong] position for you. You\'ve won from here in :green[{win_pct:0.0f}%] of your previous games.**')
                            elif lose_pct > 60.0:
                                with st.chat_message(name='assistant',avatar='❌'):
                                    st.write(f'**This is a :red[tough] position for you. You\'ve lost from here in :red[{lose_pct:0.0f}%] of your previous games.**')
                            else:
                                with st.chat_message(name='assistant',avatar='➖'):
                                    st.write(f'**This is an :orange[okay] position for you. You\'ve won from here in :orange[{win_pct:0.0f}%] of your previous games.**')
                                


                            st.write(f':trophy: **:green[Wins]**: :green[{counts["win"]}] (:green[{win_pct:0.1f}%])')
                            st.write(f':x: **:red[Losses]**: :red[{losses}] (:red[{lose_pct:0.1f}%])')
                            st.write(f':heavy_minus_sign: **:gray[Draws]**: :gray[{draws}] (:gray[{draw_pct:0.1f}%])')
                        else:
                            st.error("No similar positions found...")
                else:
                    with st.chat_message(name='assistant',avatar='👋'):
                        st.write(f'**Press play or iterate through moves to start.**')
            



            # CREATE CHESS BOARD
            with board_cols[0]:

                if play_button and not stop_button and not pause_button:
                    
                    while not stop_button and not pause_button and st.session_state['move_num'] != len(st.session_state.moves)-1:
                        #get next move
                        st.session_state.move_num += 1
                        move = st.session_state.moves[st.session_state['move_num']]

                        # add move to board
                        st.session_state.board.push(move)
                        
                        # display updated board
                        svg = chess.svg.board(st.session_state.board, size=500, flipped = not white)

                        # display move description
                        board = st.session_state.board.copy()
                        board.pop()
                        move = st.session_state.moves[st.session_state['move_num']]
                        side = sides[board.turn].capitalize()
                        fullmove_number = str(board.fullmove_number)
                        move_san = board.san(move)

                        # wait time
                        time.sleep(speed)
                        
                        
                        if white:
                            results = check_fens(games_df[games_df['white_player']==username].reset_index(), st.session_state.board.fen().split(" ")[0], white)
                        else:
                            results = check_fens(games_df[games_df['black_player']==username].reset_index(), st.session_state.board.fen().split(" ")[0], white)

                        with output.container():
                            render_svg(svg)
                            if st.session_state['move_num'] == len(st.session_state.moves)-1:
                                termination = pgn.split("Termination \"")[1].split("\"")[0]
                                st.write(f'**{side} played {fullmove_number}. {move_san} ({termination})**')
                            else:
                                st.write(f'**{side} played {fullmove_number}. {move_san}**')







                    

        
            



