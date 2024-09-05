import React, { useState } from 'react';
import './RadioboxList.css'

const RadioboxList = ({ title, columns, selectedTarget, onTargetChange, onCreateUserModel, submitTitle }) => {
    const [collapsed, setCollapsed] = useState(false);

    const handleCollapseExpand = () => {
        setCollapsed(!collapsed);
    };

    return (
        <div className='target-container'>
            <div className={`header ${collapsed ? 'collapsed' : ''}`}>
                <h2>{title}</h2>
                <button className='collapse-expand-btn' onClick={handleCollapseExpand}> {collapsed ? '-' : '+'} </button>
            </div>
        
        {!collapsed && (
            <ul className='target-list'>
                {columns.map((column, index) => (
                <li key={index}>
                    <label>
                    <input
                        type="radio"
                        value={column}
                        checked={selectedTarget === column}
                        onChange={(e) => onTargetChange(e, column)}
                    />
                    {column}
                    </label>
                </li>
                ))}
            </ul>
        )}
        
        <div className={`footer ${collapsed ? 'collapsed' : ''}`}>
            {!collapsed && <button className='select-button' onClick={onCreateUserModel}>{submitTitle}</button>}
        </div>

        </div>
    );
};

export default RadioboxList;
