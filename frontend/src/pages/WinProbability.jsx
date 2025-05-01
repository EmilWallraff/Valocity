import { useEffect, useState } from "react";

import ImageSelect from "../components/ImageSelect";
import { agentOptions } from "../data/imageSelectSets";
import { weaponOptions } from "../data/imageSelectSets";
import { armorOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";

function WinProbability() {
  const [isAttackers, setIsAttackers] = useState(true);
  const [map, setMap] = useState("Ascent");
  const [playersRed, setPlayersRed] = useState([
    { agent: "Brimstone", armor: "Heavy Armor", weapon: "Vandal" },
    { agent: "Sova", armor: "Heavy Armor", weapon: "Vandal" },
    { agent: "Sage", armor: "Heavy Armor", weapon: "Vandal" },
    { agent: "Jett", armor: "Heavy Armor", weapon: "Vandal" },
    { agent: "Phoenix", armor: "Heavy Armor", weapon: "Vandal" }
  ]);
  const [playersBlue, setPlayersBlue] = useState([
    { agent: "Brimstone", armor: "Heavy Armor", weapon: "Phantom" },
    { agent: "Sova", armor: "Heavy Armor", weapon: "Phantom" },
    { agent: "Sage", armor: "Heavy Armor", weapon: "Phantom" },
    { agent: "Jett", armor: "Heavy Armor", weapon: "Phantom" },
    { agent: "Phoenix", armor: "Heavy Armor", weapon: "Phantom" }
  ]);
  const [blueProbability, setBlueProbability] = useState(0.0);
  const [redProbability, setRedProbability] = useState(0.0);
  const [probabilityState, setProbabilityState] = useState("Outdated");

  useEffect(() => {
    document.title = 'Win Probability - valocity.gg';
  }, []);

  async function predictWinProbability() {
    const response = await fetch("http://localhost:8000/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        attacker_team: isAttackers ? "RED" : "BLUE",
        map: map,
        RED_1_agent: playersRed[0]["agent"],
        RED_1_weapon: playersRed[0]["weapon"],
        RED_1_armor: playersRed[0]["armor"],
        RED_2_agent: playersRed[1]["agent"],
        RED_2_weapon: playersRed[1]["weapon"],
        RED_2_armor: playersRed[1]["armor"],
        RED_3_agent: playersRed[2]["agent"],
        RED_3_weapon: playersRed[2]["weapon"],
        RED_3_armor: playersRed[2]["armor"],
        RED_4_agent: playersRed[3]["agent"],
        RED_4_weapon: playersRed[3]["weapon"],
        RED_4_armor: playersRed[3]["armor"],
        RED_5_agent: playersRed[4]["agent"],
        RED_5_weapon: playersRed[4]["weapon"],
        RED_5_armor: playersRed[4]["armor"],
        BLUE_1_agent: playersBlue[0]["agent"],
        BLUE_1_weapon: playersBlue[0]["weapon"],
        BLUE_1_armor: playersBlue[0]["armor"],
        BLUE_2_agent: playersBlue[1]["agent"],
        BLUE_2_weapon: playersBlue[1]["weapon"],
        BLUE_2_armor: playersBlue[1]["armor"],
        BLUE_3_agent: playersBlue[2]["agent"],
        BLUE_3_weapon: playersBlue[2]["weapon"],
        BLUE_3_armor: playersBlue[2]["armor"],
        BLUE_4_agent: playersBlue[3]["agent"],
        BLUE_4_weapon: playersBlue[3]["weapon"],
        BLUE_4_armor: playersBlue[3]["armor"],
        BLUE_5_agent: playersBlue[4]["agent"],
        BLUE_5_weapon: playersBlue[4]["weapon"],
        BLUE_5_armor: playersBlue[4]["armor"]
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch prediction");
    }
  
    const responseData = await response.json();
    setBlueProbability((responseData.BLUE * 100).toFixed(2));
    setRedProbability((responseData.RED * 100).toFixed(2));
    setProbabilityState("Updated");
    console.log("Win Probability:", redProbability, blueProbability);
  }

  function updatePlayer(index, team, field, value) {
    if (team == "RED")
    {
      setPlayersRed(prev => {
        const updated = [...prev];
        updated[index][field] = value;
        return updated;
      });
    } else if (team == "BLUE")
    {
      setPlayersBlue(prev => {
        const updated = [...prev];
        updated[index][field] = value;
        return updated;
      });
    }
    setProbabilityState("Outdated");
  }
 
  return (
    <div className="bg-darkness flex flex-col items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <h2 className="text-4xl font-bold text-white mb-4">Calculate the average Round Win Probability!</h2>

        <div className="flex flex-row gap-4">
          <button
            onClick={() => (setIsAttackers(prev => !prev), setProbabilityState("Outdated"))}
            className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition font-semibold text-lg flex items-center justify-center"
          >
            Switch Sides
          </button>

          <ImageSelect items={mapOptions} sizeClass="w-60 h-20" fillUp="true" defaultLabel={map} onChange={(selected) => (setMap(selected), setProbabilityState("Outdated"))} />

          <button
            onClick={() => predictWinProbability()}
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
                <ImageSelect items={agentOptions} sizeClass="w-20 h-20" defaultLabel={playersRed[i]["agent"]} onChange={(selected) => updatePlayer(i, "RED", "agent", selected)} />
                <ImageSelect items={armorOptions} sizeClass="w-20 h-20" defaultLabel={playersRed[i]["armor"]} onChange={(selected) => updatePlayer(i, "RED", "armor", selected)} />
              </div>
              <ImageSelect items={weaponOptions} sizeClass="w-44 h-20" defaultLabel={playersRed[i]["weapon"]} onChange={(selected) => updatePlayer(i, "RED", "weapon", selected)} />
            </div>
          ))}
        </div>
        <h3 className={`text-2xl font-semibold text-${probabilityState == "Updated" ? "white" : "element-lighter"}`}>{(redProbability == 0.0 && blueProbability == 0.0) ? '\u00A0' : `Win Probability: ${redProbability}%`}</h3>
      </div>

      <div className="w-full flex flex-col items-center space-y-4">
        <h3 className={`text-2xl font-semibold text-${isAttackers ? "brand" : "accent"}`}>{isAttackers ? "Defenders" : "Attackers"}</h3>
        <div className="flex flex-row flex-wrap justify-center gap-12">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={`row2-${i}`} className="flex flex-col items-center space-y-4">
              <div className="flex flex-row gap-4">
                <ImageSelect items={agentOptions} sizeClass="w-20 h-20" defaultLabel={playersBlue[i]["agent"]} onChange={(selected) => updatePlayer(i, "BLUE", "agent", selected)} />
                <ImageSelect items={armorOptions} sizeClass="w-20 h-20" defaultLabel={playersBlue[i]["armor"]} onChange={(selected) => updatePlayer(i, "BLUE", "armor", selected)} />
              </div>
              <ImageSelect items={weaponOptions} sizeClass="w-44 h-20" defaultLabel={playersBlue[i]["weapon"]} onChange={(selected) => updatePlayer(i, "BLUE", "weapon", selected)} />
            </div>
          ))}
        </div>
        <h3 className={`text-2xl font-semibold text-${probabilityState == "Updated" ? "white" : "element-lighter"}`}>{(redProbability == 0.0 && blueProbability == 0.0) ? '\u00A0' : `Win Probability: ${blueProbability}%`}</h3>
      </div>
    </div>
  );
}

export default WinProbability;
