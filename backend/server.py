from fastapi import FastAPI, Request, Depends, Response, HTTPException
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

import round_prediction
import weapon_processing
import agent_processing



load_dotenv()

# Initialize FastAPI app
app = FastAPI()
#app = FastAPI(docs_url=None, redoc_url=None) # Disables FastAPI docs from being exposed publicly

origins = [
    "https://valocity.app",
    "https://valocity.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # False is more secure but must be True for cookies
    #allow_methods=["GET", "POST", "HEAD"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Riot OAuth config
CLIENT_ID = os.getenv("RIOT_CLIENT_ID")
CLIENT_SECRET = os.getenv("RIOT_CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Missing Riot OAuth environment variables")

#APP_BASE_URL = "http://localhost:8000" # backend
APP_BASE_URL = "https://valocity.onrender.com" # backend
REDIRECT_URI = f"{APP_BASE_URL}/oauth/callback"

PROVIDER = "https://auth.riotgames.com"
AUTHORIZE_URL = f"{PROVIDER}/authorize"
TOKEN_URL = f"{PROVIDER}/token"
USERINFO_URL = f"{PROVIDER}/userinfo"

# Your app’s secret (for signing cookies)
APP_SECRET = os.getenv("APP_SECRET", "dev_secret")
if not APP_SECRET:
    raise RuntimeError("Missing app secret variable")
ALGORITHM = "HS256"
COOKIE_NAME = "session"

FRONTEND_URL = "https://valocity.app"



# Load encoders
encoders = joblib.load("models/round_win_predictor_v01_encoders.pkl")

# Reconstruct model
model = round_prediction.RoundClassifier(
    num_agents=len(encoders['agent'].classes_),
    num_weapons=len(encoders['weapon'].classes_),
    num_armor=len(encoders['armor'].classes_),
    num_teams=len(encoders['team'].classes_),
    num_maps=len(encoders['map'].classes_)
)

# Load weights
model.load_state_dict(torch.load('models/round_win_predictor_v01.pth', map_location=torch.device('cpu')))
model.eval()

# Define request body
class PredictRequest(BaseModel):
    attacker_team: str
    map: str
    RED_1_agent: str
    RED_1_weapon: str
    RED_1_armor: str
    RED_2_agent: str
    RED_2_weapon: str
    RED_2_armor: str
    RED_3_agent: str
    RED_3_weapon: str
    RED_3_armor: str
    RED_4_agent: str
    RED_4_weapon: str
    RED_4_armor: str
    RED_5_agent: str
    RED_5_weapon: str
    RED_5_armor: str
    BLUE_1_agent: str
    BLUE_1_weapon: str
    BLUE_1_armor: str
    BLUE_2_agent: str
    BLUE_2_weapon: str
    BLUE_2_armor: str
    BLUE_3_agent: str
    BLUE_3_weapon: str
    BLUE_3_armor: str
    BLUE_4_agent: str
    BLUE_4_weapon: str
    BLUE_4_armor: str
    BLUE_5_agent: str
    BLUE_5_weapon: str
    BLUE_5_armor: str

# Define prediction endpoint
@app.post("/predict")
def predict(request: PredictRequest):
    round_variables = []
    round_variables.append({
        "attacker_team": request.attacker_team,
        "map": request.map,
        "RED_1_agent": request.RED_1_agent,
        "RED_1_weapon": request.RED_1_weapon,
        "RED_1_armor": request.RED_1_armor,
        "RED_2_agent": request.RED_2_agent,
        "RED_2_weapon": request.RED_2_weapon,
        "RED_2_armor": request.RED_2_armor,
        "RED_3_agent": request.RED_3_agent,
        "RED_3_weapon": request.RED_3_weapon,
        "RED_3_armor": request.RED_3_armor,
        "RED_4_agent": request.RED_4_agent,
        "RED_4_weapon": request.RED_4_weapon,
        "RED_4_armor": request.RED_4_armor,
        "RED_5_agent": request.RED_5_agent,
        "RED_5_weapon": request.RED_5_weapon,
        "RED_5_armor": request.RED_5_armor,
        "BLUE_1_agent": request.BLUE_1_agent,
        "BLUE_1_weapon": request.BLUE_1_weapon,
        "BLUE_1_armor": request.BLUE_1_armor,
        "BLUE_2_agent": request.BLUE_2_agent,
        "BLUE_2_weapon": request.BLUE_2_weapon,
        "BLUE_2_armor": request.BLUE_2_armor,
        "BLUE_3_agent": request.BLUE_3_agent,
        "BLUE_3_weapon": request.BLUE_3_weapon,
        "BLUE_3_armor": request.BLUE_3_armor,
        "BLUE_4_agent": request.BLUE_4_agent,
        "BLUE_4_weapon": request.BLUE_4_weapon,
        "BLUE_4_armor": request.BLUE_4_armor,
        "BLUE_5_agent": request.BLUE_5_agent,
        "BLUE_5_weapon": request.BLUE_5_weapon,
        "BLUE_5_armor": request.BLUE_5_armor
    })
    dataframe = pd.DataFrame(round_variables)

    agent_cols = [col for col in dataframe.columns if 'agent' in col]
    for col in agent_cols:
        dataframe[col] = encoders['agent'].transform(dataframe[col])
    weapon_cols = [col for col in dataframe.columns if 'weapon' in col]
    for col in weapon_cols:
        dataframe[col] = encoders['weapon'].transform(dataframe[col])
    armor_cols  = [col for col in dataframe.columns if 'armor'  in col]
    for col in armor_cols:
        dataframe[col] = encoders['armor'].transform(dataframe[col])
    team_cols  = [col for col in dataframe.columns if 'team'  in col]
    for col in team_cols:
        dataframe[col] = encoders['team'].transform(dataframe[col])
    map_cols  = [col for col in dataframe.columns if 'map'  in col]
    for col in map_cols:
        dataframe[col] = encoders['map'].transform(dataframe[col])

    logits = model.predict_proba_from_row(dataframe)
    class_names = encoders['team'].classes_
    return {k: float(v) for k, v in zip(class_names, logits)}



class WeaponsRequest(BaseModel):
    weapons: List[str]
    maps: List[str]
    agents: List[str]

@app.post("/weapons")
def calculate(request: WeaponsRequest):
    filename_test = "logs25-1"
    path = "data/" + filename_test + ".json"
    print("server weapons function called!")

    #return weapon_processing.get_weapon_stats(path, request.weapons, request.maps, request.agents)
    
    with open("data/weapons_placeholder_data.json", "r") as f:
        return json.load(f)



class AgentsRequest(BaseModel):
    agents: List[str]
    maps: List[str]

@app.post("/agents")
def calculate(request: AgentsRequest):
    filename_test = "logs25-1"
    path = "data/" + filename_test + ".json"
    print("server agents function called!")

    #return agent_processing.get_agent_stats(path, request.agents, request.maps)

    with open("data/agents_placeholder_data.json", "r") as f:
        return json.load(f)



@app.api_route("/ping", methods=["GET", "HEAD"])
def ping():
    return {"status": "ok"}



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
async def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    # Auth header for client_id + client_secret
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

    # Fetch Riot user info
    userinfo = requests.get(
        USERINFO_URL,
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    ).json()

    # Save refresh token & user data in DB (placeholder)
    user_id = userinfo["sub"]  # unique Riot user ID
    save_tokens_to_db(user_id, tokens)  # <-- implement

    # Create your own session cookie
    session_token = create_session_token(user_id)
    response = RedirectResponse(url=FRONTEND_URL)  # redirect to frontend
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=True,        # must be True in production (https only)
        samesite="none",    # required for cross-site cookies
    )

    return response

