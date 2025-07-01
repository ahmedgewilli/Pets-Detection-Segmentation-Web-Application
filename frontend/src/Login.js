import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from './api';

function Login({ setIsAuthenticated }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await login(username, password);
      if (res.token) {
        localStorage.setItem('token', res.token);
        setIsAuthenticated(true);
        navigate('/upload'); // ✅ Redirect to /upload
      } else {
        setError(res.error || 'Login failed');
      }
    } catch (err) {
      setError('Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={username}
        onChange={e => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
}

export default Login;
