import { Link, Outlet } from "react-router-dom";

import NavigationDropdown from "../components/NavigationDropdown";

function Layout() {
  return (
    <div className="min-h-screen bg-darkness text-white">
      {/* Navigation bar */}
      <nav className="sticky top-0 z-50 flex items-center justify-between p-4 bg-black shadow-md">
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-2xl font-raj font-bold text-brand hover:text-brand-light">valocity.gg</Link>
          <NavigationDropdown items={ [
              { label: "Win Probability", image: `/images/valorant/gamemodes/5D0F264B-4EBE-CC63-C147-809E1374484B.png`, path: "/winprobability" },
            ] } label="Tools" />
            <NavigationDropdown items={ [
              { label: "Weapons", image: `/images/valorant/weapons/9C82E19D-4575-0200-1A81-3EACF00CF872_killstream.png`, path: "/weapons" },
            ] } label="Global Stats" />
        </div>
        <div className="space-x-4">
          <Link to="/login" className="text-brand hover:text-brand-light font-bold transition">Login</Link>
        </div>
      </nav>

      {/* Page content */}
      <main className="p-0">
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;
