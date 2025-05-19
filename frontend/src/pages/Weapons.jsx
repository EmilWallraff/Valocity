import { useEffect, useState } from "react";

import MultiSelect from "../components/MultiSelect";
import WeaponsList from "../components/WeaponsList";
import { weaponOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";
import { agentOptions } from "../data/imageSelectSets";

function Weapons() {
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
      document.title = 'Weapons - valocity.gg';

      updateWeaponValues()
    }, []);

    useEffect(() => {
      updateWeaponValues();
    }, [filteredWeapons, filteredMaps, filteredAgents]);

    async function updateWeaponValues() {
      const response = await fetch("http://localhost:8000/weapons", {
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

      if (!response.ok) {
        throw new Error("Failed to fetch weapon stats");
      }
    
      const responseData = await response.json();
      setData(responseData);
      console.log("Weapon Data:", data);
    }

    return (
      <div className="min-h-screen p-6 bg-darkness text-white">
        <h2 className="text-3xl font-bold text-brand mb-4">Weapons</h2>
        <div className="flex flex-col items-center space-y-4">
          <button onClick={() => updateWeaponValues()}>Update</button>
          <MultiSelect items={weaponOptions} label="Filter Weapons" sizeClass="w-44 h-20" onChange={(selected) => (setFilteredWeapons(selected))} />
          <MultiSelect items={mapOptions} label="Filter Maps" sizeClass="w-44 h-20" fillUp="true" onChange={(selected) => (setFilteredMaps(selected))} />
          <MultiSelect items={agentOptions} label="Filter Agents" sizeClass="w-44 h-20" onChange={(selected) => (setFiltereAgents(selected))} />
        </div>
        <p className="">User data will show here soon.</p>
        <div className="">
          {!data ? (
            <p>Loading weapon data...</p>
          ) : (
            <div>
              <WeaponsList data={data} />
            </div>
          )}
        </div>
      </div>
    );
  }
  
  export default Weapons;