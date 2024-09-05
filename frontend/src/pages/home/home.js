import { Link } from 'react-router-dom';
import './home.css';

function HomePage() {
  return (
    <div className="index-container">
      <h1>Welcome to the Index Page</h1>
      <div className="links">
        <Link to="/model" className="index-link">Go to Model Page</Link>
        <Link to="/models" className="index-link">Go to Models Page</Link>
      </div>
    </div>       
  );
}

export default HomePage;
