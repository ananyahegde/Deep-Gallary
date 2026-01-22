import { Link } from 'react-router-dom';

function PhotographerCard({ photographer }) {
  const imageUrl = photographer.photo
    ? `http://127.0.0.1:8000/${photographer.photo}`
    : 'https://via.placeholder.com/400';

  return (
    <Link to={`/photographer/${photographer.username}`} className="block group">
      <div className="relative overflow-hidden rounded-lg aspect-[4/5] mb-3">
        <img
          src={imageUrl}
          alt={photographer.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
        <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
      </div>
      <h3 className="text-lg font-light tracking-wide mb-1 text-gray-900">
        {photographer.name}
      </h3>
      <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed">
        {photographer.description || 'Photographer'}
      </p>
    </Link>
  );
}

export default PhotographerCard;
