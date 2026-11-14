export const ROUTE_NAMES = Object.freeze({
    home: 'home',
    dialogs: 'dialogs',
    document: 'document',
    verification: 'verification',
    settings: 'settings',
    login: 'login',
});

export const ANSWER_STATUSES = Object.freeze({
    confirmed: 'confirmed',
    refusal: 'refusal',
    clarification: 'clarification',
    correction: 'correction',
    disputed: 'disputed',
    offTopic: 'off-topic',
});

export const ANSWER_STATUS_LABELS = Object.freeze({
    [ANSWER_STATUSES.confirmed]: 'Подтверждено',
    [ANSWER_STATUSES.refusal]: 'Отказ',
    [ANSWER_STATUSES.clarification]: 'Уточнение',
    [ANSWER_STATUSES.correction]: 'Поправка',
    [ANSWER_STATUSES.disputed]: 'Спорный',
    [ANSWER_STATUSES.offTopic]: 'Вне темы',
});

export const USER_ROLES = Object.freeze({
    lawyer: 'lawyer',
    head: 'head',
});

export const REVIEW_DECISIONS = Object.freeze({
    approved: 'approved',
    needsFix: 'needs-fix',
});

export const FEEDBACK_VALUES = Object.freeze({
    correct: 'correct',
    wrong: 'wrong',
    disputed: 'disputed',
});

export const RERANK_THRESHOLD = 0.8;

export const DEFAULT_DOCUMENT_ID = 'p-17-2024';

export const NOTIFICATION_KINDS = Object.freeze({
    update: 'update',
    outdated: 'outdated',
    disputed: 'disputed',
});
