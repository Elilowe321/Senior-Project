import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import './NavBar1.css';
import { useAuth } from '../auth/AuthContext';
import { RxHamburgerMenu } from "react-icons/rx";
import { IoHomeOutline, IoPersonCircleOutline, IoGolfOutline} from "react-icons/io5";
import { PiChartLineUp } from "react-icons/pi";
import { IoMdClose, IoIosLogIn, IoIosLogOut } from "react-icons/io";
import { TfiWrite } from "react-icons/tfi";
import { MdOutlineSportsFootball, MdSportsSoccer  } from "react-icons/md";
import { RiArrowDropDownLine } from "react-icons/ri";
import { SiBetterstack } from "react-icons/si";






function NavBar1({children}) {
  const user_id = localStorage.getItem("user_id");
  const [sideNavOpen, setSideNavOpen] = useState(false);
  const [modelDropdownOpen, setModelDropdownOpen] = useState(false);
  const [loginDropdownOpen, setLoginDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);



  const { logout } = useAuth();


  const toggleSideNav = () => {
    setSideNavOpen(!sideNavOpen);
  };

  const toggleModelDropdown = () => {
    setModelDropdownOpen(!modelDropdownOpen);
  };

  const toggleLoginDropdown = () => {
    setLoginDropdownOpen(!loginDropdownOpen)
  }

  const handleClickOutside = (event) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
      setLoginDropdownOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (

    <div className="whole-page-container">

        {/* Top Nav Bar */}
        <div id='top-nav'>
            <div className='nav-center'>
                <Link className='title' to="/">C L A I R V O Y A N T</Link>
                {/* <Link className='title' to="/">L O W & P O P L O C K S</Link> */}

            </div>
            <button className='outside-button' onClick={toggleSideNav}>
                {/* {sideNavOpen ? '✕' : '☰'} */}
                {sideNavOpen ? <IoMdClose /> : <RxHamburgerMenu />}

            </button>
            <span onClick={toggleLoginDropdown} className="login-icon"><IoPersonCircleOutline /></span>

            {loginDropdownOpen && (
              <div className="dropdown-content" ref={dropdownRef}>
                {user_id ? (
                  <Link onClick={logout} to="/signin?type=login"><IoIosLogOut /> Logout</Link>
                ) : (
                  <>
                    <Link to="/signin?type=register"><TfiWrite /> Register</Link>
                    <Link to="/signin?type=login"><IoIosLogIn /> Login</Link>
                  </>
                )}
              </div>
            )}
          </div>

        {/* Side Nav Bar */}
        <div id="side-nav" className={sideNavOpen ? 'active' : ''}>

          <span id='logo'><SiBetterstack /> {sideNavOpen && <span className='logo-title'>Clairvoyant</span>} </span>
          {/* <span id='logo'><SiBetterstack /> {sideNavOpen && <span className='logo-title'>Low & Pop Locks</span>} </span> */}

          {/* <span id='logo'><img src={require('../../assets/images/lplogo.png')} style={{ height: '40px' }}/> {sideNavOpen && <span className='logo-title'>Low & Pop Locks</span>} </span> */}


            {/* Button to keep side nav open */}
            <button className='inside-button' onClick={toggleSideNav}>
              {sideNavOpen ? <IoMdClose /> : <RxHamburgerMenu />}
            </button>

            

            <div className='side-nav-content'>
                {/* If the user is logged in show this */}
                {user_id &&(
                <>
                    {/* <Link to={`/${user_id}/dashboard`}><span id='home'>&#8962;</span><span id='side-nav-words'>Dashboard</span></Link> */}
                    <Link to={`/${user_id}/dashboard`}><IoHomeOutline /> <span id='side-nav-words'>Dashboard</span></Link>


                    <Link onClick={toggleModelDropdown}>
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"></link>
                        {/* <span className="fa" id='models'>&#xf201;</span> */}
                        <PiChartLineUp/> <span id='side-nav-words'>Models</span>         
                        <span id='side-nav-words' className={`arrow-icon ${modelDropdownOpen ? 'rotate-to-180' : 'rotate-to-0'}`}><RiArrowDropDownLine /></span>               



                        {/* <span id='side-nav-words' className={`dropdown-arrow ${modelDropdownOpen ? 'open' : ''}`}></span> */}
                    </Link>


                    {modelDropdownOpen && (
                        <div style={{paddingLeft: '20px', fontSize: '18px'}}>
                            <Link to={`/${user_id}/models`}><MdOutlineSportsFootball /> <span id='side-nav-words'>Football</span></Link>
                            <Link to={`/${user_id}/models`}><IoGolfOutline /> <span id='side-nav-words'>Golf</span></Link>
                            <Link to={`/${user_id}/models`}><MdSportsSoccer /> <span id='side-nav-words'>Soccer</span></Link>
                        </div> 

                    )}

                    <Link onClick={logout}><IoIosLogOut /> <span id='side-nav-words'>Logout</span></Link>

                </>
                )}


                {/* If the user is not logged in show this */}
                {!user_id &&(
                <>
                    <Link to={'/'}><IoHomeOutline /> <span id='side-nav-words'>Home</span></Link>
                    <Link to="/signin?type=login"><IoIosLogIn /> <span id='side-nav-words'>Login</span></Link>
                    <Link to="/signin?type=register"><TfiWrite /> <span id='side-nav-words'>Register</span></Link>
                </>
                )}


            </div>

        </div>     

        {/* Main Page Content */}
        <main>
            {children}
        </main>

        {/* Footer */}
        {/* <footer>Bring me my money</footer> */}
    </div>
  );
}

export default NavBar1;
