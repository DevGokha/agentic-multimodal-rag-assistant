// Step 0: Use environment variable for API URL (for deployment)
//         Falls back to localhost:8000 for local development
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const sendQuery = async (query) => {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
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
    body: formData
  });

  return res.json();
};