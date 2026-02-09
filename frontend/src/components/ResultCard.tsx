import { SearchResult } from '../services/api';
import { SourceBadge } from './SourceBadge';

interface ResultCardProps {
    result: SearchResult;
}

export function ResultCard({ result }: ResultCardProps) {
    const displayDomain = result.domain || new URL(result.url).hostname;

    return (
        <article className="result-card">
            <div className="result-header">
                <div className="result-content">
                    <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="result-title"
                    >
                        {result.title}
                    </a>
                    <div className="result-url">
                        <SourceBadge source={result.source} />
                        <span>{displayDomain}</span>
                    </div>
                    <p className="result-snippet">{result.snippet}</p>
                </div>
                {result.thumbnail_url && (
                    <img
                        src={result.thumbnail_url}
                        alt=""
                        className="result-thumbnail"
                        loading="lazy"
                    />
                )}
            </div>
        </article>
    );
}

export function ResultCardSkeleton() {
    return (
        <article className="result-card">
            <div className="result-header">
                <div className="result-content">
                    <div className="skeleton skeleton-title"></div>
                    <div className="skeleton skeleton-url"></div>
                    <div className="skeleton skeleton-text"></div>
                    <div className="skeleton skeleton-text"></div>
                </div>
            </div>
        </article>
    );
}
