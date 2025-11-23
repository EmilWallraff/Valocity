import pandas as pd
import numpy as np
import duckdb
import time
from datetime import datetime, timedelta, timezone

import valorant_constants as vc



TRADE_DURATION = 3000
DAMAGE_PER_KILL_ESTIMATION = 140.0
ECO_HALFBUY_THRESHOLD = 1200
HALFBUY_FULLBUY_THRESHOLD = 3500

ROUND_ORDER = [
    "Pistol Round",
    f"vs Eco (<{ECO_HALFBUY_THRESHOLD}$)",
    f"vs Halfbuy ({ECO_HALFBUY_THRESHOLD}$-{HALFBUY_FULLBUY_THRESHOLD}$)",
    f"vs Fullbuy (>{HALFBUY_FULLBUY_THRESHOLD}$)",
]
RANK_LEVELS = ["", " I", " II", " III"]

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
        if player["isObserver"]:
                continue

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


    for round_stats in (round["playerStats"] for round in game_json["roundResults"] if round["roundResult"].lower() != "surrendered"):
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
        if match["teams"] == None:
            if match["matchInfo"] != None and match["matchInfo"]["matchId"] != None:
                print(f"found skewed match (id: {match['matchInfo']['matchId']})!")
            else:
                print(f"found skewed match (id unavailable)!")
            continue

        if not match["matchInfo"]["isCompleted"]:
            continue

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
            if player["isObserver"]:
                continue

            if vc.rank_names[player["competitiveTier"]] != "Unranked":
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


        if len(player_rank_values) <= 0:
            continue

        for match_round in match["roundResults"]:
            if match_round["roundResult"].lower() == "surrendered":
                continue

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
            player_stats["Usg%"] = (
                player_stats["temp_usagePoints"] / team_total_usage_points[player_stats["team"]]
                if team_total_usage_points[player_stats["team"]] > 0
                else (print(f"Warning: team_total_usage_points is 0 for team {player_stats['team']} in {match['matchInfo']['matchId']}") or 0.2)
            )
            player_stats["Rating"] = (player_stats["K/R"] * KPR_MODIFIER) + (player_stats["A/R"] * APR_MODIFIER) + (dpr * DPR_MODIFIER) + (adra * ADRA_MODIFIER) + (sr * SR_MODIFIER) + (player_stats["KAST%"] * KAST_MODIFIER) + GENERAL_MODIFIER

            for key in ("rounds", "kills", "deaths", "team", "temp_damage", "temp_kastRounds", "temp_usagePoints"):
                player_stats.pop(key, None)

        agent_stats.append({
            "Gamemode": match["matchInfo"]["queueId"].lower().capitalize(),
            "Date": time_string_from_milliseconds(match["matchInfo"]["gameStartMillis"]),
            "Patch": patch_from_game_version(match["matchInfo"]["gameVersion"]) if match["matchInfo"]["gameVersion"] != None else "",
            "Map": vc.map_names[match["matchInfo"]["mapId"]],
            "Rank": vc.rank_names[round(sum(player_rank_values) / len(player_rank_values))],
            "Draw": results["Red"] == "Draw",
            "Players": list(stats_dict.values())
        })

        weapon_stats.append({
            "Gamemode": match["matchInfo"]["queueId"].lower().capitalize(),
            "Date": time_string_from_milliseconds(match["matchInfo"]["gameStartMillis"]),
            "Patch": patch_from_game_version(match["matchInfo"]["gameVersion"]) if match["matchInfo"]["gameVersion"] != None else "",
            "Map": vc.map_names[match["matchInfo"]["mapId"]],
            "Rank": vc.rank_names[round(sum(player_rank_values) / len(player_rank_values))],
            "Player_Rounds": weapon_rounds
        })

    return agent_stats, weapon_stats



