import { useEffect, useState } from 'react';

function Login() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const [user, setUser] = useState(null);

  useEffect(() => {
    document.title = 'Login - valocity';

    fetch(`${BASE_URL}/me`, { credentials: "include" })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => setUser(null));
  }, []);

  const handleLogin = () => {
    window.location.href = "/login";
  };

  const testLogin = () => {
    fetch(`${BASE_URL}/me`, { credentials: "include" })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => setUser(null));

    console.log("User: ", user.user_id);
  };

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-8">
        <button
          onClick={handleLogin}
          className="px-6 py-3 bg-red-600 text-white rounded-2xl shadow-md"
        >
          Sign in with Riot
        </button>
{/*       <h2 className="text-4xl font-bold text-white mb-4">Working on Profiles, {user.user_id}.</h2> */}
        <h2 className="text-4xl font-bold text-white mb-4">Working on Profiles</h2>
        <button
          onClick={testLogin}
          className="px-6 py-3 bg-red-600 text-white rounded-2xl shadow-md"
        >
          Test
        </button>
      </div>
     </div>
    );
  }
  
  export default Login;