function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          <div>
            <h3 className="text-lg font-light mb-6 tracking-wider">Deep Gallary</h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              A platform for photographers to showcase their work and share their unique vision with the world.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-light mb-6 tracking-wider">Quick Links</h3>
            <ul className="space-y-3 text-sm text-gray-600">
              <li><a href="/" className="hover:text-gray-900 transition">Home</a></li>
              <li><a href="/explore" className="hover:text-gray-900 transition">Explore</a></li>
              <li><a href="/login" className="hover:text-gray-900 transition">Login</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-light mb-6 tracking-wider">Contact</h3>
            <p className="text-gray-600 text-sm">
              info@deepgallary.com
            </p>
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-gray-200 text-center text-xs text-gray-500 tracking-wide">
          © 2026 Deep Gallary. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default Footer;
