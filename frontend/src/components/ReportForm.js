import React, { useState } from 'react';
import { runWalker } from '../jacService';

function ReportForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    name: '',
    email: '',
    anonymous: true,
    image_data: ''
  });
  const [status, setStatus] = useState('');
  const [analysis, setAnalysis] = useState('');

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({
          ...prev,
          image_data: reader.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Submitting...');
    setAnalysis('');

    try {
      // Call IntakeAgent walker
      const response = await runWalker('IntakeAgent', {
        report_data: {
          title: formData.title,
          description: formData.description,
          name: formData.anonymous ? '' : formData.name,
          email: formData.anonymous ? '' : formData.email,
          image_data: formData.image_data
        }
      });

      // console.log("Submission response:", response);
      
      // Handle different response structures
      let reportId = "Unknown";
      let analysisResult = "";
      let reportStatus = "";
      
      // Helper to extract data from response
      const extractData = (res) => {
          if (res.report_id) return res;
          if (Array.isArray(res) && res.length > 0) return extractData(res[0]);
          if (res.report) return extractData(res.report);
          if (res.reports) return extractData(res.reports);
          return {};
      };
      
      const data = extractData(response);
      if (data.report_id) reportId = data.report_id;
      if (data.analysis_result) analysisResult = data.analysis_result;
      if (data.status) reportStatus = data.status;

      setStatus(`Report processed! ID: ${reportId} | Status: ${reportStatus}`);
      if (analysisResult) {
          setAnalysis(analysisResult);
      }

      // Reset form
      setFormData({
        title: '',
        description: '',
        name: '',
        email: '',
        anonymous: true,
        image_data: ''
      });
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="report-form">
      <h1>Report an Issue</h1>
      <p>Help improve our community by reporting issues, concerns, or suggestions.</p>

      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label htmlFor="title">Issue Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="Brief description of the issue"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            placeholder="Provide detailed information about the issue..."
            rows="6"
          />
        </div>

        <div className="form-group">
          <label htmlFor="image">Upload Image (Optional)</label>
          <input
            type="file"
            id="image"
            accept="image/*"
            onChange={handleImageChange}
          />
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="anonymous"
              checked={formData.anonymous}
              onChange={handleChange}
            />
            Submit anonymously
          </label>
        </div>

        {!formData.anonymous && (
          <div className="contact-info">
            <div className="form-group">
              <label htmlFor="name">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Your full name"
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@example.com"
              />
            </div>
          </div>
        )}

        <button type="submit" className="submit-btn">Submit Report</button>
      </form>

      {status && (
        <div className={`status-message ${status.includes('Error') ? 'error' : 'success'}`}>
          {status}
        </div>
      )}
      
      {analysis && (
        <div className="analysis-result" style={{marginTop: '20px', padding: '15px', backgroundColor: '#e8f5e9', borderRadius: '5px', borderLeft: '5px solid #4caf50'}}>
          <h3 style={{marginTop: 0}}>AI Analysis</h3>
          <p style={{whiteSpace: 'pre-wrap'}}>{analysis}</p>
        </div>
      )}
    </div>
  );
}

export default ReportForm;