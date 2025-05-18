import { useEffect, useState } from "react";

import ImageSelect from "../components/ImageSelect";
import MultiSelect from "../components/MultiSelect";
import WeaponsList from "../components/WeaponsList";
import { agentOptions } from "../data/imageSelectSets";
import { weaponOptions } from "../data/imageSelectSets";
import { armorOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";

function Weapons() {
  const [data, setData] = useState(null);

    useEffect(() => {
      document.title = 'Weapons - valocity.gg';

      fetch("http://localhost:8000/weapons")
        .then(res => res.json())
        .then(data => setData(data))
        .catch(err => console.error("Error fetching weapons:", err));
    }, []);

    return (
      <div className="min-h-screen p-6 bg-darkness text-white">
        <h2 className="text-3xl font-bold text-brand mb-4">Weapons</h2>
        <div className="flex flex-col items-center space-y-4">
          <ImageSelect items={weaponOptions} sizeClass="w-44 h-20" defaultLabel="Frenzy" />
          <MultiSelect items={weaponOptions} defaultSelected={weaponOptions} />
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