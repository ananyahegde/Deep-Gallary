function HeroSection() {
  return (
    <div className="relative h-screen w-full overflow-hidden">
      <div className="absolute inset-0 bg-gray-200">
        {/* Placeholder for hero image */}
        <img
          src="https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=1920"
          alt="Hero"
          className="w-full h-full object-cover"
        />
      </div>

      <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
        <div className="text-center text-white px-4">
          <h1 className="text-6xl font-light mb-4 tracking-wide">
            Discover Stories
          </h1>

          <p className="text-xl font-light mb-8 tracking-wide">
            Through the lens of talented photographers
          </p>

          <a
            href="/explore"
            className="inline-block bg-white text-gray-900 px-8 py-3 rounded hover:bg-gray-100 transition"
          >
            Explore Now
          </a>
        </div>
      </div>
    </div>
  );
}

export default HeroSection;
