import React, { useState } from 'react';
import './TopForm.css';

const TopForm = ({ title, children, showCloseButton, onClose }) => {
    const [collapsed, setCollapsed] = useState(false);

    const handleCollapseExpand = () => {
        setCollapsed(!collapsed);
    };

    return (
        <div className={`name-description-container ${collapsed ? 'collapsed' : ''}`}>
            <div className={`header ${collapsed ? 'collapsed' : ''}`}>
                <h1>{title}</h1>
                {showCloseButton && (
                    <button className='collapse-expand-btn' onClick={onClose}>
                        &times;
                    </button>
                )}
                {!showCloseButton && (
                    <button className='collapse-expand-btn' onClick={handleCollapseExpand}>
                        {collapsed ? '-' : '+'}
                    </button>
                )}
            </div>
            {!collapsed && children}
        </div>
    );
};

export default TopForm;
