import React, { useRef, useEffect } from 'react';
import { FileText, Loader2, Download, ExternalLink } from 'lucide-react';
import type { SearchResult } from '../../services/api';

interface ResultListProps {
  results: SearchResult[];
  onLoadMore: () => void;
  hasMore: boolean;
  loading: boolean;
}

const ResultList: React.FC<ResultListProps> = ({ results, onLoadMore, hasMore, loading }) => {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (loading || !hasMore) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          onLoadMore();
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
  }, [loading, hasMore, onLoadMore]);

  const handleViewFile = (resourceId: string) => {
    const fileUrl = `http://localhost:8000/resources/${resourceId}/file`;
    window.open(fileUrl, '_blank');
  };

  if (results.length === 0) {
    return <div className="no-results">No results found</div>;
  }

  return (
    <>
      <div className="result-list">
        {results.map((result, index) => (
          <div key={`${result.metadata.chunk_id}-${index}`} className="result-card">
            {/* Header with file info and page */}
            <div className="result-header">
              <div className="file-info">
                <FileText size={18} className="file-icon" />
                <span className="file-name">{result.metadata.file_name}</span>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span className="page-badge">Page {result.metadata.page_number}</span>
                <button
                  onClick={() => handleViewFile(result.metadata.resource_id)}
                  className="view-file-btn"
                  title="View file"
                >
                  <ExternalLink size={16} />
                </button>
              </div>
            </div>

            {/* Main text content snippet */}
            <div className="result-content">
              <p className="text-snippet">{result.text}</p>
            </div>

            {/* Footer with scores */}
            <div className="result-footer">
              <span className="relevance-score">
                Relevance: {(result.rerank_score * 100).toFixed(1)}%
              </span>
              <span className="result-rank">Result #{index + 1}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Infinite scroll trigger */}
      {hasMore && (
        <div ref={loadMoreRef} className="load-more-trigger">
          {loading && (
            <div className="loading-more">
              <Loader2 size={24} className="spinner" />
              <span>Loading more results...</span>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default ResultList;
