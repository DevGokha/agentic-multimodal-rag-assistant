// Step 0: Use environment variable for API URL (for deployment)
//         Falls back to localhost:8000 for local development
let BASE_URL = import.meta.env.VITE_API_URL || "https://agentic-multimodal-rag-assistant.onrender.com";
if (BASE_URL.endsWith('/')) {
  BASE_URL = BASE_URL.slice(0, -1);
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { "Authorization": `Bearer ${token}` } : {};
};

export const sendQuery = async (query) => {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders()
    },
    body: JSON.stringify({ query })
  });

  return res.json();
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload`, {
    method: "POST",
    headers: {
      ...getAuthHeaders()
    },
    body: formData
  });

  return res.json();
};

// Step 1: Upload an image to the vision model for AI-powered description
export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload-image`, {
    method: "POST",
    headers: {
      ...getAuthHeaders()
    },
    body: formData
  });

  return res.json();
};

export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Login failed');
  }

  return res.json();
};

export const register = async (email, password) => {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Registration failed');
  }

  return res.json();
};