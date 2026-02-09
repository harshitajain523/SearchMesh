import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export interface SearchResult {
    title: string;
    url: string;
    snippet: string;
    source: 'google' | 'bing' | 'duckduckgo';
    position: number;
    thumbnail_url?: string;
    image_url?: string;
    width?: number;
    height?: number;
    domain?: string;
    relevance_score: number;
    is_duplicate: boolean;
}

export interface AggregatedResults {
    query: string;
    results: SearchResult[];
    total_results: number;
    sources_queried: string[];
    sources_succeeded: string[];
    sources_failed: string[];
    duplicates_removed: number;
    processing_time_ms: number;
    cache_hit: boolean;
}

export interface SearchParams {
    query: string;
    sources?: string[];
    maxResults?: number;
    imageSearch?: boolean;
    dedupe?: boolean;
}

export async function search(params: SearchParams): Promise<AggregatedResults> {
    const searchParams = new URLSearchParams();
    searchParams.append('q', params.query);

    if (params.sources && params.sources.length > 0) {
        params.sources.forEach(s => searchParams.append('sources', s));
    }

    if (params.maxResults) {
        searchParams.append('max_results', params.maxResults.toString());
    }

    if (params.imageSearch) {
        searchParams.append('image_search', 'true');
    }

    if (params.dedupe !== undefined) {
        searchParams.append('dedupe', params.dedupe.toString());
    }

    const response = await axios.get<AggregatedResults>(
        `${API_BASE}/search?${searchParams.toString()}`
    );

    return response.data;
}

export async function getEngineStatus(): Promise<any[]> {
    const response = await axios.get(`${API_BASE}/search/engines`);
    return response.data;
}

export async function healthCheck(): Promise<{ status: string }> {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
}
