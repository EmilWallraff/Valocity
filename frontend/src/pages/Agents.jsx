import { useEffect, useState } from "react";

import MultiSelect from "../components/MultiSelect";
import StatsList from "../components/StatsList";
import { fetchWithRetry } from "../utils/fetchWithRetry";
import { mapOptions } from "../data/imageSelectSets";
import { agentOptions } from "../data/imageSelectSets";
import { rankOptions } from "../data/imageSelectSets";

const headers = [
  "Agent",
  "Pick%",
  "Win%",
  "Rating",
  "K/R",
  "A/R",
  "KAST%",
  "USE%",
];

const headerTooltips = {
  "Pick%": "Percentage of teams where one player picked the agent",
  "Win%": "Wins per non-drawn matches against a team without the agent",
  "Rating": "Average overall rating (with 1.0 being an average performance)",
  "K/R": "Kills per round",
  "A/R": "Assists per round",
  "KAST%": "Average percentage of rounds with kill, assist, survival or trade",
  "USE%": "Average percentage of contribution to team's engagements (weighted)"
};

function Agents() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const [data, setData] = useState(null);
  const [filteredAgents, setFiltereAgents] = useState(() => 
    agentOptions.map(agentOption => agentOption.label)
  );
  const [filteredMaps, setFilteredMaps] = useState(() => 
    mapOptions.map(mapOption => mapOption.label)
  );
  const [filteredRanks, setFilteredRanks] = useState(() => 
    rankOptions.map(rankOption => rankOption.label)
  );
  
  useEffect(() => {
    document.title = 'Agents - valocity';

    updateAgentValues();
  }, [filteredAgents, filteredMaps, filteredRanks]);

  async function updateAgentValues() {
    try {
      const responseData = await fetchWithRetry(`${BASE_URL}/agents`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          agents: filteredAgents,
          maps: filteredMaps,
          ranks: filteredRanks
        }),
      });

      setData(responseData);
    } catch (error) {
      console.error("Failed to fetch agent stats: ", error);
    }
  }

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <h2 className="text-4xl font-bold text-white mb-4">Stats for each Agent</h2>

        <div className="flex flex-row gap-4">
          <MultiSelect items={agentOptions} label="Filter Agents" sizeClass="w-44 h-20" onChange={(selected) => { setFiltereAgents(selected); updateAgentValues(); }} />
          <MultiSelect items={mapOptions} label="Filter Maps" sizeClass="w-44 h-20" fillUp="true" onChange={(selected) => { setFilteredMaps(selected); updateAgentValues(); }} />
          <MultiSelect items={rankOptions} label="Filter Ranks" sizeClass="w-44 h-20" fillUp="true" onChange={(selected) => { setFilteredRanks(selected); updateAgentValues(); }} />
        </div>
      </div>

      <div className="">
        {!data ? (
          <div className="flex flex-col items-center space-y-8">
            <h2 className="text-4xl font-bold text-accent mb-4">Loading Data...</h2>
          </div>
        ) : (
          <div>
            <StatsList data={data} headers={headers} defaultHeader={"Win%"} headerTooltips={headerTooltips} imageType={"agents"} />
          </div>
        )}
      </div>
    </div>
  );
}

export default Agents;