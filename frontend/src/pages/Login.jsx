import { useEffect, useState } from 'react';

function Login() {
  const BASE_URL = import.meta.env.PROD ? "https://valocity.onrender.com" : "http://localhost:8000";
  const [user, setUser] = useState(null);

  useEffect(() => {
    document.title = 'Login - valocity';

    {/*
    fetch(`${BASE_URL}/me`, { credentials: "include" })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => setUser(null));
    */}
  }, []);

  const handleLogin = () => {
    window.location.href = `${BASE_URL}/login`;
  };

  const testLogin = () => {
    fetch(`${BASE_URL}/me`, { credentials: "include" })
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(() => setUser(null));

    console.log("User: ", user);
    console.log("User id []: ", user["user_id"]);
    console.log("User id .: ", user.user_id);
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
          onClick={testLogin}
          className="w-60 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
        >
          Test (No Effect for Users)
        </button>
        <div className="">
          {!user ? (
            <h2 className="text-2xl text-white text-center max-w-3xl">No user identified yet</h2>
          ) : (
            <h2 className="text-2xl text-white text-center max-w-3xl">Welcome, {user}!</h2>
          )}
        </div>

      </div>
     </div>
    );
  }
  
  export default Login;

{/*
.slice(0, 10)
*/}