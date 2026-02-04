import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import SearchBar from './SearchBar';

function Navbar() {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <div className="flex items-center space-x-12">
            <Link to="/" className="flex items-center">
              <img
                src="/logo.png"
                alt="Deep Gallary"
                className="h-8 -mt-2"
              />
            </Link>
            <div className="hidden md:flex space-x-8">
              <Link to="/" className="text-sm tracking-wide text-gray-600 hover:text-gray-900 transition">
                HOME
              </Link>
              <Link to="/explore" className="text-sm tracking-wide text-gray-600 hover:text-gray-900 transition">
                EXPLORE
              </Link>
              <Link to="/images" className="text-sm tracking-wide text-gray-600 hover:text-gray-900 transition">
                BROWSE
              </Link>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <SearchBar />
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="text-sm tracking-wide text-gray-600 hover:text-gray-900 transition uppercase"
                >
                  {user.username}
                </button>

                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 shadow-lg">
                    <Link
                      to="/profile/edit"
                      className="block px-4 py-3 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setDropdownOpen(false)}
                    >
                      Profile
                    </Link>
                    <Link
                      to="/admin"
                      className="block px-4 py-3 text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setDropdownOpen(false)}
                    >
                      Portfolio Management
                    </Link>
                    <button
                      onClick={() => {
                        setDropdownOpen(false);
                        logout();
                      }}
                      className="block w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 border-t border-gray-200"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex space-x-6">
                <Link
                  to="/login"
                  className="text-sm tracking-wide text-gray-600 hover:text-gray-900 transition"
                >
                  LOGIN
                </Link>
                <Link
                  to="/signup"
                  className="text-sm tracking-wide text-gray-600 hover:text-gray-900 transition"
                >
                  SIGN UP
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
