import pandas as pd
import json
import helpers.data_structures as ds

weapon_names = {
    "": "NoWeapon?",
    "29A0CFAB-485B-F5D5-779A-B59F85E204A8": "Classic",
    "42DA8CCC-40D5-AFFC-BEEC-15AA47B42EDA": "Shorty",
    "44D4E95C-4157-0037-81B2-17841BF2E8E3": "Frenzy",
    "1BAA85B4-4C70-1284-64BB-6481DFC3BB4E": "Ghost",
    "E336C6B8-418D-9340-D77F-7A9E4CFE0702": "Sheriff",
    "F7E1B454-4AD4-1063-EC0A-159E56B58941": "Stinger",
    "462080D1-4035-2937-7C09-27AA2A5C27A7": "Spectre",
    "910BE174-449B-C412-AB22-D0873436B21B": "Bucky",
    "EC845BF4-4F79-DDDA-A3DA-0DB3774B2794": "Judge",
    "AE3DE142-4D85-2547-DD26-4E90BED35CF7": "Bulldog",
    "4ADE7FAA-4CF1-8376-95EF-39884480959B": "Guardian",
    "EE8E8D15-496B-07AC-E5F6-8FAE5D4C7B1A": "Phantom",
    "9C82E19D-4575-0200-1A81-3EACF00CF872": "Vandal",
    "C4883E50-4494-202C-3EC3-6B8A9284F00B": "Marshall",
    "5F0AAF7A-4289-3998-D5FF-EB9A5CF7EF5C": "Outlaw",
    "A03B24D3-4319-996D-0F8C-94BBFBA1DFC7": "Operator",
    "55D8A0F4-4274-CA67-FE2C-06AB45EFDF58": "Ares",
    "63E6C2B6-4A8E-869C-3D4C-E38355226584": "Odin",
    "2F59173C-4BED-B6C3-2191-DEA9B58BE9C7": "Knife"
}

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

