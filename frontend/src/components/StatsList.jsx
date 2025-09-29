import React, { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

import { agents } from "../data/hashcodes";
import { weapons } from "../data/hashcodes";
import { armors } from "../data/hashcodes";
import { maps } from "../data/hashcodes"; 

const statKeyMap = {
  "K/R": "kills",
  "Dmg/R": "damage",
  "Win%": "win",
  "HS%": "headshot",
  "Pick%": "pick",
  "K/D": "kd"
};

export default function StatsList({ data, headers = [], defaultHeader, headerTooltips = {}, imageType }) {
  const [expanded, setExpanded] = useState({});
  const [sortKey, setSortKey] = useState(statKeyMap[defaultHeader] || "damage");
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
        <div className="flex-2 flex items-center gap-2 basis-2/6">{headers[0]}</div>
        {headers.slice(1).map((header) => (
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
            {Array.isArray(element.subentries) && element.subentries.length > 0 ? (
              <div
                onClick={() => toggleExpand(element.id)}
                className="w-8 cursor-pointer flex justify-center"
              >
                {expanded[element.id] ? <ChevronDown /> : <ChevronRight />}
              </div>
            ) : (
              <div className="w-8" />
            )}
            <div className="flex items-center gap-2 h-16 basis-2/6">
              <div className="w-32 h-16 flex items-center justify-center overflow-hidden flex-shrink-0">
                <img
                  src={`/images/valorant/${
                    {
                      agents: 'agents/' + agents[element.name],
                      weapons: 'weapons/' + weapons[element.name] + '_killstream',
                      armors: 'armors/' + armors[element.name],
                      maps: 'maps/' + maps[element.name] + '_listview',
                    }[imageType]
                  }.png`}
                  alt={element.name}
                  className="max-w-full max-h-full object-contain"
                />
              </div>
              <span className="truncate">{element.name}</span>
            </div>

            {headers.map((header, index) => {
              if (index === 0) return null;

              return (
                <div className="flex-1 text-center">
                  {header.includes("%")
                    ? element.stats[statKeyMap[header]] != null
                      ? (element.stats[statKeyMap[header]] * 100).toFixed(0) + "%"
                      : "-"
                    : element.stats[statKeyMap[header]] != null
                      ? element.stats[statKeyMap[header]].toFixed(2)
                      : "-"}
                </div>
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
                      <div className="flex-1 text-center">
                        {header.includes("%")
                          ? entry[statKeyMap[header]] != null
                            ? (entry[statKeyMap[header]] * 100).toFixed(0) + "%"
                            : "-"
                          : entry[statKeyMap[header]] != null
                            ? entry[statKeyMap[header]].toFixed(2)
                            : "-"}
                      </div>
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
