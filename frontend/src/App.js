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
      // const response = await axios.post('http://172.20.10.2:5000/submit', {
      // const response = await axios.post('http://backend.cancelers-dilemma.svc.cluster.local:5000/submit', {
      const response = await axios.post('http://192.168.49.2:30500/submit', {
        player_id: playerId,
        clicked: clicked,
      });

      if (response.data.waiting) {
        const interval = setInterval(async () => {
          try {
            // const res = await axios.get(`http://172.20.10.2:5000/result/${playerId}`);
            // const res = await axios.get(`http://backend.cancelers-dilemma.svc.cluster.local:5000/result/${playerId}`);
            const res = await axios.get(`http://192.168.49.2:30500/result/${playerId}`);
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
    <div className={`App ${clicked ? 'dark' : 'light'}`}>
      <div className="box">
      <h1>Canceler's Dilemma</h1>

      <div className="player-select">
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

      <div className="container">
        <div className="slider-wrapper">
          <span>To Hang</span>
          <label className="switch">
            <input
              type="checkbox"
              checked={clicked}
              onChange={() => setClicked(!clicked)}
              disabled={submitted}
            />
            <span className="slider round"></span>
          </label>
          <span>or Not to Hang</span>
        </div>
      </div> 
      <button onClick={handleSubmit} disabled={submitted}>Go</button>

      {waiting && <p>⏳ Waiting for the other player...</p>}
      {result && <p className="result"><strong>{result}</strong></p>}
    </div>
    </div>
  );
}

export default App;