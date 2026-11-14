import {http} from '@/core/api/client';
import {resolveMock, USE_MOCKS} from '@/core/api/mocks';

/**
 * @typedef {Object} SessionUser
 * @property {number} id
 * @property {string} login
 * @property {string} name
 * @property {string} initials
 * @property {string} position
 * @property {'lawyer' | 'head'} role
 */

/** В режиме моков вход не нужен: показываем демонстрационного руководителя, чтобы были видны обе роли. */
const MOCK_USER = Object.freeze({
    id: 0,
    login: 'demo',
    name: 'Анна Корнеева',
    initials: 'АК',
    position: 'Юрист, договорная работа',
    role: 'head',
});

/**
 * Сессия хранится в HttpOnly-cookie, которую выставляет сервер: токен недоступен скриптам страницы.
 * @param {string} login
 * @param {string} password
 * @returns {Promise<{user: SessionUser, expiresAt: string}>}
 */
export function login(login, password) {
    if (USE_MOCKS) {
        return resolveMock({user: MOCK_USER, expiresAt: ''});
    }

    return http.post('/v1/auth/login', {login, password});
}

/** @returns {Promise<void>} */
export function logout() {
    if (USE_MOCKS) {
        return resolveMock(undefined);
    }

    return http.post('/v1/auth/logout');
}

/** @returns {Promise<SessionUser>} */
export function getMe() {
    if (USE_MOCKS) {
        return resolveMock(MOCK_USER, 0);
    }

    return http.get('/v1/auth/me');
}

/**
 * @param {string} currentPassword
 * @param {string} newPassword
 * @returns {Promise<void>}
 */
export function changePassword(currentPassword, newPassword) {
    if (USE_MOCKS) {
        return resolveMock(undefined);
    }

    return http.post('/v1/auth/password', {currentPassword, newPassword});
}
