import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { projectsAPI, imagesAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ImageGrid from '../components/ImageGrid';
import ImageModal from '../components/ImageModal';

function ProjectView() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      projectsAPI.getById(id),
      imagesAPI.getByProjectId(id)
    ])
      .then(([projectRes, imagesRes]) => {
        setProject(projectRes.data);
        setImages(imagesRes.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-gray-400 text-sm tracking-widest">LOADING…</div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-gray-400 text-sm tracking-widest">
            PROJECT NOT FOUND
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <div className="bg-gray-50 py-16">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <h1 className="text-5xl font-light tracking-wider mb-4">
              {project.project_name}
            </h1>
            {project.description && (
              <p className="text-gray-600 max-w-3xl">
                {project.description}
              </p>
            )}
          </div>
        </div>

        <div className="py-12">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            {images.length === 0 ? (
              <p className="text-gray-400 text-center py-20">
                No images in this project yet
              </p>
            ) : (
              <ImageGrid
                images={images}
                onImageClick={img => setSelectedImage(img)}
              />
            )}
          </div>
        </div>
      </main>

      <Footer />

      {selectedImage && (
        <ImageModal
          key={selectedImage._id}
          image={selectedImage}
          allImages={images}
          onClose={() => setSelectedImage(null)}
          onImageChange={img => setSelectedImage(img)}
        />
      )}

    </div>
  );
}

export default ProjectView;
