import { useEffect } from 'react';

function Dashboard() {
    useEffect(() => {
      document.title = 'Dashboard - valocity';
    }, []);

    return (
      <div className="bg-darkness items-center pt-16 p-6 space-y-16">
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">Dashboard will be available soon.</h2>
        </div>
      </div>
    );
  }
  
  export default Dashboard;
  