import React, { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

import { agents } from "../data/hashcodes";
import { maps } from "../data/hashcodes"; 

const statKeyMap = {
  "Rating": "rating",
  "Kills": "kills",
  "Deaths": "deaths",
  "Assists": "assists",
  "Dmg/R": "damage",
  "KAST%": "kast",
  "USE%": "use",
  "HS%": "headshot",
};

const headers = [
  "Rating",
  "Kills",
  "Deaths",
  "Assists",
  "Dmg/R",
  "KAST%",
  "USE%",
  "HS%",
];

const headerTooltips = {
  "Rating": "Overall rating",
  "Kills": "Total kills",
  "Deaths": "Total deaths",
  "Assists": "Total assists",
  "Dmg/R": "Damage per round",
  "KAST%": "Percentage of rounds with kill, assist, survival or trade",
  "USE%": "Percentage of contribution to team's engagements (weighted)",
  "HS%": "Headshots per hits on enemy agents",
};

export default function GamesList({ data, puuid }) {
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
        <div className="flex-2 flex items-center gap-2 basis-2/6"></div>
        {headers.map((header) => (
          <div
            key={header}
            onClick={() => handleSort(header)}
            className={`group relative flex-1 text-${sortKey === statKeyMap[header] ? sortOrder === "asc" ? "accent" : "brand" : "white"} text-center cursor-pointer`}
          >
            {header}
            {headerTooltips[header] && (
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-xs px-2 py-1 font-normal text-white bg-element-dark rounded border border-element-lighter shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                {headerTooltips[header]}
              </div>
            )}
          </div>
        ))}
      </div>

      {sortedData.map((element, index) => (
        <div key={element.id}>
          <div className={`flex items-center py-2 border-b border-l border-r border-element-lighter bg-${index % 2 === 0 ? "element-dark" : "element"}`}>
            {/* Chevron */}
            {Array.isArray(element.subentries) && element.subentries.length > 0 ? (
              <div
                onClick={() => toggleExpand(element.id)}
                className={`w-8 cursor-pointer flex justify-center text-${element.allPlayersStats[puuid].result == "Win" ? "brand" : element.allPlayersStats[puuid].result == "Loss" ? "accent" : "white"}`}
              >
                {expanded[element.id] ? <ChevronDown /> : <ChevronRight />}
              </div>
            ) : (
              <div
                className={`w-8 cursor-pointer flex justify-center text-${element.allPlayersStats[puuid].result == "Win" ? "brand" : element.allPlayersStats[puuid].result == "Loss" ? "accent" : "white"}`}
              >
                {expanded[element.id] ? <ChevronDown /> : <ChevronRight />}
              </div>
            )}

            <div className="flex items-center gap-4 h-16 basis-2/6">
              {/* Images */}
              <div className="flex items-center justify-center gap-2 flex-shrink-0">
                <img
                  src={`/images/valorant/maps/${maps[element.map]}_listview.png`}
                  alt={element.map}
                  className="w-16 h-16 rounded-md object-cover"
                />
                <img
                  src={`/images/valorant/agents/${agents[element.allPlayersStats[puuid].agent]}.png`}
                  alt={element.allPlayersStats[puuid].agent}
                  className="w-16 h-16 rounded-md object-contain"
                />
              </div>

              {/* Score and Gamemode */}
              <div className="flex flex-col items-center justify-center text-center w-32">
                <div className="flex gap-2 text-lg">
                  <span className={`text-brand ${element.allPlayersStats[puuid].result == "Win" ? "font-bold" : ""}`} >
                    {element.allPlayersStats[puuid].roundsWon}
                  </span>
                  <span className="text-white">:</span>
                  <span className={`text-accent ${element.allPlayersStats[puuid].result== "Loss" ? "font-bold" : ""}`} >
                    {element.allPlayersStats[puuid].roundsLost}
                  </span>
                </div>
                <h2 className="text-white">{element.gamemode}</h2>
              </div>
            </div>

            {/* Stats */}
            {headers.map((header, index) => {
              return (
                <div className="flex-1 text-center">{header.includes("%") ? (element.stats[statKeyMap[header]] * 100).toFixed(0) + "%" :  element.stats[statKeyMap[header]]}</div>
              );
            })}
          </div>

          {expanded[element.id] && (
            <div>
              {element.subentries.map((entry, i) => (
                <div
                  key={i}
                  className={`flex items-center py-1 border-b border-l border-r border-element-lighter bg-${index % 2 === 0 ? "element-dark" : "element"}`}
                >
                  <div className="w-8" />
                  <div className="basis-2/6">{entry.name}</div>
                  {headers.map((header, index) => {
                    if (index === 0) return null;

                    return (
                      <div className="flex-1 text-center">{header.includes("%") ? (entry[statKeyMap[header]] * 100).toFixed(0) + "%" :  entry[statKeyMap[header]]}</div>
                    );
                  })}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
