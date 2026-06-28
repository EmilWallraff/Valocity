from fastapi import FastAPI, Request, Depends, Response, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import List
import torch
import joblib
import pandas as pd
import requests
import base64
import os
import json
from dotenv import load_dotenv
from jose import jwt
import time
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote

from database import UserToken, get_db

import round_prediction
import match_processing
import valorant_constants



# Initialize FastAPI app
app = FastAPI(docs_url=None, redoc_url=None) # Disables FastAPI docs from being exposed publicly

origins = [
    "https://valocity.app",
    "https://valocity.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    #allow_origins=["*"], # Allows all sources (for example for local testing)
    allow_credentials=True, # False is more secure but must be True for cookies
    allow_methods=["GET", "POST", "HEAD"],
    allow_headers=["*"],
)

# region Constants
load_dotenv()

# Riot OAuth config:
CLIENT_ID = os.getenv("RIOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("RIOT_CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing Riot OAuth environment variables")

APP_BASE_DOMAIN = "valocity.onrender.com"
REDIRECT_URI = f"https://{APP_BASE_DOMAIN}/oauth/callback"

PROVIDER = "https://auth.riotgames.com"
AUTHORIZE_URL = f"{PROVIDER}/authorize"
TOKEN_URL = f"{PROVIDER}/token"
USERINFO_URL = f"{PROVIDER}/userinfo"

# Signing Cookies:
APP_SECRET = os.getenv("APP_SECRET")
if not APP_SECRET:
    raise RuntimeError("Missing app secret variable")
ALGORITHM = "HS256"
COOKIE_NAME = "session"
FRONTEND_URL = "https://valocity.app"

# Riot API access:
API_KEY = os.getenv("RIOT_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing Riot API key variable")

API_CALL_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": f"{API_KEY}"
}

# Workload settings:
MAX_THREADS = 10
PLAYER_STATS_MATCH_COUNT = MAX_THREADS
# endregion



# region Win Prediction
encoders = joblib.load("models/round_win_predictor_v07_encoders.pkl")

model = round_prediction.RoundClassifier(
    num_agents=len(encoders['agent'].classes_),
    num_weapons=len(encoders['weapon'].classes_),
    num_armor=len(encoders['armor'].classes_),
    num_maps=len(encoders['map'].classes_)
)

model.load_state_dict(torch.load('models/round_win_predictor_v07.pth', map_location=torch.device('cpu')))
model.eval()


class PredictRequest(BaseModel):
    map: str
    attack_1_agent: str
    attack_1_weapon: str
    attack_1_armor: str
    attack_2_agent: str
    attack_2_weapon: str
    attack_2_armor: str
    attack_3_agent: str
    attack_3_weapon: str
    attack_3_armor: str
    attack_4_agent: str
    attack_4_weapon: str
    attack_4_armor: str
    attack_5_agent: str
    attack_5_weapon: str
    attack_5_armor: str
    defense_1_agent: str
    defense_1_weapon: str
    defense_1_armor: str
    defense_2_agent: str
    defense_2_weapon: str
    defense_2_armor: str
    defense_3_agent: str
    defense_3_weapon: str
    defense_3_armor: str
    defense_4_agent: str
    defense_4_weapon: str
    defense_4_armor: str
    defense_5_agent: str
    defense_5_weapon: str
    defense_5_armor: str

@app.post("/predict")
def predict(request: PredictRequest):
    round_variables = []
    round_variables.append({
        "map": request.map,
        "attack_1_agent": request.attack_1_agent,
        "attack_1_weapon": request.attack_1_weapon,
        "attack_1_armor": request.attack_1_armor,
        "attack_2_agent": request.attack_2_agent,
        "attack_2_weapon": request.attack_2_weapon,
        "attack_2_armor": request.attack_2_armor,
        "attack_3_agent": request.attack_3_agent,
        "attack_3_weapon": request.attack_3_weapon,
        "attack_3_armor": request.attack_3_armor,
        "attack_4_agent": request.attack_4_agent,
        "attack_4_weapon": request.attack_4_weapon,
        "attack_4_armor": request.attack_4_armor,
        "attack_5_agent": request.attack_5_agent,
        "attack_5_weapon": request.attack_5_weapon,
        "attack_5_armor": request.attack_5_armor,
        "defense_1_agent": request.defense_1_agent,
        "defense_1_weapon": request.defense_1_weapon,
        "defense_1_armor": request.defense_1_armor,
        "defense_2_agent": request.defense_2_agent,
        "defense_2_weapon": request.defense_2_weapon,
        "defense_2_armor": request.defense_2_armor,
        "defense_3_agent": request.defense_3_agent,
        "defense_3_weapon": request.defense_3_weapon,
        "defense_3_armor": request.defense_3_armor,
        "defense_4_agent": request.defense_4_agent,
        "defense_4_weapon": request.defense_4_weapon,
        "defense_4_armor": request.defense_4_armor,
        "defense_5_agent": request.defense_5_agent,
        "defense_5_weapon": request.defense_5_weapon,
        "defense_5_armor": request.defense_5_armor
    })
    dataframe = pd.DataFrame(round_variables)

    agent_cols = [col for col in dataframe.columns if 'agent' in col]
    for col in agent_cols:
        dataframe[col] = encoders['agent'].transform(dataframe[col])
    weapon_cols = [col for col in dataframe.columns if 'weapon' in col]
    for col in weapon_cols:
        dataframe[col] = encoders['weapon'].transform(dataframe[col])
    armor_cols  = [col for col in dataframe.columns if 'armor' in col]
    for col in armor_cols:
        dataframe[col] = encoders['armor'].transform(dataframe[col])
    map_cols  = [col for col in dataframe.columns if 'map' in col]
    for col in map_cols:
        dataframe[col] = encoders['map'].transform(dataframe[col])

    row = dataframe.iloc[0]
    probabilities = model.predict_proba_from_row(row)
    class_names = encoders['team'].classes_
    return {k: float(v) for k, v in zip(class_names, probabilities)}
