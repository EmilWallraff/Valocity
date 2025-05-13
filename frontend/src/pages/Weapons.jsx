import { useEffect } from 'react';

import ImageSelect from "../components/ImageSelect";
import WeaponsList from "../components/WeaponsList";

function Weapons() {
    useEffect(() => {
      document.title = 'Weapons - valocity.gg';
    }, []);

    return (
      <div className="min-h-screen p-6 bg-darkness text-white">
        <h2 className="text-3xl font-bold text-brand mb-4">Weapons</h2>
        <p className="">User data will show here soon.</p>
        <div className="">
          <WeaponsList />
        </div>
      </div>
    );
  }
  
  export default Weapons;
  