@app.get("/me")
async def me(request: Request):
    session_token = request.cookies.get(COOKIE_NAME)
    if not session_token:
        raise HTTPException(401, "Not logged in")

    payload = verify_session_token(session_token)
    if not payload:
        raise HTTPException(401, "Invalid session")

    user_id = payload["sub"]
    user_tokens = get_tokens_from_db(user_id)  # <-- implement

    return {"user_id": user_id, "tokens": "hidden for frontend"}



def create_session_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 3600,  # 1h expiry for session
    }
    return jwt.encode(payload, APP_SECRET, algorithm=ALGORITHM)

def verify_session_token(token: str):
    try:
        return jwt.decode(token, APP_SECRET, algorithms=[ALGORITHM])
    except Exception:
        return None

# Example helpers (replace with DB)
user_db = {}
def save_tokens_to_db(user_id, tokens):
    user_db[user_id] = tokens
def get_tokens_from_db(user_id):
    return user_db.get(user_id)



def refresh_access_token(user_id: str):
    tokens = get_tokens_from_db(user_id)
    refresh_token = tokens["refresh_token"]

    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {auth_header}"},
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
    )

    if resp.status_code == 200:
        new_tokens = resp.json()
        save_tokens_to_db(user_id, new_tokens)
        return new_tokens["access_token"]

    raise Exception("Failed to refresh token")

