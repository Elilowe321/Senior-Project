import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './modelsHome.css';
import '../../../assets/styles/tables.css';

function ModelsHome() {
    const [models, setModels] = useState([]);
    const [selectedModelId, setSelectedModelId] = useState(null); // State to manage selected model
    const user_id = localStorage.getItem("user_id");
    const token = localStorage.getItem("authToken");
    const navigate = useNavigate();

    useEffect(() => {
        if (user_id) {
            fetch(`/cfb/models/${user_id}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setModels(data); 
                console.log(data);
            })
            .catch(error => {
                console.error('Error fetching models:', error);
            });
        } else {
            console.warn('user_id is null or undefined.');
        }
    }, []);

    const handleDelete = async (modelId) => {
        console.log("Deleting model with ID:", modelId);
    
        if (user_id && token) {

            try {
                const response = await fetch(`/cfb/models/${user_id}/${modelId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    }
                });
    
                if (!response.ok) {
                    const errorMessage = await response.text();
                    throw new Error(`Error deleting model: ${response.status} - ${errorMessage}`);
                }
    
                console.log("Model deleted successfully");
                setModels(models.filter(model => model.id !== modelId));
            } catch (error) {
                console.error('Error deleting model:', error.message);
            }
        } else {
            console.warn('user_id or token is null or undefined.');
        }
    };

    const toggleDropdown = (modelId) => {
        if (selectedModelId === modelId) {
            setSelectedModelId(null);
        } else {
            setSelectedModelId(modelId);
        }
    };

    const handleRunModel = (modelId, runType) => {
        if (runType === 'upcoming') {
            navigate(`/${user_id}/${modelId}/games`);
        } else if (runType === 'last_year') {
            navigate(`/${user_id}/${modelId}/test-accuracy`);
        } else if (runType === 'live') {
            navigate(`/${user_id}/${modelId}/live-accuracy`);
        }
    };

    const handleEdit = (modelId) => {
        navigate(`/${user_id}/model/${modelId}`);
    };

    const handleCreateNewModel = () => {
        navigate(`/${user_id}/create-model`);
    };

    return (
        <div className='model-home'>
            {/* Table Container */}
            <div id='table-container'>
                {/* Container for top header */}
                <div id='table-header'>
                    <h1 id='table-title'>Models</h1>
                    <button id='table-add-button' onClick={handleCreateNewModel}>{'+'}</button>
                </div>
                
                {/* Actual Table */}
                <table id='table'>
                    <thead>
                        <tr>
                            <th>Run</th>
                            <th>ID</th>
                            <th>Name</th>
                            {/*<th>Description</th>*/}
                            <th>Type</th>
                            <th>Target</th>
                            <th>Accuracy</th>
                            <th>Edit</th>
                            <th>Delete</th>
                        </tr>
                    </thead>
                    <tbody>
                        {models.map(model => (
                            <React.Fragment key={model.id}>
                                <tr>
                                    <td onClick={() => toggleDropdown(model.id)} style={{ cursor: 'pointer' }}>&#9654;</td>
                                    <td>{model.id}</td>
                                    <td>{model.name}</td>
                                    {/*<td>{model.description}</td>*/}
                                    <td>{model.type}</td>
                                    <td>{model.target}</td>
                                    <td>{model.classification_accuracy}</td>
                                    <td onClick={() => handleEdit(model.id)} style={{ cursor: 'pointer' }}>&#9998;</td>
                                    <td onClick={() => handleDelete(model.id)} style={{ cursor: 'pointer' }}>&#9851;</td>
                                </tr>
                                {selectedModelId === model.id && (
                                    <tr className="dropdown-row">
                                        <td colSpan="8">
                                            <div className="dropdown-container">
                                                <button onClick={() => handleRunModel(model.id, 'upcoming')}>Run on Upcoming Games</button>
                                                <button onClick={() => handleRunModel(model.id, 'last_year')}>Run on Last Year Games</button>
                                                <button onClick={() => handleRunModel(model.id, 'live')}>Run on Past Bets</button>

                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ModelsHome;
