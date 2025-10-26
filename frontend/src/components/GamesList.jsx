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
  "Rating": "Overall rating (with 1.0 being an average performance)",
  "Kills": "Total kills",
  "Deaths": "Total deaths",
  "Assists": "Total assists",
  "Dmg/R": "Damage per round",
  "KAST%": "Percentage of rounds with kill, assist, survival or trade",
  "USE%": "Percentage of contribution to team's engagements (weighted)",
  "HS%": "Headshots per hits on enemy agents",
};

const statFormatters = {
  "Rating": (val) => val.toFixed(2),
  "Kills": (val) => val.toFixed(0),
  "Deaths": (val) => val.toFixed(0),
  "Assists": (val) => val.toFixed(0),
  "Dmg/R": (val) => val.toFixed(0),
  "KAST%": (val) => (val * 100).toFixed(0) + "%",
  "USE%": (val) => (val * 100).toFixed(0) + "%",
  "HS%": (val) => (val * 100).toFixed(0) + "%",
};


export default function GamesList({ data, puuid }) {
  const [expanded, setExpanded] = useState({});

  const toggleExpand = (key) => {
    setExpanded((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const getDay = (dateStr) => {
    const date = new Date(dateStr);
    const day = date.getUTCDate();
    const month = date.toLocaleString("en-GB", { month: "long" });
    return `${day}. ${month}`;
  };

  const sortedData = [...data].sort((a, b) => new Date(b.date) - new Date(a.date));

  return (
    <div className="p-4 w-full max-w-6xl mx-auto">
      {(() => {
        let rowIndex = 0; // counter for background color stripes

        return sortedData.map((element, index) => {
          const currentDay = getDay(element.date);
          const previousDay = index > 0 ? getDay(sortedData[index - 1].date) : null;
          const showHeader = index === 0 || currentDay !== previousDay;
          const rowKey = element.matchId || `${element.date}-${index}`;

          return (
            <div key={rowKey}>
              {/* Day header */}
              {showHeader && (
                <div className={`flex border border-element-lighter py-2 text-left text-white ${rowIndex++ % 2 === 0 ? "bg-element" : "bg-element-dark"}`} >
                  <div className="w-8" />
                  <div className="flex-2 flex items-center gap-2 basis-2/6">
                    {currentDay}
                  </div>
                  {headers.map((header) => (
                    <div key={header} className="group relative flex-1 text-offwhite text-center" >
                      {header}
                      {headerTooltips[header] && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-xs px-2 py-1 font-normal text-white bg-element-dark rounded border border-element-lighter shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                          {headerTooltips[header]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Game row */}
              <div className={`flex items-center py-2 border-b border-l border-r border-element-lighter ${rowIndex++ % 2 === 0 ? "bg-element" : "bg-element-dark"}`} >

                {/* Chevron */}
                {element.allPlayersStats &&
                typeof element.allPlayersStats === "object" &&
                Object.keys(element.allPlayersStats).length > 0 ? (
                  <div
                    onClick={() => toggleExpand(rowKey)}
                    className={`w-8 cursor-pointer flex justify-center text-${element.allPlayersStats[puuid].result === "Win" ? "brand" : element.allPlayersStats[puuid].result === "Loss" ? "accent" : "white"}`}
                  >
                    {expanded[rowKey] ? <ChevronDown /> : <ChevronRight />}
                  </div>
                ) : (
                  <div className="w-8" />
                )}

                {/* Game info */}
                <div className="flex items-center gap-4 h-16 basis-2/6">
                  <div className="flex items-center justify-center gap-2 flex-shrink-0">
                    <img src={`/images/valorant/maps/${maps[element.map]}_listview.png`} alt={element.map} className="w-16 h-16 rounded-md object-cover" />
                    <img src={`/images/valorant/agents/${agents[element.allPlayersStats[puuid].agent]}.png`} alt={element.allPlayersStats[puuid].agent} className="w-16 h-16 rounded-md object-contain" />
                    <img src={`/images/valorant/ranks/${element.allPlayersStats[puuid].rank.replace(" ", "_")}.png`} alt={element.allPlayersStats[puuid].rank} className="w-14 h-14 object-contain" />
                  </div>

                  <div className="flex flex-col items-center justify-center text-center w-32">
                    <div className="flex gap-2 text-lg">
                      <span className={`text-brand ${element.allPlayersStats[puuid].result === "Win" ? "font-bold" : ""}`} >
                        {element.allPlayersStats[puuid].roundsWon}
                      </span>
                      <span className="text-white">:</span>
                      <span className={`text-accent ${element.allPlayersStats[puuid].result === "Loss" ? "font-bold" : ""}`} >
                        {element.allPlayersStats[puuid].roundsLost}
                      </span>
                    </div>
                    <h2 className="text-white">{element.gamemode}</h2>
                  </div>
                </div>

                {/* Base Player Stats */}
                {headers.map((header) => (
                  <div key={header} className="flex-1 text-center font-bold">
                    {statFormatters[header] ? statFormatters[header](element.allPlayersStats[puuid][statKeyMap[header]]) : element.allPlayersStats[puuid][statKeyMap[header]]}
                  </div>
                ))}
              </div>

              {/* Expanded Stat Rows */}
              {expanded[rowKey] && (
                <div>
                  {["Red", "Blue"].map((team) => {
                    const teamEntries = Object.entries(element.allPlayersStats).filter(([_, entry]) => entry.team === team).sort(([_, a], [__, b]) => b.rating - a.rating);

                    if (teamEntries.length === 0) return null;
                    
                    const gradientColor = element.allPlayersStats[puuid].result === "Win" ? "from-brand/45" : element.allPlayersStats[puuid].result === "Loss" ? "from-accent/45" : "from-white/45";

                    return (
                      <div key={team}>
                        {/* Team header row */}
                        <div className={`relative flex items-center text-white border-b border-l border-r border-element-lighter py-1 ${rowIndex++ % 2 === 0 ? "bg-element" : "bg-element-dark"}`} >
                          <div className={`absolute top-0 left-0 bottom-0 w-8 bg-gradient-to-r ${gradientColor} to-transparent z-10`} />
                          <div className="w-8" />
                          <div className="basis-2/6 px-2"></div>
                          {headers.map((header) => (
                            <div key={header} className="group relative flex-1 text-offwhite text-center" >
                              {header}
                              {headerTooltips[header] && (
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-xs px-2 py-1 font-normal text-white bg-element-dark rounded border border-element-lighter shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                  {headerTooltips[header]}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>

                        {/* Team player rows */}
                        {teamEntries.map(([key, entry]) => (
                          <div key={key} className={`relative flex items-center py-1 border-b border-l border-r border-element-lighter ${ rowIndex++ % 2 === 0 ? "bg-element" : "bg-element-dark" }`} >
                            <div className={`absolute top-0 left-0 bottom-0 w-8 bg-gradient-to-r ${gradientColor} to-transparent z-10`} />
                            <div className="w-8" />
                            <div className="basis-2/6">
                              <div className="flex flex-shrink-0 items-center gap-2 px-2">
                                <img src={`/images/valorant/agents/${agents[entry.agent]}.png`} alt={entry.agent} className="w-12 h-12 rounded-md object-contain" />
                                <img src={`/images/valorant/ranks/${entry.rank.replace(" ", "_")}.png`} alt={entry.rank} className="w-10 h-10 rounded-md object-contain" />
                                <Link
                                  to={`/playerprofile/${entry.name.slice(0, entry.name.lastIndexOf("#"))}_${entry.name.slice(entry.name.lastIndexOf("#")) + 1}`}
                                  className="text-white no-underline hover:no-underline focus:no-underline"
                                >
                                  {entry.name}
                                </Link>
                              </div>
                            </div>
                            {headers.map((header) => (
                              <div key={header} className="flex-1 text-center">
                                {statFormatters[header] ? statFormatters[header](entry[statKeyMap[header]]) : entry[statKeyMap[header]]}
                              </div>
                            ))}
                          </div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );

        });

      })()}
    </div>
  );

}
