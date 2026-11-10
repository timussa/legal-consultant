import {ApiError} from '@/core/api/client';

const NETWORK_ERROR_MESSAGE = 'Нет связи с сервером. Проверьте подключение и попробуйте ещё раз.';
const SERVER_ERROR_MESSAGE = 'Сервер не ответил. Попробуйте ещё раз через минуту.';
const UNKNOWN_ERROR_MESSAGE = 'Что-то пошло не так. Попробуйте ещё раз.';
const SERVER_ERROR_STATUS = 500;

/**
 * @param {unknown} error
 * @returns {string}
 */
export function getErrorMessage(error) {
    if (!(error instanceof ApiError)) {
        return UNKNOWN_ERROR_MESSAGE;
    }

    if (error.status === 0) {
        return NETWORK_ERROR_MESSAGE;
    }

    if (error.status >= SERVER_ERROR_STATUS) {
        return SERVER_ERROR_MESSAGE;
    }

    return error.serverMessage ?? UNKNOWN_ERROR_MESSAGE;
}
