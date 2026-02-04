import { useState, useEffect } from 'react';
import { imagesAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ImageGrid from '../components/ImageGrid';
import ImageModal from '../components/ImageModal';

function BrowsePage() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    imagesAPI.getAll()
      .then(res => {
        setImages(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <h1 className="text-5xl font-light tracking-wider mb-4">
            Browse Gallery
          </h1>
          <p className="text-gray-600 mb-12">
            Explore all images from our photographers
          </p>

          {loading ? (
            <p className="text-center text-gray-400 py-20">Loading...</p>
          ) : images.length === 0 ? (
            <p className="text-center text-gray-400 py-20">
              No images in the gallery yet
            </p>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-8">
                {images.length} {images.length === 1 ? 'image' : 'images'}
              </p>
              <ImageGrid images={images} onImageClick={setSelectedImage} />
            </>
          )}
        </div>
      </main>
      <Footer />

      {selectedImage && (
        <ImageModal
          image={selectedImage}
          allImages={images}
          onClose={() => setSelectedImage(null)}
          onImageChange={setSelectedImage}
        />
      )}
    </div>
  );
}

export default BrowsePage;
