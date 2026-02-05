import { useState, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, FileText, Trash2, Eye, Loader2 } from 'lucide-react';
import { useUpload } from '../../hooks/useUpload';
import { getResources, deleteResource } from '../../services/api';
import type { Resource } from '../../services/api';
import FileDetails from './FileDetails';
import './KnowledgeBase.css';

const KnowledgeBase = () => {
  const [file, setFile] = useState<File | null>(null);
  const [resources, setResources] = useState<Resource[]>([]);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [total, setTotal] = useState(0);
  const { upload, uploading, error, result, reset } = useUpload();

  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);
  const offsetRef = useRef(0);

  useEffect(() => {
    loadResources(true);
  }, []);

  useEffect(() => {
    if (result) {
      loadResources(true);
      setFile(null);
    }
  }, [result]);

  useEffect(() => {
    if (loading || loadingMore || !hasMore) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMoreResources();
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loading, loadingMore, hasMore]);

  const loadResources = async (reset: boolean = false) => {
    try {
      if (reset) {
        setLoading(true);
        offsetRef.current = 0;
      }
      const data = await getResources(0, 20);
      setResources(data.resources);
      setHasMore(data.has_more);
      setTotal(data.total);
      offsetRef.current = data.resources.length;
    } catch (err) {
      console.error('Failed to load resources:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMoreResources = async () => {
    if (loadingMore || !hasMore) return;

    try {
      setLoadingMore(true);
      const data = await getResources(offsetRef.current, 20);
      setResources(prev => [...prev, ...data.resources]);
      setHasMore(data.has_more);
      offsetRef.current += data.resources.length;
    } catch (err) {
      console.error('Failed to load more resources:', err);
    } finally {
      setLoadingMore(false);
    }
  };

  const handleDelete = async (resourceId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await deleteResource(resourceId);
      setResources(resources.filter(r => r.resource_id !== resourceId));
      if (selectedResource?.resource_id === resourceId) {
        setSelectedResource(null);
      }
    } catch (err) {
      console.error('Failed to delete resource:', err);
    }
  };

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
      console.error('Upload failed:', err);
    }
  };

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateString: string) => {
    if (!dateString) {
      return 'Date unknown';
    }
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return 'Date unknown';
      }
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Date unknown';
    }
  };

  if (selectedResource) {
    return (
      <FileDetails
        resource={selectedResource}
        onBack={() => setSelectedResource(null)}
      />
    );
  }

  return (
    <div className="knowledge-base">
      <div className="kb-header">
        <h1>Knowledge Base</h1>
        <p className="subtitle">Manage your uploaded documents and view their details</p>
      </div>

      <div className="kb-content">
        <div className="upload-section">
          <div
            {...getRootProps()}
            className={`kb-dropzone ${isDragActive ? 'active' : ''}`}
          >
            <input {...getInputProps()} />
            {!file ? (
              <>
                <Upload size={32} className="kb-upload-icon" />
                {isDragActive ? (
                  <p>Drop file here</p>
                ) : (
                  <>
                    <p>Drag & drop or click to upload</p>
                    <p className="kb-file-types">PDF, DOCX (max 50MB)</p>
                  </>
                )}
              </>
            ) : (
              <div className="kb-file-selected">
                <FileText size={32} />
                <span className="kb-file-name">{file.name}</span>
                <span className="kb-file-size">{formatFileSize(file.size)}</span>
              </div>
            )}
          </div>

          {file && !result && (
            <div className="kb-upload-actions">
              <button
                className="kb-button kb-button-primary"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? (
                  <>
                    <Loader2 size={18} className="spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload size={18} />
                    Upload & Index
                  </>
                )}
              </button>
              <button
                className="kb-button kb-button-secondary"
                onClick={() => { setFile(null); reset(); }}
                disabled={uploading}
              >
                Clear
              </button>
            </div>
          )}

          {error && (
            <div className="kb-error-message">
              {error}
            </div>
          )}

          {result && (
            <div className="kb-success-message">
              <div className="kb-success-icon">✓</div>
              <p><strong>{result.filename}</strong> uploaded successfully!</p>
              <p className="kb-success-detail">
                {result.num_chunks} chunks indexed
              </p>
            </div>
          )}
        </div>

        <div className="resources-section">
          <h2 className="resources-title">Uploaded Documents ({total})</h2>

          {loading ? (
            <div className="kb-loading">
              <Loader2 size={40} className="spin" />
              <p>Loading documents...</p>
            </div>
          ) : resources.length === 0 ? (
            <div className="kb-empty">
              <File size={60} />
              <p>No documents uploaded yet</p>
              <p className="kb-empty-hint">Upload your first document above to get started</p>
            </div>
          ) : (
            <>
              <div className="resources-list-header">
                <div></div>
                <div>Name</div>
                <div>Chunks</div>
                <div>Uploaded</div>
                <div>Actions</div>
              </div>
              <div className="resources-list">
                {resources.map((resource) => (
                  <div key={resource.resource_id} className="resource-card">
                    <div className="resource-icon">
                      <FileText />
                    </div>
                    <div className="resource-info">
                      <h3 className="resource-name">{resource.filename}</h3>
                    </div>
                    <div className="resource-meta">
                      {resource.num_chunks} chunks
                    </div>
                    <div className="resource-date">
                      {formatDate(resource.uploaded_at)}
                    </div>
                    <div className="resource-actions">
                      <button
                        className="resource-action-btn"
                        onClick={() => setSelectedResource(resource)}
                        title="View details"
                      >
                        <Eye />
                        <span className="action-btn-text">View</span>
                      </button>
                      <button
                        className="resource-action-btn resource-action-delete"
                        onClick={() => handleDelete(resource.resource_id)}
                        title="Delete"
                      >
                        <Trash2 />
                        <span className="action-btn-text">Delete</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Infinite scroll trigger */}
              {hasMore && (
                <div ref={loadMoreRef} className="kb-load-more-trigger">
                  {loadingMore && (
                    <div className="kb-loading-more">
                      <Loader2 size={24} className="spin" />
                      <span>Loading more documents...</span>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
