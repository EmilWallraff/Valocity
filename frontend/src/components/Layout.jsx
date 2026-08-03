import { Link, Outlet, useLocation } from "react-router-dom";
import { useEffect, useRef } from "react";
import { useUser } from "../contexts/UserContext";

import NavigationDropdown from "../components/NavigationDropdown";

function Layout() {
  const { userinfo, loading } = useUser();
  const { pathname } = useLocation();
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className="flex flex-col h-screen bg-darkness text-white">
      {/* Navigation bar */}
      <nav className="flex-none sticky top-0 z-50 flex items-center justify-between p-4 bg-black shadow-md">
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-2xl font-raj font-bold text-brand hover:text-brand-light">valocity</Link>
          <NavigationDropdown items={ [
            { label: "Win Probability", image: `/images/valorant/gamemodes/96BD3920-4F36-D026-2B28-C683EB0BCAC5.png`, path: "/winprobability" },
          ] } label="Tools" />
          <NavigationDropdown items={ [
            { label: "Weapons", image: `/images/valorant/weapons/E336C6B8-418D-9340-D77F-7A9E4CFE0702_killstream.png`, path: "/weapons" },
            { label: "Agents", image: `/images/valorant/roles/1B47567F-8F7B-444B-AAE3-B0C634622D10.png`, path: "/agents" },
          ] } label="Global Stats" />
          <NavigationDropdown items={ [
            { label: "Search", image: `/images/valorant/abilities/DED3520F-4264-BFED-162D-B080E2ABCCF9_Ability2.png`, path: "/profilesearch" },
            { label: "Your Profile", image: `/images/valorant/abilities/92EEEF5D-43B5-1D4A-8D03-B3927A09034B_Ultimate.png`, path: userinfo ? `/playerprofile/${userinfo.gameName}_${userinfo.tagLine}` : "/login" },
          ] } label="Profile" />
        </div>
        <div className="space-x-4">
          {loading ? (
            <span className="text-gray-400">Loading...</span>
          ) : userinfo ? (
            <Link to="/login" className="text-brand hover:text-brand-light font-bold transition">
              {userinfo.gameName ?? "Unknown"}
              {userinfo.tagLine ? " #" : ""}
              {userinfo.tagLine ?? ""}
            </Link>
          ) : (
            <Link to="/login" className="text-brand hover:text-brand-light font-bold transition">
              Login
            </Link>
          )}
        </div>
      </nav>

      {/* Scrollable content (main + footer) */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto flex flex-col">
        {/* Page content */}
        <main className="flex-grow pb-4">
          <Outlet />
        </main>
      

        {/* Footer */}
        <footer className="bg-black text-sm text-center text-white py-3">
          <div className="flex justify-center space-x-6">
            <Link to="/impressum" className="text-brand hover:text-brand-light transition">
              Impressum
            </Link>
            <Link to="/datenschutz" className="text-brand hover:text-brand-light transition">
              Datenschutzerklärung
            </Link>
            <Link to="/rights" className="text-brand hover:text-brand-light transition">
              Terms of Service and Privacy
            </Link>
          </div>
        </footer>
      </div>
    </div>
  );
}
 
export default Layout;