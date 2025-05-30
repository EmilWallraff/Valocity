import { useEffect } from 'react';
import { Link } from "react-router-dom";

function Home() {
    useEffect(() => {
      document.title = 'valocity';
    }, []);

  return (
    <div className="bg-darkness items-center pt-16 p-6 space-y-16">
      <div className="flex flex-col items-center space-y-28">
        <h1 className="text-8xl font-raj font-bold text-brand mb-4">valocity</h1>

        <div className="flex flex-col items-center space-y-4">
          <h2 className="text-2xl text-white text-center max-w-3xl">Calculate the probability to win a round with certain agents, shields and weapons on a given map and side.</h2>
          <Link
            to="/winprobability"
            className="w-80 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
          >
            Win Probability Calculator
          </Link>
        </div>

        <div className="flex flex-col items-center space-y-4">
          <h2 className="text-2xl text-white text-center max-w-3xl">Weapon stats can be filtered by map and agent and are available for different opponent loadout values.</h2>
          <Link
            to="/weapons"
            className="w-80 h-20 bg-element border border-element-lighter text-white rounded-xl hover:bg-element-light transition text-lg flex items-center justify-center"
          >
            Weapon Stats
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;


