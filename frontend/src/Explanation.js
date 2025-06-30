import React from 'react';

function Explanation() {
  return (
    <div>
      <h2>How the AI Model Works</h2>
      <ul>
        <li>Upload an image (JPG/PNG).</li>
        <li>The AI checks if the image contains a pet (cat or dog).</li>
        <li>If a pet is found, the system draws boxes and highlights the pet.</li>
        <li>If no pet is found, you'll see a clear message.</li>
        <li>Only registered users can use the AI features.</li>
      </ul>
    </div>
  );
}

export default Explanation;