import { useEffect, useState } from "react";

import ImageSelect from "../components/ImageSelect";
import { fetchWithRetry } from "../utils/fetchWithRetry";
import { agentOptions } from "../data/imageSelectSets";
import { weaponOptions } from "../data/imageSelectSets";
import { armorOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";

function WinProbability() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
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
    document.title = 'Win Probability - valocity';
  }, []);

  async function predictWinProbability() {
    try {
      const responseData = await fetchWithRetry(`${BASE_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          map: map,
          attack_1_agent: isAttackers ? playersRed[0]["agent"] : playersBlue[0]["agent"],
          attack_1_weapon: isAttackers ? playersRed[0]["weapon"] : playersBlue[0]["weapon"],
          attack_1_armor: isAttackers ? playersRed[0]["armor"] : playersBlue[0]["armor"],
          attack_2_agent: isAttackers ? playersRed[1]["agent"] : playersBlue[1]["agent"],
          attack_2_weapon: isAttackers ? playersRed[1]["weapon"] : playersBlue[1]["weapon"],
          attack_2_armor: isAttackers ? playersRed[1]["armor"] : playersBlue[1]["armor"],
          attack_3_agent: isAttackers ? playersRed[2]["agent"] : playersBlue[2]["agent"],
          attack_3_weapon: isAttackers ? playersRed[2]["weapon"] : playersBlue[2]["weapon"],
          attack_3_armor: isAttackers ? playersRed[2]["armor"] : playersBlue[2]["armor"],
          attack_4_agent: isAttackers ? playersRed[3]["agent"] : playersBlue[3]["agent"],
          attack_4_weapon: isAttackers ? playersRed[3]["weapon"] : playersBlue[3]["weapon"],
          attack_4_armor: isAttackers ? playersRed[3]["armor"] : playersBlue[3]["armor"],
          attack_5_agent: isAttackers ? playersRed[4]["agent"] : playersBlue[4]["agent"],
          attack_5_weapon: isAttackers ? playersRed[4]["weapon"] : playersBlue[4]["weapon"],
          attack_5_armor: isAttackers ? playersRed[4]["armor"] : playersBlue[4]["armor"],
          defense_1_agent: isAttackers ? playersBlue[0]["agent"] : playersRed[0]["agent"],
          defense_1_weapon: isAttackers ? playersBlue[0]["weapon"] : playersRed[0]["weapon"],
          defense_1_armor: isAttackers ? playersBlue[0]["armor"] : playersRed[0]["armor"],
          defense_2_agent: isAttackers ? playersBlue[1]["agent"] : playersRed[1]["agent"],
          defense_2_weapon: isAttackers ? playersBlue[1]["weapon"] : playersRed[1]["weapon"],
          defense_2_armor: isAttackers ? playersBlue[1]["armor"] : playersRed[1]["armor"],
          defense_3_agent: isAttackers ? playersBlue[2]["agent"] : playersRed[2]["agent"],
          defense_3_weapon: isAttackers ? playersBlue[2]["weapon"] : playersRed[2]["weapon"],
          defense_3_armor: isAttackers ? playersBlue[2]["armor"] : playersRed[2]["armor"],
          defense_4_agent: isAttackers ? playersBlue[3]["agent"] : playersRed[3]["agent"],
          defense_4_weapon: isAttackers ? playersBlue[3]["weapon"] : playersRed[3]["weapon"],
          defense_4_armor: isAttackers ? playersBlue[3]["armor"] : playersRed[3]["armor"],
          defense_5_agent: isAttackers ? playersBlue[4]["agent"] : playersRed[4]["agent"],
          defense_5_weapon: isAttackers ? playersBlue[4]["weapon"] : playersRed[4]["weapon"],
          defense_5_armor: isAttackers ? playersBlue[4]["armor"] : playersRed[4]["armor"]
        }),
      });

      setRedProbability(((isAttackers ? responseData.attacker : responseData.defender) * 100).toFixed(2));
      setBlueProbability(((isAttackers ? responseData.defender : responseData.attacker) * 100).toFixed(2));
      setProbabilityState("Updated");
    } catch (error) {
      console.error("Failed to fetch prediction: ", error);
    }
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
            className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
          >
            Switch Sides
          </button>

          <ImageSelect items={mapOptions} sizeClass="w-60 h-20" fillUp="true" defaultLabel={map} onChange={(selected) => (setMap(selected), setProbabilityState("Outdated"))} />

          <button
            onClick={() => predictWinProbability()}
            className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
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
