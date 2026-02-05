import { useState, useRef } from 'react';
import { searchDocuments } from '../services/api';
import type { SearchResponse, SearchResult } from '../services/api';

export const useSearch = () => {
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [totalFound, setTotalFound] = useState(0);
  const [searchTime, setSearchTime] = useState(0);

  const currentQueryRef = useRef<string>('');
  const offsetRef = useRef<number>(0);

  const search = async (query: string, topK: number = 10, filters?: Record<string, any>, append: boolean = false) => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    // If it's a new query, reset offset and results
    if (query !== currentQueryRef.current) {
      currentQueryRef.current = query;
      offsetRef.current = 0;
      if (!append) {
        setResults([]);
      }
    }

    setSearching(true);
    setError(null);

    try {
      const response = await searchDocuments(query, topK, filters, offsetRef.current, 10);

      setResults(prev => append ? [...prev, ...response.results] : response.results);
      setHasMore(response.has_more);
      setTotalFound(response.total_found);
      setSearchTime(response.search_time_ms);

      // Update offset for next page
      offsetRef.current += response.results.length;

      return response;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Search failed';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setSearching(false);
    }
  };

  const loadMore = async () => {
    if (!currentQueryRef.current || !hasMore || searching) {
      return;
    }
    await search(currentQueryRef.current, 10, undefined, true);
  };

  const reset = () => {
    setError(null);
    setResults([]);
    setHasMore(false);
    setTotalFound(0);
    setSearchTime(0);
    currentQueryRef.current = '';
    offsetRef.current = 0;
  };

  return { search, loadMore, searching, error, results, hasMore, totalFound, searchTime, reset };
};
