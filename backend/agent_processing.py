import pandas as pd
import json
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

def get_agent_stats(json_file: str, filtered_agents, filtered_maps):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        total_games = 0
        agent_stats = {value: {
            "games": 0,
            "nm_wins": 0,
            "nm_losses": 0,
            "rounds": 0,
            "kills": 0,
            "deaths": 0,
            "damage": 0
        } for value in agent_names.values()}

        for match in data.get("matches", []):
            player_match_data = ds.BiKeyDict()
            map = map_names[match.get("matchInfo").get("mapId")]
            if map not in filtered_maps:
                continue

            total_games += 1

            if next((d for d in match.get("teams", []) if d.get("teamId").upper() == "RED"), None)["won"]:
                winner = "RED"
            elif next((d for d in match.get("teams", []) if d.get("teamId").upper() == "BLUE"), None)["won"]:
                winner = "BLUE"
            else:
                winner = "NONE"
            agents_played = {
                "RED": [],
                "BLUE": []
            }

            red_player_count = 1
            blue_player_count = 1
            for player in match.get("players", []):
                player_id = player.get("puuid")
                agent = agent_names[player.get("characterId")]
                team = player.get("teamId")

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

                agents_played[team].append(agent)
                player_match_data.add(player_id, player_match_id, {"puuid": player_id, "player_match_id": player_match_id, "agent": agent, "team": team})

            for player in match.get("players", []):
                agent = player_match_data.get(player.get("puuid"))["agent"]
                if agent not in filtered_agents:
                    continue

                agent_stats[agent]["games"] += 1

                team = player_match_data.get(player.get("puuid"))["team"]
                opponent_team = "BLUE" if team == "RED" else "RED"
                if agent not in agents_played[opponent_team]:
                    if winner == team:
                        agent_stats[agent]["nm_wins"] += 1
                    elif winner == opponent_team:
                        agent_stats[agent]["nm_losses"] += 1

            for round in match.get("roundResults", []):
                for player_stat in round.get("playerStats", []):
                    agent_played = player_match_data.get(player_stat.get("puuid"))["agent"]

                    if agent_played in filtered_agents:
                        agent_stats[agent_played]["rounds"] += 1

                    for kill_entry in player_stat.get("kills", []):
                        if agent_played in filtered_agents:
                            agent_stats[agent_played]["kills"] += 1
                        victim_agent = player_match_data.get(kill_entry.get("victim"))["agent"]
                        if victim_agent in filtered_agents:
                            agent_stats[victim_agent]["deaths"] += 1

                    for damage_entry in player_stat.get("damage", []):
                        if agent_played in filtered_agents:
                            agent_stats[agent_played]["damage"] += damage_entry.get("damage")


        processed_stats = [{
            "id": 0,
            "name": "",
            "stats": {"pick": 0, "win": 0, "kd": 0, "kills": 0, "damage": 0}
        } for value in agent_names.values()]
        
        def safe_divide(dividend, divisor):
            if divisor == 0:
                return 0
            else:
                return dividend / divisor

        for index, agent in enumerate(agent_names.values()):
            processed_stats[index]["id"] += index
            processed_stats[index]["name"] = agent
            processed_stats[index]["stats"]["pick"] = safe_divide(agent_stats[agent]["games"], total_games * 2)
            processed_stats[index]["stats"]["win"] = safe_divide(agent_stats[agent]["nm_wins"], agent_stats[agent]["nm_wins"] + agent_stats[agent]["nm_losses"])
            processed_stats[index]["stats"]["kd"] = safe_divide(agent_stats[agent]["kills"], agent_stats[agent]["deaths"])
            processed_stats[index]["stats"]["kills"] = safe_divide(agent_stats[agent]["kills"], agent_stats[agent]["rounds"])
            processed_stats[index]["stats"]["damage"] = safe_divide(agent_stats[agent]["damage"], agent_stats[agent]["rounds"])

        for index in reversed(range(len(processed_stats))):
            if processed_stats[index]["name"] not in filtered_agents:
                print(f'{processed_stats[index]["name"]} is not in filtered agents -> gonna delete')
                del processed_stats[index]

        return processed_stats
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return pd.DataFrame()