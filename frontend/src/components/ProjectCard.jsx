import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { imagesAPI } from '../services/api';

function ProjectCard({ project }) {
  const [isHovered, setIsHovered] = useState(false);
  const [coverImage, setCoverImage] = useState('https://via.placeholder.com/600x400');

  useEffect(() => {
    imagesAPI.getByProjectId(project._id)
      .then(res => {
        if (res.data && res.data.length > 0 && res.data[0].metadata?.filename) {
          setCoverImage(`http://127.0.0.1:8000/uploads/images/${res.data[0].metadata.filename}`);
        }
      })
      .catch(err => console.error(err));
  }, [project._id]);

  return (
    <Link
      to={`/project/${project._id}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="block group"
    >
      <div className="relative overflow-hidden aspect-[4/3] mb-4">
        <img
          src={coverImage}
          alt={project.project_name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        {isHovered && project.project_name && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center transition-opacity duration-300">
            <h3 className="text-white text-2xl font-light tracking-wider px-4 text-center">
              {project.project_name}
            </h3>
          </div>
        )}
      </div>
      {!isHovered && (
        <h3 className="text-base font-light tracking-wide text-gray-900">
          {project.project_name}
        </h3>
      )}
      {project.description && (
        <p className="text-xs text-gray-500 mt-2 line-clamp-2">
          {project.description}
        </p>
      )}
    </Link>
  );
}

export default ProjectCard;
