import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ProgressCircle from '../../components/progress/ProgressCircle';
import BetGames from '../../components/bets/BetGame';
import './games.css'
import '../../assets/styles/tables.css'

function Games() {
    const { user_id, model_id } = useParams();
    const token = localStorage.getItem("authToken");
    const navigate = useNavigate();
    const [gameData, setGameData] = useState([]);
    const [modelType, setModelType] = useState();
    const [loading, setLoading] = useState(true);
    const [currentTable, setCurrentTable] = useState('confidence');
    const underlineRef = useRef(null);
    const [initialButton, setInitialButton] = useState(true);

    useEffect(() => {
        const fetchGameData = async () => {
            console.log("Running model with ID:", model_id);

            if (user_id && token) {
                try {
                    const bodyData = {
                        user_id: user_id,
                        model_id: model_id
                    };

                    const model = await fetch(`/cfb/${user_id}/models/${model_id}`, {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });

                    const modelData = await model.json();
                    setModelType(modelData.type);

                    const response = await fetch(`/games/${user_id}/cfb/${model_id}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(bodyData),
                    });

                    if (!response.ok) {
                        const errorMessage = await response.text();
                        setLoading(false);
                        throw new Error(`Error running model: ${response.status} - ${errorMessage}`);
                    }

                    const data = await response.json();

                    const gamesArray = Object.values(data);
                    setGameData(gamesArray);

                    // console.log(gamesArray)

                    setLoading(false);

                } catch (error) {
                    setLoading(false);
                    console.error('Error running model:', error.message);
                }
            } else {
                setLoading(false);
                console.warn('user_id or token is null or undefined.');
            }
        };

        fetchGameData();

    }, []);


    const calculateAccuracy = () => {
        let correctCount = 0;
        let totalCount = 0;
    
        gameData.forEach(game => {
            if (modelType === 'classification' && game.odds !== null && game.odds !== 0) {
                if (game.random_forest_class_prediction !== undefined && game.winner !== undefined) {
                    totalCount++;
                    if (game.random_forest_class_prediction === game.winner) {
                        correctCount++;
                    }
                }
            }
        });
    
        const percentage = totalCount > 0 ? (correctCount / totalCount) * 100 : 0;
        return { correctCount, percentage };
    };
    

    const sortGames = (criteria) => {
        let sortedGames;
        if (criteria === 'confidence') {
            sortedGames = [...gameData].sort((a, b) => b.random_forest_class_proba - a.random_forest_class_proba);
        } else if (criteria === 'value') {
            sortedGames = [...gameData].sort((a, b) => b.odds - a.odds);
        } else if (criteria === 'best') {
            sortedGames = [...gameData].sort((a, b) => {
                const impliedProbaA = a.odds < 0 
                    ? (-a.odds) / (-a.odds + 100) 
                    : 100 / (a.odds + 100);
                const impliedProbaB = b.odds < 0 
                    ? (-b.odds) / (-b.odds + 100) 
                    : 100 / (b.odds + 100);
                const valueA = a.random_forest_class_proba - (impliedProbaA / 100);
                const valueB = b.random_forest_class_proba - (impliedProbaB / 100);
                const weightFactor = 0.1; // Adjust this factor to fine-tune the prioritization
                const adjustedValueA = valueA + (weightFactor * a.odds);
                const adjustedValueB = valueB + (weightFactor * b.odds);
                return adjustedValueB - adjustedValueA;
            });
        } else {
            sortedGames = gameData;
        }

        return sortedGames.sort((a, b) => (a.odds === 0) - (b.odds === 0));
    };

    const renderTableRows = (games) => {
        return games.map(game => (
            <tr key={game.game_id}>
                <td>{game.game_id}</td>
                {modelType === 'classification' ? (
                    <>
                        <td style={{ color: game.random_forest_class_prediction === 1 ? 'green' : 'red' }}>{game.home_team}</td>
                        <td style={{ color: game.random_forest_class_prediction === 1 ? 'red' : 'green' }}>{game.away_team}</td>
                        <td><ProgressCircle size={60} progress={game.random_forest_class_proba} strokeWidth={5} /></td>
                        <td>{game.odds > 0 ? `+${game.odds}` : game.odds}</td>
                        {/* <td>{game.winner}</td> */}
                        <td>
                            <BetGames
                                title={`${game.home_team} vs ${game.away_team}`}
                            />
                        </td>
                    </>
                ) : modelType === 'regression' ? (
                    <>
                        <td>{game.home_team}</td>
                        <td>{game.away_team}</td>
                        <td>{parseFloat(game.random_forest_home).toFixed(2)}</td>
                        <td>{parseFloat(game.random_forest_away).toFixed(2)}</td>
                    </>
                ) : null}
            </tr>
        ));
    };

    const getGamesToDisplay = () => {
        if (currentTable === 'confidence') {
            return sortGames('confidence');
        }
        if (currentTable === 'value') {
            return sortGames('value');
        }
        if (currentTable === 'best') {
            return sortGames('best');
        }
        return gameData;
    };

    const updateUnderline = (buttonElement) => {
        const underline = underlineRef.current;
        underline.style.width = `${buttonElement.offsetWidth}px`;
        underline.style.left = `${buttonElement.offsetLeft}px`;
        setInitialButton(false);
    };

    useEffect(() => {
        const activeButton = document.querySelector('.table-selector button.active');
        if (activeButton) {
            updateUnderline(activeButton);
        }
    }, [currentTable]);
    const { correctCount, percentage } = calculateAccuracy();

    return (
        <div className='games-home'>
            {loading ? (
                <div className='loader-back'>
                    <div className='loader'></div>
                </div>
            ) : (
                <>
                    {/* Display Accuracy */}
                    {modelType === 'classification' && (
                        <div className="accuracy-info">
                            <p>Total Correct Predictions: {correctCount}</p>
                            <p>Accuracy: {percentage.toFixed(2)}%</p>
                        </div>
                    )}
    
                    {/* Table Container */}
                    <div id='table-container'>
                        {/* Container for top header */}
                        <div id='table-header'>
                            <div id='table-title-wrapper'>
                                <h1 id='table-title'>Games</h1>
                            </div>
    
                            <div className='table-selector'>
                                <button 
                                    onClick={() => {
                                        setCurrentTable('confidence');
                                        updateUnderline(document.querySelector('.table-selector button:nth-child(1)'));
                                    }}
                                    className={currentTable === 'confidence' ? 'active' : ''}
                                >
                                    Most Confident
                                    {initialButton && (
                                        <div className='initial'></div>
                                    )}
                                </button>
                            
                                <button 
                                    onClick={() => {
                                        setCurrentTable('value');
                                        updateUnderline(document.querySelector('.table-selector button:nth-child(2)'));
                                    }}
                                    className={currentTable === 'value' ? 'active' : ''}
                                >
                                    Best Value
                                </button>
                                <button 
                                    onClick={() => {
                                        setCurrentTable('best');
                                        updateUnderline(document.querySelector('.table-selector button:nth-child(3)'));
                                    }}
                                    className={currentTable === 'best' ? 'active' : ''}
                                >
                                    Best Bet
                                </button>
                                <div className="underline" ref={underlineRef}></div>
                            </div>
                        </div>
    
                        {/* Actual Table */}
                        <table id='table'>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Home Team</th>
                                    <th>Away Team</th>
                                    {modelType === 'classification' ? (
                                        <>
                                            <th>Probability</th>
                                            <th>Betting Line</th>
                                            {/* <th>Winner</th> */}
                                            <th>Place Bet</th>
                                        </>
                                    ) : modelType === 'regression' ? (
                                        <>
                                            <th>Random Forest Home</th>
                                            <th>Random Forest Away</th>
                                        </>
                                    ) : null}
                                </tr>
                            </thead>
                            <tbody>
                                {renderTableRows(getGamesToDisplay())}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
    
}

export default Games;

