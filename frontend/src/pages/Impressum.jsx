import { useEffect } from 'react';

function Impressum() {
    useEffect(() => {
      document.title = 'valocity';
    }, []);

    return (
      <div className="bg-darkness items-center pt-16 p-6 space-y-16">
        <div className="flex flex-col items-center space-y-8">
          <h2 className="text-4xl font-bold text-white mb-4">Impressum</h2>
          <div className="text-white text-base space-y-4">
            <h2 className="text-xl font-semibold mt-4">Betreiber</h2>
            <p>
              Emil Wallraff<br />
              Goethestraße 10<br />
              97072 Würzburg
            </p>
            <h2 className="text-xl font-semibold mt-4">Kontakt</h2>
            <p>
              Telefon: +49 151 68175368<br />
              E-Mail: <a href="mailto:emilwallraff@gmail.com" className="text-brand hover:text-brand-light underline">emilwallraff@gmail.com</a>
            </p>
          </div>
        </div>
      </div>
    );
}
  
export default Impressum;