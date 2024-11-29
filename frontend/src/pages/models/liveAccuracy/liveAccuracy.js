import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import '../../games/games.css';
import '../../../assets/styles/tables.css'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function LiveAccuracy() {
  const { user_id, model_id } = useParams();
  const [gameData, setGameData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minProbability, setMinProbability] = useState(0); // State for minimum probability filter
  const [submittedProbability, setSubmittedProbability] = useState(0); // Track submitted value
  const token = useMemo(() => localStorage.getItem("authToken"), []);

  useEffect(() => {
    const fetchGameData = async () => {
      if (!user_id || !token) {
        setLoading(false);
        setError('user_id or token is missing.');
        return;
      }

      setLoading(true);

      try {
        const response = await fetch(`/cfb/model_accuracy_live_with_probability?user_id=${user_id}&model_id=${model_id}&min_probability=${submittedProbability}`, { 
          method: 'GET', 
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        setGameData(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchGameData();
  }, [user_id, model_id, token, submittedProbability]); // Add submittedProbability to dependency array

  const handleProbabilityChange = (e) => {
    setMinProbability(Number(e.target.value)); // Update the input value
  };

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page refresh on submit
    setSubmittedProbability(minProbability); // Set submitted value to trigger data fetch
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!gameData) return <p>No data available</p>;

  return (
    <div id='table-container'>
      <div id='table-header'>
        <h1 id='table-title'>PREVIOUS BETS</h1>
        <form onSubmit={handleSubmit}>
          <div id='probability-filter'>
            <label htmlFor="minProbability">Min Probability: </label>
            <input
              type="number"
              id="minProbability"
              value={minProbability}
              onChange={handleProbabilityChange}
              min="0"
              max="100"
              step="1"
            />
            <button type="submit">Submit</button>
          </div>
        </form>
      </div>

      <table id='table'>
        <thead>
          <tr>
            <th>Game ID</th>
            <th>Prediction</th>
            <th>Actual</th>
            <th>Probability</th>
            <th>Odds</th>
            <th>Correct</th>
          </tr>
        </thead>
        <tbody>
          {gameData.finished_games.map((game) => (
            <tr key={game.game_id} className={game.is_correct ? 'correct-row' : 'incorrect-row'}>
              <td>{game.game_id}</td>
              <td>{game.prediction}</td>
              <td>{game.actual}</td>
              <td>{(game.probability).toFixed(2)}%</td>
              <td>{game.odds}</td>
              <td>{game.is_correct ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LiveAccuracy;
