import { useState, useEffect } from 'react';
import { ArrowLeft, FileText, Loader2, Package } from 'lucide-react';
import { getResourceDetails } from '../../services/api';
import type { Resource, ChunkDetail } from '../../services/api';
import './KnowledgeBase.css';

interface FileDetailsProps {
  resource: Resource;
  onBack: () => void;
}

const FileDetails: React.FC<FileDetailsProps> = ({ resource, onBack }) => {
  const [chunks, setChunks] = useState<ChunkDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadChunks();
  }, [resource.resource_id]);

  const loadChunks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getResourceDetails(resource.resource_id);
      setChunks(data);
    } catch (err) {
      setError('Failed to load chunk details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="file-details">
      <button className="back-button" onClick={onBack}>
        <ArrowLeft size={20} />
        Back to Knowledge Base
      </button>

      <div className="file-details-header">
        <div className="file-details-icon">
          <FileText size={40} />
        </div>
        <div className="file-details-info">
          <h1>{resource.filename}</h1>
          <div className="file-details-meta">
            <span><Package size={16} /> {resource.num_chunks} chunks</span>
            <span>•</span>
            <span>Uploaded {formatDate(resource.uploaded_at)}</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="kb-loading">
          <Loader2 size={40} className="spin" />
          <p>Loading chunks...</p>
        </div>
      ) : error ? (
        <div className="kb-error-message">{error}</div>
      ) : (
        <div className="chunks-list">
          <h2 className="chunks-title">Document Chunks ({chunks.length})</h2>
          {chunks.map((chunk, index) => (
            <div key={chunk.chunk_id} className="chunk-card">
              <div className="chunk-header">
                <span className="chunk-number">Chunk #{index + 1}</span>
                <span className="chunk-page">Page {chunk.page_number}</span>
              </div>

              <div className="chunk-content">
                <p className="chunk-text">{chunk.text}</p>
              </div>

              <div className="chunk-metadata">
                <h4>Metadata</h4>
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <span className="metadata-label">Chunk ID:</span>
                    <span className="metadata-value">{chunk.chunk_id}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Page:</span>
                    <span className="metadata-value">{chunk.page_number}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="metadata-label">Characters:</span>
                    <span className="metadata-value">{chunk.text.length}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileDetails;
