
const JASECI_URL = process.env.REACT_APP_API_URL || ''; // Use env var or default to relative path

// Log the API URL on startup to help with debugging
if (process.env.NODE_ENV === 'development') {
    console.log('JAC API URL:', JASECI_URL || '(using proxy from package.json)');
}

export const runWalker = async (walkerName, context = {}) => {
    const token = localStorage.getItem('jac_token');
    const headers = {
        'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${JASECI_URL}/walker/${walkerName}`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(context),
        });

        // Check content type before parsing
        const contentType = response.headers.get('content-type');
        
        if (!response.ok) {
            // Try to get error details
            let errorMessage = `Walker ${walkerName} failed: ${response.statusText}`;
            if (contentType && contentType.includes('application/json')) {
                const errorData = await response.json();
                errorMessage = errorData.message || errorData.error || errorMessage;
            } else {
                // If response is HTML, read it as text for debugging
                const textResponse = await response.text();
                console.error('Received non-JSON response:', textResponse.substring(0, 200));
                errorMessage = `API endpoint returned ${response.status}. Check if backend is running on the correct port.`;
            }
            throw new Error(errorMessage);
        }

        // Ensure we're getting JSON before parsing
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            console.error('Expected JSON but received:', textResponse.substring(0, 200));
            throw new Error('API returned non-JSON response. Ensure backend is properly configured.');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error running walker ${walkerName}:`, error);
        throw error;
    }
};
