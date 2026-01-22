import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { photographersAPI, projectsAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ProjectCard from '../components/ProjectCard';

function PhotographerProfile() {
  const { username } = useParams();
  const [photographer, setPhotographer] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      photographersAPI.getByUsername(username),
      projectsAPI.getByUsername(username)
    ])
      .then(([photographerRes, projectsRes]) => {
        setPhotographer(photographerRes.data[0]);
        setProjects(projectsRes.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [username]);

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

  if (!photographer) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-gray-400 text-sm tracking-widest">PHOTOGRAPHER NOT FOUND</div>
        </main>
        <Footer />
      </div>
    );
  }

  const imageUrl = photographer.photo
    ? `http://127.0.0.1:8000/${photographer.photo}`
    : 'https://via.placeholder.com/400';

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        {/* Profile Header */}
        <div className="bg-gray-50 py-20">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="flex flex-col md:flex-row items-center md:items-start gap-12">
              <div className="w-48 h-48 rounded-full overflow-hidden flex-shrink-0">
                <img
                  src={imageUrl}
                  alt={photographer.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-grow text-center md:text-left">
                <h1 className="text-5xl font-light tracking-wider mb-4">
                  {photographer.name}
                </h1>
                <p className="text-gray-600 mb-6 leading-relaxed max-w-2xl">
                  {photographer.description || 'Photographer'}
                </p>
                <div className="text-sm text-gray-500">
                  <p>{photographer.email}</p>
                  {photographer.contact && <p>{photographer.contact}</p>}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Projects Section */}
        <div className="py-20">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <h2 className="text-3xl font-light tracking-wider mb-12">Projects</h2>
            {projects.length === 0 ? (
              <p className="text-gray-400 text-center py-20">No projects yet</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {projects.map(project => (
                  <ProjectCard key={project._id} project={project} />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default PhotographerProfile;
