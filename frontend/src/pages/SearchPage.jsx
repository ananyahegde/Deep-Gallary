import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { imagesAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ImageGrid from '../components/ImageGrid';
import ImageModal from '../components/ImageModal';

function SearchPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    if (!query) return;

    setLoading(true);
    imagesAPI.search(query)
      .then(res => {
        setImages(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [query]);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <h1 className="text-3xl font-light tracking-wide mb-2">
            Search Results
          </h1>
          <p className="text-gray-600 mb-12">
            Showing results for "{query}"
          </p>

          {loading ? (
            <p className="text-center text-gray-400 py-20">Loading...</p>
          ) : images.length === 0 ? (
            <p className="text-center text-gray-400 py-20">
              No images found for "{query}"
            </p>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-8">
                {images.length} {images.length === 1 ? 'image' : 'images'} found
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

export default SearchPage;
