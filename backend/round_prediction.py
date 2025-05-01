import torch
from torch.utils.data import Dataset
import torch.nn as nn
import torch.nn.functional as F


class RoundDataset(Dataset):
    def __init__(self, dataframe):
        self.dataframe = dataframe

        self.red_slot_cols = [f"RED_{i}_{k}" for i in range(1,6) for k in ["agent", "weapon", "armor"]]
        self.blue_slot_cols = [f"BLUE_{i}_{k}" for i in range(1,6) for k in ["agent", "weapon", "armor"]]
        self.meta_cols = ["attacker_team", "map"]

        self.X_red = torch.tensor(self.dataframe[self.red_slot_cols].values, dtype=torch.long)
        self.X_blue = torch.tensor(self.dataframe[self.blue_slot_cols].values, dtype=torch.long)
        self.X_meta = torch.tensor(self.dataframe[self.meta_cols].values, dtype=torch.long)
        self.y = torch.tensor(self.dataframe["winner_team"].values, dtype=torch.long)

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        return {
            "red": self.X_red[idx].reshape(5, 3),
            "blue": self.X_blue[idx].reshape(5, 3),
            "meta": self.X_meta[idx],
            "label": self.y[idx]
        }



class RoundClassifier(nn.Module):
    def __init__(self, num_agents, num_weapons, num_armor, num_teams, num_maps, embed_dim=32):
        super().__init__()

        # Embeddings for slot elements
        self.agent_embed = nn.Embedding(num_agents, embed_dim)
        self.weapon_embed = nn.Embedding(num_weapons, embed_dim)
        self.armor_embed = nn.Embedding(num_armor, embed_dim)

        # Embeddings for meta
        self.team_embed = nn.Embedding(num_teams, embed_dim)
        self.map_embed = nn.Embedding(num_maps, embed_dim)

        # Shared MLP for slots
        self.slot_encoder = nn.Sequential(
            nn.Linear(embed_dim * 3, 64),
            nn.ReLU(),
            nn.Linear(64, 64)
        )

        # Final classifier
        self.classifier = nn.Sequential(
            nn.Linear(64 * 2 + embed_dim * 2, 128),  # RED + BLUE + meta
            nn.ReLU(),
            nn.Linear(128, 2)  # 2 classes
        )

    def encode_slots(self, slot_tensor):  # [batch, 5, 3]
        agent = self.agent_embed(slot_tensor[:, :, 0])
        weapon = self.weapon_embed(slot_tensor[:, :, 1])
        armor = self.armor_embed(slot_tensor[:, :, 2])

        slot_feat = torch.cat([agent, weapon, armor], dim=-1)  # [batch, 5, 3*embed_dim]
        encoded = self.slot_encoder(slot_feat)  # [batch, 5, 64]
        return encoded.mean(dim=1)  # Permutation-invariant pooling

    def forward(self, red, blue, meta):
        red_encoded = self.encode_slots(red)    # [batch, 64]
        blue_encoded = self.encode_slots(blue)  # [batch, 64]

        meta_team = self.team_embed(meta[:, 0])
        meta_map = self.map_embed(meta[:, 1])
        meta_encoded = torch.cat([meta_team, meta_map], dim=-1)  # [batch, 2*embed_dim]

        # Fix dimensions (CHATGPT ADDED THIS FOR THE BACKEND, WORKED WITHOUT IN THE JUPYTER NOTEBOOK)
        if meta_encoded.dim() == 3:
            meta_encoded = meta_encoded.squeeze(1)  # Squeeze the middle dimension

        full = torch.cat([red_encoded, blue_encoded, meta_encoded], dim=-1)  # [batch, 64*2 + embed*2]
        return self.classifier(full)
    
    def predict_proba_from_row(self, row, device="cpu"):
        # Build input tensors from a single row (Series or dict-like)
        red = torch.tensor(
            [row[f"RED_{i}_{k}"] for i in range(1, 6) for k in ["agent", "weapon", "armor"]],
            dtype=torch.long
        ).view(1, 5, 3).to(device)

        blue = torch.tensor(
            [row[f"BLUE_{i}_{k}"] for i in range(1, 6) for k in ["agent", "weapon", "armor"]],
            dtype=torch.long
        ).view(1, 5, 3).to(device)

        meta = torch.tensor(
            [row["attacker_team"], row["map"]],
            dtype=torch.long
        ).unsqueeze(0).to(device)

        self.eval()
        with torch.no_grad():
            logits = self.forward(red, blue, meta)
            probs = F.softmax(logits, dim=1)
        
        return probs.squeeze().cpu().numpy()  # returns np.array([p_class_0, p_class_1])




def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0

    with torch.no_grad():
        for batch in loader:
            red = batch["red"].to(device)
            blue = batch["blue"].to(device)
            meta = batch["meta"].to(device)
            labels = batch["label"].to(device)

            logits = model(red, blue, meta)
            preds = torch.argmax(logits, dim=1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)

    acc = correct / total
    print(f"Accuracy: {acc:.4f}")
