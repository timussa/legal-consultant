import {http} from '@/core/api/client';
import {resolveMock, USE_MOCKS} from '@/core/api/mocks';
import {NOTIFICATIONS} from '@/core/data/notifications';

/** @returns {Promise<import('@/core/data/notifications').AppNotification[]>} */
export function getNotifications() {
    if (USE_MOCKS) {
        return resolveMock([...NOTIFICATIONS]);
    }

    return http.get('/v1/notifications');
}

/**
 * @param {string[]} ids
 * @returns {Promise<void>}
 */
export function markNotificationsRead(ids) {
    if (USE_MOCKS) {
        return resolveMock(undefined);
    }

    return http.post('/v1/notifications/read', {ids});
}
