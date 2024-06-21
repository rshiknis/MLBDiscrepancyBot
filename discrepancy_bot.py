import discord
import pandas as pd
from tabulate import tabulate
import requests
import json

def fetch_prizepicks_data():
    response = requests.get("https://partner-api.prizepicks.com/projections?per_page=1000")
    data = response.json()
    
    projections = data["data"]
    included = data["included"]
    
    flattened_data = []
    for item in projections:
        attributes = item["attributes"]
        relationships = item["relationships"]
        league_id = relationships["league"]["data"]["id"]
        player_id = relationships["new_player"]["data"]["id"]
        projection_type_id = relationships["projection_type"]["data"]["id"]
        stat_type_id = relationships["stat_type"]["data"]["id"]
        entry_type = attributes.get("odds_type", "standard") 
        flattened_data.append({
            "id": item["id"],
            "board_time": attributes["board_time"],
            "description": attributes["description"],
            "line_score": attributes["line_score"],
            "odds_type": attributes["odds_type"],
            "projection_type": attributes["projection_type"],
            "stat_type": attributes["stat_type"],
            "league_id": league_id,
            "player_id": player_id,
            "projection_type_id": projection_type_id,
            "stat_type_id": stat_type_id,
            "start_time": attributes["start_time"],
            "status": attributes["status"],
            "updated_at": attributes["updated_at"],
            "is_promo": attributes.get("is_promo", False),
            "flash_sale_line_score": attributes.get("flash_sale_line_score"),
            "end_time": attributes.get("end_time"),
            "refundable": attributes.get("refundable", False),
            "today": attributes.get("today", False),
            "custom_image": attributes.get("custom_image"),
            "discount_percentage": attributes.get("discount_percentage"),
            "League" : attributes.get("league"), 
            "entry_type": entry_type
        })
    
    player_data = []
    for item in included:
        if item["type"] == "new_player":
            player_data.append({
                "player_id": item["id"],
                "display_name": item["attributes"]["display_name"],
                "league" : item["attributes"]["league"]
            })    
    
    df_projections = pd.DataFrame(flattened_data)
    df_players = pd.DataFrame(player_data)
    df_merged = pd.merge(df_projections, df_players, on="player_id", how="left")
    df_merged = df_merged[['display_name', 'league', 'stat_type', 'line_score', 'entry_type', 'projection_type_id', 'start_time']]
    df_merged['line_score'] = df_merged['line_score'].astype(float)
    
    rename_dict = {
        'Hits Allowed': 'Player Hits Allowed',
        'Walks Allowed': 'Player Walks',
        'Stolen Bases': 'Player Stolen Bases',
        'Pitching Outs': 'Player Outs',
        'Home Runs': 'Player Home Runs',
        'Doubles': 'Player Doubles',
        'Singles': 'Player Singles',
        'Runs': 'Player Runs',
        'Hitter Strikeouts': 'Player Batting Strikeouts',
        'Walks': 'Player Batting Walks',
        'RBIs': 'Player RBIs',
        'Pitcher Strikeouts': 'Player Strikeouts',
        'Total Bases': 'Player Bases',
        'Hits+Runs+RBIs': 'Player Hits + Runs + RBIs',
        'Hits': 'Player Hits',
        'Earned Runs allowed': 'Player Earned Runs'
    }
    df_merged['stat_type'] = df_merged['stat_type'].replace(rename_dict)
    return df_merged

def fetch_draftkings_data():
    url = 'https://api.opticodds.com/api/v2/games'
    params = {
        'sport': 'baseball',
        'league': 'MLB'
    }
    headers = {
        'X-Api-Key': 'Enter API Key'
    }

    response = requests.get(url, headers=headers, params=params)

    # Check if the response is successful
    if response.status_code == 200:
        # Decode and parse the JSON response
        response_content = response.content
        if isinstance(response_content, bytes):
            response_content = response_content.decode('utf-8')
        
        data_dict = json.loads(response_content)
        data = data_dict.get('data', [])
        
        # Extract game details
        games = []
        for game in data:
            if game.get('status', '') == 'unplayed':
                games.append({
                    'game_id': game.get('id', ''),
                    'start_time': game.get('start_date', ''),
                    'home_team': game.get('home_team', ''),
                    'away_team': game.get('away_team', ''),
                    'status': game.get('status', '')
                })
        
        df_games = pd.DataFrame(games)
        return df_games
    else:
        print(f"Error: {response.status_code}")
        print(response.content)
        return None

