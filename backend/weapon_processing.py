import pandas as pd
import json
import helpers.data_structures as ds

import valorant_constants as vc



def get_weapon_stats(json_file: str, filtered_weapons, filtered_maps, filtered_agents):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        weapon_stats = {value: [] for value in vc.weapon_names.values()}

        for match in data.get("matches", []):
            player_match_data = ds.BiKeyDict()
            map = vc.map_names[match.get("matchInfo").get("mapId")]
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

                player_match_data.add(player_id, player_match_id, {"puuid": player_id, "player_match_id": player_match_id, "agent": vc.agent_names[player.get("characterId")], "team": player.get("teamId")})


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
                    if vc.weapon_names[player_stat.get("economy").get("weapon")] not in filtered_weapons:
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

                    weapon_stats[vc.weapon_names[player_stat.get("economy").get("weapon")]].append({
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
        } for value in vc.weapon_names.values()}

        for weapon in vc.weapon_names.values():
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
        } for value in vc.weapon_names.values()]

        def get_totals(stat):
            return total_stats[weapon]["pistol"][stat] + total_stats[weapon]["eco"][stat] + total_stats[weapon]["halfbuy"][stat] + total_stats[weapon]["fullbuy"][stat]
        
        def safe_divide(dividend, divisor):
            if divisor == 0:
                return 0
            else:
                return dividend / divisor

        for index, weapon in enumerate(vc.weapon_names.values()):
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