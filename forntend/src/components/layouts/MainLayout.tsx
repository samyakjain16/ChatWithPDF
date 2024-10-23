import { Outlet } from 'react-router-dom';
import Navbar from '/Users/mayankjain/Downloads/pdf-chat-app/forntend/src/components/shared/Navbar.tsx';

const MainLayout = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;