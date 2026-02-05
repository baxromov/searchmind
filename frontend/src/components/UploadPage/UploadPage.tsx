import { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FolderOpen, FileText, Upload as UploadIcon, Loader2, CheckCircle } from 'lucide-react';
import { useUpload } from '../../hooks/useUpload';

const UploadPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const { upload, uploading, error, result, reset } = useUpload();

  const onDrop = (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      reset();
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;

    try {
      await upload(file);
    } catch (err) {
      // Error handled by hook
    }
  };

  const handleReset = () => {
    setFile(null);
    reset();
  };

  return (
    <div className="upload-page">
      <div className="upload-header">
        <h1>Upload Documents</h1>
        <p className="subtitle">Upload PDF or DOCX files to index and search</p>
      </div>

      <div className="upload-container">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
        >
          <input {...getInputProps()} />
          {!file ? (
            <>
              <div className="upload-icon">
                <FolderOpen size={64} strokeWidth={1.5} />
              </div>
              {isDragActive ? (
                <p>Drop the file here...</p>
              ) : (
                <>
                  <p>Drag & drop a file here, or click to select</p>
                  <p className="file-types">Supported: PDF, DOCX (max 50MB)</p>
                </>
              )}
            </>
          ) : (
            <>
              <div className="file-selected">
                <FileText size={56} strokeWidth={1.5} className="file-icon" />
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              </div>
            </>
          )}
        </div>

        {file && !result && (
          <div className="upload-actions">
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <Loader2 size={18} className="spin-icon" />
                  Uploading...
                </>
              ) : (
                <>
                  <UploadIcon size={18} />
                  Upload & Index
                </>
              )}
            </button>
            <button
              className="reset-button"
              onClick={handleReset}
              disabled={uploading}
            >
              Clear
            </button>
          </div>
        )}

        {uploading && (
          <div className="upload-progress">
            <Loader2 size={50} className="spinner" />
            <p>Processing document...</p>
            <p className="progress-detail">Extracting text, chunking, and indexing</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {result && (
          <div className="success-message">
            <div className="success-icon">
              <CheckCircle size={48} strokeWidth={2.5} />
            </div>
            <h3>Upload Successful!</h3>
            <div className="result-details">
              <p><strong>File:</strong> {result.filename}</p>
              <p><strong>Chunks indexed:</strong> {result.num_chunks}</p>
              <p><strong>Resource ID:</strong> {result.resource_id}</p>
            </div>
            <button className="new-upload-button" onClick={handleReset}>
              <UploadIcon size={18} />
              Upload Another Document
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPage;
