import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import { fetchWithRetry } from "../utils/fetchWithRetry";

import MultiSelect from "../components/MultiSelect";
import GamesList from "../components/GamesList";
import { gamemodeOptions } from "../data/imageSelectSets";

function PlayerProfile() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const storageKey = "recentProfiles";
  const [playerinfo, setPlayerinfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [data, setData] = useState([]);
  const [filteredGamemodes, setFilteredGamemodes] = useState(["Competitive"]);

  const { playername } = useParams();
  const [gameName, tagLine] = playername.split(/[-_]/);

  useEffect(() => {
    document.title = 'Profile - valocity';

    setPlayerinfo(null);
    setLoading(true);
    setLoadingMatches(false);
    setData([]);
    setFilteredGamemodes(["Competitive"])

    fetchPlayer();
  }, [gameName, tagLine]);

  const fetchPlayer = async () => {
    try {
      const res = await fetch(`${BASE_URL}/riot/player_by_riot_id?gameName=${encodeURIComponent(gameName)}&tagLine=${encodeURIComponent(tagLine)}`, { credentials: "include" });

      if (!res.ok) {
        setLoading(false);
        return;
      }

      const data = await res.json();
      setPlayerinfo(data || null);
      if (data && data.status === "public") {
        updateMatchHistory(data, filteredGamemodes, false);

        const newEntry = {
          gamename: data.gameName,
          tagline: data.tagLine,
          timestamp: Date.now(),
        };
        const stored = JSON.parse(localStorage.getItem(storageKey)) || [];
        const filtered = stored.filter(
          (p) => !(p.gamename === newEntry.gamename && p.tagline === newEntry.tagline)
        );
        const updated = [newEntry, ...filtered];
        localStorage.setItem(storageKey, JSON.stringify(updated));
      }
      setLoading(false);
    } catch (error) {
      console.log("Error fetching user:", error);
      setLoading(false);
    }
  };

  async function updateMatchHistory(playerInfo, gameModes, expand) {
    try {
      setLoadingMatches(true);

      const offset = expand ? data.length : 0;
      const responseData = await fetchWithRetry(`${BASE_URL}/riot/player_matches?puuid=${playerInfo.puuid}&count=${5}&offset=${offset}&gamemodes=${gameModes}`, { credentials: "include" });

      setData(prev => [...prev, ...responseData]);
    } catch (error) {
      console.error("Failed to fetch match history: ", error);
    } finally {
      setLoadingMatches(false);
    }
  }

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      {loading ? (
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">Loading Profile...</h2>
        </div>
      ) : playerinfo && playerinfo.status === "public" ? (
        <>
          <div className="flex flex-col items-center space-y-8">
            <h2 className="text-4xl font-bold text-white mb-4">
              {playerinfo
                ? `${playerinfo.gameName ?? "Unknown"}${playerinfo.tagLine ? " #" + playerinfo.tagLine : ""}`
                : "Unknown"}
            </h2>

            <div className="flex flex-row gap-4">
              <MultiSelect items={gamemodeOptions} label="Filter Gamemodes" sizeClass="w-60 h-20" defaultSelected={filteredGamemodes} onChange={(selected) => { console.log("called multiselect"); setFilteredGamemodes(selected); updateMatchHistory(playerinfo, selected, false); }} />
            </div>
          </div>

          <div>
            {data.length === 0 ? (
              loadingMatches ? (
                <div className="flex flex-col items-center space-y-8">
                  <h2 className="text-4xl font-bold text-accent mb-4">Loading Matches...</h2>
                </div>
              ) : (
                <div className="flex flex-col items-center space-y-8">
                  <h2 className="text-4xl font-bold text-accent mb-4">No Matches found.</h2>
                </div>
              )
            ) : (
              <div className="flex flex-col items-center space-y-8">
                <GamesList data={data} puuid={playerinfo.puuid} />

                <button
                  onClick={() => updateMatchHistory(playerinfo, filteredGamemodes, true)}
                  disabled={loadingMatches}
                  className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center disabled:opacity-50"
                >
                  {loadingMatches ? "Loading..." : "Load More"}
                </button>
              </div>
            )}
          </div>
        </>
      ) : playerinfo && playerinfo.status === "private" ? (
        <>
          <div className="flex flex-col items-center space-y-8">
            <h2 className="text-4xl font-bold text-white mb-4">
              {playerinfo
                ? `${playerinfo.gameName ?? "Unknown"}${playerinfo.tagLine ? " #" + playerinfo.tagLine : ""}`
                : "Unknown"}
            </h2>
          </div>

          <div className="flex flex-col items-center space-y-8">
            <h2 className="text-2xl text-white text-center max-w-3xl">This profile is private. If it is your account, you can view your stats by logging in with your Riot account.</h2>

            <Link
              key="/login"
              to="/login"
              className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
            >
              Login
            </Link>
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">404: Profile not found</h2>
        </div>
      )}

    </div>
  );
}

export default PlayerProfile;