from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import joblib
import pandas as pd

import round_prediction
import weapon_processing

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, set this more securely
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/weapons")
def get_weapons():
    filename_test = "logs25-1"
    path = "data/" + filename_test + ".json"
    return weapon_processing.get_weapon_stats(path)