import { useState, useEffect } from 'react';
import { photographersAPI } from '../services/api';
import PhotographerCard from './PhotographerCard';

function ExploreSection() {
  const [photographers, setPhotographers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    photographersAPI.getAll()
      .then(res => {
        setPhotographers(res.data.slice(0, 8));
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <p className="text-center text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <h2 className="text-4xl font-light text-center mb-12">
        Featured Photographers
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
        {photographers.map(photographer => (
          <PhotographerCard
            key={photographer.username}
            photographer={photographer}
          />
        ))}
      </div>

      <div className="text-center mt-12">
        <a
          href="/explore"
          className="inline-block border border-gray-900 text-gray-900 px-8 py-3 rounded hover:bg-gray-900 hover:text-white transition"
        >
          View All Photographers
        </a>
      </div>
    </div>
  );
}

export default ExploreSection;
