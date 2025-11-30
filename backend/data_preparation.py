import pandas as pd
import json
from sklearn.preprocessing import LabelEncoder
import helpers.data_structures as ds

import valorant_constants as vc



def get_attacker(round_number):
    if round_number <= 11:
        return "red"
    elif round_number <= 23:
        return "blue"
    elif round_number % 2 == 0:
        return "red"
    else:
        return "blue"
    
def get_defender(round_number):
    if round_number <= 11:
        return "blue"
    elif round_number <= 23:
        return "red"
    elif round_number % 2 == 0:
        return "blue"
    else:
        return "red"
    
def get_team_side(team, round_number):
    if round_number <= 11:
        if team == "red":
            return "attacker"
        if team == "blue":
            return "defender"
    elif round_number <= 23:
        if team == "red":
            return "defender"
        if team == "blue":
            return "attacker"
    elif round_number % 2 == 0:
        if team == "red":
            return "attacker"
        if team == "blue":
            return "defender"
    else:
        if team == "red":
            return "defender"
        if team == "blue":
            return "attacker"



def json_to_dataframe(json_file: str) -> pd.DataFrame:
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        round_variables = []

        for match in data:
            if match["teams"] == None:
                continue
            if not match["matchInfo"]["isCompleted"]:
                continue

            player_match_data = ds.BiKeyDict()
            map = vc.map_names[match.get("matchInfo").get("mapId")]

            red_player_count = 1
            blue_player_count = 1
            for player in match.get("players", []):
                if player["isObserver"]:
                    continue

                player_id = player.get("puuid")

                player_match_id = ""
                team_id = player.get("teamId").lower()
                if (team_id == "red"):
                    player_match_id = f"{team_id}_{red_player_count}"
                    red_player_count = red_player_count + 1
                elif (team_id == "blue"):
                    player_match_id = f"{team_id}_{blue_player_count}"
                    blue_player_count = blue_player_count + 1
                else:
                    print(F"Player {player_id} (in match {match.get("matchInfo").get("matchId")}) has team id other than blue or red!")

                player_match_data.add(player_id, player_match_id, {"puuid": player_id, "player_match_id": player_match_id, "agent": vc.agent_names[player.get("characterId")]})

            for round in match.get("roundResults", []):
                if round.get("roundResult").lower() == "surrendered":
                    continue

                player_loadouts = {}
                for player_stat in round.get("playerStats", []):
                    puuid = player_stat.get("puuid")
                    player_match_id = player_match_data.get(puuid)["player_match_id"]
                    player_loadouts[player_match_id] = {"agent": player_match_data.get(puuid)["agent"], "weapon": vc.weapon_names[player_stat.get("economy").get("weapon")], "armor": vc.shield_names[player_stat.get("economy").get("armor")]}

                round_num = round.get("roundNum")
                attacker_team = get_attacker(round_num)
                defender_team = get_defender(round_num)
                if attacker_team == defender_team:
                    print(F"Something went wrong big time with the teams!")

                if get_team_side(round.get("winningTeam").lower(), round_num) != round.get("winningTeamRole").lower():
                    print(F"I fucked up with the teams!")

                round_variables.append({
                    "winner": round.get("winningTeamRole").lower(),
                    "map": map,
                    "attack_1_agent": player_loadouts[f"{attacker_team}_1"]["agent"],
                    "attack_1_weapon": player_loadouts[f"{attacker_team}_1"]["weapon"],
                    "attack_1_armor": player_loadouts[f"{attacker_team}_1"]["armor"],
                    "attack_2_agent": player_loadouts[f"{attacker_team}_2"]["agent"],
                    "attack_2_weapon": player_loadouts[f"{attacker_team}_2"]["weapon"],
                    "attack_2_armor": player_loadouts[f"{attacker_team}_2"]["armor"],
                    "attack_3_agent": player_loadouts[f"{attacker_team}_3"]["agent"],
                    "attack_3_weapon": player_loadouts[f"{attacker_team}_3"]["weapon"],
                    "attack_3_armor": player_loadouts[f"{attacker_team}_3"]["armor"],
                    "attack_4_agent": player_loadouts[f"{attacker_team}_4"]["agent"],
                    "attack_4_weapon": player_loadouts[f"{attacker_team}_4"]["weapon"],
                    "attack_4_armor": player_loadouts[f"{attacker_team}_4"]["armor"],
                    "attack_5_agent": player_loadouts[f"{attacker_team}_5"]["agent"],
                    "attack_5_weapon": player_loadouts[f"{attacker_team}_5"]["weapon"],
                    "attack_5_armor": player_loadouts[f"{attacker_team}_5"]["armor"],
                    "defense_1_agent": player_loadouts[f"{defender_team}_1"]["agent"],
                    "defense_1_weapon": player_loadouts[f"{defender_team}_1"]["weapon"],
                    "defense_1_armor": player_loadouts[f"{defender_team}_1"]["armor"],
                    "defense_2_agent": player_loadouts[f"{defender_team}_2"]["agent"],
                    "defense_2_weapon": player_loadouts[f"{defender_team}_2"]["weapon"],
                    "defense_2_armor": player_loadouts[f"{defender_team}_2"]["armor"],
                    "defense_3_agent": player_loadouts[f"{defender_team}_3"]["agent"],
                    "defense_3_weapon": player_loadouts[f"{defender_team}_3"]["weapon"],
                    "defense_3_armor": player_loadouts[f"{defender_team}_3"]["armor"],
                    "defense_4_agent": player_loadouts[f"{defender_team}_4"]["agent"],
                    "defense_4_weapon": player_loadouts[f"{defender_team}_4"]["weapon"],
                    "defense_4_armor": player_loadouts[f"{defender_team}_4"]["armor"],
                    "defense_5_agent": player_loadouts[f"{defender_team}_5"]["agent"],
                    "defense_5_weapon": player_loadouts[f"{defender_team}_5"]["weapon"],
                    "defense_5_armor": player_loadouts[f"{defender_team}_5"]["armor"]
                })
        
        return pd.DataFrame(round_variables)
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return pd.DataFrame()



def encode_dataframe(dataframe):
    agent_cols = [col for col in dataframe.columns if 'agent' in col]
    weapon_cols = [col for col in dataframe.columns if 'weapon' in col]
    armor_cols = [col for col in dataframe.columns if 'armor' in col]
    map_cols = [col for col in dataframe.columns if 'map' in col]
    team_cols = [col for col in dataframe.columns if 'winner' in col]

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

    map_encoder = LabelEncoder()
    map_encoder.fit(dataframe[map_cols].values.ravel())
    for col in map_cols:
        dataframe[col] = map_encoder.transform(dataframe[col])
    encoders['map'] = map_encoder

    team_encoder = LabelEncoder()
    team_encoder.fit(dataframe[team_cols].values.ravel())
    for col in team_cols:
        dataframe[col] = team_encoder.transform(dataframe[col])
    encoders['team'] = team_encoder

    return dataframe, encoders



if __name__ == '__main__':
    filename = "data/logs25-1.json"
    dataframe = json_to_dataframe(filename)
    encode_dataframe(dataframe)