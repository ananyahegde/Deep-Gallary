import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

function SignupPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: '',
    name: '',
    email: '',
    password: '',
    contact: '',
  });

  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setFormError('');

    try {
      const formData = new FormData();
      Object.entries(form).forEach(([key, value]) => {
        formData.append(key, value);
      });

      await api.post('/admins', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      navigate('/login');
    } catch (err) {
      const data = err.response?.data;

      if (Array.isArray(data?.detail)) {
        const fieldErrors = {};
        data.detail.forEach((item) => {
          const field = item.loc[item.loc.length - 1];
          fieldErrors[field] = item.msg;
        });
        setErrors(fieldErrors);
        return;
      }

      if (typeof data?.detail === 'string') {
        setFormError(data.detail);
        return;
      }

      setFormError('Signup failed');
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link to="/" className="text-2xl font-light tracking-wider text-gray-900">
              Deep Gallary
            </Link>
            <div className="flex items-center space-x-8">
              <Link to="/" className="text-sm text-gray-600 hover:text-gray-900">
                HOME
              </Link>
              <Link to="/explore" className="text-sm text-gray-600 hover:text-gray-900">
                EXPLORE
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Signup Form */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-24">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-light tracking-wide text-gray-900 mb-3">
              Join Deep Gallary
            </h1>
            <p className="text-sm text-gray-600 tracking-wide">
              Create your admin account
            </p>
          </div>

          <div className="space-y-6">
            {formError && (
              <div className="bg-red-50 border border-red-200 px-4 py-3">
                <p className="text-sm text-red-600">{formError}</p>
              </div>
            )}

            {/* Username */}
            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                USERNAME
              </label>
              <input
                type="text"
                name="username"
                value={form.username}
                onChange={handleChange}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
              {errors.username && <p className="text-xs text-red-600 mt-1">{errors.username}</p>}
            </div>

            {/* Name */}
            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                NAME
              </label>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
              {errors.name && <p className="text-xs text-red-600 mt-1">{errors.name}</p>}
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                EMAIL
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
              {errors.email && <p className="text-xs text-red-600 mt-1">{errors.email}</p>}
            </div>

            {/* Contact */}
            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                CONTACT
              </label>
              <input
                type="text"
                name="contact"
                value={form.contact}
                onChange={handleChange}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
              {errors.contact && <p className="text-xs text-red-600 mt-1">{errors.contact}</p>}
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                PASSWORD
              </label>
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
              {errors.password && <p className="text-xs text-red-600 mt-1">{errors.password}</p>}
            </div>

            <button
              onClick={handleSubmit}
              className="w-full bg-gray-900 text-white py-3 text-sm tracking-wider hover:bg-gray-800 transition-colors"
            >
              SIGN UP
            </button>

            <div className="text-center pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <Link to="/login" className="text-gray-900 hover:underline">
                  Login
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;
