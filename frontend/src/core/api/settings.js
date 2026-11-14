import {http} from '@/core/api/client';
import {USE_MOCKS} from '@/core/api/mocks';

/** @returns {Promise<Record<string, unknown> | null>} null — хранить только локально (режим моков) */
export function getServerSettings() {
    if (USE_MOCKS) {
        return Promise.resolve(null);
    }

    return http.get('/v1/settings');
}

/**
 * @param {Record<string, unknown>} settings
 * @returns {Promise<unknown>}
 */
export function saveServerSettings(settings) {
    if (USE_MOCKS) {
        return Promise.resolve(undefined);
    }

    return http.put('/v1/settings', settings);
}
