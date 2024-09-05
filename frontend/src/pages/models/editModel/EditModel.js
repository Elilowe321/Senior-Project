import React, { useState, useEffect } from 'react';
import { useParams, useNavigate  } from 'react-router-dom';
import './EditModel.css'
import CheckboxList from '../../../components/CheckboxList/CheckboxList';
import RadioboxList from '../../../components/RadioboxList/RadioboxList';
import TopForm from '../../../components/TopForm/TopForm';

function EditModel() {
  
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
  const navigate  = useNavigate();
  const {user_id, modelId} = useParams();
  const token = localStorage.getItem("authToken");


  const [model, setModel] = useState([]);

    useEffect(() => {
      const fetchModel = async () => {
          if (user_id && modelId) {
              try {
                  const response = await fetch(`/cfb/${user_id}/models/${modelId}`, {
                      method: 'GET',
                      headers: {
                          'Authorization': `Bearer ${token}`,
                      },
                  });
                  if (!response.ok) {
                      throw new Error('Network response was not ok');
                  }
                  const data = await response.json();
                  setModel(data);
                  setName(data.name);
                  setDescription(data.description);
                  setSelectedTarget(data.target);

                  // Get columns
                  const columns = await fetch(`/cfb/models/reverse_columns`, {
                      method: 'POST',
                      headers: {
                          'Content-Type': 'application/json',
                      },
                      body: JSON.stringify(data.columns), // Replace with your actual columns array
                  });

                  const cols = await columns.json();

                  // TODO:: IF something isnt selected on offensive side, the numbers ill be off
                  setSelectedOffensiveColumns(cols.slice(0, 20));
                  setSelectedDefensiveColumns(cols.slice(20));

                  // console.log("OffenseColumns: ", cols.slice(0, 19));
                  // console.log("DefenseColumns: ", cols.slice(19));


              } catch (error) {
                  console.error('Error fetching model:', error);
              }
          } else {
              console.warn('user_id or modelID is null or undefined.');
          }
      };

      fetchModel();
    }, []);

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
        setOffensiveColumns(data.slice(0, 19)); // First 19 columns are offensive
        setDefensiveColumns(data.slice(19));    // Rest are defensive
        setTargetColumns(data)
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
  const editUserModel = (modelId) => {
    const user_id = localStorage.getItem("user_id");
    const token = localStorage.getItem("authToken");
    console.log("TOKEN: ", token)

    const model_columns = selectedOffensiveColumns.concat(selectedDefensiveColumns); // Combine offensive and defensive columns
    var type = '';
    if(selectedTarget === 'target') {
      type = 'classification';
    } else {
      type = 'regression';
    }

    const data = {
        model_columns: model_columns,
        name: name,
        type: type,
        target: selectedTarget,
        description: description
    };

    setLoading(true);

    fetch(`/cfb//models/${user_id}/${modelId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    })
      .then(response => {
        if (!response.ok) {
          setLoading(false);
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(responseData => {
        setLoading(false);
        navigate(`/${user_id}/models`);
        console.log('User model Edited:', responseData);
        // Handle success response here
      })
      .catch(error => {
        setLoading(false);
        console.error('Error editing user model:', error);
        // Handle error here
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
          <TopForm title="Model Editor">
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
            submitTitle='Submit Edit'
            selectedTarget={selectedTarget}
            onTargetChange={handleTargetChange}
            onCreateUserModel={editUserModel}
          />
        </>
      )}
  
      {/* <button className='select-button' onClick={createUserModel}>Create User Model</button> */}
    </div>
  );
}

export default EditModel;
