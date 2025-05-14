import React, { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

const headers = ["Weapon", "Damage/Round", "Kills/Round", "Win%", "HS%"];

const statKeyMap = {
  "Kills/Round": "kills",
  "Damage/Round": "damage",
  "Win%": "win",
  "HS%": "headshot",
};

const mockData = [
  {
    id: 1,
    name: "Phantom",
    image: `/images/valorant/weapons/EE8E8D15-496B-07AC-E5F6-8FAE5D4C7B1A_killstream.png`,
    stats: { kills: 0.712, damage: 123.2342, win: 52.234, headshot: 26.234 },
    subentries: [
      { name: "Pistol Round", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Eco (<1000$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Halfbuy (1000$-3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Fullbuy (>3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
    ],
  },
  {
    id: 2,
    name: "Vandal",
    image: `/images/valorant/weapons/9C82E19D-4575-0200-1A81-3EACF00CF872_killstream.png`,
    stats: { kills: 0.609, damage: 112.2342, win: 48.2342, headshot: 29.234 },
    subentries: [
      { name: "Pistol Round", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Eco (<1000$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Halfbuy (1000$-3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Fullbuy (>3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
    ],
  },
  {
    id: 3,
    name: "Frenzy",
    image: `/images/valorant/weapons/44D4E95C-4157-0037-81B2-17841BF2E8E3_killstream.png`,
    stats: { kills: 0.919, damage: 98.234, win: 56.234, headshot: 18.2423342 },
    subentries: [
      { name: "Pistol Round", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Eco (<1000$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Halfbuy (1000$-3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Fullbuy (>3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
    ],
  },
  {
    id: 4,
    name: "Marshall",
    image: `/images/valorant/weapons/C4883E50-4494-202C-3EC3-6B8A9284F00B_killstream.png`,
    stats: { kills: 0.3012, damage: 45.234, win: 23.234, headshot: 34.213426 },
    subentries: [
      { name: "Pistol Round", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Eco (<1000$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Halfbuy (1000$-3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Fullbuy (>3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
    ],
  }
];

export default function WeaponsList() {
  const [expanded, setExpanded] = useState({});
  const [sortKey, setSortKey] = useState("damage");
  const [sortOrder, setSortOrder] = useState("desc");

  const toggleExpand = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleSort = (label) => {
    const key = statKeyMap[label];
    if (!key) return;

    if (sortKey === key) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortOrder("desc");
    }
  };

  const sortedData = [...mockData].sort((a, b) => {
    const aVal = a.stats[sortKey];
    const bVal = b.stats[sortKey];
    return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
  });

  return (
    <div className="p-4 w-full max-w-5xl mx-auto">
      <div className="flex font-bold border border-element-lighter py-2 text-left bg-element">
        <div className="w-6" />
        <div className="flex-2 flex items-center gap-2 basis-2/6">Weapon</div>
        {headers.slice(1).map((header) => (
          <div
            key={header}
            onClick={() => handleSort(header)}
            className={`flex-1 text-${sortKey === statKeyMap[header] ? sortOrder === "asc" ? "accent" : "brand" : "white"} text-center cursor-pointer`}
          >
            {header}
          </div>
        ))}
      </div>

      {sortedData.map((weapon, index) => (
        <div key={weapon.id}>
          <div className={`flex items-center py-2 border-b border-l border-r border-element-lighter bg-${index % 2 === 0 ? "element-dark" : "element"}`}>
            <div
              onClick={() => toggleExpand(weapon.id)}
              className="w-8 cursor-pointer flex justify-center"
            >
              {expanded[weapon.id] ? <ChevronDown /> : <ChevronRight />}
            </div>
            <div className="flex items-center gap-2 h-16 basis-2/6">
              <div className="w-32 h-16 flex items-center justify-center overflow-hidden flex-shrink-0">
                <img src={weapon.image} alt={weapon.name} className="max-w-full max-h-full object-contain" />
              </div>
              <span className="truncate">{weapon.name}</span>
            </div>
            <div className="flex-1 text-center">{weapon.stats.damage.toFixed(2)}</div>
            <div className="flex-1 text-center">{weapon.stats.kills.toFixed(2)}</div>
            <div className="flex-1 text-center">{weapon.stats.win.toFixed(2)}</div>
            <div className="flex-1 text-center">{weapon.stats.headshot.toFixed(2)}</div>
          </div>

          {expanded[weapon.id] && (
            <div>
              {weapon.subentries.map((entry, i) => (
                <div
                  key={i}
                  className={`flex items-center py-1 border-b border-l border-r border-element-lighter bg-${index % 2 === 0 ? "element" : "element-dark"}`}
                >
                  <div className="w-8" />
                  <div className="basis-2/6">{entry.name}</div>
                  <div className="flex-1 text-center">{entry.damage.toFixed(2)}</div>
                  <div className="flex-1 text-center">{entry.kills.toFixed(2)}</div>
                  <div className="flex-1 text-center">{entry.win.toFixed(2)}</div>
                  <div className="flex-1 text-center">{entry.headshot.toFixed(2)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
