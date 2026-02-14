interface SourceFiltersProps {
    sources: string[];
    activeSources: string[];
    onToggle: (source: string) => void;
}

const sourceInfo: Record<string, { label: string; className: string }> = {
    google: { label: 'Google', className: 'google' },
    duckduckgo: { label: 'DuckDuckGo', className: 'duckduckgo' },
};

export function SourceFilters({ sources, activeSources, onToggle }: SourceFiltersProps) {
    return (
        <div className="source-filters">
            {sources.map(source => {
                const info = sourceInfo[source] || { label: source, className: '' };
                const isActive = activeSources.includes(source);

                return (
                    <button
                        key={source}
                        className={`source-toggle ${info.className} ${isActive ? 'active' : ''}`}
                        onClick={() => onToggle(source)}
                        type="button"
                    >
                        <span className="source-dot" />
                        {info.label}
                    </button>
                );
            })}
        </div>
    );
}
