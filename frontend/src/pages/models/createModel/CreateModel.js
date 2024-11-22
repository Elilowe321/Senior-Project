import React, { useState, useEffect } from 'react';
import { useNavigate  } from 'react-router-dom';
import './CreateModel.css'
import CheckboxList from '../../../components/CheckboxList/CheckboxList';
import RadioboxList from '../../../components/RadioboxList/RadioboxList';
import TopForm from '../../../components/TopForm/TopForm';

function CreateModel() {
  
  // ========== Get all columns and categorize them into offensive and defensive ==========
  const [offensiveColumns, setOffensiveColumns] = useState([]);
  const [defensiveColumns, setDefensiveColumns] = useState([]);
  const [selectedOffensiveColumns, setSelectedOffensiveColumns] = useState([]);
  const [selectedDefensiveColumns, setSelectedDefensiveColumns] = useState([]);
  const [targetColumns, setTargetColumns] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [modelError, setModelError] = useState(''); // State for error message
  const navigate  = useNavigate();


  // Get all columns options for user to choose from
  useEffect(() => {
    fetch('/cfb/models/columns')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setOffensiveColumns(data.slice(0, 20)); // First 20 columns are offensive
        setDefensiveColumns(data.slice(20));    // Rest are defensive
        // setTargetColumns(data)
        setTargetColumns([...data, 'target']); // Add 'target' option to target columns
        // console.log(data);
      })
      .catch(error => {
        console.error('Error fetching columns:', error);
      });
  }, []);

  // If user selects an offensive stat
  const handleOffensiveCheckboxChange = (e, column) => {
    const isChecked = e.target.checked;
    if (isChecked) {
      setSelectedOffensiveColumns([...selectedOffensiveColumns, column]);
    } else {
      setSelectedOffensiveColumns(selectedOffensiveColumns.filter(selectedColumn => selectedColumn !== column));
    }
  };

  // If user selects a defensive stat
  const handleDefensiveCheckboxChange = (e, column) => {
    const isChecked = e.target.checked;
    if (isChecked) {
      setSelectedDefensiveColumns([...selectedDefensiveColumns, column]);
    } else {
      setSelectedDefensiveColumns(selectedDefensiveColumns.filter(selectedColumn => selectedColumn !== column));
    }
  };


  // User wants to select all offensive stats
  const handleSelectAllOffensive = () => {
    if (selectedOffensiveColumns.length === offensiveColumns.length) {
      setSelectedOffensiveColumns([]);
    } else {
      setSelectedOffensiveColumns(offensiveColumns);
    }
  };

  // User wants to select all defensive stats
  const handleSelectAllDefensive = () => {
    if (selectedDefensiveColumns.length === defensiveColumns.length) {
      setSelectedDefensiveColumns([]);
    } else {
      setSelectedDefensiveColumns(defensiveColumns);
    }
  };

  // User wants to select a target
  const handleTargetChange = (e, column) => {
    setSelectedTarget(column);
  };

  // Handle input change for model name
  const handleNameChange = (e) => {
    setName(e.target.value);
    console.log(name);
  };

  // Handle input change for model description
  const handleDescriptionChange = (e) => {
    setDescription(e.target.value);
  };

  // Sends user chosen stats to create api to create model
  const createUserModel = () => {
    const user_id = localStorage.getItem("user_id");
    const token = localStorage.getItem("authToken");

    const model_columns = [...selectedOffensiveColumns, ...selectedDefensiveColumns];
    const type = selectedTarget === 'target' ? 'classification' : 'regression';

    const data = {
      user_id,
      model_columns,
      name,
      type,
      target: selectedTarget,
      description
    };

    setLoading(true);

    fetch(`/cfb/models/${user_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })
      .then(response => {
        setLoading(false);
        if (!response.ok) {
          if (response.status === 404) {
            setModelError("Name already in use");
          }
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(responseData => {
        navigate(`/${user_id}/models`);
        console.log('User model created:', responseData.id);
      })
      .catch(error => {
        setLoading(false);
        console.error('Error creating user model:', error);
      });
  };

  return (
    <div className='model-page-container'>
      {loading ? (
        <div className='loader-back'>
          <div className='loader'></div>
        </div>
      ) : (
        <>
          <TopForm title="Model Creator">
            {modelError && <p className="error-message">{modelError}</p>} {/* Display error */}
            <input
              type="text"
              placeholder="Model Name"
              value={name}
              onChange={handleNameChange}
            />
            <textarea
              placeholder="Model Description"
              value={description}
              onChange={handleDescriptionChange}
            />
          </TopForm>
  
          {/* Container for the offensive and defensive stats */}
          <div className='stats-container'>
            <CheckboxList
              title="OFFENSIVE STATS"
              columns={offensiveColumns}
              selectedColumns={selectedOffensiveColumns}
              onCheckboxChange={handleOffensiveCheckboxChange}
              onSelectAll={handleSelectAllOffensive}
            />
            <CheckboxList
              title="DEFENSIVE STATS"
              columns={defensiveColumns}
              selectedColumns={selectedDefensiveColumns}
              onCheckboxChange={handleDefensiveCheckboxChange}
              onSelectAll={handleSelectAllDefensive}
            />
          </div>
  
          <RadioboxList
            title="Select A Target"
            columns={targetColumns}
            submitTitle='Create User Model'
            selectedTarget={selectedTarget}
            onTargetChange={handleTargetChange}
            onCreateUserModel={createUserModel}
          />
        </>
      )}
  
      {/* <button className='select-button' onClick={createUserModel}>Create User Model</button> */}
    </div>
  );
}

export default CreateModel;
