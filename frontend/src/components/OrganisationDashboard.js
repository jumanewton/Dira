import React, { useState, useEffect } from 'react';
import { jacSpawn } from 'jac-client';

function OrganisationDashboard() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedOrg, setSelectedOrg] = useState('Sample Government Agency');

  useEffect(() => {
    fetchReports();
  }, [selectedOrg]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call a walker to get reports for the organization
      // For now, we'll simulate with mock data
      const mockReports = [
        {
          id: '1',
          title: 'Pothole on Main Street',
          description: 'Large pothole causing traffic issues',
          status: 'routed',
          urgency: 'medium',
          category: 'infrastructure',
          submitted_at: '2025-12-01T10:00:00Z',
          entities: '{"locations": ["Main Street"]}'
        },
        {
          id: '2',
          title: 'Street Light Out',
          description: 'Street light not working for 3 days',
          status: 'routed',
          urgency: 'low',
          category: 'utility',
          submitted_at: '2025-11-30T15:30:00Z',
          entities: '{"locations": ["Elm Street"]}'
        }
      ];
      setReports(mockReports);
    } catch (error) {
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateReportStatus = async (reportId, newStatus) => {
    try {
      // Call walker to update report status
      await jacSpawn('StatusUpdateAgent', '', {
        report_id: reportId,
        status: newStatus
      });

      // Update local state
      setReports(reports.map(report =>
        report.id === reportId ? { ...report, status: newStatus } : report
      ));
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const filteredReports = reports.filter(report => {
    if (filter === 'all') return true;
    return report.status === filter;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'submitted': return 'status-submitted';
      case 'classified': return 'status-classified';
      case 'routed': return 'status-routed';
      case 'resolved': return 'status-resolved';
      default: return 'status-default';
    }
  };

  const redactSensitiveInfo = (text) => {
    // Simple redaction - in production, use more sophisticated NLP
    return text.replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[REDACTED SSN]')
               .replace(/\b\d{16}\b/g, '[REDACTED CARD]');
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="org-dashboard">
      <h1>Organization Dashboard</h1>
      <p>Manage reports assigned to your organization</p>

      <div className="dashboard-controls">
        <div className="org-selector">
          <label>Organization:</label>
          <select value={selectedOrg} onChange={(e) => setSelectedOrg(e.target.value)}>
            <option value="Sample Government Agency">Sample Government Agency</option>
            <option value="Sample Utility Company">Sample Utility Company</option>
          </select>
        </div>

        <div className="filter-controls">
          <label>Filter by status:</label>
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Reports</option>
            <option value="routed">Routed</option>
            <option value="resolved">Resolved</option>
            <option value="in-progress">In Progress</option>
          </select>
        </div>
      </div>

      <div className="reports-list">
        {filteredReports.length === 0 ? (
          <p className="no-reports">No reports found for the selected criteria.</p>
        ) : (
          filteredReports.map(report => (
            <div key={report.id} className="report-card">
              <div className="report-header">
                <h3>{redactSensitiveInfo(report.title)}</h3>
                <span className={`status-badge ${getStatusColor(report.status)}`}>
                  {report.status}
                </span>
              </div>

              <div className="report-meta">
                <span className="urgency">Urgency: {report.urgency}</span>
                <span className="category">Category: {report.category}</span>
                <span className="date">
                  Submitted: {new Date(report.submitted_at).toLocaleDateString()}
                </span>
              </div>

              <p className="report-description">
                {redactSensitiveInfo(report.description)}
              </p>

              <div className="report-actions">
                {report.status === 'routed' && (
                  <button
                    onClick={() => updateReportStatus(report.id, 'in-progress')}
                    className="btn-primary"
                  >
                    Start Working
                  </button>
                )}
                {report.status === 'in-progress' && (
                  <button
                    onClick={() => updateReportStatus(report.id, 'resolved')}
                    className="btn-success"
                  >
                    Mark Resolved
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default OrganisationDashboard;