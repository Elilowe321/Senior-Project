import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import './login.css';
import TopForm from '../../components/TopForm/TopForm';
import { useAuth } from '../../components/auth/AuthContext';

const Login = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { login } = useAuth();

    const queryParams = new URLSearchParams(location.search);
    const initialType = queryParams.get('type') || 'login';
    const [type, setType] = useState(initialType);

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [loginError, setLoginError] = useState(''); // State to hold login error message

    const handleUsernameChange = (e) => setUsername(e.target.value);
    const handlePasswordChange = (e) => setPassword(e.target.value);
    const handleFirstNameChange = (e) => setFirstName(e.target.value);
    const handleLastNameChange = (e) => setLastName(e.target.value);
    const handleEmailChange = (e) => setEmail(e.target.value);

    // Update component state when location changes
    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        const newType = queryParams.get('type') || 'login';
        setType(newType);
    }, [location.search]);

    // Function to update URL parameters
    const updateURLParams = (newType) => {
        const searchParams = new URLSearchParams(location.search);
        searchParams.set('type', newType);
        navigate(`${location.pathname}?${searchParams.toString()}`);
    };

    const toggleType = () => {
        const newType = type === 'register' ? 'login' : 'register';
        setType(newType);
        updateURLParams(newType);

        setUsername('');
        setFirstName('');
        setLastName('');
        setEmail('');
        setPassword('');
        setLoginError(''); // Clear error message when switching forms
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        const grant_type = '';
        const scope = '';
        const client_id = '';
        const client_secret = '';

        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `grant_type=${encodeURIComponent(grant_type)}&username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&scope=${encodeURIComponent(scope)}&client_id=${encodeURIComponent(client_id)}&client_secret=${encodeURIComponent(client_secret)}`,
            });

            if (!response.ok) {
                const errorData = await response.json();
                setLoginError(errorData.detail); // Set error message from response
                return;
            }

            const responseData = await response.json();

            // Store the access token and user data in localStorage
            login(responseData["access_token"], responseData["user"]["user_id"]);

            // Navigate to the protected route after successful login
            navigate(`/${responseData.user.user_id}/dashboard`);
        } catch (error) {
            console.error('Error creating user token:', error);
            setLoginError('An unexpected error occurred. Please try again.');
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
    
        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_name: username,
                    first_name: firstName,
                    last_name: lastName,
                    email: email,
                    password: password
                }),
            });
    
            if (response.ok) {
                await handleLogin(e);
            } else {
                const errorData = await response.json();
                setLoginError(errorData.detail); // Display specific error message
            }
        } catch (error) {
            console.error('Error registering user:', error);
            setLoginError('Registration failed: An unexpected error occurred.');
        }
    };
    

    return (
        <div className='login-container'>
            <div className={`flip-card ${type === 'register' ? 'flipped' : ''}`}>
                <div className='flip-card-front'>
                    <TopForm title="Login">
                        {loginError && <p className="error-message">{loginError}</p>}

                        <form onSubmit={handleLogin}>
                            <input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={handleUsernameChange}
                            />
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={handlePasswordChange}
                            />
                            <button type="submit" className='select-button' style={{ marginTop: '10px' }}>
                                Login
                            </button>
                            <button type="button" onClick={toggleType} style={{ marginTop: '10px' }}>
                                Create an Account
                            </button>
                        </form>
                    </TopForm>
                </div>

                <div className='flip-card-back'>
                <TopForm title="Register">
                    {loginError && <p className="error-message">{loginError}</p>}
                    <form onSubmit={handleRegister}>
                        <input
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={handleUsernameChange}
                        />
                        <input
                            type="text"
                            placeholder="First Name"
                            value={firstName}
                            onChange={handleFirstNameChange}
                        />
                        <input
                            type="text"
                            placeholder="Last Name"
                            value={lastName}
                            onChange={handleLastNameChange}
                        />
                        <input
                            type="email"
                            placeholder="Email"
                            value={email}
                            onChange={handleEmailChange}
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={handlePasswordChange}
                        />
                        <button type="submit" className='select-button' style={{ marginTop: '10px' }}>
                            Register
                        </button>
                        <button type="button" onClick={toggleType} style={{ marginTop: '10px' }}>
                            Already Have an Account?
                        </button>
                    </form>
                </TopForm>
                </div>
            </div>
        </div>
    );
};

export default Login;
