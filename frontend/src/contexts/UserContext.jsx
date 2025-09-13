import { createContext, useContext, useState, useEffect } from "react";

const UserContext = createContext();

export function UserProvider({ children }) {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";

  const [userinfo, setUserinfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserinfo();
  }, []);

  const fetchUserinfo = async () => {
    try
    {
      const res = await fetch(`${BASE_URL}/riot/me`, { credentials: "include" });

      if (!res.ok) {
        setUserinfo(null);
        setLoading(false);
        return;
      }

      const data = await res.json();

      setUserinfo(data || null);
    }
    catch (err)
    {
      console.error("Error fetching userinfo:", err);
      setUserinfo(null);
    }
    finally
    {
      setLoading(false);
    }
  };

  return (
    <UserContext.Provider value={{ userinfo, setUserinfo, loading, fetchUserinfo }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
