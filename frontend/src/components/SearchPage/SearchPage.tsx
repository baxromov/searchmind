import { useState, useEffect } from 'react';
import { useSearch } from '../../hooks/useSearch';
import SearchBar from './SearchBar';
import ResultList from './ResultList';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const { search, loadMore, searching, error, results, hasMore, totalFound, searchTime } = useSearch();

  useEffect(() => {
    if (!query.trim()) {
      return;
    }

    const debounceTimer = setTimeout(() => {
      search(query);
    }, 500);

    return () => clearTimeout(debounceTimer);
  }, [query]);

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>Document Search</h1>
        <p className="subtitle">Search across your uploaded documents</p>
        <SearchBar
          value={query}
          onChange={setQuery}
          isLoading={searching}
        />
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {searching && results.length === 0 && (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Searching documents...</span>
        </div>
      )}

      {results.length > 0 && (
        <>
          <div className="results-summary">
            Found {results.length} results
            {totalFound > results.length && ` (showing ${results.length} of ${totalFound})`}
            <span className="search-time"> • {searchTime.toFixed(0)}ms</span>
          </div>
          <ResultList
            results={results}
            onLoadMore={loadMore}
            hasMore={hasMore}
            loading={searching}
          />
        </>
      )}
    </div>
  );
};

export default SearchPage;
