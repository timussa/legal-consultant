export const ROUTE_NAMES = Object.freeze({
    home: 'home',
    dialogs: 'dialogs',
    document: 'document',
    verification: 'verification',
});

export const ANSWER_STATUSES = Object.freeze({
    confirmed: 'confirmed',
    refusal: 'refusal',
    clarification: 'clarification',
    correction: 'correction',
    disputed: 'disputed',
});

export const ANSWER_STATUS_LABELS = Object.freeze({
    [ANSWER_STATUSES.confirmed]: 'Подтверждено',
    [ANSWER_STATUSES.refusal]: 'Отказ',
    [ANSWER_STATUSES.clarification]: 'Уточнение',
    [ANSWER_STATUSES.correction]: 'Поправка',
    [ANSWER_STATUSES.disputed]: 'Спорный',
});

export const USER_ROLES = Object.freeze({
    lawyer: 'lawyer',
    head: 'head',
});

export const FEEDBACK_VALUES = Object.freeze({
    correct: 'correct',
    wrong: 'wrong',
    disputed: 'disputed',
});

export const RERANK_THRESHOLD = 0.8;

export const DEFAULT_DOCUMENT_ID = 'p-17-2024';
