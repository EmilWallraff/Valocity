import { useEffect } from 'react';

import ImageSelect from "../components/ImageSelect";
import { agentOptions } from "../data/imageSelectSets";
import { weaponOptions } from "../data/imageSelectSets";
import { armorOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";

function WinProbability() {
    useEffect(() => {
      document.title = 'Win Probability Calculator - valocity.gg';
    }, []);

    return (
      <div className="min-h-screen p-6 bg-darkness text-white">
        <h2 className="text-3xl font-bold text-brand mb-4">Win Probability Calculator</h2>
        <p className="">Data will show here soon.</p>
        <ImageSelect items={agentOptions} sizeClass="w-20 h-20" defaultLabel = "Jett" />
        <ImageSelect items={weaponOptions} sizeClass="w-60 h-20" defaultLabel = "Vandal" />
        <ImageSelect items={armorOptions} defaultLabel = "Heavy Armor" />
        <ImageSelect items={mapOptions} />
      </div>
    );
  }
  
  export default WinProbability;