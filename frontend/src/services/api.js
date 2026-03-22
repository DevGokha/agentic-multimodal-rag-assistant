const BASE_URL = "http://localhost:8000";

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