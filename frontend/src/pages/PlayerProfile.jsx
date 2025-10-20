import { useEffect, useState } from "react";

import { useUser } from "../contexts/UserContext";
import { fetchWithRetry } from "../utils/fetchWithRetry";

import MultiSelect from "../components/MultiSelect";
import GamesList from "../components/GamesList";

function PlayerProfile() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const { userinfo, fetchUserinfo } = useUser();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.title = 'Profile - valocity';

    updateMatchHistory();
  }, []);

  async function updateMatchHistory() {
    try {
      setLoading(true);
      console.log("puuid: ", userinfo.puuid);
      const responseData = await fetchWithRetry(`${BASE_URL}/riot/player_matches?puuid=${userinfo.puuid}&gamemode=${"Competitive"}&count=${5}&offset=${data.length}`, {
        credentials: "include"
      });

      setData(prev => [...prev, ...responseData]);
      console.log("Match History: ", responseData);
    } catch (error) {
      console.error("Failed to fetch match history: ", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <h2 className="text-4xl font-bold text-white mb-4">
          {userinfo
            ? `${userinfo.gameName ?? "Unknown"}${userinfo.tagLine ? " #" + userinfo.tagLine : ""}`
            : "Log in to see your Profile."}
        </h2>
      </div>

      <div>
        {data.length === 0 ? (
          loading ? (
            <div className="flex flex-col items-center space-y-8">
              <h2 className="text-4xl font-bold text-accent mb-4">Loading Matches...</h2>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-8">
              <h2 className="text-4xl font-bold text-accent mb-4">No Matches found. Try logging in.</h2>
            </div>
          )
        ) : (
          <div className="flex flex-col items-center space-y-8">
            <GamesList data={data} puuid={userinfo.puuid} />

            <button
              onClick={updateMatchHistory}
              disabled={loading}
              className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center disabled:opacity-50"
            >
              {loading ? "Loading..." : "Load More"}
            </button>
          </div>
        )}
      </div>

    </div>
  );
}

export default PlayerProfile;