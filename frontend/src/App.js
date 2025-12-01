import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { jacSpawn } from 'jac-client';
import './App.css';
import './App.css';

// Components
import ReportForm from './components/ReportForm';
import OrganisationDashboard from './components/OrganisationDashboard';
import PublicTransparency from './components/PublicTransparency';
import Analytics from './components/Analytics';

function App() {
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