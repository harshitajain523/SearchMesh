import { useState, FormEvent } from 'react';

interface SearchBarProps {
    initialQuery?: string;
    onSearch: (query: string) => void;
    isLoading?: boolean;
    compact?: boolean;
}

export function SearchBar({
    initialQuery = '',
    onSearch,
    isLoading = false,
    compact = false
}: SearchBarProps) {
    const [query, setQuery] = useState(initialQuery);

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query.trim());
        }
    };

    return (
        <form className="search-bar" onSubmit={handleSubmit}>
            <div className="search-input-wrapper">
                <div className="search-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="11" cy="11" r="8" />
                        <path d="m21 21-4.35-4.35" />
                    </svg>
                </div>
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search the web..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    autoFocus={!compact}
                />
                <button
                    type="submit"
                    className="search-button"
                    disabled={isLoading || !query.trim()}
                >
                    {isLoading ? 'Searching...' : 'Search'}
                </button>
            </div>
        </form>
    );
}
