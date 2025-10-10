import pandas as pd
import json
from sklearn.preprocessing import LabelEncoder
import helpers.data_structures as ds

import valorant_constants as vc



def get_attacker(round_number):
    if round_number <= 11:
        return "RED"
    elif round_number <= 23:
        return "BLUE"
    elif round_number % 2 == 1:
        return "RED"
    else:
        return "BLUE"



def json_to_dataframe(json_file: str) -> pd.DataFrame:
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        round_variables = []

        for match in data.get("matches", []):
            player_match_data = ds.BiKeyDict()
            map = vc.map_names[match.get("matchInfo").get("mapId")]

            red_player_count = 1
            blue_player_count = 1
            for player in match.get("players", []):
                player_id = player.get("puuid")

                player_match_id = ""
                team_id = player.get("teamId")
                if (team_id == "RED"):
                    player_match_id = f"{team_id}_{red_player_count}"
                    red_player_count = red_player_count + 1
                elif (team_id == "BLUE"):
                    player_match_id = f"{team_id}_{blue_player_count}"
                    blue_player_count = blue_player_count + 1
                else:
                    print(F"Player {player_id} has team id other than BLUE or RED!")

                player_match_data.add(player_id, player_match_id, {"puuid": player_id, "player_match_id": player_match_id, "agent": vc.agent_names[player.get("characterId")]})

            for round in match.get("roundResults", []):
                player_loadouts = {}
                for player_stat in round.get("playerStats", []):
                    puuid = player_stat.get("puuid")
                    player_match_id = player_match_data.get(puuid)["player_match_id"]
                    player_loadouts[player_match_id] = {"agent": player_match_data.get(puuid)["agent"], "weapon": vc.weapon_names[player_stat.get("economy").get("weapon")], "armor": vc.shield_names[player_stat.get("economy").get("armor")]}

                round_variables.append({
                    "winner_team": round.get("winningTeam"),
                    "attacker_team": get_attacker(round.get("roundNum")),
                    "map": map,
                    "RED_1_agent": player_loadouts["RED_1"]["agent"],
                    "RED_1_weapon": player_loadouts["RED_1"]["weapon"],
                    "RED_1_armor": player_loadouts["RED_1"]["armor"],
                    "RED_2_agent": player_loadouts["RED_2"]["agent"],
                    "RED_2_weapon": player_loadouts["RED_2"]["weapon"],
                    "RED_2_armor": player_loadouts["RED_2"]["armor"],
                    "RED_3_agent": player_loadouts["RED_3"]["agent"],
                    "RED_3_weapon": player_loadouts["RED_3"]["weapon"],
                    "RED_3_armor": player_loadouts["RED_3"]["armor"],
                    "RED_4_agent": player_loadouts["RED_4"]["agent"],
                    "RED_4_weapon": player_loadouts["RED_4"]["weapon"],
                    "RED_4_armor": player_loadouts["RED_4"]["armor"],
                    "RED_5_agent": player_loadouts["RED_5"]["agent"],
                    "RED_5_weapon": player_loadouts["RED_5"]["weapon"],
                    "RED_5_armor": player_loadouts["RED_5"]["armor"],
                    "BLUE_1_agent": player_loadouts["BLUE_1"]["agent"],
                    "BLUE_1_weapon": player_loadouts["BLUE_1"]["weapon"],
                    "BLUE_1_armor": player_loadouts["BLUE_1"]["armor"],
                    "BLUE_2_agent": player_loadouts["BLUE_2"]["agent"],
                    "BLUE_2_weapon": player_loadouts["BLUE_2"]["weapon"],
                    "BLUE_2_armor": player_loadouts["BLUE_2"]["armor"],
                    "BLUE_3_agent": player_loadouts["BLUE_3"]["agent"],
                    "BLUE_3_weapon": player_loadouts["BLUE_3"]["weapon"],
                    "BLUE_3_armor": player_loadouts["BLUE_3"]["armor"],
                    "BLUE_4_agent": player_loadouts["BLUE_4"]["agent"],
                    "BLUE_4_weapon": player_loadouts["BLUE_4"]["weapon"],
                    "BLUE_4_armor": player_loadouts["BLUE_4"]["armor"],
                    "BLUE_5_agent": player_loadouts["BLUE_5"]["agent"],
                    "BLUE_5_weapon": player_loadouts["BLUE_5"]["weapon"],
                    "BLUE_5_armor": player_loadouts["BLUE_5"]["armor"]
                })
        
        return pd.DataFrame(round_variables)
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return pd.DataFrame()



def encode_dataframe(dataframe):
    agent_cols = [col for col in dataframe.columns if 'agent' in col]
    weapon_cols = [col for col in dataframe.columns if 'weapon' in col]
    armor_cols  = [col for col in dataframe.columns if 'armor'  in col]
    team_cols  = [col for col in dataframe.columns if 'team'  in col]
    map_cols  = [col for col in dataframe.columns if 'map'  in col]

    encoders = {}

    agent_encoder = LabelEncoder()
    agent_encoder.fit(dataframe[agent_cols].values.ravel())
    for col in agent_cols:
        dataframe[col] = agent_encoder.transform(dataframe[col])
    encoders['agent'] = agent_encoder

    weapon_encoder = LabelEncoder()
    weapon_encoder.fit(dataframe[weapon_cols].values.ravel())
    for col in weapon_cols:
        dataframe[col] = weapon_encoder.transform(dataframe[col])
    encoders['weapon'] = weapon_encoder

    armor_encoder = LabelEncoder()
    armor_encoder.fit(dataframe[armor_cols].values.ravel())
    for col in armor_cols:
        dataframe[col] = armor_encoder.transform(dataframe[col])
    encoders['armor'] = armor_encoder

    team_encoder = LabelEncoder()
    team_encoder.fit(dataframe[team_cols].values.ravel())
    for col in team_cols:
        dataframe[col] = team_encoder.transform(dataframe[col])
    encoders['team'] = team_encoder

    map_encoder = LabelEncoder()
    map_encoder.fit(dataframe[map_cols].values.ravel())
    for col in map_cols:
        dataframe[col] = map_encoder.transform(dataframe[col])
    encoders['map'] = map_encoder

    return dataframe, encoders



if __name__ == '__main__':
    filename = "data/logs25-1.json"
    dataframe = json_to_dataframe(filename)
    encode_dataframe(dataframe)