# This uses a surprisingly accurate but still technically very crude approximation of VLR player rating
def calculate_player_agent_and_weapon_stats(match, puuid):
    if match["teams"] == None:
        if match["matchInfo"] != None and match["matchInfo"]["matchId"] != None:
            print(f"found skewed match (id: {match['matchInfo']['matchId']})!")
        else:
            print(f"found skewed match (id unavailable)!")
        return {}, {}

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
        if player["isObserver"]:
            continue

        if vc.rank_names[player["competitiveTier"]] != "Unranked":
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
        if match_round["roundResult"].lower() == "surrendered":
            continue

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

            if player_round_stats["puuid"] == puuid:
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
        player_stats["Usg%"] = (player_stats["temp_usagePoints"] / team_total_usage_points[player_stats["team"]]) if team_total_usage_points[player_stats["team"]] > 0 else 0.2
        player_stats["Rating"] = (player_stats["K/R"] * KPR_MODIFIER) + (player_stats["A/R"] * APR_MODIFIER) + (dpr * DPR_MODIFIER) + (adra * ADRA_MODIFIER) + (sr * SR_MODIFIER) + (player_stats["KAST%"] * KAST_MODIFIER) + GENERAL_MODIFIER

        for key in ("rounds", "kills", "deaths", "team", "temp_damage", "temp_kastRounds", "temp_usagePoints"):
            player_stats.pop(key, None)


    agent_stats = {
        "MatchId": match["matchInfo"]["matchId"],
        "Gamemode": match["matchInfo"]["queueId"].lower().capitalize(),
        "Date": time_string_from_milliseconds(match["matchInfo"]["gameStartMillis"]),
        "Patch": patch_from_game_version(match["matchInfo"]["gameVersion"]) if match["matchInfo"]["gameVersion"] != None else "",
        "Map": vc.map_names[match["matchInfo"]["mapId"]],
        "Rank": vc.rank_names[round(sum(player_rank_values) / len(player_rank_values)) if len(player_rank_values) > 0 else 0],
        "Draw": results["Red"] == "Draw",
        "Player": stats_dict[puuid]
    }

    weapon_stats = {
        "Gamemode": match["matchInfo"]["queueId"].lower().capitalize(),
        "Date": time_string_from_milliseconds(match["matchInfo"]["gameStartMillis"]),
        "Patch": patch_from_game_version(match["matchInfo"]["gameVersion"]) if match["matchInfo"]["gameVersion"] != None else "",
        "Map": vc.map_names[match["matchInfo"]["mapId"]],
        "Rank": vc.rank_names[round(sum(player_rank_values) / len(player_rank_values)) if len(player_rank_values) > 0 else 0],
        "Player_Rounds": weapon_rounds
    }

    return agent_stats, weapon_stats



def format_agent_stats_for_display(filepath, filtered_agents, filtered_maps, filtered_ranks, filtered_gamemodes = ["Competitive"], single_player_pickrate = False):
    filtered_ranks_extended = [
        f"{word}{suffix}"
        for word in filtered_ranks
        for suffix in RANK_LEVELS
    ]
    
    con = duckdb.connect()

    filters = []

    if filtered_maps:
        filters.append(f"Map IN {tuple(filtered_maps)}")
    if filtered_ranks_extended:
        filters.append(f"Rank IN {tuple(filtered_ranks_extended)}")
    if filtered_agents:
        filters.append(f"Agent IN {tuple(filtered_agents)}")
    if filtered_gamemodes:
        filters.append(f"Gamemode IN {tuple(filtered_gamemodes)}")

    where_clause = " AND ".join(filters) if filters else "TRUE"

    query = f"""
    CREATE OR REPLACE VIEW filtered_agents AS
    SELECT *
    FROM '{filepath}'
    WHERE {where_clause};
    """

    con.execute(query)

    total_matches_df = con.execute("""
    SELECT COUNT(DISTINCT MatchID) AS total_matches
    FROM filtered_agents;
    """).fetchdf()
    total_matches = total_matches_df.iloc[0]["total_matches"] or 1

    df = con.execute("""
    SELECT
        Agent,
        AVG(Rating) AS avg_rating,
        AVG("K/R") AS avg_kr,
        AVG("A/R") AS avg_ar,
        AVG("KAST%") AS avg_kast,
        AVG("USE%") AS avg_use,
        COUNT(*) AS matches,
        SUM(CASE WHEN NOT Mirror AND Result = 'Win' THEN 1 ELSE 0 END) AS unmirrored_wins,
        SUM(CASE WHEN NOT Mirror AND Result = 'Loss' THEN 1 ELSE 0 END) AS unmirrored_losses,
    FROM filtered_agents
    GROUP BY Agent;
    """).fetchdf()

    con.close()

    processed_stats = []

    for i, row in enumerate(df.itertuples(index=False)):
        decisive = row.unmirrored_wins + row.unmirrored_losses
        win_rate = (row.unmirrored_wins / decisive) if decisive > 0 else 0
        if single_player_pickrate:
            pick_rate = float((row.matches / total_matches)) if total_matches > 0 else 0
        else:
            pick_rate = float((row.matches / (total_matches * 2))) if total_matches > 0 else 0

        processed_stats.append({
            "id": i,
            "name": row.Agent,
            "stats": {
                "Rating": row.avg_rating,
                "K/R": row.avg_kr,
                "A/R": row.avg_ar,
                "KAST%": row.avg_kast,
                "Usg%": row.avg_use,
                "Win%": win_rate,
                "Pick%": pick_rate,
            }
        })

    return processed_stats



