
// React Frontend - basic structure using create-react-app
// Pages: Login, Register, Upload, About
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './Login';
import Register from './Register';
import Upload from './Upload';
import About from './About';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Router>
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