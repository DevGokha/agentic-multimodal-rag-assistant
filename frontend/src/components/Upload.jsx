import { useState } from "react";
import { uploadFile } from "../services/api";

function Upload() {
  // Step 1: State for file, upload status, and loading
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [isError, setIsError] = useState(false);

  // Step 2: Handle file selection
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus("");
    setIsError(false);
  };

  // Step 3: Handle file upload to backend
  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setIsError(false);
    try {
      const res = await uploadFile(file);
      setStatus(res.message || "✅ Upload successful!");
    } catch {
      setStatus("❌ Upload failed. Please try again.");
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Render the upload UI
  return (
    <div className="upload-section">
      <span className="upload-label">📄 Document</span>

      {/* Step 5: Custom styled file input */}
      <div className="file-input-wrapper">
        <div className="file-input-btn">
          📁 {file ? "Change file" : "Choose file"}
        </div>
        <input type="file" onChange={handleFileChange} disabled={loading} />
      </div>

      {/* Step 6: Show selected file name */}
      {file && <span className="file-name">{file.name}</span>}

      {/* Step 7: Upload button */}
      <button
        className="upload-btn"
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? "Uploading..." : "Upload"}
      </button>

      {/* Step 8: Status message */}
      {status && (
        <span className={`upload-status ${isError ? "error" : ""}`}>
          {status}
        </span>
      )}
    </div>
  );
}

export default Upload;