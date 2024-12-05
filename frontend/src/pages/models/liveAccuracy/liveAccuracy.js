import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { useParams } from 'react-router-dom';
import '../../games/games.css';

function LiveAccuracy() {
  const { user_id, model_id } = useParams();
  const [chartData, setChartData] = useState(null);
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minProbability, setMinProbability] = useState(50); // Start at 50
  const token = localStorage.getItem("authToken");

  useEffect(() => {
    const fetchChartData = async () => {
      if (!user_id || !token) {
        setLoading(false);
        setError('user_id or token is missing.');
        return;
      }

      setLoading(true);
      const probabilities = Array.from({ length: 51 }, (_, i) => 50 + i); // [50, 51, ..., 100]
      const results = [];

      try {
        for (const min_probability of probabilities) {
          const response = await fetch(`/cfb/model_accuracy_live_with_probability?user_id=${user_id}&model_id=${model_id}&min_probability=${min_probability}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });

          if (!response.ok) {
            throw new Error('Network response was not ok');
          }

          const data = await response.json();
          results.push({ probability: min_probability, accuracy: data.accuracy });
          if (min_probability === minProbability) {
            setTableData(data); // Update table data for selected probability
          }
        }

        // Prepare chart data
        const labels = results.map(item => `${item.probability}%`);
        const data = results.map(item => item.accuracy);

        setChartData({
          labels,
          datasets: [
            {
              label: 'Accuracy (%)',
              data,
              borderColor: 'rgba(75,192,192,1)',
              backgroundColor: 'rgba(75,192,192,0.2)',
            },
          ],
        });
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [user_id, model_id, token, minProbability]);

  const handleProbabilityChange = (e) => {
    setMinProbability(Number(e.target.value));
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div id="live-accuracy-container">
      
      <div id="table-container">
        <div id="table-header">
          <h2>Details for {minProbability}% Probability</h2>
          <div id="probability-filter">
            <label htmlFor="minProbability">Select Min Probability: </label>
            <input
              type="number"
              id="minProbability"
              value={minProbability}
              onChange={handleProbabilityChange}
              min="50"
              max="100"
              step="1"
            />
          </div>
        </div>

        {tableData && (
          <table id="table">
            <thead>
              <tr>
                <th>Accuracy</th>
                <th>Total Predictions</th>
                <th>Correct Predictions</th>
                <th>Positive Predictions</th>
                <th>Correct Positive Predictions</th>
                <th>Negative Predictions</th>
                <th>Correct Negative Predictions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{tableData.accuracy}%</td>
                <td>{tableData.total_predictions}</td>
                <td>{tableData.correct_predictions}</td>
                <td>{tableData.positive_predictions}</td>
                <td>{tableData.correct_pos_predictions}</td>
                <td>{tableData.negative_predictions}</td>
                <td>{tableData.correct_neg_predictions}</td>
              </tr>
            </tbody>
          </table>
        )}
      </div>

      <h1>Live Accuracy Chart and Table</h1>
      <div id="chart-container">
        {chartData && <Line data={chartData} />}
      </div>

      
    </div>
  );
}

export default LiveAccuracy;
