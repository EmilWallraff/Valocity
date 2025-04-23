import { useEffect } from 'react';

function Dashboard() {
    useEffect(() => {
      document.title = 'Dashboard - valocity.gg';
    }, []);

    return (
      <div className="min-h-screen p-6 bg-darkness text-white">
        <h2 className="text-3xl font-bold text-brand mb-4">Dashboard</h2>
        <p className="">User data will show here soon.</p>
      </div>
    );
  }
  
  export default Dashboard;
  