import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, timezone

import valorant_constants as vc



TRADE_DURATION = 3000
DAMAGE_PER_KILL_ESTIMATION = 140.0
ECO_HALFBUY_THRESHOLD = 1200
HALFBUY_FULLBUY_THRESHOLD = 3500

KPR_MODIFIER = 0.898060946867
APR_MODIFIER = 0.227872913948
DPR_MODIFIER = -0.433940698092
ADRA_MODIFIER = 0.00252436539
SR_MODIFIER = 0.433940698092
KAST_MODIFIER = 0.312874869548
GENERAL_MODIFIER = 0.17492523147187433



# This uses a surprisingly accurate but still technically very crude approximation of VLR player rating
def format_match(game_json):
    teams = {t["teamId"].capitalize(): t for t in game_json["teams"]}
    red_team_entry, blue_team_entry = teams["Red"], teams["Blue"]

    results = {
        "Red": "Win" if red_team_entry["won"] else "Loss" if blue_team_entry["won"] else "Draw",
        "Blue": "Win" if blue_team_entry["won"] else "Loss" if red_team_entry["won"] else "Draw",
    }

    won_rounds = {"Red": red_team_entry["roundsWon"], "Blue": blue_team_entry["roundsWon"]}
    lost_rounds = {"Red": blue_team_entry["roundsWon"], "Blue": red_team_entry["roundsWon"]}

    stats_dict = {}

    for player in game_json["players"]:
        team = player["teamId"]
        stats_dict[player["puuid"]] = {
            "result": results[team],
            "roundsWon": won_rounds[team],
            "roundsLost": lost_rounds[team],
            "team": team,
            "name": f"{player['gameName']} #{player['tagLine']}",
            "rank": vc.rank_names[player["competitiveTier"]],
            "agent": vc.agent_names[player["characterId"]],
            "rounds": player["stats"]["roundsPlayed"],
            "kills": player["stats"]["kills"],
            "deaths": player["stats"]["deaths"],
            "assists": player["stats"]["assists"],
            **{k: 0 for k in ("temp_damage","temp_kastRounds","temp_headshots",
                               "temp_bodyshots","temp_legshots","temp_usagePoints")}
        }

    for round_stats in (round["playerStats"] for round in game_json["roundResults"]):
        playersKast = {key: False for key in stats_dict.keys()}
        kills = []

        for player_round_stats in round_stats:
            player_stats_dict_entry = stats_dict[player_round_stats["puuid"]]
            for damage_instance in player_round_stats["damage"]:
                if player_stats_dict_entry["team"] != stats_dict[damage_instance["receiver"]]["team"]:
                    player_stats_dict_entry["temp_damage"] += damage_instance["damage"]
                    player_stats_dict_entry["temp_headshots"] += damage_instance["headshots"]
                    player_stats_dict_entry["temp_bodyshots"] += damage_instance["bodyshots"]
                    player_stats_dict_entry["temp_legshots"] += damage_instance["legshots"]

            for kill_instance in player_round_stats["kills"]:
                kill_entry = {
                    "killer": kill_instance["killer"],
                    "victim": kill_instance["victim"],
                    "time": kill_instance["timeSinceRoundStartMillis"],
                    "assistants": kill_instance["assistants"],
                    "playersAliveBefore": {"Red": 0, "Blue": 0},
                }
                kill_entry["playersAliveBefore"][stats_dict[kill_instance["victim"]]["team"]] += 1
                for survivor in kill_instance["playerLocations"]:
                    kill_entry["playersAliveBefore"][stats_dict[survivor["puuid"]]["team"]] += 1
                kills.append(kill_entry)

        for kill_entry in kills:
            if stats_dict[kill_entry["killer"]]["team"] != stats_dict[kill_entry["victim"]]["team"]:
                playersKast[kill_entry["killer"]] = True

            for assistant in kill_entry["assistants"]:
                playersKast[assistant] = True

            if any((k.get("victim") == kill_entry["killer"] or k.get("victim") in kill_entry["assistants"]) for k in kills if kill_entry["time"] < k.get("time") <= kill_entry["time"] + TRADE_DURATION):
                playersKast[kill_entry["victim"]] = True


            stats_dict[kill_entry["killer"]]["temp_usagePoints"] += min(kill_entry["playersAliveBefore"]["Red"], kill_entry["playersAliveBefore"]["Blue"])
            stats_dict[kill_entry["victim"]]["temp_usagePoints"] += min(kill_entry["playersAliveBefore"]["Red"], kill_entry["playersAliveBefore"]["Blue"])

        for player in playersKast:
            if playersKast[player] or not any(k.get("victim") == player for k in kills):
                stats_dict[player]["temp_kastRounds"] += 1


    team_total_usage_points = {
        "Red": sum([p["temp_usagePoints"] for p in stats_dict.values() if p["team"] == "Red"]),
        "Blue": sum([p["temp_usagePoints"] for p in stats_dict.values() if p["team"] == "Blue"]),
    }

    for player_stats in stats_dict.values():
        kpr = player_stats["kills"] / player_stats["rounds"]
        apr = player_stats["assists"] / player_stats["rounds"]
        dpr = player_stats["deaths"] / player_stats["rounds"]
        adra = (player_stats["temp_damage"] - (player_stats["kills"] * DAMAGE_PER_KILL_ESTIMATION)) / player_stats["rounds"]
        sr = (player_stats["rounds"] - player_stats["deaths"]) / player_stats["rounds"]

        player_stats["headshot"] = player_stats["temp_headshots"] / (player_stats["temp_headshots"] + player_stats["temp_bodyshots"] + player_stats["temp_legshots"])
        player_stats["damage"] = player_stats["temp_damage"] / player_stats["rounds"]
        player_stats["kast"] = player_stats["temp_kastRounds"] / player_stats["rounds"]
        player_stats["use"] = player_stats["temp_usagePoints"] / team_total_usage_points[player_stats["team"]]
        player_stats["rating"] = (kpr * KPR_MODIFIER) + (apr * APR_MODIFIER) + (dpr * DPR_MODIFIER) + (adra * ADRA_MODIFIER) + (sr * SR_MODIFIER) + (player_stats["kast"] * KAST_MODIFIER) + GENERAL_MODIFIER

        for key in ("temp_damage", "temp_kastRounds", "temp_headshots", "temp_bodyshots", "temp_legshots", "temp_usagePoints"):
            player_stats.pop(key, None)

    return {
        "matchId": game_json["matchInfo"]["matchId"],
        "date": time_string_from_milliseconds(game_json["matchInfo"]["gameStartMillis"]),
        "gamemode": game_json["matchInfo"]["queueId"].capitalize(),
        "map": vc.map_names[game_json["matchInfo"]["mapId"]],
        "allPlayersStats": stats_dict
    }



