import { useState, useCallback } from 'react';
import { useSearch } from '../hooks/useSearch';
import { SearchBar } from '../components/SearchBar';
import { SourceFilters } from '../components/SourceFilters';
import { ResultCard, ResultCardSkeleton } from '../components/ResultCard';
import { SearchParams } from '../services/api';

const ALL_SOURCES = ['google', 'duckduckgo'];

export function SearchPage() {
    const [searchParams, setSearchParams] = useState<SearchParams | null>(null);
    const [activeSources, setActiveSources] = useState<string[]>(ALL_SOURCES);

    const { data, isLoading, error, refetch } = useSearch(searchParams);

    const handleSearch = useCallback((query: string) => {
        setSearchParams({
            query,
            sources: activeSources,
            maxResults: 30,
            dedupe: true,
        });
    }, [activeSources]);

    const handleToggleSource = useCallback((source: string) => {
        setActiveSources(prev => {
            if (prev.includes(source)) {
                // Don't allow removing all sources
                if (prev.length === 1) return prev;
                return prev.filter(s => s !== source);
            }
            return [...prev, source];
        });
    }, []);

    const hasSearched = searchParams !== null;
    const hasResults = data && data.results.length > 0;

    return (
        <div className="app">
            <header className="header">
                <div className="header-content">
                    <div className="logo">
                        <div className="logo-icon">⚡</div>
                        <span>SearchMesh</span>
                    </div>
                </div>
            </header>

            <main className="main-content">
                <section className={`search-section ${hasSearched ? 'compact' : ''}`}>
                    {!hasSearched && (
                        <>
                            <h1 className="search-title">Search Smarter</h1>
                            <p className="search-subtitle">
                                Aggregating results from Google and DuckDuckGo with intelligent deduplication, powered by Azure Computer Vision
                            </p>
                        </>
                    )}

                    <SearchBar
                        onSearch={handleSearch}
                        isLoading={isLoading}
                        initialQuery={searchParams?.query}
                        compact={hasSearched}
                    />

                    <SourceFilters
                        sources={ALL_SOURCES}
                        activeSources={activeSources}
                        onToggle={handleToggleSource}
                    />
                </section>

                {hasSearched && (
                    <section className="results-section">
                        {/* Results Header */}
                        {data && (
                            <div className="results-header">
                                <span className="results-count">
                                    {data.total_results} results for "{data.query}"
                                </span>
                                <div className="results-stats">
                                    <span>⚡ {data.processing_time_ms.toFixed(0)}ms</span>
                                    {data.duplicates_removed > 0 && (
                                        <span>🔄 {data.duplicates_removed} duplicates removed</span>
                                    )}
                                    <span>
                                        ✓ {data.sources_succeeded.join(', ')}
                                        {data.sources_failed.length > 0 && (
                                            <> | ✗ {data.sources_failed.join(', ')}</>
                                        )}
                                    </span>
                                </div>
                            </div>
                        )}

                        {/* Loading State */}
                        {isLoading && (
                            <div className="result-list">
                                {[...Array(5)].map((_, i) => (
                                    <ResultCardSkeleton key={i} />
                                ))}
                            </div>
                        )}

                        {/* Error State */}
                        {error && !isLoading && (
                            <div className="error-container">
                                <div className="error-icon">⚠️</div>
                                <p className="error-message">
                                    {error.message || 'Something went wrong. Please try again.'}
                                </p>
                                <button className="retry-button" onClick={() => refetch()}>
                                    Try Again
                                </button>
                            </div>
                        )}

                        {/* Empty State */}
                        {!isLoading && !error && hasSearched && !hasResults && (
                            <div className="empty-state">
                                <div className="empty-icon">🔍</div>
                                <p>No results found for "{searchParams?.query}"</p>
                            </div>
                        )}

                        {/* Results */}
                        {!isLoading && hasResults && (
                            <div className="result-list">
                                {data.results.map((result, index) => (
                                    <ResultCard key={`${result.url}-${index}`} result={result} />
                                ))}
                            </div>
                        )}
                    </section>
                )}
            </main>

            <footer className="footer">
                <p>SearchMesh - Federated Search Engine</p>
            </footer>
        </div>
    );
}
