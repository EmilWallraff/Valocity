import { useEffect, useState } from "react";

import MultiSelect from "../components/MultiSelect";
import WeaponsList from "../components/WeaponsList";
import { mapOptions } from "../data/imageSelectSets";
import { agentOptions } from "../data/imageSelectSets";

const headers = [
  "Agent",
  "Pick%",
  "Win%",
  "K/D",
  "Kills/Round",
  "Damage/Round",
];

function Agents() {
  const [data, setData] = useState(null);
  const [filteredAgents, setFiltereAgents] = useState(() => 
    agentOptions.map(agentOption => agentOption.label)
  );
  const [filteredMaps, setFilteredMaps] = useState(() => 
    mapOptions.map(mapOption => mapOption.label)
  );

    useEffect(() => {
      document.title = 'Agents - valocity.gg';

      updateAgentValues()
    }, []);

    useEffect(() => {
      updateAgentValues();
    }, [filteredAgents, filteredMaps]);

    async function updateAgentValues() {
      const response = await fetch("http://localhost:8000/agents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          agents: filteredAgents,
          maps: filteredMaps
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch agent stats");
      }
    
      const responseData = await response.json();
      setData(responseData);
      console.log("Agent Data:", data);
    }

    return (
      <div className="bg-darkness items-center pt-16 p-6 space-y-16">
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">Stats for each Agent</h2>

          <div className="flex flex-row gap-4">
            <MultiSelect items={agentOptions} label="Filter Agents" sizeClass="w-44 h-20" onChange={(selected) => (setFiltereAgents(selected))} />
            <MultiSelect items={mapOptions} label="Filter Maps" sizeClass="w-44 h-20" fillUp="true" onChange={(selected) => (setFilteredMaps(selected))} />
          </div>
        </div>

        <div className="">
          {!data ? (
            <div className="flex flex-col items-center space-y-8">
              <h2 className="text-4xl font-bold text-accent mb-4">Loading Data...</h2>
            </div>
          ) : (
            <div>
              <WeaponsList data={data} headers={headers} />
            </div>
          )}
        </div>
      </div>
    );
  }
  
  export default Agents;