
const JASECI_URL = process.env.REACT_APP_API_URL || ''; // Use env var or default to relative path

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

        if (!response.ok) {
            throw new Error(`Walker ${walkerName} failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error(`Error running walker ${walkerName}:`, error);
        throw error;
    }
};
