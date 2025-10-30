import { useEffect, useState } from "react";

import { useUser } from "../contexts/UserContext";
import { fetchWithRetry } from "../utils/fetchWithRetry";

import ProfileSearchBar from "../components/ProfileSearchBar";

function ProfileSearch() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const storageKey = "recentProfiles";
  const { userinfo, fetchUserinfo } = useUser();
  const [data, setData] = useState([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    document.title = 'Search Profiles - valocity';
  }, []);

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <h2 className="text-4xl font-bold text-white mb-4">
          {searching ? "Searching..." : "Search for Player"}
        </h2>
      </div>

      <div>
        <div className="flex flex-col items-center space-y-8">
          <ProfileSearchBar recents={(JSON.parse(localStorage.getItem(storageKey) || "[]") ?? []).map?.((p) => `${p.gamename}#${p.tagline}`) || []} />
        </div>
      </div>

    </div>
  );
}

export default ProfileSearch;