def get_weapon_stats(json_file: str, filtered_weapons, filtered_maps, filtered_agents):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        weapon_stats = {value: [] for value in weapon_names.values()}

        for match in data.get("matches", []):
            player_match_data = ds.BiKeyDict()
            map = map_names[match.get("matchInfo").get("mapId")]
            if map not in filtered_maps:
                continue


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

                player_match_data.add(player_id, player_match_id, {"puuid": player_id, "player_match_id": player_match_id, "agent": agent_names[player.get("characterId")], "team": player.get("teamId")})


            for round in match.get("roundResults", []):

                red_total_loadout = 0
                blue_total_loadout = 0
                for player_stat in round.get("playerStats", []):
                    if player_match_data.get(player_stat.get("puuid"))["team"] == "RED":
                        red_total_loadout += player_stat.get("economy").get("loadoutValue")
                    elif player_match_data.get(player_stat.get("puuid"))["team"] == "BLUE":
                        blue_total_loadout += player_stat.get("economy").get("loadoutValue")
                    else:
                        print(F"Player {player_id} has team id other than BLUE or RED!")
                red_loadout = red_total_loadout / 5
                blue_loadout = blue_total_loadout / 5

                for player_stat in round.get("playerStats", []):
                    if player_match_data.get(player_stat.get("puuid"))["agent"] not in filtered_agents:
                        continue
                    if weapon_names[player_stat.get("economy").get("weapon")] not in filtered_weapons:
                        continue

                    kills = 0
                    damage = 0
                    headshots = 0
                    bodyshots = 0
                    legshots = 0

                    for kill_entry in player_stat.get("kills", []):
                        kills += 1

                    for damage_entry in player_stat.get("damage", []):
                        damage += damage_entry.get("damage")
                        headshots += damage_entry.get("headshots")
                        bodyshots += damage_entry.get("bodyshots")
                        legshots += damage_entry.get("legshots")

                    weapon_stats[weapon_names[player_stat.get("economy").get("weapon")]].append({
                        "kills": kills,
                        "damage": damage,
                        "win": player_match_data.get(player_stat.get("puuid"))["team"] == round.get("winningTeam"),
                        "headshots": headshots,
                        "bodyshots": bodyshots,
                        "legshots": legshots,
                        "pistol_round": round.get("roundNum") == 0 or round.get("roundNum") == 12,
                        "opponent_loadout": blue_loadout if player_match_data.get(player_stat.get("puuid"))["team"] == "RED" else red_loadout
                    })


        total_stats = {value: {
            "pistol": {"rounds": 0, "kills": 0, "damage": 0, "wins": 0, "losses": 0 , "headshots": 0, "bodyshots": 0, "legshots": 0},
            "eco": {"rounds": 0, "kills": 0, "damage": 0, "wins": 0, "losses": 0 , "headshots": 0, "bodyshots": 0, "legshots": 0},
            "halfbuy": {"rounds": 0, "kills": 0, "damage": 0, "wins": 0, "losses": 0 , "headshots": 0, "bodyshots": 0, "legshots": 0},
            "fullbuy": {"rounds": 0, "kills": 0, "damage": 0, "wins": 0, "losses": 0 , "headshots": 0, "bodyshots": 0, "legshots": 0}
        } for value in weapon_names.values()}

        for weapon in weapon_names.values():
            for weapon_entry in weapon_stats[weapon]:
                if weapon_entry["pistol_round"]:
                    round_type = "pistol"
                elif weapon_entry["opponent_loadout"] < 1000:
                    round_type = "eco"
                elif weapon_entry["opponent_loadout"] < 3500:
                    round_type = "halfbuy"
                else:
                    round_type = "fullbuy"

                total_stats[weapon][round_type]["rounds"] += 1
                total_stats[weapon][round_type]["kills"] += weapon_entry["kills"]
                total_stats[weapon][round_type]["damage"] += weapon_entry["damage"]
                total_stats[weapon][round_type]["headshots"] += weapon_entry["headshots"]
                total_stats[weapon][round_type]["bodyshots"] += weapon_entry["bodyshots"]
                total_stats[weapon][round_type]["legshots"] += weapon_entry["legshots"]
                if weapon_entry["win"]:
                    total_stats[weapon][round_type]["wins"] += 1
                else:
                    total_stats[weapon][round_type]["losses"] += 1


        processed_stats = [{
            "id": 0,
            "name": "",
            "stats": {"kills": 0, "damage": 0, "win": 0, "headshot": 0},
            "subentries": [
                {"name": "Pistol Round", "kills": 0, "damage": 0, "win": 0, "headshot": 0},
                {"name": "vs Eco (<1000$)", "kills": 0, "damage": 0, "win": 0, "headshot": 0},
                {"name": "vs Halfbuy (1000$-3500$)", "kills": 0, "damage": 0, "win": 0, "headshot": 0},
                {"name": "vs Fullbuy (>3500$)", "kills": 0, "damage": 0, "win": 0, "headshot": 0}
            ]
        } for value in weapon_names.values()]

        def get_totals(stat):
            return total_stats[weapon]["pistol"][stat] + total_stats[weapon]["eco"][stat] + total_stats[weapon]["halfbuy"][stat] + total_stats[weapon]["fullbuy"][stat]
        
        def safe_divide(dividend, divisor):
            if divisor == 0:
                return 0
            else:
                return dividend / divisor

        for index, weapon in enumerate(weapon_names.values()):
            processed_stats[index]["id"] += index
            processed_stats[index]["name"] = weapon
            processed_stats[index]["stats"]["kills"] = safe_divide(get_totals("kills"), get_totals("rounds"))
            processed_stats[index]["stats"]["damage"] = safe_divide(get_totals("damage"), get_totals("rounds"))
            processed_stats[index]["stats"]["win"] = safe_divide(get_totals("wins"), get_totals("wins") + get_totals("losses"))
            processed_stats[index]["stats"]["headshot"] = safe_divide(get_totals("headshots"), get_totals("headshots") + get_totals("bodyshots") + get_totals("legshots"))
            processed_stats[index]["subentries"][0]["kills"] = safe_divide(total_stats[weapon]["pistol"]["kills"], total_stats[weapon]["pistol"]["rounds"])
            processed_stats[index]["subentries"][0]["damage"] = safe_divide(total_stats[weapon]["pistol"]["damage"], total_stats[weapon]["pistol"]["rounds"])
            processed_stats[index]["subentries"][0]["win"] = safe_divide(total_stats[weapon]["pistol"]["wins"], total_stats[weapon]["pistol"]["wins"] + total_stats[weapon]["pistol"]["losses"])
            processed_stats[index]["subentries"][0]["headshot"] =safe_divide(total_stats[weapon]["pistol"]["headshots"], total_stats[weapon]["pistol"]["headshots"] + total_stats[weapon]["pistol"]["bodyshots"] + total_stats[weapon]["pistol"]["legshots"])
            processed_stats[index]["subentries"][1]["kills"] = safe_divide(total_stats[weapon]["eco"]["kills"], total_stats[weapon]["eco"]["rounds"])
            processed_stats[index]["subentries"][1]["damage"] = safe_divide(total_stats[weapon]["eco"]["damage"], total_stats[weapon]["eco"]["rounds"])
            processed_stats[index]["subentries"][1]["win"] = safe_divide(total_stats[weapon]["eco"]["wins"], total_stats[weapon]["eco"]["wins"] + total_stats[weapon]["eco"]["losses"])
            processed_stats[index]["subentries"][1]["headshot"] =safe_divide(total_stats[weapon]["eco"]["headshots"], total_stats[weapon]["eco"]["headshots"] + total_stats[weapon]["eco"]["bodyshots"] + total_stats[weapon]["eco"]["legshots"])
            processed_stats[index]["subentries"][2]["kills"] = safe_divide(total_stats[weapon]["halfbuy"]["kills"], total_stats[weapon]["halfbuy"]["rounds"])
            processed_stats[index]["subentries"][2]["damage"] = safe_divide(total_stats[weapon]["halfbuy"]["damage"], total_stats[weapon]["halfbuy"]["rounds"])
            processed_stats[index]["subentries"][2]["win"] = safe_divide(total_stats[weapon]["halfbuy"]["wins"], total_stats[weapon]["halfbuy"]["wins"] + total_stats[weapon]["halfbuy"]["losses"])
            processed_stats[index]["subentries"][2]["headshot"] =safe_divide(total_stats[weapon]["halfbuy"]["headshots"], total_stats[weapon]["halfbuy"]["headshots"] + total_stats[weapon]["halfbuy"]["bodyshots"] + total_stats[weapon]["halfbuy"]["legshots"])
            processed_stats[index]["subentries"][3]["kills"] = safe_divide(total_stats[weapon]["fullbuy"]["kills"], total_stats[weapon]["fullbuy"]["rounds"])
            processed_stats[index]["subentries"][3]["damage"] = safe_divide(total_stats[weapon]["fullbuy"]["damage"], total_stats[weapon]["fullbuy"]["rounds"])
            processed_stats[index]["subentries"][3]["win"] = safe_divide(total_stats[weapon]["fullbuy"]["wins"], total_stats[weapon]["fullbuy"]["wins"] + total_stats[weapon]["fullbuy"]["losses"])
            processed_stats[index]["subentries"][3]["headshot"] =safe_divide(total_stats[weapon]["fullbuy"]["headshots"], total_stats[weapon]["fullbuy"]["headshots"] + total_stats[weapon]["fullbuy"]["bodyshots"] + total_stats[weapon]["fullbuy"]["legshots"])

            if total_stats[weapon]["pistol"]["rounds"] <= 0:
                del processed_stats[index]["subentries"][0]

        for index in reversed(range(len(processed_stats))):
            if processed_stats[index]["name"] not in filtered_weapons:
                print(f'{processed_stats[index]["name"]} is not in filtered weapons -> gonna delete')
                del processed_stats[index]


        #del processed_stats[0]
        return processed_stats
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return pd.DataFrame()