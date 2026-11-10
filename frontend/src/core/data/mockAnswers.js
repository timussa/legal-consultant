import {ANSWER_STATUSES} from '@/core/constants';

const PAYMENT_SOURCE = Object.freeze({
    documentId: 'p-17-2024',
    clauseId: '4.2',
    title: 'Договор П-17/2024, п. 4.2',
    meta: 'договор от 12.02.2024',
    before: 'Покупатель оплачивает Товар',
    quote: 'в течение 30 (тридцати) календарных дней с даты подписания универсального передаточного документа (УПД)',
    after: 'на соответствующую партию.',
});

/** @type {Readonly<Record<string, import('@/core/types/assistant').Answer>>} */
export const MOCK_ANSWERS = Object.freeze({
    payment: {
        status: ANSWER_STATUSES.confirmed,
        verdict: 'Проверено 1 из 1',
        totalDurationLabel: '1,9 с',
        context: [{label: 'Договор', value: 'П-17/2024'}],
        paragraphs: [
            [
                {text: 'Покупатель оплачивает каждую партию '},
                {text: 'в течение 30 календарных дней', isBold: true},
                {text: ' с даты подписания УПД на эту партию'},
                {cite: 1},
                {text: '.'},
            ],
        ],
        sources: [PAYMENT_SOURCE],
        steps: [
            {title: 'Разбор вопроса', detail: 'договор П-17/2024, тема: срок оплаты', durationLabel: '0,2 с'},
            {title: 'Поиск по базе', detail: '17 фрагментов в 21 документе', durationLabel: '0,4 с'},
            {title: 'Реранжирование', detail: '1 фрагмент выше порога 0,80', durationLabel: '0,5 с'},
            {title: 'Составление ответа', detail: '1 утверждение со ссылкой', durationLabel: '0,5 с'},
            {title: 'Самопроверка', detail: 'утверждение подтверждено', durationLabel: '0,3 с'},
        ],
        followUps: ['Какая неустойка за просрочку оплаты?'],
    },
    notFound: {
        status: ANSWER_STATUSES.refusal,
        verdict: 'Обоснованный отказ',
        totalDurationLabel: '1,6 с',
        context: [{label: 'Договор', value: 'не указан'}],
        paragraphs: [
            [
                {text: 'В базе знаний '},
                {text: 'нет положений', isBold: true},
                {
                    text: ', которые отвечают на этот вопрос, поэтому вывод я не делаю. Уточните договор или приложите документ.',
                },
            ],
        ],
        sources: [],
        checkedDocuments: ['Договоры и допсоглашения', 'Внутренние документы', 'Законы в действующей редакции'],
        steps: [
            {title: 'Разбор вопроса', detail: 'тема определена', durationLabel: '0,2 с'},
            {title: 'Поиск по базе', detail: '9 фрагментов', durationLabel: '0,4 с'},
            {title: 'Реранжирование', detail: '0 фрагментов выше порога 0,80', durationLabel: '0,5 с'},
            {title: 'Решение', detail: 'данных недостаточно — обоснованный отказ', durationLabel: '0,5 с'},
        ],
    },
});

export const MOCK_ANSWER_KEYWORDS = Object.freeze([
    {key: 'notFound', words: ['пт-05', 'альфа-трейдинг']},
    {key: 'approval', words: ['соглас', 'финдиректор', 'финансов', 'подпис']},
    {key: 'payment', words: ['оплат', 'срок оплаты']},
]);
