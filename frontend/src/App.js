import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, Link } from 'react-router-dom';
import Login from './Login';
import Register from './Register';
import Upload from './Upload';
import About from './About';
import './App.css'; // Ensure App.css is imported for styling

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Handler for the AI Model link
  const handleAiModelClick = (e) => {
    if (!isAuthenticated) {
      e.preventDefault();
      alert('login first');
    }
  };

  return (
    <Router>
      <nav style={{ margin: '10px' }}>
        <Link to="/login" style={{ marginRight: '10px' }}>Login</Link>
        <Link to="/register" style={{ marginRight: '10px' }}>Register</Link>
        <Link to="/upload" style={{ marginRight: '10px' }} onClick={handleAiModelClick}>Use the AI Model</Link>
        <Link to="/about">About</Link>
      </nav>
      <Routes>
        <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/upload" element={isAuthenticated ? <Upload /> : <Navigate to="/login" />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

export default App;