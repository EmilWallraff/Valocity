import { useEffect } from 'react';
import { Link } from "react-router-dom";

function Home() {
    useEffect(() => {
      document.title = 'valocity';
    }, []);

    const pages = [
      {
        label: "Calculate the probability to win a round with certain agents, shields and weapons on a given map and side. Designed to help figuring out ideal buys in specific situations.",
        image: "/images/valorant/gamemodes/5D0F264B-4EBE-CC63-C147-809E1374484B.png",
        path: "/winprobability",
      },
      {
        label: "Analyse your match history and get insights in statistics like Player Rating which is used as the go-to for professional players.",
        image: "/images/valorant/abilities/7F94D92C-4234-0A36-9646-3A87EB8B5C89_Grenade.png",
        path: "/playerprofile",
      },
      {
        label: "Global Weapon stats can be filtered by map and agent and are available for different opponent loadout values.",
        image: "/images/valorant/weapons/E336C6B8-418D-9340-D77F-7A9E4CFE0702_killstream.png",
        path: "/weapons",
      },
      {
        label: "Global Agent stats can be filtered by map.",
        image: "/images/valorant/roles/1B47567F-8F7B-444B-AAE3-B0C634622D10.png",
        path: "/agents",
      },
    ];

  return (
    <>
      <div className="fixed left-1/4 top-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center gap-3 pointer-events-none z-[9999]">
        <span className="text-brand font-raj text-9xl font-bold drop-shadow-md">
          valocity
        </span>
        <img src="/images/branding/Logo_Cyan.png" alt="valocity logo" className="w-36" />
      </div>

      <div className="flex h-full">
        {/* Left half (empty) */}
        <div className="w-1/2 bg-darkness" />

        {/* Right half with scrollable buttons */}
        <div className="w-1/2 overflow-y-auto px-40 pt-56 pb-56 space-y-20 scrollbar-thin scrollbar-thumb-brand scrollbar-track-element-dark">
          {pages.map((page) => (
            <Link
              key={page.path}
              to={page.path}
              className="flex items-center bg-element hover:bg-element-light border border-element-lighter text-white rounded-2xl shadow-md transition p-8 space-x-8"
            >
              <img
                src={page.image}
                alt={page.label}
                className="w-28 h-28 object-contain rounded-md"
              />
              <span className="text-3xl font-semibold">{page.label}</span>
            </Link>
          ))}
        </div>
      </div>

    </>

    
  );
}

export default Home;


