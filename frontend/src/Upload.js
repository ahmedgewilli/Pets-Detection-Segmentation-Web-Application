import React, { useState } from 'react';

function Upload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch('/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <h2>Upload an Image</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="image/*" onChange={e => setFile(e.target.files[0])} required />
        <button type="submit" disabled={loading}>{loading ? "Analyzing..." : "Upload"}</button>
      </form>
      {result && (
        <div>
          {result.message ? (
            <p>{result.message}</p>
          ) : (
            <div>
              <h3>Detection Results:</h3>
              {/* Display bounding boxes and masks here, e.g. overlay on image */}
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Upload;