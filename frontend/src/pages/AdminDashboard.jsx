import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsAPI } from '../services/api';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';

function AdminDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [editingProject, setEditingProject] = useState(null);

  useEffect(() => {
    if (!user) return;
    loadProjects();
  }, [user]);

  const loadProjects = async () => {
    try {
      const res = await projectsAPI.getByUsername(user.username);
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (!user) return null;

  const createProject = async () => {
    setError('');
    if (!name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      await projectsAPI.create({ project_name: name, description });
      setName('');
      setDescription('');
      loadProjects();
    } catch (e) {
      setError('Failed to create project');
      console.error(e);
    }
  };

  const updateProject = async () => {
    setError('');
    if (!editingProject) return;

    try {
      await projectsAPI.update(editingProject._id, {
        project_name: name,
        description,
      });
      setEditingProject(null);
      setName('');
      setDescription('');
      loadProjects();
    } catch (e) {
      setError('Failed to update project');
      console.error(e);
    }
  };

  const deleteProject = async (projectId) => {
    if (!confirm('Delete this project? All images will be deleted too.')) return;

    try {
      await projectsAPI.delete(projectId);
      loadProjects();
    } catch (err) {
      alert('Failed to delete project');
      console.error(err);
    }
  };

  const startEdit = (project) => {
    setEditingProject(project);
    setName(project.project_name);
    setDescription(project.description || '');
  };

  const cancelEdit = () => {
    setEditingProject(null);
    setName('');
    setDescription('');
    setError('');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <h1 className="text-3xl font-light tracking-wide mb-8">
          Admin Dashboard
        </h1>

        <div className="mb-12 max-w-md">
          <h2 className="text-sm tracking-widest mb-4">
            {editingProject ? 'EDIT PROJECT' : 'NEW PROJECT'}
          </h2>
          {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Project name"
            className="w-full border border-gray-200 px-4 py-3 text-sm mb-4"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description"
            className="w-full border border-gray-200 px-4 py-3 text-sm mb-4 h-24"
          />

          <div className="flex gap-2">
            <button
              onClick={editingProject ? updateProject : createProject}
              className="bg-black text-white px-6 py-2 text-sm"
            >
              {editingProject ? 'UPDATE' : 'CREATE'}
            </button>
            {editingProject && (
              <button
                onClick={cancelEdit}
                className="border border-gray-300 px-6 py-2 text-sm"
              >
                CANCEL
              </button>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-sm tracking-widest mb-6">YOUR PROJECTS</h2>
          {projects.length === 0 ? (
            <p className="text-gray-400 text-center py-20">
              No projects yet. Create your first project above.
            </p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((p) => (
                <div
                  key={p._id}
                  className="border border-gray-200 p-6 group"
                >
                  <h3 className="text-lg font-light mb-2">{p.project_name}</h3>
                  {p.description && (
                    <p className="text-sm text-gray-600 mb-4">
                      {p.description}
                    </p>
                  )}

                  <div className="flex gap-2 text-sm">
                    <button
                      onClick={() => navigate(`/project/${p._id}/manage`)}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      Manage Images
                    </button>
                    <span className="text-gray-300">|</span>
                    <button
                      onClick={() => startEdit(p)}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      Edit
                    </button>
                    <span className="text-gray-300">|</span>
                    <button
                      onClick={() => deleteProject(p._id)}
                      className="text-red-600 hover:text-red-800"
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

export default AdminDashboard;
