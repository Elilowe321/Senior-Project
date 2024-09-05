import React, { useState, useEffect } from 'react';
import './dashboard.css';

function Dashboard({ sideNavOpen }) {
    const [earnings, setEarnings] = useState(null);
    const token = localStorage.getItem("authToken");
    const user_id = localStorage.getItem("user_id");

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`/auth/${user_id}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                setEarnings(data.earnings);
            } catch (error) {
                console.error('Error fetching earnings:', error);
            }
        };

        fetchData();
    }, [token, user_id]); // Ensure useEffect runs when token or user_id changes

    return (
        <div className={`dashboard-container ${sideNavOpen ? 'shifted' : ''}`}>

            {/* Example content, you can replace with your actual content */}
            <div id='content1'>
                <h2>Earnings</h2>
                <p>{earnings !== null ? `$${earnings}` : 'Loading...'}</p>
            </div>
            <div id='content2'>
                <h2>Column 2</h2>
                <p>Content goes here...</p>
            </div>
            <div id='content3'>
                <h2>Column 3</h2>
                <p>Content goes here...</p>
            </div>
        </div>
    );
}

export default Dashboard;
