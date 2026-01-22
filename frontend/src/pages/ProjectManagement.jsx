import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI, imagesAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';

function ProjectManagement() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [title, setTitle] = useState('');
  const [caption, setCaption] = useState('');
  const [tags, setTags] = useState([]);
  const [editingImage, setEditingImage] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProject();
    loadImages();
  }, [id]);

  const loadProject = async () => {
    try {
      const res = await projectsAPI.getById(id);
      setProject(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadImages = async () => {
    try {
      const res = await imagesAPI.getByProjectId(id);
      setImages(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setShowForm(false);
    setTitle('');
    setCaption('');
    setTags([]);
    setError('');
  };

  const handleGenerateAI = async () => {
    if (!selectedFile) return;

    setGenerating(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await imagesAPI.generatePreview(formData);
      setCaption(res.data.caption);
      setTags(res.data.tags);
      setUseAI(true);
      setShowForm(true);
    } catch (err) {
      console.error(err);
      setError('Failed to generate AI data');
    } finally {
      setGenerating(false);
    }
  };

  const handleCustom = () => {
    setUseAI(false);
    setShowForm(true);
    setCaption('');
    setTags([]);
  };

  const uploadImage = async () => {
    setError('');

    if (!caption.trim()) {
      setError('Caption is required');
      return;
    }

    if (!tags || tags.length === 0) {
      setError('At least one tag is required');
      return;
    }

    if (!selectedFile) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('title', title);
      formData.append('caption', caption);
      formData.append('tags', tags.join(','));

      await imagesAPI.upload(id, formData);

      setSelectedFile(null);
      setPreview(null);
      setShowForm(false);
      setTitle('');
      setCaption('');
      setTags([]);
      setError('');
      loadImages();
    } catch (err) {
      console.error(err);
      setError('Failed to upload image');
    } finally {
      setUploading(false);
    }
  };

  const startEditImage = (img) => {
    setEditingImage(img);
    setTitle(img.title || '');
    setCaption(img.ai_generated_caption || '');
    setTags(img.tags || []);
  };

  const updateImage = async () => {
    if (!editingImage) return;

    setError('');

    if (!caption.trim()) {
      setError('Caption is required');
      return;
    }

    if (!tags || tags.length === 0) {
      setError('At least one tag is required');
      return;
    }

    try {
      await imagesAPI.update(editingImage._id, {
        title,
        ai_generated_caption: caption,
        tags,
      });
      setEditingImage(null);
      setTitle('');
      setCaption('');
      setTags([]);
      setError('');
      loadImages();
    } catch (err) {
      console.error(err);
      setError('Failed to update image');
    }
  };

  const cancelEdit = () => {
    setEditingImage(null);
    setTitle('');
    setCaption('');
    setTags([]);
    setError('');
  };

  const cancelUpload = () => {
    setSelectedFile(null);
    setPreview(null);
    setShowForm(false);
    setTitle('');
    setCaption('');
    setTags([]);
    setError('');
  };

  const deleteImage = async (imageId) => {
    if (!confirm('Delete this image?')) return;

    try {
      await imagesAPI.delete(imageId);
      loadImages();
    } catch (err) {
      console.error(err);
      alert('Failed to delete image');
    }
  };

  if (!project || !user) return null;

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <button
          onClick={() => navigate('/admin')}
          className="text-sm text-gray-600 hover:text-gray-900 mb-8"
        >
          ← Back to Dashboard
        </button>

        <h1 className="text-3xl font-light tracking-wide mb-2">
          {project.project_name}
        </h1>
        {project.description && (
          <p className="text-gray-600 mb-8">{project.description}</p>
        )}

        {/* Upload Section */}
        <div className="border-t border-b border-gray-200 py-8 mb-12">
          <h2 className="text-sm tracking-widest mb-6">
            {editingImage ? 'EDIT IMAGE' : 'UPLOAD IMAGE'}
          </h2>

          {error && (
            <p className="text-sm text-red-600 mb-4">{error}</p>
          )}

          {!editingImage ? (
            <>
              {/* File Upload */}

              {!selectedFile ? (
                <div>
                  <label
                    htmlFor="file-upload"
                    className="inline-block cursor-pointer bg-black text-white px-8 py-3 text-sm rounded-xs hover:bg-gray-900 transition"
                  >
                    Choose Image
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Preview with X button */}
                  <div>
                    <div className="relative bg-gray-50 border border-gray-200 p-4 flex items-center justify-center" style={{ minHeight: '400px' }}>
                      <img
                        src={preview}
                        alt="Preview"
                        className="max-w-full max-h-[500px] object-contain"
                      />
                      <button
                        onClick={cancelUpload}
                        className="absolute top-4 right-4 w-8 h-8 bg-black/70 hover:bg-black text-white rounded-full flex items-center justify-center transition"
                      >
                        ×
                      </button>
                    </div>

                    {!showForm && (
                      <div className="mt-6 flex gap-4">
                        <button
                          onClick={handleGenerateAI}
                          disabled={generating}
                          className="flex-1 bg-black text-white px-6 py-3 text-sm disabled:opacity-50"
                        >
                          {generating ? 'Generating...' : 'Generate AI Caption & Tags'}
                        </button>
                        <button
                          onClick={handleCustom}
                          className="flex-1 border border-gray-900 text-gray-900 px-6 py-3 text-sm hover:bg-gray-900 hover:text-white transition"
                        >
                          Add Custom Caption & Tags
                        </button>
                      </div>
                    )}

                    {showForm && (
                      <button
                        onClick={() => {
                          setShowForm(false);
                          setTitle('');
                          setCaption('');
                          setTags([]);
                          setError('');
                        }}
                        className="mt-4 text-sm text-gray-600 hover:text-gray-900"
                      >
                        ← Back to Options
                      </button>
                    )}
                  </div>

                  {/* Form */}
                  {showForm && (
                    <div>
                      <input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Title (optional)"
                        className="w-full border border-gray-200 px-4 py-3 text-sm mb-4"
                      />

                      <textarea
                        value={caption}
                        onChange={(e) => setCaption(e.target.value)}
                        placeholder="Caption *"
                        className="w-full border border-gray-200 px-4 py-3 text-sm mb-4"
                        rows={4}
                        required
                      />

                      <div className="mb-6">
                        <label className="text-xs text-gray-500 mb-2 block">
                          Tags * (comma-separated)
                        </label>
                        <input
                          value={tags.join(', ')}
                          onChange={(e) => setTags(e.target.value.split(',').map(t => t.trim()).filter(Boolean))}
                          placeholder="architecture, house, garden"
                          className="w-full border border-gray-200 px-4 py-3 text-sm"
                          required
                        />
                        {tags.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {tags.map((tag, i) => (
                              <span
                                key={i}
                                className="px-3 py-1 bg-gray-100 text-sm"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <button
                        onClick={uploadImage}
                        disabled={uploading}
                        className="w-full bg-black text-white px-6 py-3 text-sm disabled:opacity-50"
                      >
                        {uploading ? 'Uploading...' : 'Upload Image'}
                      </button>
                    </div>
                  )}
                </div>
              )}

            </>
          ) : (
            /* Edit Form */
            <div className="max-w-2xl">
              <div className="mb-6">
                <img
                  src={`http://127.0.0.1:8000${editingImage.path}`}
                  alt={editingImage.title || 'Image'}
                  className="max-w-full max-h-64 object-contain"
                />
              </div>

              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Title (optional)"
                className="w-full border border-gray-200 px-4 py-3 text-sm mb-4"
              />

              <textarea
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                placeholder="Caption *"
                className="w-full border border-gray-200 px-4 py-3 text-sm mb-4"
                rows={3}
                required
              />

              <div className="mb-6">
                <label className="text-xs text-gray-500 mb-2 block">
                  Tags * (comma-separated)
                </label>
                <input
                  value={tags.join(', ')}
                  onChange={(e) => setTags(e.target.value.split(',').map(t => t.trim()).filter(Boolean))}
                  placeholder="architecture, house, garden"
                  className="w-full border border-gray-200 px-4 py-3 text-sm"
                  required
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={updateImage}
                  className="bg-black text-white px-6 py-2 text-sm"
                >
                  Update Image
                </button>
                <button
                  onClick={cancelEdit}
                  className="border border-gray-300 px-6 py-2 text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Images Grid */}
        <div>
          <h2 className="text-sm tracking-widest mb-6">
            IMAGES ({images.length})
          </h2>

          {images.length === 0 ? (
            <p className="text-gray-400 text-center py-20">
              No images yet. Upload your first image above.
            </p>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {images.map((img) => (
                <div key={img._id} className="relative group">
                  <img
                    src={`http://127.0.0.1:8000${img.path}`}
                    alt={img.title || 'Image'}
                    className="w-full aspect-square object-cover"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                    <button
                      onClick={() => startEditImage(img)}
                      className="bg-gray-100 text-gray-700 px-3 py-1 text-sm rounded hover:bg-gray-200 transition flex items-center gap-1"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteImage(img._id)}
                      className="bg-rose-50 text-rose-700 px-3 py-1 text-sm rounded hover:bg-rose-100 transition flex items-center gap-1"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default ProjectManagement;
