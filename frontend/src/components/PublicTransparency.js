import React, { useState, useEffect } from 'react';

function PublicTransparency() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('resolved');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchPublicReports();
  }, []);

  const fetchPublicReports = async () => {
    try {
      setLoading(true);
      // Mock data - in real implementation, fetch from backend
      const mockReports = [
        {
          id: '1',
          title: 'Pothole on Main Street',
          description: 'Large pothole causing traffic issues - RESOLVED: Filled and paved',
          status: 'resolved',
          urgency: 'medium',
          category: 'infrastructure',
          submitted_at: '2025-11-15T10:00:00Z',
          resolved_at: '2025-11-20T14:30:00Z',
          resolution_time: '5 days',
          organization: 'Sample Government Agency',
          entities: '{"locations": ["Main Street"]}'
        },
        {
          id: '2',
          title: 'Street Light Out',
          description: 'Street light not working - RESOLVED: Replaced bulb and wiring',
          status: 'resolved',
          urgency: 'low',
          category: 'utility',
          submitted_at: '2025-11-10T15:30:00Z',
          resolved_at: '2025-11-18T09:15:00Z',
          resolution_time: '8 days',
          organization: 'Sample Utility Company',
          entities: '{"locations": ["Elm Street"]}'
        },
        {
          id: '3',
          title: 'Park Bench Damaged',
          description: 'Bench in city park is broken - RESOLVED: Repaired and reinforced',
          status: 'resolved',
          urgency: 'low',
          category: 'infrastructure',
          submitted_at: '2025-11-05T12:00:00Z',
          resolved_at: '2025-11-12T16:45:00Z',
          resolution_time: '7 days',
          organization: 'Sample Government Agency',
          entities: '{"locations": ["City Park"]}'
        }
      ];
      setReports(mockReports);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredReports = reports.filter(report => {
    const matchesFilter = filter === 'all' || report.status === filter;
    const matchesSearch = searchTerm === '' ||
      report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const redactSensitiveInfo = (text) => {
    // Privacy controls - redact sensitive information
    return text.replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[REDACTED]')
               .replace(/\b\d{16}\b/g, '[REDACTED]')
               .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[EMAIL REDACTED]');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return 'status-resolved';
      case 'in-progress': return 'status-progress';
      default: return 'status-default';
    }
  };

  if (loading) {
    return <div className="loading">Loading public reports...</div>;
  }

  return (
    <div className="public-transparency">
      <h1>Public Transparency</h1>
      <p>View resolved reports and track government responsiveness</p>

      <div className="transparency-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-controls">
          <label>Status:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="resolved">Resolved</option>
            <option value="in-progress">In Progress</option>
            <option value="all">All Public Reports</option>
          </select>
        </div>
      </div>

      <div className="transparency-stats">
        <div className="stat-card">
          <h3>{reports.filter(r => r.status === 'resolved').length}</h3>
          <p>Resolved Reports</p>
        </div>
        <div className="stat-card">
          <h3>{Math.round(reports.reduce((acc, r) => acc + parseInt(r.resolution_time), 0) / reports.length)} days</h3>
          <p>Average Resolution Time</p>
        </div>
        <div className="stat-card">
          <h3>{new Set(reports.map(r => r.organization)).size}</h3>
          <p>Organizations Involved</p>
        </div>
      </div>

      <div className="reports-grid">
        {filteredReports.length === 0 ? (
          <p className="no-reports">No reports found matching your criteria.</p>
        ) : (
          filteredReports.map(report => (
            <div key={report.id} className="public-report-card">
              <div className="report-header">
                <h3>{redactSensitiveInfo(report.title)}</h3>
                <span className={`status-badge ${getStatusColor(report.status)}`}>
                  {report.status}
                </span>
              </div>

              <div className="report-meta">
                <span className="organization">Handled by: {report.organization}</span>
                <span className="resolution-time">Resolved in: {report.resolution_time}</span>
                <span className="date">
                  Submitted: {new Date(report.submitted_at).toLocaleDateString()}
                </span>
              </div>

              <p className="report-description">
                {redactSensitiveInfo(report.description)}
              </p>

              <div className="report-footer">
                <span className="category">Category: {report.category}</span>
                <span className="urgency">Urgency: {report.urgency}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default PublicTransparency;