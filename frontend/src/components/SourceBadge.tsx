import { SearchResult } from '../services/api';

interface SourceBadgeProps {
    source: SearchResult['source'];
}

export function SourceBadge({ source }: SourceBadgeProps) {
    const labels: Record<string, string> = {
        google: 'Google',
        duckduckgo: 'DDG',
        azure_vision: 'Azure',
    };

    return (
        <span className={`source-badge ${source}`}>
            {labels[source] || source}
        </span>
    );
}
