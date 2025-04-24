import { useEffect, useState } from "react";

import ImageSelect from "../components/ImageSelect";
import { agentOptions } from "../data/imageSelectSets";
import { weaponOptions } from "../data/imageSelectSets";
import { armorOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";

function WinProbability() {
  const [isAttackers, setIsAttackers] = useState(true);
  const defaultAgents = ["Brimstone", "Sova", "Sage", "Jett", "Phoenix"];

  useEffect(() => {
    document.title = 'Win Probability - valocity.gg';
  }, []);

  return (
    <div className="bg-darkness flex flex-col items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <h2 className="text-4xl font-bold text-white mb-4">Calculate the average Round Win Probability!</h2>

        <div className="flex flex-row gap-4">
          <button
            onClick={() => setIsAttackers(prev => !prev)}
            className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition font-semibold text-lg flex items-center justify-center"
          >
            Switch Sides
          </button>

          <ImageSelect items={mapOptions} sizeClass="w-60 h-20" fillUp="true" defaultLabel="Ascent" />

          <button
            className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition font-semibold text-lg flex items-center justify-center"
          >
            Calculate
          </button>
        </div>
      </div>

      <div className="w-full flex flex-col items-center space-y-4">
        <h3 className={`text-2xl font-semibold text-${isAttackers ? "accent" : "brand"}`}>{isAttackers ? "Attackers" : "Defenders"}</h3>
        <div className="flex flex-row flex-wrap justify-center gap-12">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={`row1-${i}`} className="flex flex-col items-center space-y-4">
              <div className="flex flex-row gap-4">
                <ImageSelect items={agentOptions} sizeClass="w-20 h-20" defaultLabel={defaultAgents[i]} />
                <ImageSelect items={armorOptions} sizeClass="w-20 h-20" defaultLabel="Heavy Armor" />
              </div>
              <ImageSelect items={weaponOptions} sizeClass="w-44 h-20" defaultLabel="Vandal" />
            </div>
          ))}
        </div>
      </div> 

      <div className="w-full flex flex-col items-center space-y-4">
        <h3 className={`text-2xl font-semibold text-${isAttackers ? "brand" : "accent"}`}>{isAttackers ? "Defenders" : "Attackers"}</h3>
        <div className="flex flex-row flex-wrap justify-center gap-12">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={`row2-${i}`} className="flex flex-col items-center space-y-4">
              <div className="flex flex-row gap-4">
                <ImageSelect items={agentOptions} sizeClass="w-20 h-20" defaultLabel={defaultAgents[i]} />
                <ImageSelect items={armorOptions} sizeClass="w-20 h-20" defaultLabel="Heavy Armor" />
              </div>
              <ImageSelect items={weaponOptions} sizeClass="w-44 h-20" defaultLabel="Phantom" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default WinProbability;