def format_weapon_stats_for_display(filepath, filtered_weapons, filtered_agents, filtered_maps, filtered_ranks, filtered_gamemodes = ["Competitive"]):
    filtered_ranks_extended = [
        f"{word}{suffix}"
        for word in filtered_ranks
        for suffix in RANK_LEVELS
    ]

    con = duckdb.connect()

    filters = []

    if filtered_maps:
        filters.append(f"Map IN {tuple(filtered_maps)}")
    if filtered_ranks_extended:
        filters.append(f"Rank IN {tuple(filtered_ranks_extended)}")
    if filtered_agents:
        filters.append(f"Agent IN {tuple(filtered_agents)}")
    if filtered_weapons:
        filters.append(f"Weapon IN {tuple(filtered_weapons)}")
    if filtered_gamemodes:
        filters.append(f"Gamemode IN {tuple(filtered_gamemodes)}")

    where_clause = " AND ".join(filters) if filters else "TRUE"

    query = f"""
    CREATE OR REPLACE VIEW filtered_rounds AS
    SELECT *,
        CASE 
            WHEN PistolRound THEN 'Pistol Round'
            WHEN OpponentAverageLoadout < {ECO_HALFBUY_THRESHOLD} THEN 'vs Eco (<{ECO_HALFBUY_THRESHOLD}$)'
            WHEN OpponentAverageLoadout < {HALFBUY_FULLBUY_THRESHOLD} THEN 'vs Halfbuy ({ECO_HALFBUY_THRESHOLD}$-{HALFBUY_FULLBUY_THRESHOLD}$)'
            ELSE 'vs Fullbuy (>{HALFBUY_FULLBUY_THRESHOLD}$)'
        END AS RoundType
    FROM '{filepath}'
    WHERE {where_clause};
    """

    con.execute(query)

    sub_df = con.execute("""
    SELECT 
        Weapon,
        RoundType,
        SUM(Damage) AS total_damage,
        SUM(Kills) AS total_kills,
        SUM(CASE WHEN Win THEN 1 ELSE 0 END) AS total_wins,
        SUM(Headshots) AS total_headshots,
        SUM(Bodyshots) AS total_bodyshots,
        SUM(Legshots) AS total_legshots,
        COUNT(*) AS rounds
    FROM filtered_rounds
    GROUP BY Weapon, RoundType;
    """).fetchdf()

    main_df = con.execute("""
    SELECT 
        Weapon,
        SUM(Damage) AS total_damage,
        SUM(Kills) AS total_kills,
        SUM(CASE WHEN Win THEN 1 ELSE 0 END) AS total_wins,
        SUM(Headshots) AS total_headshots,
        SUM(Bodyshots) AS total_bodyshots,
        SUM(Legshots) AS total_legshots,
        COUNT(*) AS rounds
    FROM filtered_rounds
    GROUP BY Weapon;
    """).fetchdf()

    con.close()

    processed_stats = {}

    for i, row in enumerate(main_df.itertuples(index=False)):
        weapon = row.Weapon
        total_shots = row.total_headshots + row.total_bodyshots + row.total_legshots

        stats = {
            "Dmg/R": row.total_damage / row.rounds if row.rounds else 0,
            "K/R": row.total_kills / row.rounds if row.rounds else 0,
            "Win%": row.total_wins / row.rounds if row.rounds else 0,
            "HS%": (row.total_headshots / total_shots) if total_shots > 0 else 0,
        }

        processed_stats[weapon] = {
            "id": i,
            "name": weapon,
            "stats": stats,
            "subentries": { round_type: {"Dmg/R": 0, "K/R": 0, "Win%": 0, "HS%": 0} for round_type in ROUND_ORDER }
        }

    for row in sub_df.itertuples(index=False):
        weapon = row.Weapon
        if weapon not in processed_stats:
            continue

        total_shots = row.total_headshots + row.total_bodyshots + row.total_legshots
        sub_stats = {
            "Dmg/R": row.total_damage / row.rounds if row.rounds else 0,
            "K/R": row.total_kills / row.rounds if row.rounds else 0,
            "Win%": row.total_wins / row.rounds if row.rounds else 0,
            "HS%": (row.total_headshots / total_shots) if total_shots > 0 else 0,
        }

        processed_stats[weapon]["subentries"][row.RoundType] = sub_stats

    for weapon_data in processed_stats.values():
        if (
            "Pistol Round" in weapon_data["subentries"]
            and weapon_data["subentries"]["Pistol Round"]["Dmg/R"] == 0
        ):
            weapon_data["subentries"].pop("Pistol Round", None)

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


