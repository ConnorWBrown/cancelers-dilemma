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
// import { generate } from "random-words";
import './App.css';
import { v4 as uuidv4 } from 'uuid';

// Use env var for backend base URL so we can swap between local dev and cluster easily.
// Example: REACT_APP_API_URL=http://127.0.0.1:49831 npm start
const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';



function App() {
  const [clicked, setClicked] = useState(false);
  const [result, setResult] = useState('');
  const [waiting, setWaiting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [playerId, setPlayerId] = useState(() => {
    return localStorage.getItem('playerId') || 'player1';
  });
  const [gameId, setGameId] = useState(() => {
    // Priority: URL query param (?gameId=...) or bare query (?<id>) -> localStorage -> new uuid
    try {
      const params = new URLSearchParams(window.location.search);
      // check explicit key
      let id = params.get('gameId') || params.get('id');
      if (!id) {
        // handle bare query like /?8a7f... (no key)
        const raw = window.location.search.replace(/^\?/, '');
        if (raw) {
          id = raw;
        }
      }
      if (id) {
        return id;
      }
    } catch (e) {
      // ignore and fallback
    }
    return localStorage.getItem('gameId');
  });

  useEffect(() => {
    localStorage.setItem('playerId', playerId);
  }, [playerId]);

  useEffect(() => {
    // persist gameId so reloads keep the same game unless overridden by URL
    if (gameId) localStorage.setItem('gameId', gameId);
  }, [gameId]);

  useEffect(() => {
    // reflect current gameId in the URL so it can be shared: /?{gameId}
    try {
      const newSearch = '?' + encodeURIComponent(gameId);
      if (window.location.search !== newSearch) {
        window.history.replaceState(null, '', window.location.pathname + newSearch);
      }
    } catch (e) {
      // ignore
    }
  }, [gameId]);

  const newEvent = async () => {
    setGameId(uuidv4().substring(0, 8));
  };

  const handleSubmit = async () => {
    setWaiting(true);
    setSubmitted(true);
    try {
      // const response = await axios.post('http://172.20.10.2:5000/submit', {
      // const response = await axios.post('http://backend.cancelers-dilemma.svc.cluster.local:5000/submit', {
      // include gameId so backend can persist multiple gamestates
      const response = await axios.post(`${API_BASE}/submit`, {
        player_id: playerId,
        clicked: clicked,
        game_id: gameId,
      });

      if (response.data.waiting) {
        const interval = setInterval(async () => {
          try {
            // Poll using gameId so we get the right gamestate
            const res = await axios.get(`${API_BASE}/result/${gameId}/${playerId}`);
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
      {/* <div>Current event: {generate({ exactly: 3, join:"-", minLength: 4, maxLength: 5, seed:gameId })}</div> */}
      <div>Current event: {gameId}</div>
      <button onClick={newEvent} >Create New Event</button>
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