# This uses a surprisingly accurate but still technically very crude approximation of VLR player rating
def calculate_agent_and_weapon_stats(matches):
    agent_stats = []
    weapon_stats = []
        
    for match in matches:
        teams = {t["teamId"].capitalize(): t for t in match["teams"]}
        red_team_entry, blue_team_entry = teams["Red"], teams["Blue"]

        results = {
            "Red": "Win" if red_team_entry["won"] else "Loss" if blue_team_entry["won"] else "Draw",
            "Blue": "Win" if blue_team_entry["won"] else "Loss" if red_team_entry["won"] else "Draw",
        }

        agents_per_team = {
            "Red": [],
            "Blue": [],
        }
        for player in match["players"]:
            agents_per_team[player["teamId"]].append(vc.agent_names[player["characterId"]])

        other_team = {
            "Red": "Blue",
            "Blue": "Red",
        }

        stats_dict = {}
        weapon_rounds = []
        player_rank_values = []

        for player in match["players"]:
            player_rank_values.append(player["competitiveTier"])
            stats_dict[player["puuid"]] = {
                "Agent": vc.agent_names[player["characterId"]],
                "Result": results[player["teamId"]],
                "Mirror": vc.agent_names[player["characterId"]] in agents_per_team[other_team[player["teamId"]]],
                "K/R": player["stats"]["kills"] / player["stats"]["roundsPlayed"],
                "A/R": player["stats"]["assists"] / player["stats"]["roundsPlayed"],
                "rounds": player["stats"]["roundsPlayed"],
                "kills": player["stats"]["kills"],
                "deaths": player["stats"]["deaths"],
                "team": player["teamId"],
                **{k: 0 for k in ("temp_damage","temp_kastRounds","temp_usagePoints")}
            }

        for match_round in match["roundResults"]:
            round_stats = match_round["playerStats"]
            playersKast = {key: False for key in stats_dict.keys()}
            kills = []

            team_players_active = { "Red": 0, "Blue": 0 }
            team_money_spent = { "Red": 0, "Blue": 0 }
            for player_round_stats in round_stats:
                player_team = stats_dict[player_round_stats["puuid"]]["team"]
                team_players_active[player_team] += 1
                team_money_spent[player_team] += player_round_stats["economy"]["loadoutValue"]
            team_loadouts = {
                "Red": team_money_spent["Red"] / team_players_active["Red"],
                "Blue": team_money_spent["Blue"] / team_players_active["Blue"],
            }

            for player_round_stats in round_stats:
                player_round_damage = 0
                player_round_headshots = 0
                player_round_bodyshots = 0
                player_round_legshots = 0

                player_stats_dict_entry = stats_dict[player_round_stats["puuid"]]
                for damage_instance in player_round_stats["damage"]:
                    if player_stats_dict_entry["team"] != stats_dict[damage_instance["receiver"]]["team"]:
                        player_stats_dict_entry["temp_damage"] += damage_instance["damage"]
                        player_round_damage += damage_instance["damage"]
                        player_round_headshots += damage_instance["headshots"]
                        player_round_bodyshots += damage_instance["bodyshots"]
                        player_round_legshots += damage_instance["legshots"]

                for kill_instance in player_round_stats["kills"]:
                    kill_entry = {
                        "killer": kill_instance["killer"],
                        "victim": kill_instance["victim"],
                        "time": kill_instance["timeSinceRoundStartMillis"],
                        "assistants": kill_instance["assistants"],
                        "playersAliveBefore": {"Red": 0, "Blue": 0},
                    }
                    kill_entry["playersAliveBefore"][stats_dict[kill_instance["victim"]]["team"]] += 1
                    for survivor in kill_instance["playerLocations"]:
                        kill_entry["playersAliveBefore"][stats_dict[survivor["puuid"]]["team"]] += 1
                    kills.append(kill_entry)

                # print(f"{player_stats_dict_entry["Agent"]} has {vc.weapon_names[player_round_stats["economy"]["weapon"]]} and {vc.shield_names[player_round_stats["economy"]["armor"]]} -> money spent: {player_round_stats["economy"]["spent"]}, loadout value: {player_round_stats["economy"]["loadoutValue"]}")

                weapon_rounds.append({
                    "Agent": player_stats_dict_entry["Agent"],
                    "Weapon": vc.weapon_names[player_round_stats["economy"]["weapon"]],
                    "Win": match_round["winningTeam"] == player_stats_dict_entry["team"],
                    "PistolRound": match_round["roundNum"] == 0 or match_round["roundNum"] == 12,
                    "OpponentAverageLoadout": team_loadouts[other_team[player_stats_dict_entry["team"]]],
                    "Kills": len(player_round_stats["kills"]),
                    "Damage": player_round_damage,
                    "Headshots": player_round_headshots,
                    "Bodyshots": player_round_bodyshots,
                    "Legshots": player_round_legshots
                })

            for kill_entry in kills:
                if stats_dict[kill_entry["killer"]]["team"] != stats_dict[kill_entry["victim"]]["team"]:
                    playersKast[kill_entry["killer"]] = True

                for assistant in kill_entry["assistants"]:
                    playersKast[assistant] = True

                if any((k.get("victim") == kill_entry["killer"] or k.get("victim") in kill_entry["assistants"]) for k in kills if kill_entry["time"] < k.get("time") <= kill_entry["time"] + TRADE_DURATION):
                    playersKast[kill_entry["victim"]] = True


                stats_dict[kill_entry["killer"]]["temp_usagePoints"] += min(kill_entry["playersAliveBefore"]["Red"], kill_entry["playersAliveBefore"]["Blue"])
                stats_dict[kill_entry["victim"]]["temp_usagePoints"] += min(kill_entry["playersAliveBefore"]["Red"], kill_entry["playersAliveBefore"]["Blue"])

            for player in playersKast:
                if playersKast[player] or not any(k.get("victim") == player for k in kills):
                    stats_dict[player]["temp_kastRounds"] += 1


        team_total_usage_points = {
            "Red": sum([p["temp_usagePoints"] for p in stats_dict.values() if p["team"] == "Red"]),
            "Blue": sum([p["temp_usagePoints"] for p in stats_dict.values() if p["team"] == "Blue"]),
        }

        for player_stats in stats_dict.values():
            dpr = player_stats["deaths"] / player_stats["rounds"]
            adra = (player_stats["temp_damage"] - (player_stats["kills"] * DAMAGE_PER_KILL_ESTIMATION)) / player_stats["rounds"]
            sr = (player_stats["rounds"] - player_stats["deaths"]) / player_stats["rounds"]

            player_stats["KAST%"] = player_stats["temp_kastRounds"] / player_stats["rounds"]
            player_stats["USE%"] = player_stats["temp_usagePoints"] / team_total_usage_points[player_stats["team"]]
            player_stats["Rating"] = (player_stats["K/R"] * KPR_MODIFIER) + (player_stats["A/R"] * APR_MODIFIER) + (dpr * DPR_MODIFIER) + (adra * ADRA_MODIFIER) + (sr * SR_MODIFIER) + (player_stats["KAST%"] * KAST_MODIFIER) + GENERAL_MODIFIER

            for key in ("rounds", "kills", "deaths", "team", "temp_damage", "temp_kastRounds", "temp_usagePoints"):
                player_stats.pop(key, None)

        agent_stats.append({
            "Date": time_string_from_milliseconds(match["matchInfo"]["gameStartMillis"]),
            "Patch": patch_from_game_version(match["matchInfo"]["gameVersion"]) if match["matchInfo"]["gameVersion"] != None else "",
            "Map": vc.map_names[match["matchInfo"]["mapId"]],
            "Rank": vc.rank_names[round(sum(player_rank_values) / len(player_rank_values))],
            "Draw": results["Red"] == "Draw",
            "Players": list(stats_dict.values())
        })

        weapon_stats.append({
            "Date": time_string_from_milliseconds(match["matchInfo"]["gameStartMillis"]),
            "Patch": patch_from_game_version(match["matchInfo"]["gameVersion"]) if match["matchInfo"]["gameVersion"] != None else "",
            "Map": vc.map_names[match["matchInfo"]["mapId"]],
            "Rank": vc.rank_names[round(sum(player_rank_values) / len(player_rank_values))],
            "Player_Rounds": weapon_rounds
        })

    return agent_stats, weapon_stats