# endregion



# region Player and Stats Requests
@app.get("/player_by_riot_id")
async def get_player_by_riot_id(gameName: str, tagLine: str, db: Session = Depends(get_db)):
    # parameters are already URI encoded. If we need them raw, we can use 'unquote()'
    riot_endpoint = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(gameName)}/{quote(tagLine)}"

    resp = requests.get(riot_endpoint, headers=API_CALL_HEADERS)
    
    if resp.status_code == 404:
        print("user not found by Riot")
        data = {"status": "nonexistent"}
        return data
    elif resp.status_code == 200:
        db_user = db.query(UserToken).filter(UserToken.puuid == resp.json()["puuid"]).first()
        if db_user:
            print("user found in database")
            data = resp.json()
            data["status"] = "public"
            return data
        else:
            print("user not found in database")
            data = resp.json()
            data["status"] = "private"
            return data
    else:
        print("riot wrong response code, probably some error")
        raise HTTPException(resp.status_code, f"Riot API error: {resp.text}")


class PlayerMatchesRequest(BaseModel):
    puuid: str
    count: int
    offset: int
    gamemodes: List[str]

@app.post("/player_matches")
async def get_matches(request: PlayerMatchesRequest):
    # We have to try all regions here, I'm afraid...
    riot_player_matches_endpoint = f"https://eu.api.riotgames.com/val/match/v1/matchlists/by-puuid/{request.puuid}"

    resp = requests.get(riot_player_matches_endpoint, headers=API_CALL_HEADERS)

    if resp.status_code != 200:
        print("riot wrong response code, probably some error")
        raise HTTPException(resp.status_code, f"Riot API error: {resp.text}")
    
    player_matches = resp.json()["history"]
    relevant_match_ids = []
    offset_counter = 0

    for match in player_matches:
        if match["queueId"].lower() in [gamemode.lower() for gamemode in request.gamemodes]:
            if offset_counter < request.offset:
                offset_counter += 1
            else:
                relevant_match_ids.append(match["matchId"])
                if len(relevant_match_ids) >= request.count:
                    break

    print(f"Number of relevant matches: {len(relevant_match_ids)}")
    
    match_history = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_match = {executor.submit(fetch_match, mid): mid for mid in relevant_match_ids}
        for future in as_completed(future_to_match):
            try:
                match_history.append(match_processing.format_match(future.result()))
            except Exception as e:
                print(f"Error fetching match {future_to_match[future]}: {e}")

    return match_history


class PlayerStatsRequest(BaseModel):
    puuid: str
    gamemodes: List[str]
    maps: List[str]
    agents: List[str]

