import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

import { fetchWithRetry } from "../utils/fetchWithRetry";

import SegmentedControl from "../components/SegmentedControl";
import MultiSelect from "../components/MultiSelect";
import GamesList from "../components/GamesList";
import StatsList from "../components/StatsList";
import { gamemodeOptions } from "../data/imageSelectSets";
import { mapOptions } from "../data/imageSelectSets";
import { agentOptions } from "../data/imageSelectSets";

const agentHeaders = [
  "Agent",
  "Pick%",
  "Win%",
  "Rating",
  "K/R",
  "A/R",
  "KAST%",
  "Usg%",
];

const agentHeaderTooltips = {
  "Pick%": "Percentage of games where the agent was picked",
  "Win%": "Wins per non-drawn matches against a team without the agent",
  "Rating": "Average overall rating (with 1.0 being an average performance)",
  "K/R": "Kills per round",
  "A/R": "Assists per round",
  "KAST%": "Average percentage of rounds with kill, assist, survival or trade",
  "Usg%": "Average percentage of contribution to team's engagements (weighted)"
};

const weaponHeaders = [
  "Weapon",
  "Dmg/R",
  "K/R",
  "Win%",
  "HS%"
];

const weaponHeaderTooltips = {
  "Dmg/R": "Damage per round",
  "K/R": "Kills per round",
  "Win%": "Percentage of rounds won when starting with the weapon as main weapon",
  "HS%": "Headshots per hits on enemy agents"
};

function PlayerProfile() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const storageKey = "recentProfiles";
  const [playerinfo, setPlayerinfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subPage, setSubPage] = useState("Matches");

  const [loadingMatches, setLoadingMatches] = useState(false);
  const [matches, setMatches] = useState([]);
  const [loadingStats, setLoadingStats] = useState(false);
  const [weaponStats, setWeaponStats] = useState(null);
  const [agentStats, setAgentStats] = useState(null);

  const [filteredGamemodes, setFilteredGamemodes] = useState(["Competitive"]);

  const { playername } = useParams();
  const [gameName, tagLine] = playername.split(/[-_]/);

  useEffect(() => {
    document.title = 'Profile - valocity';

    setPlayerinfo(null);
    setLoading(true);
    setSubPage("Matches");

    setLoadingMatches(false);
    setMatches([]);
    setLoadingStats(false);
    setWeaponStats(null);
    setAgentStats(null);

    setFilteredGamemodes(["Competitive"])

    fetchPlayer();
  }, [gameName, tagLine]);

  const fetchPlayer = async () => {
    try {
      const res = await fetch(`${BASE_URL}/player_by_riot_id?gameName=${encodeURIComponent(gameName)}&tagLine=${encodeURIComponent(tagLine)}`, { credentials: "include" });

      if (!res.ok) {
        setLoading(false);
        return;
      }

      const responseData = await res.json();
      setPlayerinfo(responseData || null);
      if (responseData && responseData.status === "public") {
        const newEntry = {
          gamename: responseData.gameName,
          tagline: responseData.tagLine,
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

  async function updateMatchHistory(gameModes, expand) {
    try {
      setLoadingMatches(true);

      const responseData = await fetchWithRetry(`${BASE_URL}/player_matches`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          puuid: playerinfo.puuid,
          count: 5,
          offset: expand ? matches.length : 0,
          gamemodes: gameModes
        }),
      });

      if (expand) {
        setMatches(prev => [...prev, ...responseData]);
      } else {
        setMatches(responseData);
      }
    } catch (error) {
      console.error("Failed to fetch match history: ", error);
    } finally {
      setLoadingMatches(false);
    }
  }

  async function updateStats(gameModes) {
    try {
      setLoadingStats(true);

      const responseData = await fetchWithRetry(`${BASE_URL}/player_stats`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          puuid: playerinfo.puuid,
          gamemodes: gameModes,
          maps: mapOptions.map(mapOption => mapOption.label),
          agents: agentOptions.map(agentOption => agentOption.label)
        }),
      });

      console.log("Stats request response: ", responseData);

      setAgentStats(responseData[0]);
      setWeaponStats(responseData[1]);
    } catch (error) {
      console.error("Failed to fetch player stats: ", error);
    } finally {
      setLoadingStats(false);
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
              <MultiSelect items={gamemodeOptions} label="Filter Gamemodes" sizeClass="w-60 h-20" defaultSelected={filteredGamemodes} onChange={(selected) => { setFilteredGamemodes(selected); updateMatchHistory(selected, false); updateStats(selected); }} />
            </div>
            <SegmentedControl items={["Matches", "Agents", "Weapons"]} defaultSelected={subPage} onChange={(selected) => { setSubPage(selected); }} />
          </div>

          <>
            {subPage === "Matches" ? (
              <div>
                {matches.length === 0 ? (
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
                    <GamesList data={matches} puuid={playerinfo.puuid} />

                    <button
                      onClick={() => updateMatchHistory(filteredGamemodes, true)}
                      disabled={loadingMatches}
                      className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center disabled:opacity-50"
                    >
                      {loadingMatches ? "Loading..." : "Load More"}
                    </button>
                  </div>
                )}
              </div>
            ) : subPage === "Agents" ? (
              <div>
                {agentStats === null ? (
                  loadingStats ? (
                    <div className="flex flex-col items-center space-y-8">
                      <h2 className="text-4xl font-bold text-accent mb-4">Loading Agent Stats...</h2>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center space-y-8">
                      <h2 className="text-4xl font-bold text-accent mb-4">No Agent Stats found.</h2>
                    </div>
                  )
                ) : (
                  <div className="flex flex-col items-center space-y-8">
                    <StatsList key="agents" data={agentStats} headers={agentHeaders} defaultHeader={"Win%"} headerTooltips={agentHeaderTooltips} imageType={"agents"} />
                  </div>
                )}
              </div>
            ) : subPage === "Weapons" ? (
              <div>
                {weaponStats === null ? (
                  loadingStats ? (
                    <div className="flex flex-col items-center space-y-8">
                      <h2 className="text-4xl font-bold text-accent mb-4">Loading Weapon Stats...</h2>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center space-y-8">
                      <h2 className="text-4xl font-bold text-accent mb-4">No Weapon Stats found.</h2>
                    </div>
                  )
                ) : (
                  <div className="flex flex-col items-center space-y-8">
                    <StatsList key="weapons" data={weaponStats} headers={weaponHeaders} defaultHeader={"K/R"} headerTooltips={weaponHeaderTooltips} imageType={"weapons"} />
                  </div>
                )}
              </div>
            ) : ( <></> )}
          </>

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