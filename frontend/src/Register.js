import React, { useState } from 'react';
import { register } from './api';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault(); // ⛔ Prevent default GET form behavior
    setMessage('');
    setError('');
    try {
      const res = await register(username, password);
      if (res.error) {
        setError(res.error);
      } else {
        setMessage('Registered! Please login.');
      }
    } catch (err) {
      console.error(err);
      setError('Registration failed.');
    }
  };

  return (
    <form onSubmit={handleSubmit} autoComplete="off">
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        autoComplete="username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        autoComplete="new-password"
      />
      <button type="submit">Register</button>
      {message && <div style={{ color: 'green' }}>{message}</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
}

export default Register;
