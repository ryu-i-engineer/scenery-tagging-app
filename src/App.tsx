import React from 'react';
import './App.css';
import logo from './assets/images/ryuina.jpg';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Scenery Tagging Service(Demo)</h1>
        <img src={logo} className="App-logo" alt="logo" />
        <label htmlFor="uploadImage">Select a scenery photo(JPG/JPEG only)</label>
        <input type="file" id='uploadImage' className='uploadImage' accept='.jpg, .jepg' />

      </header>
    </div>
  );
}

export default App;
