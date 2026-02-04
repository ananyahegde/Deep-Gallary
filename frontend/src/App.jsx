import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import ExplorePage from './pages/ExplorePage';
import PhotographerProfile from './pages/PhotographerProfile';
import ProjectView from './pages/ProjectView';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import AdminDashboard from './pages/AdminDashboard';
import ProjectManagement from './pages/ProjectManagement';
import AdminProfile from './pages/AdminProfile';
import SearchPage from './pages/SearchPage';
import BrowsePage from './pages/BrowsePage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-white">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/explore" element={<ExplorePage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/photographer/:username" element={<PhotographerProfile />} />
            <Route path="/project/:id" element={<ProjectView />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/project/:id/manage" element={<ProjectManagement />} />
            <Route path="/profile/edit" element={<AdminProfile />} />
            <Route path="/images" element={<BrowsePage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
