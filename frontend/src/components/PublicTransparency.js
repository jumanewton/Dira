import React, { useState, useEffect } from 'react';
import { runWalker } from '../jacService';

function PublicTransparency() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [trackId, setTrackId] = useState('');
  const [trackResult, setTrackResult] = useState(null);

  useEffect(() => {
    fetchPublicReports();
  }, []);

  const fetchPublicReports = async () => {
    try {
      setLoading(true);
      const response = await runWalker('get_public_reports', {});
      
      let reportsList = [];
      if (response.reports && Array.isArray(response.reports)) {
          reportsList = Array.isArray(response.reports[0]) ? response.reports[0] : response.reports;
      } else if (response.report && Array.isArray(response.report)) {
          // Jac returns a list of reports, so we need to take the first element if it's a list of lists
          // response.report is typically [[{...}, {...}]]
          reportsList = Array.isArray(response.report[0]) ? response.report[0] : response.report;
      } else if (Array.isArray(response)) {
          reportsList = response;
      }

      // Add mock data if list is empty for demo purposes
      if (reportsList.length === 0) {
          reportsList = [
            {
              id: '1',
              title: 'Pothole on Main Street',
              description: 'Large pothole causing traffic issues - RESOLVED: Filled and paved',
              status: 'resolved',
              urgency: 'medium',
              category: 'infrastructure',
              submitted_at: '2025-11-15T10:00:00Z',
              resolution_time: '5 days',
              organization: 'Sample Government Agency'
            }
          ];
      }

      // Sort by date (newest first) and limit to max 25 reports
      reportsList.sort((a, b) => new Date(b.submitted_at) - new Date(a.submitted_at));
      reportsList = reportsList.slice(0, 25);

      setReports(reportsList);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTrackReport = async (e) => {
      e.preventDefault();
      if (!trackId) return;
      
      try {
          const response = await runWalker('get_report_status', { report_id: trackId });
          let result = null;
          
          // Check for reports array (standard Jac response)
          if (response.reports && Array.isArray(response.reports) && response.reports.length > 0) {
              result = response.reports[0];
          } else if (response.report && Array.isArray(response.report) && response.report.length > 0) {
              result = response.report[0];
          } else if (response.result && response.result.found_report && Object.keys(response.result.found_report).length > 0) {
              // Fallback: check if found_report is in the result object (if reports array is empty)
              result = response.result.found_report;
          } else {
              result = { error: "Report not found" };
          }
          
          setTrackResult(result);
      } catch (error) {
          setTrackResult({ error: error.message });
      }
  };

  const filteredReports = reports.filter(report => {
    // If a report is being tracked and found, filter to show only that report
    if (trackResult && trackResult.id && !trackResult.error) {
        return report.id === trackResult.id;
    }

    const matchesFilter = filter === 'all' || report.status === filter;
    const matchesSearch = searchTerm === '' ||
      (report.title && report.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (report.description && report.description.toLowerCase().includes(searchTerm.toLowerCase()));
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
        <div className="track-box">
            <h3>Track Your Report</h3>
            <form onSubmit={handleTrackReport} className="track-form">
                <input 
                    type="text" 
                    placeholder="Enter Report ID" 
                    value={trackId}
                    onChange={(e) => {
                        setTrackId(e.target.value);
                        // Clear track result when user types to reset filter
                        if (trackResult) setTrackResult(null);
                    }}
                />
                <button type="submit">Track</button>
            </form>
            {trackResult && (
                <div className="track-result">
                    {trackResult.error ? (
                        <p className="error">{trackResult.error}</p>
                    ) : (
                        <div className="status-card">
                            <p><strong>Status:</strong> {trackResult.status}</p>
                            <p><strong>Category:</strong> {trackResult.category}</p>
                            <p><strong>Urgency:</strong> {trackResult.urgency}</p>
                        </div>
                    )}
                </div>
            )}
        </div>

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