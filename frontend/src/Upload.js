import React, { useState } from 'react';
import { upload } from './api';

function Upload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    const token = localStorage.getItem('token');
    if (!file) {
      setError('Please select a file.');
      setLoading(false);
      return;
    }
    try {
      const data = await upload(file, token);
      if (data.error || data.message === 'No pets found in the image') {
        setError(data.error || data.message);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError('Upload failed.');
    }
    setLoading(false);
  };

  return (
    <div className="upload-container">
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <button type="submit" disabled={loading}>{loading ? 'Uploading...' : 'Upload'}</button>
      </form>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {result && (
        <div className="result-container">
          <h3>{result.message}</h3>
          <div>Classification: {result.classification}</div>
          <div>Boxes: {result.boxes && result.boxes.length > 0 ? result.boxes.map((box, i) => (
            <div key={i}>{box[4]} (confidence: {box[5].toFixed(2)})</div>
          )) : 'None'}</div>
          <div>Mask summary: {result.mask_summary && JSON.stringify(result.mask_summary)}</div>
          {result.segmentation_preview && (
            <div>
              <img src={result.segmentation_preview} alt="Segmentation Preview" style={{ maxWidth: 300, border: '1px solid #ccc', marginTop: 10 }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Upload;