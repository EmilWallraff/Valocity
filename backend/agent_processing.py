import pandas as pd
import json
import helpers.data_structures as ds

import valorant_constants as vc



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
        } for value in vc.agent_names.values()}

        for match in data.get("matches", []):
            if match.get("teams") is None:
                continue

            player_match_data = ds.BiKeyDict()
            map = vc.map_names[match.get("matchInfo").get("mapId")]
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
                agent = vc.agent_names[player.get("characterId")]
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
        } for value in vc.agent_names.values()]
        
        def safe_divide(dividend, divisor):
            if divisor == 0:
                return 0
            else:
                return dividend / divisor

        for index, agent in enumerate(vc.agent_names.values()):
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