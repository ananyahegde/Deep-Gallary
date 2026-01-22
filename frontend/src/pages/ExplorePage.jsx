import { useState, useEffect } from 'react';
import { photographersAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import PhotographerCard from '../components/PhotographerCard';

function ExplorePage() {
  const [photographers, setPhotographers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    photographersAPI.getAll()
      .then(res => {
        setPhotographers(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-gray-400 text-sm tracking-widest">LOADING...</div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="mb-16">
            <h1 className="text-5xl font-light tracking-wider mb-4">All Photographers</h1>
            <p className="text-gray-500 tracking-wide">
              Browse through our community of talented photographers
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12">
            {photographers.map(photographer => (
              <PhotographerCard key={photographer.username} photographer={photographer} />
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default ExplorePage;
