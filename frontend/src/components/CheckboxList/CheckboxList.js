import React, { useState } from 'react';
import './CheckboxList.css';

const CheckboxList = ({ title, columns, selectedColumns, onCheckboxChange, onSelectAll }) => {
  const [collapsed, setCollapsed] = useState(false);

  const handleCollapseExpand = () => {
    setCollapsed(!collapsed);
  };

  return (
    <div className={`columns-container ${collapsed ? 'collapsed' : ''}`}>
    <div className={`header ${collapsed ? 'collapsed' : ''}`}>
    <h2>{title}</h2>
        <button className='collapse-expand-btn' onClick={handleCollapseExpand}>
          {collapsed ? '-' : '+'}
        </button>
      </div>
      {!collapsed && (
        <ul className='stats-grid'>
          {columns.map((column, index) => (
            <li key={index}>
              <label>
                <input
                  type="checkbox"
                  value={column}
                  checked={selectedColumns.includes(column)}
                  onChange={(e) => onCheckboxChange(e, column)}
                />
                {column}
              </label>
            </li>
          ))}
        </ul>
      )}
    <div className={`footer ${collapsed ? 'collapsed' : ''}`}>
        {!collapsed && <button className='select-button' onClick={onSelectAll}>Select All</button>}
      </div>
    </div>
  );
};

export default CheckboxList;
