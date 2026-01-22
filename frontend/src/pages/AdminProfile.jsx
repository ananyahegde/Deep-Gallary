import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { photographersAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function AdminProfile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [contact, setContact] = useState('');
  const [photo, setPhoto] = useState(null);
  const [preview, setPreview] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!user) return;
    setName(user.name);
    setDescription(user.description || '');
    setContact(user.contact || '');
    setPreview(user.photo ? `http://127.0.0.1:8000/${user.photo}` : '/default-profile.jpg');
  }, [user]);

  if (!user) return null;

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPhoto(file);
    setPreview(URL.createObjectURL(file));
  };

  const updateProfile = async () => {
    setError('');
    setSuccess('');
    setUploading(true);

    try {
      const formData = new FormData();
      if (name !== user.name) formData.append('name', name);
      if (description !== user.description) formData.append('description', description);
      if (contact !== user.contact) formData.append('contact', contact);
      if (photo) formData.append('photo', photo);

      formData.append('username', user.username);

      await photographersAPI.update(formData);
      setSuccess('Profile updated successfully!');

      // Refresh user data
      setTimeout(() => window.location.reload(), 1500);
    } catch (err) {
      setError('Failed to update profile');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow max-w-3xl mx-auto px-6 lg:px-8 py-16">
        <button
          onClick={() => navigate('/admin')}
          className="text-sm text-gray-600 hover:text-gray-900 mb-8"
        >
          ← Back to Dashboard
        </button>

        <h1 className="text-3xl font-light tracking-wide mb-8">Edit Profile</h1>

        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}
        {success && <p className="text-sm text-green-600 mb-4">{success}</p>}

        {/* Profile Photo */}
        <div className="mb-8">
          <label className="text-sm tracking-wide text-gray-700 mb-2 block">
            PROFILE PHOTO
          </label>
          <div className="flex items-center gap-6">
            <div className="w-32 h-32 rounded-full overflow-hidden flex-shrink-0 bg-gray-100">
              <img
                src={preview}
                alt="Profile"
                className="w-full h-full object-cover"
                onError={(e) => e.target.src = '/default-profile.jpg'}
              />
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handlePhotoChange}
              className="text-sm"
            />
          </div>
        </div>

        {/* Name */}
        <div className="mb-6">
          <label className="text-sm tracking-wide text-gray-700 mb-2 block">
            NAME
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-gray-200 px-4 py-3 text-sm"
          />
        </div>

        {/* Description */}
        <div className="mb-6">
          <label className="text-sm tracking-wide text-gray-700 mb-2 block">
            BIO
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full border border-gray-200 px-4 py-3 text-sm h-32"
            placeholder="Tell people about yourself..."
          />
        </div>

        {/* Contact */}
        <div className="mb-8">
          <label className="text-sm tracking-wide text-gray-700 mb-2 block">
            CONTACT
          </label>
          <input
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            className="w-full border border-gray-200 px-4 py-3 text-sm"
            placeholder="Phone or social media"
          />
        </div>

        {/* Read-only fields */}
        <div className="mb-6 pb-6 border-b border-gray-200">
          <p className="text-xs text-gray-500 mb-2">Username: {user.username}</p>
          <p className="text-xs text-gray-500">Email: {user.email}</p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={updateProfile}
            disabled={uploading}
            className="bg-black text-white px-8 py-3 text-sm disabled:opacity-50"
          >
            {uploading ? 'Updating...' : 'Save Changes'}
          </button>
          <button
            onClick={() => navigate('/')}
            className="border border-gray-300 px-8 py-3 text-sm"
          >
            Cancel
          </button>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default AdminProfile;
