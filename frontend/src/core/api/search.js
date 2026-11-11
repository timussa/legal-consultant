import {http} from '@/core/api/client';
import {resolveMock, USE_MOCKS} from '@/core/api/mocks';
import {DOCUMENTS} from '@/core/data/documents';
import {searchDocuments} from '@/core/utils/search';

const SEARCH_MOCK_LATENCY_MS = 120;

/**
 * @param {string} query
 * @returns {Promise<import('@/core/utils/search').SearchHit[]>}
 */
export function searchKnowledgeBase(query) {
    if (USE_MOCKS) {
        return resolveMock(searchDocuments(Object.values(DOCUMENTS), query), SEARCH_MOCK_LATENCY_MS);
    }

    return http.get(`/v1/search?q=${encodeURIComponent(query)}`);
}
