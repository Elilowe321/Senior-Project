import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Line } from 'react-chartjs-2';
import '../../games/games.css';
import '../../../assets/styles/tables.css';
import './TestAccuracy.css'
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

function TestAccuracy() {
  const { user_id, model_id } = useParams();
  const [gameData, setGameData] = useState({});
  const [minProbability, setMinProbability] = useState(0); // State for minimum probability filter
  const [submittedProbability, setSubmittedProbability] = useState(0); // Track submitted value

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const token = useMemo(() => localStorage.getItem("authToken"), []);


  const handleProbabilityChange = (e) => {
    setMinProbability(Number(e.target.value)); // Update the input value
  };

  const handleSubmit = (e) => {
    e.preventDefault(); // Prevent page refresh on submit
    setSubmittedProbability(minProbability); // Set submitted value to trigger data fetch
  };

  useEffect(() => {
    const fetchGameData = async () => {
      if (!user_id || !token) {
        setLoading(false);
        setError('user_id or token is null or undefined.');
        return;
      }
  
      setLoading(true); // Trigger loading state before making the request
  
      try {
        console.log('Fetching data...');
  
        // Fetch data for all combinations in a single request
        const response = await fetch(`/cfb/test-accuracy?user_id=${user_id}&model_id=${model_id}&min_probability=${submittedProbability}`, { 
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
        console.log(data);
  
        // Structure data by year and safe_bet
        const structuredData = data.reduce((acc, item) => {
          const { year, safe_bet } = item;
          if (!acc[year]) acc[year] = {};
          acc[year][safe_bet] = item;
          return acc;
        }, {});
  
        setGameData(structuredData);
      } catch (error) {
        console.log("Error fetching data:", error);
        setError('Error fetching data');
      } finally {
        setLoading(false); // Turn off the loading state when fetching is done
      }
    };
  
    fetchGameData();
  }, [user_id, model_id, token, submittedProbability]); // Include submittedProbability as a dependency


  const generateChartData = (weeklyStats) => {
    if (!weeklyStats) return { weeklyData: null, cumulativeData: null };
  
    const labels = weeklyStats.map(week => `Week ${week.week}`);
    const totalWeeklyProfit = weeklyStats.map(week => week.profit);
    const totalCumulativeProfit = totalWeeklyProfit.reduce((acc, profit, index) => {
      acc.push((acc[index - 1] || 0) + profit);
      return acc;
    }, []);
    
    const negOddsWeeklyProfit = weeklyStats.map(week => week.profit_neg_odds);
    const negOddsCumulativeProfit = negOddsWeeklyProfit.reduce((acc, profit, index) => {
      acc.push((acc[index - 1] || 0) + profit);
      return acc;
    }, []);
    
    const posOddsWeeklyProfit = weeklyStats.map(week => week.profit_pos_odds);
    const posOddsCumulativeProfit = posOddsWeeklyProfit.reduce((acc, profit, index) => {
      acc.push((acc[index - 1] || 0) + profit);
      return acc;
    }, []);
  
    return {
      weeklyData: {
        labels,
        datasets: [
          {
            label: 'Total Weekly Profit',
            data: totalWeeklyProfit,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
          },
          {
            label: 'Negative Odds Weekly Profit',
            data: negOddsWeeklyProfit,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
          },
          {
            label: 'Positive Odds Weekly Profit',
            data: posOddsWeeklyProfit,
            borderColor: 'rgba(153, 102, 255, 1)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
          },
        ],
      },
      cumulativeData: {
        labels,
        datasets: [
          {
            label: 'Total Cumulative Profit',
            data: totalCumulativeProfit,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
          },
          {
            label: 'Negative Odds Cumulative Profit',
            data: negOddsCumulativeProfit,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
          },
          {
            label: 'Positive Odds Cumulative Profit',
            data: posOddsCumulativeProfit,
            borderColor: 'rgba(153, 102, 255, 1)',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
          },
        ],
      }
    };
  };

  const renderTable = (data, key) => (
    <div id='table-container'>
      <div id='table-header'>
        <h1 id='table-title'>{`Data for ${key}`}</h1>
      </div>
      <table id='table'>
        <thead>
          <tr>
            <th>Week</th>
            <th>Total Predictions</th>
            <th>Correct Predictions</th>
            <th>Money In</th>
            <th>Profit</th>
            <th>Total Out</th>
            <th>Negative Odds Predictions</th>
            <th>Negative Odds Correct</th>
            <th>Negative Odds Money In</th>
            <th>Negative Odds Profit</th>
            <th>Negative Odds Total Out</th>
            <th>Positive Odds Predictions</th>
            <th>Positive Odds Correct</th>
            <th>Positive Odds Money In</th>
            <th>Positive Odds Profit</th>
            <th>Positive Odds Total Out</th>
          </tr>
        </thead>
        <tbody>
          {data.weekly_stats?.map((week, index) => (
            <tr key={index}>
              <td>{week.week}</td>
              <td>{week.total_predictions}</td>
              <td>{week.correct_predictions}</td>
              <td>{week.money_in.toFixed(2)}</td>
              <td>{week.profit.toFixed(2)}</td>
              <td>{week.total_out.toFixed(2)}</td>
              <td>{week.total_predictions_neg_odds}</td>
              <td>{week.correct_predictions_neg_odds}</td>
              <td>{week.money_in_neg_odds.toFixed(2)}</td>
              <td>{week.profit_neg_odds.toFixed(2)}</td>
              <td>{week.total_out_neg_odds.toFixed(2)}</td>
              <td>{week.total_predictions_pos_odds}</td>
              <td>{week.correct_predictions_pos_odds}</td>
              <td>{week.money_in_pos_odds.toFixed(2)}</td>
              <td>{week.profit_pos_odds.toFixed(2)}</td>
              <td>{week.total_out_pos_odds.toFixed(2)}</td>
            </tr>
          ))}
          <tr>
            <td>Total</td>
            <td>{data.total_predictions}</td>
            <td>{data.correct_predictions}</td>
            <td>{data.money_in?.toFixed(2)}</td>
            <td>{data.profit?.toFixed(2)}</td>
            <td>{data.total_out?.toFixed(2)}</td>
            <td>{data.negative_odds?.total_predictions}</td>
            <td>{data.negative_odds?.correct_predictions}</td>
            <td>{data.negative_odds?.money_in?.toFixed(2)}</td>
            <td>{data.negative_odds?.profit?.toFixed(2)}</td>
            <td>{data.negative_odds?.total_out?.toFixed(2)}</td>
            <td>{data.positive_odds?.total_predictions}</td>
            <td>{data.positive_odds?.correct_predictions}</td>
            <td>{data.positive_odds?.money_in?.toFixed(2)}</td>
            <td>{data.positive_odds?.profit?.toFixed(2)}</td>
            <td>{data.positive_odds?.total_out?.toFixed(2)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );

  return (
    
    <div className='games-home'>
      {loading ? (
        <div>
          <p>May take up to 3 minutes</p>
          <div className='loader-back'>
            <div className='loader'></div>
          </div>
        </div>
      ) : error ? (
        <div>
          <p>Error: {error}</p>
        </div>
      ) : Object.keys(gameData).length > 0 ? (
        <>

          <form onSubmit={handleSubmit}>
            <div id='probability-filter'>
              Select a min probability for chosen bets
              <label htmlFor="minProbability"> </label>
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
          <div id='tables-charts-container'>
            {Object.entries(gameData).map(([year, safeBets]) => (
              Object.entries(safeBets).map(([safeBet, data]) => {
                const { weeklyData, cumulativeData } = generateChartData(data.weekly_stats);
                return (
                  <div key={`${year}-${safeBet}`}>
                    {renderTable(data, `${year}`)}
                    <div id='chart-only-conatiner'>
                      <div id='chart'>
                        <h2>Weekly Profit</h2>
                        <Line
                          data={weeklyData}
                          // width={400}
                          // height={300}
                          options={{
                            scales: {
                              x: {
                                title: {
                                  display: true,
                                  text: 'Weeks'
                                }
                              },
                              y: {
                                title: {
                                  display: true,
                                  text: 'Profit ($)'
                                }
                              }
                            }
                          }}
                        />
                      </div>
                      <div id='chart'>
                        <h2>Cumulative Profit</h2>
                        <Line
                          data={cumulativeData}
                          // width={800}
                          // height={600}
                          options={{
                            scales: {
                              x: {
                                title: {
                                  display: true,
                                  text: 'Weeks'
                                }
                              },
                              y: {
                                title: {
                                  display: true,
                                  text: 'Cumulative Profit ($)'
                                }
                              }
                            }
                          }}
                        />
                      </div>
                      </div>
                  </div>
                );
              })
            ))}
          </div>
        </>
      ) : (
        <div>
          <p>No data available</p>
        </div>
      )}
    </div>
  );
}

export default TestAccuracy
