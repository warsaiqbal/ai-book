// Login page component for Docusaurus
import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    // Ensure we're running on the client side
    setIsClient(true);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    // In a real implementation, this would call an API
    // This is simplified for demonstration
    if (username === 'student' && password === 'robotics123') {
      // Store user in localStorage
      localStorage.setItem('user', JSON.stringify({ username }));
      // Redirect to the homepage after login
      window.location.href = '/';
    } else {
      setError('Invalid credentials. Please try again.');
    }
  };

  // Only render the form if we're on the client side
  if (!isClient) {
    return (
      <Layout title="Login" description="Login to access the Physical AI & Humanoid Robotics course content">
        <div className="container margin-vert--lg">
          <div className="row">
            <div className="col col--6 col--offset-3">
              <h1>Login to Course Content</h1>
              <p>Loading login form...</p>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Login" description="Login to access the Physical AI & Humanoid Robotics course content">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--6 col--offset-3">
            <h1>Login to Course Content</h1>
            <form onSubmit={handleSubmit}>
              <div className="margin-bottom--md">
                <label htmlFor="username">Username</label>
                <input
                  id="username"
                  type="text"
                  className="form-control"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="margin-bottom--md">
                <label htmlFor="password">Password</label>
                <input
                  id="password"
                  type="password"
                  className="form-control"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && (
                <div className="alert alert--danger" role="alert">
                  {error}
                </div>
              )}
              <button type="submit" className="button button--primary">
                Login
              </button>
            </form>

            <div className="margin-top--lg">
              <p>Don't have an account? <a href="/register">Register here</a></p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}