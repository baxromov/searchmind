import React from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  isLoading: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({ value, onChange, isLoading }) => {
  return (
    <div className="search-bar">
      <input
        type="text"
        className="search-input"
        placeholder="Search your documents..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={isLoading}
      />
    </div>
  );
};

export default SearchBar;