def get_game_odds(game_id):
    url = 'https://api.opticodds.com/api/v2/game-odds'
    params = {
        'sport': 'baseball',
        'league': 'MLB',
        'sportsbook': 'DraftKings',
        'game_id': game_id
    }
    headers = {
        'X-Api-Key': 'Enter API Key'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response_content = response.content
        if isinstance(response_content, bytes):
            response_content = response_content.decode('utf-8')
        
        data_dict = json.loads(response_content)
        data = data_dict.get('data', [])

        player_odds = []
        for game in data:
            for odds in game.get('odds', []):
                if odds.get('player_id'):
                    player_odds.append({
                        'player_name': odds.get('selection', '').lower(),
                        'market_name': odds.get('market_name', '').lower(),
                        'bet_points': odds.get('bet_points', None),
                        'price': odds.get('price', None),
                        'selection_line': odds.get('selection_line', None)
                    })
        
        df = pd.DataFrame(player_odds)
        return df
    else:
        print(f"Error: {response.status_code}")
        print(response.content)
        return None

def merge_over_under(df):
    df_over = df[df['selection_line'] == 'over'].rename(columns={'price': 'over_price'})
    df_under = df[df['selection_line'] == 'under'].rename(columns={'price': 'under_price'})
    
    df_merged = pd.merge(df_over, df_under, on=['player_name', 'market_name', 'bet_points'], how='inner')
    
    df_merged = df_merged[['player_name', 'market_name', 'bet_points', 'over_price', 'under_price']]
    
    return df_merged

def handle_user_messages(df, msg) -> str:
    message = msg.content.lower()
    if message == "hi":
        return 'Hi there'
    elif message == "hello":
        return 'Hello user. Welcome'
    if message == "discrepancy":
        player_data = df[
        (df['entry_type'] == 'Standard') & 
        (df['PP'] < df['DK']) &
        (df['league'] != 'MLBLIVE') &
        (df['Over'] > df['Under']) 
        ]
        if player_data.empty:
            player_data = df[
            (df['entry_type'] == 'Standard') & 
            (df['PP'] > df['DK']) &
            (df['league'] != 'MLBLIVE') &
            (df['Under'] > df['Over']) 
            ]
            if player_data.empty:
                return "No discrepancies right now, check later!"
            else:
                player_data = player_data.reset_index(drop=True)
                player_data_str = player_data.to_string(index=False, header=True).split('\n')
                formatted_str = "```\n" + "\n".join(player_data_str) + "\n```"
                return formatted_str
        else:
            second_discrep = df[
            (df['entry_type'] == 'Standard') & 
            (df['PP'] > df['DK']) &
            (df['league'] != 'MLBLIVE') &
            (df['Under'] > df['Over']) 
            ]
            if not second_discrep.empty:
                player_data = pd.concat([player_data, second_discrep], ignore_index=True)
            player_data = player_data.reset_index(drop=True)
            player_data_str = player_data.to_string(index=False, header=True).split('\n')
            formatted_str = "```\n" + "\n".join(player_data_str) + "\n```"
            return formatted_str
    elif message == 'ev plays':
        player_data = df[
        (df['entry_type'] == 'standard') & 
        (df['PP'] == df['DK']) & 
        ((df['Over'] <= -135) | (df['Under'] <= -135))
        ]
        if player_data.empty:
            return "No +EV on the board right now. Check again later"
        player_data = player_data.reset_index(drop=True)
        player_data_str = player_data.to_string(index=False, header=True).split('\n')
        formatted_str = "```\n" + "\n".join(player_data_str) + "\n```"
        return formatted_str
    else:
        player_data = df[df['Name'].str.contains(message, na=False)]
        if player_data.empty:
            return "Player not found."
        player_data = player_data.reset_index(drop=True)
    
        player_data_str = player_data.to_string(index=False, header=True).split('\n')
        formatted_str = "```\n" + "\n".join(player_data_str) + "\n```"
        return formatted_str

async def processMessage(df, message):
    try:
        botfeedback = handle_user_messages(df, message)
        if botfeedback:
            await message.channel.send(botfeedback)
    except Exception as error:
        print(error)

def runBot():
    discord_token = 'Enter Discord Bot Token'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    df_prizepicks = fetch_prizepicks_data()
    df_games = fetch_draftkings_data()


    all_props = pd.DataFrame()
    if df_games is not None:
        for _, game in df_games.iterrows():
            game_id = game['game_id']
            df_props = get_game_odds(game_id)
            if df_props is not None and not df_props.empty:
                all_props = pd.concat([all_props, df_props], ignore_index=True)
    
    if not all_props.empty:
        merged_props = merge_over_under(all_props)
        df_prizepicks['display_name'] = df_prizepicks['display_name'].str.lower()
        df_prizepicks['stat_type'] = df_prizepicks['stat_type'].str.lower()

        df_merged = pd.merge(df_prizepicks, merged_props, left_on=['display_name', 'stat_type'], right_on=['player_name', 'market_name'], how='inner')
        df_merged = df_merged[['display_name', 'league', 'stat_type', 'line_score', 'bet_points','entry_type', 'over_price', 'under_price']]
        df_merged = df_merged.rename(columns = {'display_name' : 'Name', 'stat_type': 'Prop', 'line_score' : 'PP', 'bet_points' : 'DK', 'over_price': 'Over', 'under_price': 'Under'})
        df_merged['Prop'] = df_merged['Prop'].replace({'player batting strikeouts': 'hitter strikeouts', 'player hits + runs + rbis' : 'player h+r+r'})
        @client.event
        async def on_ready():
            print(f'{client.user} is live')

        @client.event
        async def on_message(message):
            if message.author == client.user:
                return
            await processMessage(df_merged, message)

        client.run(discord_token)

