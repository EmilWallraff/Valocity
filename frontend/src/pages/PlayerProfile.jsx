import { useEffect, useState } from "react";

import { useUser } from "../contexts/UserContext";
import { fetchWithRetry } from "../utils/fetchWithRetry";

import MultiSelect from "../components/MultiSelect";
import GamesList from "../components/GamesList";

/*
const data = [
  {
    date: "14.09.2025",
    gamemode: "Competitive",
    map: "Haven",
    result: "Win",
    team_rounds: 13,
    opponent_rounds: 6,
    agent: "Sova",
    stats: { rating: 1.01, kills: 17, deaths: 16, assists: 7, damage: 130, kast: 0.68, use: 0.21, headshot: 0.30 },
    */
    /*
    subentries: [
      { name: "Pistol Round", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Eco (<1000$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Halfbuy (1000$-3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
      { name: "vs Fullbuy (>3500$)", kills: 3, damage: 1, win: 0, headshot: 1.20 },
    ],
    */
    /*
  },
  {
    date: "14.09.2025",
    gamemode: "Competitive",
    map: "Ascent",
    result: "Loss",
    team_rounds: 13,
    opponent_rounds: 15,
    agent: "Iso",
    stats: { rating: 1.12, kills: 0, deaths: 12, assists: 4, damage: 125, kast: 0.65, use: 0.23, headshot: 0.26 },
  },
  {
    date: "13.09.2025",
    gamemode: "Competitive",
    map: "Haven",
    result: "Draw",
    team_rounds: 15,
    opponent_rounds: 15,
    agent: "Waylay",
    stats: { rating: 1.00, kills: 16, deaths: 5, assists: 12, damage: 160, kast: 0.71, use: 0.24, headshot: 0.45 },
  },
  {
    date: "17.09.2022",
    gamemode: "Unrated",
    map: "Haven",
    result: "Loss",
    team_rounds: 6,
    opponent_rounds: 2,
    agent: "Sova",
    stats: { rating: 0.86, kills: 4, deaths: 0, assists: 0, damage: 134, kast: 0.82, use: 0.18, headshot: 0.21 },
  }
];
*/

function PlayerProfile() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const { userinfo, fetchUserinfo } = useUser();
  const [data, setData] = useState(null);

  useEffect(() => {
    document.title = 'Profile - valocity';

    updateMatchHistory();
  }, []);

  const getUserData = async () => {
    try {
      const res = await fetch(`${BASE_URL}/riot/matches?puuid=${userinfo.puuid}&gamemode=${"competitive"}&count=${2}`, { credentials: "include" });

      console.log("puuid: " + userinfo.puuid);

      if (!res.ok) {
        console.log("res not ok.");
        return;
      }

      const responseData = await res.json();

      if (responseData == null){
        console.log("res data is null.");
      } else {
        setData(responseData);
        console.log("received response data not equalling null!");
        console.log("res data: ", data);
        console.log("res data puuid: ", data[0].agent);
      }
    }
    catch (err)
    {
      console.log("error");
      console.error("Error fetching userinfo:", err);
    }
    finally
    {
      console.log("finished process");
    }
  };

  async function updateMatchHistory() {
    try {
      const responseData = await fetchWithRetry(`${BASE_URL}/riot/matches?puuid=${userinfo.puuid}&gamemode=${"competitive"}&count=${2}`, {
        credentials: "include"
      });

      setData(responseData);
      console.log("Match History: ", responseData);
    } catch (error) {
      console.error("Failed to fetch match history: ", error);
    }
  }

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">

      <div className="bg-darkness flex flex-col items-center pt-16 p-6 space-y-16">
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">Player Profiles are still work in progress.</h2>

          <h2 className="text-2xl text-white text-center max-w-3xl">Testy Test Text.</h2>
        </div>
      </div>

      <div className="">

        {!data ? (
          <div className="flex flex-col items-center space-y-8">
            <h2 className="text-4xl font-bold text-accent mb-4">Loading Data...</h2>
          </div>
        ) : (
          <div>
            {/* <GamesList data={data} headers={headers} headerTooltips={headerTooltips} /> */}
            <GamesList data={data} />
          </div>
        )}

        {/*
        <div>
          <GamesList data={data} />
        </div>
        */}

      </div>

    </div>
  );
}

export default PlayerProfile;