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



def format_match(game_json, puuid, gamemode):
    player_entry = next((player for player in game_json["players"] if player.get("puuid") == puuid), None)
    player_team_entry = next((team for team in game_json["teams"] if team.get("teamId") == player_entry["teamId"]), None)
    opponent_team_entry = next((team for team in game_json["teams"] if team.get("teamId") != player_entry["teamId"]), None)

    return {
        "date": time_string_from_milliseconds(game_json["matchInfo"]["gameStartMillis"]),
        "gamemode": gamemode,
        "map": map_names[game_json["matchInfo"]["mapId"]],
        "result": "Win" if player_team_entry["won"] else "Loss" if opponent_team_entry["won"] else "Draw",
        "team_rounds": player_team_entry["roundsWon"],
        "opponent_rounds": opponent_team_entry["roundsWon"],
        "agent": agent_names[player_entry["characterId"]],
        "stats": {
            "rating": (player_entry["stats"]["kills"] / player_entry["stats"]["deaths"]),
            "kills": player_entry["stats"]["kills"],
            "deaths": player_entry["stats"]["deaths"],
            "assists": player_entry["stats"]["assists"],
            "damage": 0,
            "kast": 0,
            "use": 0,
            "headshot": 0,
        },
    }



def time_string_from_milliseconds(milliseconds):
    game_datetime = datetime.fromtimestamp(milliseconds / 1000.0, tz=timezone.utc)
    return game_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")