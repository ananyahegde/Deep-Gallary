import { useState } from 'react';

function ImageGrid({ images, onImageClick }) {
  return (
    <div className="columns-1 sm:columns-2 lg:columns-3 gap-4 space-y-4">
      {images.map((image) => {
        const imageUrl = `http://127.0.0.1:8000${image.path}`;

        return (
          <div
            key={image.id}
            className="break-inside-avoid group cursor-pointer relative"
            onClick={() => onImageClick(image)}
          >
            <div className="relative overflow-hidden">
              <img
                src={imageUrl}
                alt={image.title || 'Image'}
                className="w-full h-auto group-hover:scale-105 transition-transform duration-500"
              />
              {image.title && (
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                  <p className="text-white text-lg font-light tracking-wide px-4 text-center">
                    {image.title}
                  </p>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default ImageGrid;
