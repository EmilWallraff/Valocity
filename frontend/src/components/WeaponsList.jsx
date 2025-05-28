import React, { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

import { weapons } from "../data/hashcodes";

const statKeyMap = {
  "Kills/Round": "kills",
  "Damage/Round": "damage",
  "Win%": "win",
  "HS%": "headshot",
  "Pick%": "pick",
  "K/D": "kd"
};

export default function WeaponsList({ data, headers = [] }) {
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

  const sortedData = [...data].sort((a, b) => {
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
                <img src={`/images/valorant/weapons/${weapons[weapon.name]}_killstream.png`} alt={weapon.name} className="max-w-full max-h-full object-contain" />
              </div>
              <span className="truncate">{weapon.name}</span>
            </div>
            <div className="flex-1 text-center">{weapon.stats.damage.toFixed(2)}</div>
            <div className="flex-1 text-center">{weapon.stats.kills.toFixed(2)}</div>
            <div className="flex-1 text-center">{(weapon.stats.win * 100).toFixed(0)}%</div>
            <div className="flex-1 text-center">{(weapon.stats.headshot * 100).toFixed(0)}%</div>
          </div>

          {expanded[weapon.id] && (
            <div>
              {weapon.subentries.map((entry, i) => (
                <div
                  key={i}
                  className={`flex items-center py-1 border-b border-l border-r border-element-lighter bg-${index % 2 === 0 ? "element-dark" : "element"}`}
                >
                  <div className="w-8" />
                  <div className="basis-2/6">{entry.name}</div>
                  <div className="flex-1 text-center">{entry.damage.toFixed(2)}</div>
                  <div className="flex-1 text-center">{entry.kills.toFixed(2)}</div>
                  <div className="flex-1 text-center">{(entry.win * 100).toFixed(0)}%</div>
                  <div className="flex-1 text-center">{(entry.headshot * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
