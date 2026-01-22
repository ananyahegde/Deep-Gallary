import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { imagesAPI } from '../services/api';

function ImageModal({ image, allImages, onClose, onImageChange }) {
  const navigate = useNavigate();
  const [similarImages, setSimilarImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!image?._id) return;
    setLoading(true);
    imagesAPI.getSimilar(image._id, 3)
      .then(res => {
        setSimilarImages(res.data);
        setLoading(false);
      })
      .catch(() => {
        const others = allImages.filter(img => img._id !== image._id);
        setSimilarImages(others.slice(0, 3));
        setLoading(false);
      });
  }, [image, allImages]);

  const imageUrl = `http://127.0.0.1:8000${image.path}`;

  const handleTagClick = (tag) => {
    onClose();
    navigate(`/search?q=${encodeURIComponent(tag)}`);
  };

  return (
    <div className="fixed inset-0 bg-black/95 z-50 flex" onClick={onClose}>
      <button
        onClick={onClose}
        className="fixed top-6 right-6 text-white/80 hover:text-white text-4xl z-10 transition"
      >
        ×
      </button>

      <div className="flex-1 flex items-center justify-center px-8 py-12" onClick={e => e.stopPropagation()}>
        <div className="flex gap-8 items-center h-full max-w-7xl w-full">
          {/* Main image + caption */}
          <div className="flex-1 flex flex-col items-center justify-center">
            <div className="mb-6 flex items-center justify-center max-h-[70vh]">
              <img
                src={imageUrl}
                alt={image.title || 'Image'}
                className="max-h-full max-w-full object-contain"
              />
            </div>

            {/* Caption + tags */}
            <div className="text-center max-w-2xl">
              {image.ai_generated_caption && (
                <p className="text-white/70 italic text-base mb-4">
                  "{image.ai_generated_caption}"
                </p>
              )}
              {image.tags?.length > 0 && (
                <div className="flex flex-wrap justify-center gap-2">
                  {image.tags.map((tag, i) => (
                    <button
                      key={i}
                      onClick={() => handleTagClick(tag)}
                      className="px-4 py-2 text-sm tracking-wide bg-white/5 text-white/70 border border-white/10 rounded hover:bg-white/10 transition cursor-pointer"
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Similar images sidebar */}
          {similarImages.length > 0 && (
            <div className="w-80 flex-shrink-0 flex flex-col h-full py-8">
              <h3 className="text-white/80 text-xs tracking-widest mb-6">
                SIMILAR IMAGES
              </h3>
              {loading ? (
                <p className="text-white/60 text-xs">Loading…</p>
              ) : (
                <div className="space-y-6 overflow-y-auto pr-2">
                  {similarImages.map(img => (
                    <div
                      key={img._id}
                      className="cursor-pointer group"
                      onClick={() => onImageChange(img)}
                    >
                      <img
                        src={`http://127.0.0.1:8000${img.path}`}
                        alt={img.title || 'Similar'}
                        className="w-full aspect-[4/3] object-cover group-hover:opacity-70 transition"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ImageModal;
