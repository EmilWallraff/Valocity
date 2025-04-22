import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-darkness text-white text-center p-4">

      <h1 className="text-4xl font-raj font-bold text-brand mb-4">valocity.gg</h1>
      <p className="mb-8">Your personalized AI dashboard</p>

      <div className="space-x-4">
        <Link to="/login">
          <button className="bg-brand text-darkness px-6 py-2 rounded-xl hover:bg-brand-light transition">
            Log In
          </button>
        </Link>
        <Link to="/winprobability">
          <button className="bg-gray-200 text-darkness px-6 py-2 rounded-xl hover:bg-gray-300 transition">
            Win Probability Calculator
          </button>
        </Link>
        <Link to="/dashboard">
          <button className="bg-gray-200 text-darkness px-6 py-2 rounded-xl hover:bg-gray-300 transition">
            Dashboard
          </button>
        </Link>
      </div>

    </div>
  );
}

export default Home;