@app.post("/player_stats")
async def get_player_stats(request: PlayerStatsRequest):
    # We have to try all regions here, I'm afraid...
    riot_player_matches_endpoint = f"https://eu.api.riotgames.com/val/match/v1/matchlists/by-puuid/{request.puuid}"

    resp = requests.get(riot_player_matches_endpoint, headers=API_CALL_HEADERS)

    if resp.status_code != 200:
        print("riot wrong response code, probably some error")
        raise HTTPException(resp.status_code, f"Riot API error: {resp.text}")
    
    player_matches = resp.json()["history"]
    relevant_match_ids = []

    for match in player_matches:
        if match["queueId"].lower() in [gamemode.lower() for gamemode in request.gamemodes]:
            relevant_match_ids.append(match["matchId"])
            if len(relevant_match_ids) >= PLAYER_STATS_MATCH_COUNT:
                break

    print(f"Number of relevant matches: {len(relevant_match_ids)}")

    base_path = Path("/tmp/player_stats_temp")
    subfolder_path = base_path / request.puuid
    json_file_path = subfolder_path / "processed_matches.json"

    subfolder_path.mkdir(parents=True, exist_ok=True)
    if not json_file_path.exists():
        print(f"JSON file not found. Creating new file at {json_file_path}")
        processed_match_ids = []
    else:
        print(f"JSON file found. Reading contents...")
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                processed_match_ids = json.load(f)
                if not isinstance(processed_match_ids, list):
                    print("Warning: File contents were not a list. Resetting to empty list.")
                    processed_match_ids = []
        except json.JSONDecodeError:
            print("Warning: File was corrupted or empty. Resetting to empty list.")
            processed_match_ids = []

    new_match_ids = [mid for mid in relevant_match_ids if mid not in processed_match_ids]

    if new_match_ids:
        print(f"Adding {len(new_match_ids)} new match IDs to {json_file_path.name}")
        processed_match_ids.extend(new_match_ids)

        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(processed_match_ids, f, ensure_ascii=False, indent=2)
    else:
        print("No new match IDs to add.")

    agent_rows = []
    weapon_rows = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_match = {executor.submit(fetch_match, mid): mid for mid in new_match_ids}
        for future in as_completed(future_to_match):
            try:
                agent_stats, weapon_stats = match_processing.calculate_player_agent_and_weapon_stats(future.result(), request.puuid)
                agent_rows.append({
                    "MatchID": agent_stats["MatchId"],
                    "Gamemode": agent_stats["Gamemode"],
                    "Date": agent_stats["Date"],
                    "Patch": agent_stats["Patch"],
                    "Map": agent_stats["Map"],
                    "Rank": agent_stats["Rank"],
                    **agent_stats["Player"]
                })
                for pr in weapon_stats["Player_Rounds"]:
                    weapon_rows.append({
                        "Gamemode": weapon_stats["Gamemode"],
                        "Date": weapon_stats["Date"],
                        "Patch": weapon_stats["Patch"],
                        "Map": weapon_stats["Map"],
                        "Rank": weapon_stats["Rank"],
                        **pr
                    })
            except Exception as e:
                print(f"Error fetching match {future_to_match[future]}: {e}")

    def append_or_create_parquet(file_path: Path, new_rows: list[dict]):
        new_df = pd.DataFrame(new_rows)

        if file_path.exists():
            existing_df = pd.read_parquet(file_path)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            print(f"Appended {len(new_rows)} rows to {file_path.name}")
        else:
            combined_df = new_df
            print(f"Created new parquet file {file_path.name}")

        combined_df.to_parquet(file_path, index=False)

    agent_parquet_file_path = subfolder_path / "agent_stats.parquet"
    weapon_parquet_file_path = subfolder_path / "weapon_stats.parquet"
    append_or_create_parquet(agent_parquet_file_path, agent_rows)
    append_or_create_parquet(weapon_parquet_file_path, weapon_rows)
    agent_display_stats = match_processing.format_agent_stats_for_display(agent_parquet_file_path, request.agents, request.maps, list(valorant_constants.rank_names.values()), request.gamemodes, True)
    weapon_display_stats = match_processing.format_weapon_stats_for_display(weapon_parquet_file_path, list(valorant_constants.weapon_names.values()), request.agents, request.maps, list(valorant_constants.rank_names.values()), request.gamemodes)

    return agent_display_stats, weapon_display_stats


class WeaponsRequest(BaseModel):
    weapons: List[str]
    maps: List[str]
    agents: List[str]
    ranks: List[str]

@app.post("/weapons")
def get_weapon_stats(request: WeaponsRequest):
    folder = Path("data")
    files = folder.glob("weapon_stats*")

    def parse_version(filename):
        version_str = filename.stem.split("_")[-1]
        return tuple(map(int, version_str.split(".")))

    latest_file = max(files, key=parse_version)
    return match_processing.format_weapon_stats_for_display(latest_file, request.weapons, request.agents, request.maps, request.ranks)


class AgentsRequest(BaseModel):
    agents: List[str]
    maps: List[str]
    ranks: List[str]

@app.post("/agents")
def get_agent_stats(request: AgentsRequest):
    folder = Path("data")
    files = folder.glob("agent_stats_*")

    def parse_version(filename):
        version_str = filename.stem.split("_")[-1]
        return tuple(map(int, version_str.split(".")))

    latest_file = max(files, key=parse_version)
    return match_processing.format_agent_stats_for_display(latest_file, request.agents, request.maps, request.ranks)



