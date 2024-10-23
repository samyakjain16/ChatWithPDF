import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold">
              PDF Chat
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <Link to="/" className="text-gray-700 hover:text-gray-900">
              Home
            </Link>
            <Link to="/chat" className="text-gray-700 hover:text-gray-900">
              Chat
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;