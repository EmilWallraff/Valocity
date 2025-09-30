import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, timezone

map_names = {
    "/Game/Maps/Infinity/Infinity": "Abyss",
    "/Game/Maps/Ascent/Ascent": "Ascent",
    "/Game/Maps/Duality/Duality": "Bind",
    "/Game/Maps/Foxtrot/Foxtrot": "Breeze",
    "/Game/Maps/Rook/Rook": "Corrode",
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

TRADE_DURATION = 2500



def format_match(game_json):
    red_team_entry = next((team for team in game_json["teams"] if team.get("teamId").lower() == "red"), None)
    blue_team_entry = next((team for team in game_json["teams"] if team.get("teamId").lower() == "blue"), None)
    results = {
        "Red": "Win" if red_team_entry["won"] else "Loss" if blue_team_entry["won"] else "Draw",
        "Blue": "Win" if blue_team_entry["won"] else "Loss" if red_team_entry["won"] else "Draw"
    }
    won_rounds = {
        "Red": red_team_entry["roundsWon"],
        "Blue": blue_team_entry["roundsWon"]
    }
    lost_rounds = {
        "Red": blue_team_entry["roundsWon"],
        "Blue": red_team_entry["roundsWon"]
    }

    stats_dict = {}

    for player in game_json["players"]:
        stats_dict[player["puuid"]] = {
            "result": results[player["teamId"]],
            "roundsWon": won_rounds[player["teamId"]],
            "roundsLost": lost_rounds[player["teamId"]],
            "team": player["teamId"],
            "rank": player["competitiveTier"],
            "agent": agent_names[player["characterId"]],
            "rounds": player["stats"]["roundsPlayed"],
            "kills": player["stats"]["kills"],
            "deaths": player["stats"]["deaths"],
            "assists": player["stats"]["assists"],
            "temp_damage": 0,
            "temp_kastRounds": 0,
            "temp_headshots": 0,
            "temp_bodyshots": 0,
            "temp_legshots": 0,
            "temp_usagePoints": 0,
        }

    for round_stats in (round["playerStats"] for round in game_json["roundResults"]):

        playersKast = {key: False for key in stats_dict.keys()}

        kills = []

        for player_round_stats in round_stats:
            for damage_instance in player_round_stats["damage"]:
                if stats_dict[player_round_stats["puuid"]]["team"] != stats_dict[damage_instance["receiver"]]["team"]:
                    stats_dict[player_round_stats["puuid"]]["temp_damage"] += damage_instance["damage"]
                    stats_dict[player_round_stats["puuid"]]["temp_headshots"] += damage_instance["headshots"]
                    stats_dict[player_round_stats["puuid"]]["temp_bodyshots"] += damage_instance["bodyshots"]
                    stats_dict[player_round_stats["puuid"]]["temp_legshots"] += damage_instance["legshots"]

            for kill_instance in player_round_stats["kills"]:
                kill_entry = {
                    "killer": kill_instance["killer"],
                    "victim": kill_instance["victim"],
                    "time": kill_instance["timeSinceRoundStartMillis"],
                    "assistants": kill_instance["assistants"],
                    "playersAliveBefore": {
                        "Red": 0,
                        "Blue": 0
                    }
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
        player_stats["headshot"] = player_stats["temp_headshots"] / (player_stats["temp_headshots"] + player_stats["temp_bodyshots"] + player_stats["temp_legshots"])
        player_stats["damage"] = player_stats["temp_damage"] / player_stats["rounds"]
        player_stats["rating"] = player_stats["kills"] / player_stats["deaths"]
        player_stats["kast"] = player_stats["temp_kastRounds"] / player_stats["rounds"]
        player_stats["use"] = player_stats["temp_usagePoints"] / team_total_usage_points[player_stats["team"]]

        del player_stats["temp_damage"]
        del player_stats["temp_kastRounds"]
        del player_stats["temp_headshots"]
        del player_stats["temp_bodyshots"]
        del player_stats["temp_legshots"]
        del player_stats["temp_usagePoints"]


    return {
        "matchId": game_json["matchInfo"]["matchId"],
        "date": time_string_from_milliseconds(game_json["matchInfo"]["gameStartMillis"]),
        "gamemode": game_json["matchInfo"]["queueId"].capitalize(),
        "map": map_names[game_json["matchInfo"]["mapId"]],
        "allPlayersStats": stats_dict
    }



def time_string_from_milliseconds(milliseconds):
    game_datetime = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
    return game_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")