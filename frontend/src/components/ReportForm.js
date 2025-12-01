import React, { useState } from 'react';
import { jacSpawn } from 'jac-client';

function ReportForm() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    name: '',
    email: '',
    anonymous: true
  });
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Submitting...');

    try {
      // Call IntakeAgent walker
      const result = await jacSpawn('IntakeAgent', '', {
        report_data: {
          title: formData.title,
          description: formData.description,
          name: formData.anonymous ? '' : formData.name,
          email: formData.anonymous ? '' : formData.email
        }
      });

      setStatus(`Report submitted successfully! ID: ${result.report_id}`);
      // Reset form
      setFormData({
        title: '',
        description: '',
        name: '',
        email: '',
        anonymous: true
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
    </div>
  );
}

export default ReportForm;