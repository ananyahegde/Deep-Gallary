import videoSource from '../assets/video.mp4';

function HeroSection() {
  return (
    <div className="relative h-screen w-full overflow-hidden">
      <div className="absolute inset-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
        >
          <source
            src={videoSource}
            type="video/mp4"
          />
        </video>
        <div className="absolute inset-0 bg-black/10"></div>
      </div>

      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center px-4">
          <h1 className="text-6xl font-light mb-4 tracking-wide text-white drop-shadow-2xl">
            Discover Stories
          </h1>
          <p className="text-xl font-light mb-8 tracking-wide text-white drop-shadow-xl">
            Through the lens of talented photographers
          </p>
          <a
            href="/explore"
            className="inline-block bg-white text-gray-900 px-8 py-3 rounded-lg hover:bg-gray-100 transition shadow-xl"
          >
            Explore Now
          </a>
        </div>
      </div>
    </div>
  );
}

export default HeroSection;
