import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, timezone

import valorant_constants as vc



TRADE_DURATION = 3000
DAMAGE_PER_KILL_ESTIMATION = 140.0
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





def time_string_from_milliseconds(milliseconds):
    game_datetime = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
    return game_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")