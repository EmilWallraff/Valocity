import { Link, Outlet } from "react-router-dom";
import { useUser } from "../contexts/UserContext";

import NavigationDropdown from "../components/NavigationDropdown";

function Layout() {
  const { userinfo, loading } = useUser();

  return (
    <div className="flex flex-col min-h-screen bg-darkness text-white">
      {/* Navigation bar */}
      <nav className="sticky top-0 z-50 flex items-center justify-between p-4 bg-black shadow-md">
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-2xl font-raj font-bold text-brand hover:text-brand-light">valocity</Link>
          <NavigationDropdown items={ [
              { label: "Win Probability", image: `/images/valorant/gamemodes/5D0F264B-4EBE-CC63-C147-809E1374484B.png`, path: "/winprobability" },
            ] } label="Tools" />
            <NavigationDropdown items={ [
              { label: "Weapons", image: `/images/valorant/weapons/9C82E19D-4575-0200-1A81-3EACF00CF872_killstream.png`, path: "/weapons" },
              { label: "Agents", image: `/images/valorant/roles/1B47567F-8F7B-444B-AAE3-B0C634622D10.png`, path: "/agents" },
            ] } label="Global Stats" />
        </div>
        <div className="space-x-4">
          {loading ? (
            <span className="text-gray-400">Loading...</span>
          ) : userinfo ? (
            <Link to="/login" className="text-brand hover:text-brand-light font-bold transition">
              {userinfo.gameName ?? "Unknown"}
              {userinfo.tagLine ? "#" : ""}
              {userinfo.tagLine ?? ""}
            </Link>
          ) : (
            <Link to="/login" className="text-brand hover:text-brand-light font-bold transition">
              Login
            </Link>
          )}
        </div>
      </nav>

      {/* Page content */}
      <main className="flex-1">
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
  );
}

export default Layout;
