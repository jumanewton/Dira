import React, { useState } from 'react';
import { jacSpawn } from 'jac-client';  // Import jacSpawn from jac-client

function App() {
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
    <div className="App">
      <h1>PublicLens - Report Issues</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title:</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>
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
          <>
            <div>
              <label>Name:</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
              />
            </div>
            <div>
              <label>Email:</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>
          </>
        )}
        <button type="submit">Submit Report</button>
      </form>
      {status && <p>{status}</p>}
    </div>
  );
}

export default App;