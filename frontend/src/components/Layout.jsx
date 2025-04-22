import { Link, Outlet } from "react-router-dom";

function Layout() {
  return (
    <div className="min-h-screen bg-darkness text-white">
      {/* Navigation bar */}
      <nav className="sticky top-0 z-50 flex items-center justify-between p-4 bg-black shadow-md">
        <Link to="/" className="text-2xl font-raj font-bold text-brand">valocity.gg</Link>
        <div className="space-x-4">
          <Link to="/dashboard" className="text-brand hover:text-brand-light transition">Login</Link>
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
