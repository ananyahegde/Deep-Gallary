import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError('Invalid credentials');
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

      {/* Login Form */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-24">
        <div className="max-w-md mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-3xl font-light tracking-wide text-gray-900 mb-3">
              Welcome Back
            </h1>
            <p className="text-sm text-gray-600 tracking-wide">
              Login to Deep Gallary
            </p>
          </div>

          <div className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 px-4 py-3">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                USERNAME
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-xs tracking-wider text-gray-700 mb-2">
                PASSWORD
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-200 px-4 py-3 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                required
              />
            </div>

            <button
              onClick={handleSubmit}
              className="w-full bg-gray-900 text-white py-3 text-sm tracking-wider hover:bg-gray-800 transition-colors"
            >
              LOGIN
            </button>

            <div className="text-center pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link to="/signup" className="text-gray-900 hover:underline">
                  Sign up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
