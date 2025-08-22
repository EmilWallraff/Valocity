import { useEffect, useState } from 'react';

function Login() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const [user, setUser] = useState(null);

  useEffect(() => {
    document.title = 'Login - valocity';

    updateUser();
  }, []);

  const handleLogin = () => {
    window.location.href = `${BASE_URL}/login`;
  };

  const updateUser = async () => {
    try {
      const res = await fetch(`${BASE_URL}/me`, { credentials: "include" });

      if (!res.ok) {
        console.error("Failed to fetch user:", res.status);
        setUser(null);
        return;
      }

      const data = await res.json();

      if (!data || !data.user_id) {
        console.warn("User data missing or malformed:", data);
        setUser(null);
        return;
      }

      setUser(data);
      console.log("User: ", user);

    } catch (err) {
      console.error("Error fetching user:", err);
      setUser(null);
    }
  };

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">

        <h2 className="text-4xl font-bold text-white mb-4">Profiles are still work in progress.</h2>
        <button
          onClick={handleLogin}
          className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
        >
          Sign in with Riot
        </button>
        <h2 className="text-2xl text-white text-center max-w-3xl">By signing in with Riot you acknowledge that your profile becomes public.</h2>
        <button
          onClick={updateUser}
          className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
        >
          Test (No Effect for Users)
        </button>
        <div className="">
          {!user ? (
            <h2 className="text-2xl text-white text-center max-w-3xl">No user identified yet.</h2>
          ) : (
            <h2 className="text-2xl text-white text-center max-w-3xl">Welcome, {user.user_id?.slice(0, 10) ?? "Unknown"}!</h2>
          )}
        </div>

      </div>
    </div>
  );
}
  
export default Login;