def fetch_match(match_id):
    riot_match_endpoint = f"https://eu.api.riotgames.com/val/match/v1/matches/{match_id}"
    print(f"Requesting match with: {riot_match_endpoint}")

    match_resp = requests.get(riot_match_endpoint, headers=API_CALL_HEADERS)

    if match_resp.status_code != 200:
        print("riot wrong response code, probably some error")
        raise HTTPException(match_resp.status_code, f"Riot API error: {match_resp.text}")
    return match_resp.json()
# endregion



# region Authentification
@app.get("/login")
async def login():
    link = (
        f"{AUTHORIZE_URL}?redirect_uri={REDIRECT_URI}"
        f"&client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&scope=openid offline_access"
    )
    return RedirectResponse(link)

@app.get("/oauth/callback")
async def oauth_callback(response: Response, request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    # Exchange code for tokens
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    # Exchange code for tokens
    token_resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth_header}"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
    )

    if token_resp.status_code != 200:
        return JSONResponse({"error": "Token request failed", "details": token_resp.text}, status_code=400)

    tokens = token_resp.json()

    expires_in = tokens.get("expires_in", 3600)

    # Fetch Riot user info
    userinfo = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    ).json()

    user_id = userinfo["sub"]

    # Save/update in SQLite
    db_user = db.query(UserToken).filter(UserToken.user_id == user_id).first()
    if db_user:
        db_user.access_token = tokens["access_token"]
        db_user.refresh_token = tokens["refresh_token"]
        db_user.id_token = tokens["id_token"]
        db_user.scope = tokens.get("scope", "")
        db_user.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    else:
        # Riot account endpoint (choose region closest to your server)
        riot_endpoint = "https://europe.api.riotgames.com/riot/account/v1/accounts/me"

        resp = requests.get(
            riot_endpoint,
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )

        if resp.status_code != 200:
            print("riot wrong response code, probably some error")
            raise HTTPException(resp.status_code, f"Riot API error: {resp.text}")

        db_user = UserToken(
            user_id=user_id,
            puuid=resp.json()["puuid"],
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            id_token=tokens["id_token"],
            scope=tokens.get("scope", ""),
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        db.add(db_user)

    db.commit()

    # Create your own session cookie
    session_token = create_session_token(user_id)
    response = RedirectResponse(url=FRONTEND_URL)  # redirect to frontend
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=True,            # must be True in production (https only)
        samesite="none",        # required for cross-site cookies
        domain=APP_BASE_DOMAIN  # force backend domain
    )

    return response

@app.get("/riot/me")
async def riot_me(request: Request, db: Session = Depends(get_db)):
    # Verify session cookie
    session_token = request.cookies.get(COOKIE_NAME)
    if not session_token:
        raise HTTPException(401, "Not logged in")
    else:
        print("session token found")

    payload = verify_session_token(session_token)
    if not payload:
        raise HTTPException(401, "Invalid session")
    else:
        print("session token verified")

    user_id = payload["sub"]
    db_user = db.query(UserToken).filter(UserToken.user_id == user_id).first()
    if not db_user:
        raise HTTPException(404, "User not found")
    else:
        print("user found in database")

    # Refresh if expired
    if not db_user.expires_at or datetime.utcnow() >= db_user.expires_at:
        refreshed = refresh_tokens(db, db_user)
        if not refreshed:
            print("tried and failed to refresh token")
            raise HTTPException(401, "Failed to refresh token")
        else:
            print("token refreshed")
        db_user = refreshed

    access_token = db_user.access_token

    # Riot account endpoint (choose region closest to your server)
    riot_endpoint = "https://europe.api.riotgames.com/riot/account/v1/accounts/me"

    resp = requests.get(
        riot_endpoint,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if resp.status_code != 200:
        print("riot wrong response code, probably some error")
        raise HTTPException(resp.status_code, f"Riot API error: {resp.text}")

    return resp.json()



def create_session_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 7*24*3600, # expiry for session
    }
    return jwt.encode(payload, APP_SECRET, algorithm=ALGORITHM)

def verify_session_token(token: str):
    try:
        return jwt.decode(token, APP_SECRET, algorithms=[ALGORITHM])
    except Exception:
        return None

def refresh_tokens(db, user: UserToken):
    if not user.refresh_token:
        return None

    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth_header}"},
        data={"grant_type": "refresh_token", "refresh_token": user.refresh_token},
    )

    if resp.status_code != 200:
        return None

    new_tokens = resp.json()
    expires_in = new_tokens.get("expires_in", 3600)

    # Update DB
    user.access_token = new_tokens["access_token"]
    user.refresh_token = new_tokens.get("refresh_token", user.refresh_token)
    user.id_token = new_tokens.get("id_token", user.id_token)
    user.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    db.commit()
    db.refresh(user)

    return user
# endregion



@app.api_route("/ping", methods=["GET", "HEAD"])
def ping():
    return {"status": "ok"}