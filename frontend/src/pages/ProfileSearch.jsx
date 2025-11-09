import { useEffect, useState } from "react";

import ProfileSearchBar from "../components/ProfileSearchBar";

function ProfileSearch() {
  const storageKey = "recentProfiles";
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