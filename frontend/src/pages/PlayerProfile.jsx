import { useEffect, useState } from "react";
import { useUser } from "../contexts/UserContext";

function PlayerProfile() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";

  const { userinfo, fetchUserinfo } = useUser();

  useEffect(() => {
    document.title = 'Profile - valocity';

    getUserData();
  }, []);

  const getUserData = async () => {
    try {
      const res = await fetch(`${BASE_URL}/riot/matchlist?puuid=${userinfo.puuid}`, { credentials: "include" });

      console.log("puuid: " + userinfo.puuid);

      if (!res.ok) {
        console.log("res not ok.");
        return;
      }

      const data = await res.json();

      if (data == null){
        console.log("res data is null.");
      } else {
        console.log("res data: " + data);
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

  return (
    <div className="bg-darkness flex flex-col items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <h2 className="text-4xl font-bold text-white mb-4">Player Profiles are still work in progress.</h2>

        <h2 className="text-2xl text-white text-center max-w-3xl">Testy Test Text.</h2>
      </div>
    </div>
  );
}

export default PlayerProfile;