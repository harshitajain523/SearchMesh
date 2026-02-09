import { useQuery } from '@tanstack/react-query';
import { search, SearchParams, AggregatedResults } from '../services/api';

export function useSearch(params: SearchParams | null) {
    return useQuery<AggregatedResults, Error>({
        queryKey: ['search', params],
        queryFn: () => search(params!),
        enabled: !!params?.query,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
}
