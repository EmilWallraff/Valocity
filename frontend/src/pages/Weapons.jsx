import { useEffect, useState } from "react";

import ImageSelect from "../components/ImageSelect";
import WeaponsList from "../components/WeaponsList";

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