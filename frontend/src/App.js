import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { jacSpawn } from 'jac-client'; // Assuming jac-client has some auth method, or we use fetch
import './App.css';

// Components
import ReportForm from './components/ReportForm';
import OrganisationDashboard from './components/OrganisationDashboard';
import PublicTransparency from './components/PublicTransparency';
import Analytics from './components/Analytics';

function App() {
  const [isLoggedIn, setIsLoggedIn] = React.useState(false);

  useEffect(() => {
    // Auto-login as admin for demo purposes to share the graph
    const login = async () => {
      try {
        // We need to hit the login endpoint. 
        // If jac-client doesn't expose login directly, we use fetch.
        // Assuming the proxy is set up to localhost:8002
        const response = await fetch('/user/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: "admin@publiclens.com", password: "password123" })
        });
        
        if (response.ok) {
            const data = await response.json();
            const token = data.token;
            console.log("Logged in as admin. Token:", token);
            localStorage.setItem('jac_token', token);
            setIsLoggedIn(true);
        } else {
            // Try create if login fails
             const createResponse = await fetch('/user/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: "admin@publiclens.com", password: "password123" })
            });
            if (createResponse.ok) {
                // Login again
                 const loginResponse = await fetch('/user/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: "admin@publiclens.com", password: "password123" })
                });
                if (loginResponse.ok) {
                    const data = await loginResponse.json();
                    localStorage.setItem('jac_token', data.token);
                    setIsLoggedIn(true);
                }
            }
        }
      } catch (error) {
        console.error("Login failed:", error);
        // Allow rendering even if login fails, maybe guest mode works?
        setIsLoggedIn(true); 
      }
    };
    login();
  }, []);

  if (!isLoggedIn) {
      return <div className="loading">Initializing PublicLens...</div>;
  }

  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <Link to="/">PublicLens</Link>
          </div>
          <ul className="nav-links">
            <li><Link to="/">Report Issue</Link></li>
            <li><Link to="/transparency">Public View</Link></li>
            <li><Link to="/dashboard">Org Dashboard</Link></li>
            <li><Link to="/analytics">Analytics</Link></li>
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<ReportForm />} />
            <Route path="/transparency" element={<PublicTransparency />} />
            <Route path="/dashboard" element={<OrganisationDashboard />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;