def format_agent_stats_for_display(agent_stats, filtered_agents, filtered_maps, filtered_ranks):
    number_matches_considered = 0
    processed_stats = {
        agent: {
            "id": i,
            "name": agent,
            "stats": {"Rating": 0, "K/R": 0, "A/R": 0, "KAST%": 0, "USE%": 0, "matches": 0, "unmirrored_wins": 0, "unmirrored_losses": 0}
        }
        for i, agent in enumerate(filtered_agents)
    }

    for match in agent_stats:
        if match["Map"] not in filtered_maps:
            continue

        if not any(rank.lower() in match["Rank"].lower() for rank in filtered_ranks):
            continue

        number_matches_considered += 1
        for player in match["Players"]:
            if player["Agent"] not in filtered_agents:
                continue
            agent_stat_totals = processed_stats[player["Agent"]]["stats"]
            agent_stat_totals["Rating"] += player["Rating"]
            agent_stat_totals["K/R"] += player["K/R"]
            agent_stat_totals["A/R"] += player["A/R"]
            agent_stat_totals["KAST%"] += player["KAST%"]
            agent_stat_totals["USE%"] += player["USE%"]
            agent_stat_totals["matches"] += 1
            agent_stat_totals["unmirrored_wins"] += 1 if (not player["Mirror"] and player["Result"] == "Win") else 0
            agent_stat_totals["unmirrored_losses"] += 1 if (not player["Mirror"] and player["Result"] == "Loss") else 0

    for entry in processed_stats.values():
        if entry["stats"]["matches"] > 0:
            entry["stats"]["Rating"] /= entry["stats"]["matches"]
            entry["stats"]["K/R"] /= entry["stats"]["matches"]
            entry["stats"]["A/R"] /= entry["stats"]["matches"]
            entry["stats"]["KAST%"] /= entry["stats"]["matches"]
            entry["stats"]["USE%"] /= entry["stats"]["matches"]

        number_decisive_matches = entry["stats"]["unmirrored_wins"] + entry["stats"]["unmirrored_losses"]
        entry["stats"]["Win%"] = (entry["stats"]["unmirrored_wins"] / number_decisive_matches) if (number_decisive_matches > 0) else 0
        entry["stats"]["Pick%"] = (entry["stats"]["matches"] / (number_matches_considered * 2)) if (number_matches_considered > 0) else 0

        for key in ("matches", "unmirrored_wins", "unmirrored_losses"):
            entry["stats"].pop(key, None)

    return list(processed_stats.values())



