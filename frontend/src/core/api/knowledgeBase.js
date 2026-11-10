import {http} from '@/core/api/client';
import {resolveMock, USE_MOCKS} from '@/core/api/mocks';
import {KNOWLEDGE_BASE_OVERVIEW} from '@/core/data/knowledgeBase';

/** @returns {Promise<import('@/core/types/knowledgeBase').KnowledgeBaseOverview>} */
export function getKnowledgeBaseOverview() {
    if (USE_MOCKS) {
        return resolveMock(KNOWLEDGE_BASE_OVERVIEW);
    }

    return http.get('/v1/knowledge-base');
}
