import {NOTIFICATION_KINDS, ROUTE_NAMES} from '@/core/constants';

/**
 * @typedef {Object} AppNotification
 * @property {string} id
 * @property {string} kind
 * @property {string} title
 * @property {string} text
 * @property {string} dateLabel
 * @property {boolean} [isHeadOnly] Видно только руководителю
 * @property {import('vue-router').RouteLocationRaw | null} target
 */

/** @type {ReadonlyArray<AppNotification>} */
export const NOTIFICATIONS = Object.freeze([
    {
        id: 'outdated-398',
        kind: NOTIFICATION_KINDS.outdated,
        title: 'Ответ №398 устарел',
        text: 'Порог для финансового директора теперь 3 млн ₽. Переспросите по новой редакции регламента.',
        dateLabel: 'сегодня',
        target: {name: ROUTE_NAMES.dialogs, params: {dialogId: '412'}},
    },
    {
        id: 'disputed-418',
        kind: NOTIFICATION_KINDS.disputed,
        title: 'Спорный ответ №418',
        text: 'О. Шишкина отметила ответ о санкционной проверке как спорный.',
        dateLabel: 'сегодня',
        isHeadOnly: true,
        target: {name: ROUTE_NAMES.home},
    },
    {
        id: 'reglament-2025',
        kind: NOTIFICATION_KINDS.update,
        title: 'Регламент согласования, ред. 2025',
        text: 'Финансовый директор — свыше 3 млн ₽, генеральный — свыше 15 млн ₽, согласование только в СЭД.',
        dateLabel: '01.03.2025',
        target: {name: ROUTE_NAMES.document, params: {documentId: 'reglament'}, query: {edition: 'edition-2025'}},
    },
    {
        id: 'compliance-k12',
        kind: NOTIFICATION_KINDS.update,
        title: 'Письмо комплаенс К-12',
        text: 'С 21.04.2025 иностранные контрагенты проходят санкционную проверку до подписания.',
        dateLabel: '15.04.2025',
        target: null,
    },
]);