def format_weapon_stats_for_display(weapon_stats, filtered_weapons, filtered_agents, filtered_maps, filtered_ranks):
    processed_stats = {
        weapon: {
            "id": i,
            "name": weapon,
            "stats": {"Dmg/R": 0, "K/R": 0, "Win%": 0, "headshots": 0, "bodyshots": 0, "legshots": 0, "rounds": 0},
            "subentries": {
                "Pistol Round": {"Dmg/R": 0, "K/R": 0, "Win%": 0, "headshots": 0, "bodyshots": 0, "legshots": 0, "rounds": 0},
                f"vs Eco (<{ECO_HALFBUY_THRESHOLD}$)": {"Dmg/R": 0, "K/R": 0, "Win%": 0, "headshots": 0, "bodyshots": 0, "legshots": 0, "rounds": 0},
                f"vs Halfbuy ({ECO_HALFBUY_THRESHOLD}$-{HALFBUY_FULLBUY_THRESHOLD}$)": {"Dmg/R": 0, "K/R": 0, "Win%": 0, "headshots": 0, "bodyshots": 0, "legshots": 0, "rounds": 0},
                f"vs Fullbuy (>{HALFBUY_FULLBUY_THRESHOLD}$)": {"Dmg/R": 0, "K/R": 0, "Win%": 0, "headshots": 0, "bodyshots": 0, "legshots": 0, "rounds": 0}
            }
        }
        for i, weapon in enumerate(filtered_weapons)
    }

    for match in weapon_stats:
        if match["Map"] not in filtered_maps:
            continue

        if not any(rank.lower() in match["Rank"].lower() for rank in filtered_ranks):
            continue

        for player_round in match["Player_Rounds"]:
            if player_round["Agent"] not in filtered_agents:
                continue
            if player_round["Weapon"] not in filtered_weapons:
                continue
            weapon_stat_totals = processed_stats[player_round["Weapon"]]["stats"]
            weapon_stat_totals["Dmg/R"] += player_round["Damage"]
            weapon_stat_totals["K/R"] += player_round["Kills"]
            weapon_stat_totals["Win%"] += 1 if (player_round["Win"]) else 0
            weapon_stat_totals["headshots"] += player_round["Headshots"]
            weapon_stat_totals["bodyshots"] += player_round["Bodyshots"]
            weapon_stat_totals["legshots"] += player_round["Legshots"]
            weapon_stat_totals["rounds"] += 1
            round_type = get_round_type(player_round["PistolRound"], player_round["OpponentAverageLoadout"])
            weapon_stat_subentry_totals = processed_stats[player_round["Weapon"]]["subentries"][round_type]
            weapon_stat_subentry_totals["Dmg/R"] += player_round["Damage"]
            weapon_stat_subentry_totals["K/R"] += player_round["Kills"]
            weapon_stat_subentry_totals["Win%"] += 1 if (player_round["Win"]) else 0
            weapon_stat_subentry_totals["headshots"] += player_round["Headshots"]
            weapon_stat_subentry_totals["bodyshots"] += player_round["Bodyshots"]
            weapon_stat_subentry_totals["legshots"] += player_round["Legshots"]
            weapon_stat_subentry_totals["rounds"] += 1

    for entry in processed_stats.values():
        if entry["subentries"]["Pistol Round"]["rounds"] <= 0:
            entry["subentries"].pop("Pistol Round", None)

        if entry["stats"]["rounds"] > 0:
            entry["stats"]["Dmg/R"] /= entry["stats"]["rounds"]
            entry["stats"]["K/R"] /= entry["stats"]["rounds"]
            entry["stats"]["Win%"] /= entry["stats"]["rounds"]
        number_total_shots = entry["stats"]["headshots"] + entry["stats"]["bodyshots"] + entry["stats"]["legshots"]
        entry["stats"]["HS%"] = (entry["stats"]["headshots"] / number_total_shots) if (number_total_shots > 0) else 0

        for subentry in entry["subentries"].values():
            if subentry["rounds"] > 0:
                subentry["Dmg/R"] /= subentry["rounds"]
                subentry["K/R"] /= subentry["rounds"]
                subentry["Win%"] /= subentry["rounds"]
            number_total_shots = subentry["headshots"] + subentry["bodyshots"] + subentry["legshots"]
            subentry["HS%"] = (subentry["headshots"] / number_total_shots) if (number_total_shots > 0) else 0

        for key in ("rounds", "headshots", "bodyshots", "legshots"):
            entry["stats"].pop(key, None)
            for subentry in entry["subentries"].values():
                subentry.pop(key, None)

    return list(processed_stats.values())



def time_string_from_milliseconds(milliseconds):
    game_datetime = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
    return game_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")

def patch_from_game_version(game_version):
    parts = game_version.split("-")
    if len(parts) >= 2:
        return parts[1]
    return ""

def get_round_type(pistol_round, average_opponent_loadout):
    if pistol_round:
        return "Pistol Round"
    elif average_opponent_loadout < ECO_HALFBUY_THRESHOLD:
        return f"vs Eco (<{ECO_HALFBUY_THRESHOLD}$)"
    elif average_opponent_loadout < HALFBUY_FULLBUY_THRESHOLD:
        return f"vs Halfbuy ({ECO_HALFBUY_THRESHOLD}$-{HALFBUY_FULLBUY_THRESHOLD}$)"
    else:
        return f"vs Fullbuy (>{HALFBUY_FULLBUY_THRESHOLD}$)"


