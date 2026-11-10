import {ANSWER_STATUSES} from '@/core/constants';
import {SOURCES} from '@/core/data/sources';

const PAYMENT_SOURCE = Object.freeze({
    documentId: 'p-17-2024',
    clauseId: '4.2',
    title: 'Договор П-17/2024, п. 4.2',
    meta: 'договор от 12.02.2024',
    before: 'Покупатель оплачивает Товар',
    quote: 'в течение 30 (тридцати) календарных дней с даты подписания универсального передаточного документа (УПД)',
    after: 'на соответствующую партию.',
});

export const OLD_LAW_ANSWER = Object.freeze({
    status: ANSWER_STATUSES.refusal,
    verdict: 'Нет редакции на 2018 год',
    totalDurationLabel: '1,7 с',
    context: [{label: 'Закон', value: 'НК РФ, ст. 164'}],
    paragraphs: [
        [
            {text: 'В базе есть только '},
            {text: 'действующая редакция', isBold: true},
            {text: ' ст. 164 НК РФ: сейчас общая ставка НДС — '},
            {text: '22 %', isBold: true},
            {cite: 1},
            {text: ', пункт изменён с 01.01.2026.'},
        ],
        [
            {text: 'Редакции, действовавшей в 2018 году, в базе нет, поэтому ставку на 2018 год '},
            {text: 'не подтверждаю', isBold: true},
            {text: ' и не делаю выводов по старым периодам.'},
        ],
    ],
    sources: [SOURCES.taxVatRate],
    checkedDocuments: ['НК РФ, ст. 164 — действующая редакция'],
    missingInfo: ['Редакция ст. 164 НК РФ, действовавшая в 2018 году'],
    steps: [
        {title: 'Разбор вопроса', detail: 'закон, период: 2018 год', durationLabel: '0,2 с'},
        {title: 'Выбор редакции', detail: 'в базе только действующая редакция ст. 164', durationLabel: '0,1 с'},
        {title: 'Поиск по базе', detail: '12 фрагментов', durationLabel: '0,4 с'},
        {title: 'Составление ответа', detail: 'действующая ставка со ссылкой', durationLabel: '0,6 с'},
        {title: 'Самопроверка', detail: 'вывод на 2018 год не подтверждён — убран', durationLabel: '0,4 с'},
    ],
});

export const UNLAWFUL_ANSWER = Object.freeze({
    status: ANSWER_STATUSES.refusal,
    verdict: 'Помочь обойти порядок не могу',
    totalDurationLabel: '1,9 с',
    context: [
        {label: 'Договор', value: 'П-17/2024'},
        {label: 'Регламент', value: 'ред. 2025'},
    ],
    paragraphs: [
        [
            {text: 'Оформить договор задним числом, чтобы не согласовывать его с финансовым директором, '},
            {text: 'я помочь не могу', isBold: true},
            {text: '.'},
        ],
        [
            {text: 'По регламенту договоры дороже 3 млн ₽ согласуются с финансовым директором'},
            {cite: 1},
            {text: ', а согласование оформляется в СЭД'},
            {cite: 2},
            {
                text: ', где фиксируется, когда и кем оно проведено. Последствия нарушения порядка в базе знаний не описаны, поэтому оценивать их я не буду.',
            },
        ],
    ],
    sources: [SOURCES.regulation2025Finance, SOURCES.regulation2025Format],
    nextSteps: ['Завести согласование в СЭД', 'Финансовый директор', 'Подписание'],
    steps: [
        {title: 'Разбор вопроса', detail: 'просьба обойти порядок согласования', durationLabel: '0,2 с'},
        {title: 'Проверка допустимости', detail: 'действие противоречит регламенту', durationLabel: '0,3 с'},
        {title: 'Поиск по базе', detail: 'регламент согласования, ред. 2025', durationLabel: '0,4 с'},
        {title: 'Составление ответа', detail: 'правильный порядок со ссылками', durationLabel: '0,6 с'},
        {title: 'Самопроверка', detail: '2 утверждения подтверждены', durationLabel: '0,4 с'},
    ],
});

export const OFF_TOPIC_ANSWER = Object.freeze({
    status: ANSWER_STATUSES.offTopic,
    verdict: 'Вопрос вне компетенции',
    totalDurationLabel: '0,4 с',
    context: [{label: 'Тема', value: 'не юридическая'}],
    paragraphs: [
        [
            {text: 'Я отвечаю на юридические вопросы по базе знаний: договоры, внутренние регламенты и законы. '},
            {text: 'Курсы валют в базе нет', isBold: true},
            {
                text: ', поэтому подсказать не смогу. Если вопрос связан с договором — например, с оплатой в валюте, — уточните договор, и я посмотрю условия.',
            },
        ],
    ],
    sources: [],
    steps: [
        {title: 'Разбор вопроса', detail: 'тема не относится к юридической базе', durationLabel: '0,2 с'},
        {title: 'Решение', detail: 'объяснить границы компетенции', durationLabel: '0,2 с'},
    ],
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
    oldLaw: OLD_LAW_ANSWER,
    unlawful: UNLAWFUL_ANSWER,
    offTopic: OFF_TOPIC_ANSWER,
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
        missingInfo: ['Номер договора или название документа, о котором вопрос'],
        steps: [
            {title: 'Разбор вопроса', detail: 'тема определена', durationLabel: '0,2 с'},
            {title: 'Поиск по базе', detail: '9 фрагментов', durationLabel: '0,4 с'},
            {title: 'Реранжирование', detail: '0 фрагментов выше порога 0,80', durationLabel: '0,5 с'},
            {title: 'Решение', detail: 'данных недостаточно — обоснованный отказ', durationLabel: '0,5 с'},
        ],
    },
});

export const MOCK_ANSWER_KEYWORDS = Object.freeze([
    {key: 'offTopic', words: ['курс доллар', 'курс валют', 'погод', 'рецепт']},
    {key: 'unlawful', words: ['задним числом', 'обойти', 'в обход']},
    {key: 'oldLaw', words: ['2018', '2019', '2020', 'раньше действовал']},
    {key: 'notFound', words: ['пт-05', 'альфа-трейдинг']},
    {key: 'approval', words: ['соглас', 'финдиректор', 'финансов', 'подпис']},
    {key: 'payment', words: ['оплат', 'срок оплаты']},
]);
