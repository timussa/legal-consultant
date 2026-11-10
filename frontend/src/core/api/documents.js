import {http} from '@/core/api/client';
import {resolveMock, USE_MOCKS} from '@/core/api/mocks';
import {DOCUMENTS} from '@/core/data/documents';

/**
 * @param {string} documentId
 * @returns {Promise<import('@/core/types/document').LegalDocument | null>}
 */
export function getDocument(documentId) {
    if (USE_MOCKS) {
        return resolveMock(DOCUMENTS[documentId] ?? null);
    }

    return http.get(`/v1/documents/${encodeURIComponent(documentId)}`);
}
