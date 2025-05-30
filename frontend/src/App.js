// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [clicked, setClicked] = useState(false);
  const [result, setResult] = useState('');
  const [waiting, setWaiting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [playerId, setPlayerId] = useState(() => {
    return localStorage.getItem('playerId') || 'player1';
  });

  useEffect(() => {
    localStorage.setItem('playerId', playerId);
  }, [playerId]);

  const handleSubmit = async () => {
    setWaiting(true);
    setSubmitted(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/submit', {
        player_id: playerId,
        clicked: clicked,
      });

      if (response.data.waiting) {
        const interval = setInterval(async () => {
          try {
            const res = await axios.get(`http://127.0.0.1:5000/result/${playerId}`);
            if (res.data.result) {
              clearInterval(interval);
              setResult(res.data.result);
              setWaiting(false);
            }
          } catch (error) {
            console.error('Polling error:', error);
          }
        }, 1000);
      } else {
        setResult(response.data.result);
        setWaiting(false);
      }
    } catch (err) {
      console.error('Submit error:', err);
      setWaiting(false);
    }
  };

  return (
    <div className="App">
      <h1>Canceler's Dilemma</h1>

      <div>
        <label>
          <input
            type="radio"
            value="player1"
            checked={playerId === 'player1'}
            onChange={() => setPlayerId('player1')}
            disabled={submitted}
          />
          Player 1
        </label>
        <label>
          <input
            type="radio"
            value="player2"
            checked={playerId === 'player2'}
            onChange={() => setPlayerId('player2')}
            disabled={submitted}
          />
          Player 2
        </label>
      </div>

      <div>
        <label>
          Yes
          <input
            type="checkbox"
            checked={clicked}
            onChange={() => setClicked(!clicked)}
            disabled={submitted}
          />
        </label>
      </div>

      <button onClick={handleSubmit} disabled={submitted}>Go</button>

      {waiting && <p>Waiting for the other player...</p>}
      {result && <p><strong>{result}</strong></p>}
    </div>
  );
}

export default App;