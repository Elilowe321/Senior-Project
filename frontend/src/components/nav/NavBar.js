import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './NavBar.css';
import { useAuth } from '../auth/AuthContext';

function NavBar({ sideNavOpen, toggleSideNav }) {
  const user_id = localStorage.getItem("user_id");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const { logout } = useAuth();

  const dropdownRef = useRef(null);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const toggleModelDropdown = () => {
    setModelDropdownOpen(!modelDropdownOpen);
  };

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setDropdownOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <nav className="navbar">
      <div className={`sidenav ${sideNavOpen ? 'active' : ''}`}>
        <button className="smallbtn" onClick={toggleSideNav}>
              {sideNavOpen ? '✕' : '☰'}
          </button>

        {/* Sidenav content */}

        {/* Conditional rendering based on sideNavOpen */}
        {user_id &&(
          <>
            <Link to={`/${user_id}/dashboard`} className="sidenav-link"><span id='home'>&#8962;</span> Dashboard</Link>
            <Link onClick={toggleModelDropdown} className="sidenav-link"><span id='models'>&#9775;</span> Models<span className={`arrow ${modelDropdownOpen ? 'open' : ''}`}></span></Link>

            {modelDropdownOpen && (
              <div className="side-nav-show">
                <Link to={`/${user_id}/models`} style={{ fontSize: '20px' }} className="sidenav-link"> <span id='football'>&#127944;</span> Football</Link>
                <Link to={`/${user_id}/models`} style={{ fontSize: '20px' }} className="sidenav-link"> <span id='football'>&#9971;</span> Golf</Link>
                <Link to={`/${user_id}/models`} style={{ fontSize: '20px' }} className="sidenav-link"> <span id='football'>&#9917;</span> Soccer</Link>
              </div> 

            )}
            

            <Link className="sidenav-link" onClick={logout}><span id='logout'>&#9888;</span> Logout</Link>
          </>
        )}

        {sideNavOpen && !user_id &&(
          <>
            <Link to="/signin?type=register" className="sidenav-link">&#x1F4E6; Register</Link>
            <Link to="/signin?type=login" className="sidenav-link">&#x1F511; Login</Link>
          </>
        )}    

        {!sideNavOpen && !user_id &&(
          <>
            <Link to="/signin?type=register" className="sidenav-link">&#x1F4E6;</Link>
            <Link to="/signin?type=login" className="sidenav-link">&#x1F511;</Link>
          </>
        )}  
      </div>

      <ul className="navbar-list">
        <li className='openbtn'>
          <button className="navbar-link" onClick={toggleSideNav}>
              {sideNavOpen ? '✕' : '☰'}
          </button>
        </li>
        <div className={`navbar-center ${sideNavOpen ? 'hidden' : ''}`}>
          {/* Logo or brand name */}
          <li>
            <Link to="/" className="navbar-link">C L A I R V O Y A N T</Link>
          </li>
        </div>
        <li className="navbar-item-right" ref={dropdownRef}>
          {/* Dropdown button */}
          <button onClick={toggleDropdown} className={`navbar-link ${sideNavOpen ? 'hidden' : ''}`} style={{ fontSize: '24px' }}>&#x1F3C8;</button>
          {/* Dropdown content */}
          {dropdownOpen && (
            <div className="dropdown-content show">
              {user_id ? (
                <Link onClick={logout} to="/signin?type=login">&#x1F6AA; Logout</Link>
              ) : (
                <>
                  <Link to="/signin?type=register">&#x1F4E6; Register</Link>
                  <Link to="/signin?type=login">&#x1F511; Login</Link>
                </>
              )}
            </div>
          )}
        </li>
      </ul>
    </nav>
  );
}

export default NavBar;
