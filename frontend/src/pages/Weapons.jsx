import { useEffect, useState } from "react";

import MultiSelect from "../components/MultiSelect";
import StatsList from "../components/StatsList";
import { fetchWithRetry } from "../utils/fetchWithRetry";
import { weaponOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";
import { agentOptions } from "../data/imageSelectSets";

const headers = [
  "Weapon",
  "Dmg/R",
  "K/R",
  "Win%",
  "HS%"
];

const headerTooltips = {
  "Dmg/R": "Damage per round",
  "K/R": "Kills per round",
  "Win%": "Percentage of rounds won when starting with the weapon as main weapon",
  "HS%": "Headshots per hits on enemy agents"
};

function Weapons() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const [data, setData] = useState(null);
  const [filteredWeapons, setFilteredWeapons] = useState(() => 
    weaponOptions.map(weaponOption => weaponOption.label)
  );
  const [filteredMaps, setFilteredMaps] = useState(() => 
    mapOptions.map(mapOption => mapOption.label)
  );
  const [filteredAgents, setFiltereAgents] = useState(() => 
    agentOptions.map(agentOption => agentOption.label)
  );

    useEffect(() => {
      document.title = 'Weapons - valocity';

      updateWeaponValues()
    }, [filteredWeapons, filteredMaps, filteredAgents]);

    async function updateWeaponValues() {
      try {
        const responseData = await fetchWithRetry(`${BASE_URL}/weapons`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            weapons: filteredWeapons,
            maps: filteredMaps,
            agents: filteredAgents
          }),
        });

        setData(responseData);
        console.log("Weapon Data: ", responseData);
      } catch (error) {
        console.error("Failed to fetch weapon stats: ", error);
      }
    }

    return (
      <div className="bg-darkness items-center pt-16 p-6 space-y-16">
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">Stats when Starting the Round with each Weapon</h2>

          <div className="flex flex-row gap-4">
            <MultiSelect items={weaponOptions} label="Filter Weapons" sizeClass="w-44 h-20" onChange={(selected) => (setFilteredWeapons(selected))} />
            <MultiSelect items={mapOptions} label="Filter Maps" sizeClass="w-44 h-20" fillUp="true" onChange={(selected) => (setFilteredMaps(selected))} />
            <MultiSelect items={agentOptions} label="Filter Agents" sizeClass="w-44 h-20" onChange={(selected) => (setFiltereAgents(selected))} />
          </div>
        </div>

        <div className="">
          {!data ? (
            <div className="flex flex-col items-center space-y-8">
              <h2 className="text-4xl font-bold text-accent mb-4">Loading Data...</h2>
            </div>
          ) : (
            <div>
              <StatsList data={data} headers={headers} defaultHeader={"Dmg/R"} headerTooltips={headerTooltips} imageType={"weapons"} />
            </div>
          )}
        </div>
      </div>
    );
  }
  
  export default Weapons;