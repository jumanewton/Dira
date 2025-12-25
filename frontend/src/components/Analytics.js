import React, { useState, useEffect } from 'react';
import { runWalker } from '../jacService';
import ReactMarkdown from 'react-markdown';

function Analytics() {
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);
  const [aiInsights, setAiInsights] = useState('');
  const [generatingInsights, setGeneratingInsights] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await runWalker('get_analytics', {});
      
      let data = {};
      if (response.reports && Array.isArray(response.reports) && response.reports.length > 0) {
          data = response.reports[0];
      } else if (response.report && Array.isArray(response.report) && response.report.length > 0) {
          data = response.report[0];
      } else if (response.result && response.result.metrics) {
          data = response.result.metrics;
      } else {
          data = response;
      }

      // Ensure default values to prevent crashes
      const safeData = {
          totalReports: data.totalReports || 0,
          uniqueReports: data.uniqueReports || 0,
          duplicateReports: data.duplicateReports || 0,
          resolvedReports: data.resolvedReports || 0,
          avgResolutionTime: data.avgResolutionTime || 0,
          reportsByCategory: data.reportsByCategory || {},
          reportsByUrgency: data.reportsByUrgency || {},
          reportsByStatus: data.reportsByStatus || {},
          monthlyTrend: data.monthlyTrend || []
      };

      setMetrics(safeData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Set empty defaults on error
      setMetrics({
          totalReports: 0,
          uniqueReports: 0,
          duplicateReports: 0,
          resolvedReports: 0,
          avgResolutionTime: 0,
          reportsByCategory: {},
          reportsByUrgency: {},
          reportsByStatus: {},
          monthlyTrend: []
      });
    } finally {
      setLoading(false);
    }
  };

  const generateAIInsights = async () => {
    try {
      setGeneratingInsights(true);
      const response = await runWalker('generate_ai_insights', { metrics: metrics });
      
      let insights = "No insights generated.";
      if (response.insights) insights = response.insights;
      else if (response.report && response.report[0] && response.report[0].insights) insights = response.report[0].insights;
      else if (response.reports && response.reports[0] && response.reports[0].insights) insights = response.reports[0].insights;

      setAiInsights(insights);
    } catch (error) {
      console.error("Error generating AI insights:", error);
      setAiInsights("Failed to generate AI insights. Please try again.");
    } finally {
      setGeneratingInsights(false);
    }
  };

  const renderBarChart = (data, title, color = '#4CAF50') => {
    if (!data || Object.keys(data).length === 0) {
        return (
            <div className="chart-container">
                <h4>{title}</h4>
                <p>No data available</p>
            </div>
        );
    }
    const maxValue = Math.max(...Object.values(data));
    return (
      <div className="chart-container">
        <h4>{title}</h4>
        <div className="bar-chart">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="bar-item">
              <div className="bar-label">{key}</div>
              <div className="bar-container">
                <div
                  className="bar"
                  style={{
                    width: `${(value / maxValue) * 100}%`,
                    backgroundColor: color
                  }}
                >
                  <span className="bar-value">{value}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTrendChart = (data) => {
    const maxReports = Math.max(...data.map(d => d.reports));
    return (
      <div className="chart-container">
        <h4>Monthly Trend</h4>
        <div className="trend-chart">
          {data.map((item, index) => (
            <div key={index} className="trend-item">
              <div className="trend-label">{item.month}</div>
              <div className="trend-bars">
                <div
                  className="trend-bar reports"
                  style={{ height: `${(item.reports / maxReports) * 100}%` }}
                  title={`Reports: ${item.reports}`}
                >
                  <span className="trend-value">{item.reports}</span>
                </div>
                <div
                  className="trend-bar resolved"
                  style={{ height: `${(item.resolved / maxReports) * 100}%` }}
                  title={`Resolved: ${item.resolved}`}
                >
                  <span className="trend-value">{item.resolved}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="trend-legend">
          <div className="legend-item">
            <div className="legend-color reports"></div>
            <span>Reports Submitted</span>
          </div>
          <div className="legend-item">
            <div className="legend-color resolved"></div>
            <span>Reports Resolved</span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  const resolutionRate = metrics.uniqueReports > 0 
    ? ((metrics.resolvedReports / metrics.uniqueReports) * 100).toFixed(1) 
    : "0.0";

  // Dynamic Insight Calculations
  let mostCommonCategory = "N/A";
  if (metrics.reportsByCategory && Object.keys(metrics.reportsByCategory).length > 0) {
      mostCommonCategory = Object.entries(metrics.reportsByCategory)
          .sort((a, b) => b[1] - a[1])[0][0];
  }

  let trendMessage = "Data insufficient for trend analysis.";
  if (metrics.monthlyTrend && metrics.monthlyTrend.length >= 2) {
      const current = metrics.monthlyTrend[metrics.monthlyTrend.length - 1].reports;
      const previous = metrics.monthlyTrend[metrics.monthlyTrend.length - 2].reports;
      if (previous > 0) {
          const change = ((current - previous) / previous) * 100;
          trendMessage = `Report submissions have ${change >= 0 ? 'increased' : 'decreased'} by ${Math.abs(change).toFixed(0)}% compared to last month.`;
      } else {
          trendMessage = "Report submissions are increasing from zero baseline.";
      }
  } else if (metrics.monthlyTrend && metrics.monthlyTrend.length === 1) {
      trendMessage = "First month of data collection established.";
  }

  return (
    <div className="analytics">
      <h1>Analytics Dashboard</h1>
      <p>Insights into public reporting patterns and resolution metrics</p>

      <div className="metrics-overview">
        <div className="metric-card">
          <h2>{metrics.totalReports}</h2>
          <p>Total Submissions</p>
        </div>
        <div className="metric-card">
          <h2>{metrics.uniqueReports}</h2>
          <p>Unique Issues</p>
        </div>
        <div className="metric-card">
          <h2>{metrics.duplicateReports}</h2>
          <p>Duplicates</p>
        </div>
        <div className="metric-card">
          <h2>{metrics.resolvedReports}</h2>
          <p>Resolved Reports</p>
        </div>
        <div className="metric-card">
          <h2>{resolutionRate}%</h2>
          <p>Resolution Rate</p>
        </div>
        <div className="metric-card">
          <h2>{metrics.avgResolutionTime} days</h2>
          <p>Avg Resolution Time</p>
        </div>
      </div>

      <div className="charts-grid">
        {renderBarChart(metrics.reportsByCategory, 'Reports by Category', '#2196F3')}
        {renderBarChart(metrics.reportsByUrgency, 'Reports by Urgency', '#FF9800')}
        {renderBarChart(metrics.reportsByStatus, 'Reports by Status', '#4CAF50')}
        {renderTrendChart(metrics.monthlyTrend)}
      </div>

      <div className="insights-section">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
            <h3>Key Insights</h3>
            <button 
                onClick={generateAIInsights} 
                disabled={generatingInsights}
                className="ai-insights-btn"
            >
                {generatingInsights ? '🔄 Generating...' : '✨ Generate AI Executive Summary'}
            </button>
        </div>

        {aiInsights && (
            <div className="insight-card" style={{marginBottom: '20px', borderLeft: '6px solid #4CAF50', backgroundColor: 'var(--card-bg)', border: '1px solid var(--border-color)'}}>
                <h4 style={{color: '#4CAF50', display: 'flex', alignItems: 'center', gap: '8px'}}>
                    <span>🤖</span> AI Executive Summary
                </h4>
                <div style={{lineHeight: '1.6', color: 'var(--text-primary)'}}>
                    <ReactMarkdown>{aiInsights}</ReactMarkdown>
                </div>
            </div>
        )}

        <div className="insights-grid">
          <div className="insight-card">
            <h4>Most Common Issues</h4>
            <p><strong>{mostCommonCategory}</strong> issues represent the largest category of reports, indicating areas where public services need improvement.</p>
          </div>
          <div className="insight-card">
            <h4>Response Efficiency</h4>
            <p>The average resolution time of <strong>{metrics.avgResolutionTime} days</strong> shows {metrics.avgResolutionTime < 5 ? "excellent" : "standard"} responsiveness to public concerns.</p>
          </div>
          <div className="insight-card">
            <h4>Trending</h4>
            <p>{trendMessage}</p>
          </div>
          <div className="insight-card">
            <h4>Resolution Rate</h4>
            <p>With a <strong>{resolutionRate}%</strong> resolution rate, the system is {parseFloat(resolutionRate) > 50 ? "effectively" : "working on"} addressing reported issues.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;