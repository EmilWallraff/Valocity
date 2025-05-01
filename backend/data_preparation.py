import pandas as pd
import json
from sklearn.preprocessing import LabelEncoder
import helpers.data_structures as ds

map_names = {
    "/Game/Maps/Infinity/Infinity": "Abyss",
    "/Game/Maps/Ascent/Ascent": "Ascent",
    "/Game/Maps/Duality/Duality": "Bind",
    "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
    "/Game/Maps/Canyon/Canyon": "Fracture",
    "/Game/Maps/Triad/Triad": "Haven",
    "/Game/Maps/Port/Port": "Icebox",
    "/Game/Maps/Jam/Jam": "Lotus",
    "/Game/Maps/Pitt/Pitt": "Pearl",
    "/Game/Maps/Bonsai/Bonsai": "Split",
    "/Game/Maps/Juliett/Juliett": "Sunset"
}

agent_names = {
    "5f8d3a7f-467b-97f3-062c-13acf203c006": "Breach",
 	"9f0d8ba9-4140-b941-57d3-a7ad57c6b417": "Brimstone",
 	"add6443a-41bd-e414-f6ad-e58d267f4e95": "Jett",
	"22697a3d-45bf-8dd7-4fec-84a9e28c69d7": "Chamber",
    "1e58de9c-4950-5125-93e9-a0aee9f98746": "Killjoy",
    "f94c3b30-42be-e959-889c-5aa313dba261": "Raze",
    "a3bfb853-43b2-7238-a4f1-ad90e9e46bcc": "Reyna",
    "320b2a48-4d9b-a075-30f1-1f93a9b638fa": "Sova",
    "eb93336a-449b-9c1b-0a54-a891f7921d69": "Phoenix",
    "8e253930-4c05-31dd-1b6c-968525494517": "Omen",
    "569fdd95-4d10-43ab-ca70-79becc718b46": "Sage",
    "41fb69c1-4189-7b37-f117-bcaf1e96f1bf": "Astra",
    "601dbbe7-43ce-be57-2a40-4abd24953621": "KAY/O",
    "707eab51-4836-f488-046a-cda6bf494859": "Viper",
    "117ed9e3-49f3-6512-3ccf-0cada7e3823b": "Cypher",
    "7f94d92c-4234-0a36-9646-3a87eb8b5c89": "Yoru",
    "6f2a04ca-43e0-be17-7f36-b3908627744d": "Skye",
    "0e38b510-41a8-5780-5e8f-568b2a4f2d6c": "Iso",
    "b444168c-4e35-8076-db47-ef9bf368f384": "Tejo",
    "efba5359-4016-a1e5-7626-b1ae76895940": "Vyse",
    "bb2a4828-46eb-8cd1-e765-15848195d751": "Neon",
    "1dbf2edd-4729-0984-3115-daa5eed44993": "Clove",
    "e370fa57-4757-3604-3648-499e1f642d3f": "Gekko",
    "cc8b64c8-4b25-4ff9-6e7f-37b4da43d235": "Deadlock",
    "df1cb487-4902-002e-5c17-d28e83e78588": "Waylay",
    "dade69b4-4f5a-8528-247b-219e5a1facd6": "Fade",
    "95b78ed7-4637-86d9-7e41-71ba8c293152": "Harbor"
}

weapon_names = {
    "": "NoWeapon?",
    "2F59173C-4BED-B6C3-2191-DEA9B58BE9C7": "Knife",
    "29A0CFAB-485B-F5D5-779A-B59F85E204A8": "Classic",
    "C4883E50-4494-202C-3EC3-6B8A9284F00B": "Marshall",
    "A03B24D3-4319-996D-0F8C-94BBFBA1DFC7": "Operator",
    "9C82E19D-4575-0200-1A81-3EACF00CF872": "Vandal",
    "462080D1-4035-2937-7C09-27AA2A5C27A7": "Spectre",
    "1BAA85B4-4C70-1284-64BB-6481DFC3BB4E": "Ghost",
    "55D8A0F4-4274-CA67-FE2C-06AB45EFDF58": "Ares",
    "EE8E8D15-496B-07AC-E5F6-8FAE5D4C7B1A": "Phantom",
    "E336C6B8-418D-9340-D77F-7A9E4CFE0702": "Sheriff",
    "44D4E95C-4157-0037-81B2-17841BF2E8E3": "Frenzy",
    "4ADE7FAA-4CF1-8376-95EF-39884480959B": "Guardian",
    "42DA8CCC-40D5-AFFC-BEEC-15AA47B42EDA": "Shorty",
    "EC845BF4-4F79-DDDA-A3DA-0DB3774B2794": "Judge",
    "63E6C2B6-4A8E-869C-3D4C-E38355226584": "Odin",
    "910BE174-449B-C412-AB22-D0873436B21B": "Bucky",
    "F7E1B454-4AD4-1063-EC0A-159E56B58941": "Stinger",
    "AE3DE142-4D85-2547-DD26-4E90BED35CF7": "Bulldog",
    "5F0AAF7A-4289-3998-D5FF-EB9A5CF7EF5C": "Outlaw"
}

shield_names = {
    "": "None",
    "NONE": "None",
    "LIGHT_SHIELD": "Light",
    "REGEN_SHIELD": "Regen",
    "HEAVY_SHIELD": "Heavy"
}



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
            map = map_names[match.get("matchInfo").get("mapId")]

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

                player_match_data.add(player_id, player_match_id, {"puuid": player_id, "player_match_id": player_match_id, "agent": agent_names[player.get("characterId")]})

            for round in match.get("roundResults", []):
                player_loadouts = {}
                for player_stat in round.get("playerStats", []):
                    puuid = player_stat.get("puuid")
                    player_match_id = player_match_data.get(puuid)["player_match_id"]
                    player_loadouts[player_match_id] = {"agent": player_match_data.get(puuid)["agent"], "weapon": weapon_names[player_stat.get("economy").get("weapon")], "armor": shield_names[player_stat.get("economy").get("armor")]}

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