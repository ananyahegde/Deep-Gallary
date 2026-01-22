import { useState, useCallback } from 'react';
import Cropper from 'react-easy-crop';

function ImageCropModal({ image, onCropComplete, onCancel }) {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

  const onCropChange = (crop) => {
    setCrop(crop);
  };

  const onZoomChange = (zoom) => {
    setZoom(zoom);
  };

  const onCropAreaChange = useCallback((croppedArea, croppedAreaPixels) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const handleSave = () => {
    onCropComplete(croppedAreaPixels);
  };

  return (
    <div className="fixed inset-0 bg-black/90 z-50 flex flex-col">
      <div className="flex-1 relative">
        <Cropper
          image={image}
          crop={crop}
          zoom={zoom}
          aspect={1}
          cropShape="round"
          showGrid={false}
          onCropChange={onCropChange}
          onZoomChange={onZoomChange}
          onCropComplete={onCropAreaChange}
        />
      </div>

      <div className="bg-white p-6">
        <div className="max-w-md mx-auto">
          <label className="text-sm text-gray-700 block mb-2">Zoom</label>
          <input
            type="range"
            min={1}
            max={3}
            step={0.1}
            value={zoom}
            onChange={(e) => setZoom(Number(e.target.value))}
            className="w-full mb-6"
          />

          <div className="flex gap-4">
            <button
              onClick={handleSave}
              className="flex-1 bg-black text-white px-6 py-3 text-sm"
            >
              Save
            </button>
            <button
              onClick={onCancel}
              className="flex-1 border border-gray-300 px-6 py-3 text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ImageCropModal;
