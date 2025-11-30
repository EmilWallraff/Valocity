import torch
from torch.utils.data import Dataset
import torch.nn as nn
import torch.nn.functional as F


class RoundDataset(Dataset):
    def __init__(self, dataframe):
        self.dataframe = dataframe

        self.attack_slot_cols = [f"attack_{i}_{k}" for i in range(1,6) for k in ["agent", "weapon", "armor"]]
        self.defense_slot_cols = [f"defense_{i}_{k}" for i in range(1,6) for k in ["agent", "weapon", "armor"]]
        self.meta_cols = ["map"]

        self.X_attack = torch.tensor(self.dataframe[self.attack_slot_cols].values, dtype=torch.long)
        self.X_defense = torch.tensor(self.dataframe[self.defense_slot_cols].values, dtype=torch.long)
        self.X_meta = torch.tensor(self.dataframe[self.meta_cols].values, dtype=torch.long)
        self.y = torch.tensor(self.dataframe["winner"].values, dtype=torch.long)

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        return {
            "attack": self.X_attack[idx].reshape(5, 3),
            "defense": self.X_defense[idx].reshape(5, 3),
            "meta": self.X_meta[idx],
            "label": self.y[idx]
        }



class RoundClassifier(nn.Module):
    def __init__(self, num_agents, num_weapons, num_armor, num_maps, embed_dim=32, hidden_dim=128, num_slots=5):
        super().__init__()
        self.num_slots = num_slots
        self.embed_dim = embed_dim

        # Embeddings
        self.agent_embed = nn.Embedding(num_agents, embed_dim)
        self.weapon_embed = nn.Embedding(num_weapons, embed_dim)
        self.armor_embed = nn.Embedding(num_armor, embed_dim)
        self.map_embed = nn.Embedding(num_maps, embed_dim)

        # Per-slot encoder: considers agent+weapon+armor together
        self.slot_encoder = nn.Sequential(
            nn.Linear(embed_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(p=0.2)
        )


        # Optional: attention across slots
        self.slot_attention = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=4, batch_first=True)

        # Classifier: attack + defense + map
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * num_slots * 2 + embed_dim, 256),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(128, 2)
        )

    def encode_slots(self, slot_tensor):  # slot_tensor: [batch, 5, 3]
        agent = self.agent_embed(slot_tensor[:, :, 0])
        weapon = self.weapon_embed(slot_tensor[:, :, 1])
        armor = self.armor_embed(slot_tensor[:, :, 2])

        # Concatenate per slot
        slot_feat = torch.cat([agent, weapon, armor], dim=-1)  # [batch, 5, 3*embed_dim]
        encoded = self.slot_encoder(slot_feat)  # [batch, 5, hidden_dim]

        # Apply attention across slots
        attn_output, _ = self.slot_attention(encoded, encoded, encoded)  # [batch, 5, hidden_dim]
        attn_output = F.dropout(attn_output, p=0.2, training=self.training)

        return attn_output.reshape(encoded.size(0), -1)  # Flatten to [batch, 5*hidden_dim]

    def forward(self, attack, defense, meta):
        attack_encoded = self.encode_slots(attack)    # [batch, hidden_dim*5]
        defense_encoded = self.encode_slots(defense)  # [batch, hidden_dim*5]

        map_emb = self.map_embed(meta[:, 0])  # [batch, embed_dim]

        # Concatenate everything
        x = torch.cat([attack_encoded, defense_encoded, map_emb], dim=-1)
        return self.classifier(x)
    
    def predict_proba_from_row(self, row, device="cpu"):
        # Build input tensors from a single row (Series or dict-like)
        attack = torch.tensor(
            [row[f"attack_{i}_{k}"] for i in range(1, 6) for k in ["agent", "weapon", "armor"]],
            dtype=torch.long
        ).view(1, 5, 3).to(device)

        defense = torch.tensor(
            [row[f"defense_{i}_{k}"] for i in range(1, 6) for k in ["agent", "weapon", "armor"]],
            dtype=torch.long
        ).view(1, 5, 3).to(device)

        meta = torch.tensor(
            [row["map"]],
            dtype=torch.long
        ).unsqueeze(0).to(device)

        self.eval()
        with torch.no_grad():
            logits = self.forward(attack, defense, meta)
            probs = F.softmax(logits, dim=1)
        
        return probs.squeeze().cpu().numpy()  # returns np.array([p_class_0, p_class_1])



def evaluate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    soft_sum = 0.0  # sum of probability assigned to correct label

    with torch.no_grad():
        for batch in loader:
            attack = batch["attack"].to(device)
            defense = batch["defense"].to(device)
            meta = batch["meta"].to(device)
            labels = batch["label"].to(device)

            logits = model(attack, defense, meta)

            # Hard predictions (for standard accuracy)
            preds = torch.argmax(logits, dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            # Soft probability score
            probs = F.softmax(logits, dim=1)
            correct_probs = probs[torch.arange(labels.size(0)), labels]
            soft_sum += correct_probs.sum().item()

    acc = correct / total
    soft_acc = soft_sum / total  # average "closeness"

    print(f"Accuracy: {acc:.4f}")
    print(f"Soft Accuracy: {soft_acc:.4f}")
