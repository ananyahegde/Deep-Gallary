import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import HeroSection from '../components/HeroSection';
import ExploreSection from '../components/ExploreSection';

function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow">
        <HeroSection />
        <ExploreSection />
      </main>
      <Footer />-
    </div>
  );
}

export default HomePage;
