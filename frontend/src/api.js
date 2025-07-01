const API_URL = "http://localhost:5000"; // Make sure backend runs on port 5000

export async function register(username, password) {
  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return res.json();
}

export async function login(username, password) {
  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  return res.json();
}

export async function upload(file, token) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    headers: { Authorization: token },
    body: formData,
  });
  return res.json();
}
