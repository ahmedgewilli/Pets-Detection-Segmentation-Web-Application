const API_URL = "https://huggingface.co/spaces/Ahmedgewilli/pets-detection";

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

export async function uploadImage(token, file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/upload`, {
    method: "POST",
    headers: { Authorization: token },
    body: formData,
  });
  return res.json();
}

export async function whoami(token) {
  const res = await fetch(`${API_URL}/whoami`, {
    headers: { Authorization: token },
  });
  return res.json();
}

export async function logout(token) {
  const res = await fetch(`${API_URL}/logout`, {
    method: "POST",
    headers: { Authorization: token },
  });
  return res.json();
}
