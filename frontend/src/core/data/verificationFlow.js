export const FLOW_NODE_KINDS = Object.freeze({
    start: 'start',
    action: 'action',
    decision: 'decision',
    clarification: 'clarification',
    refusal: 'refusal',
    fix: 'fix',
    guard: 'guard',
    finish: 'finish',
});

export const FLOW_ICONS = Object.freeze({
    question: 'question',
    parse: 'parse',
    search: 'search',
    compose: 'compose',
    selfcheck: 'selfcheck',
});

/** Основная линия: шаги, через которые проходит каждый вопрос. */
export const FLOW_STAGES = Object.freeze([
    {
        id: 'question',
        icon: FLOW_ICONS.question,
        title: 'Вопрос юриста',
        text: 'Свободный текст, можно приложить договор',
        chip: '«Можно подписать?»',
    },
    {
        id: 'parse',
        icon: FLOW_ICONS.parse,
        title: 'Разбор',
        text: 'Договор, дата события, тема',
        chip: '10.11.2026',
    },
    {
        id: 'search',
        icon: FLOW_ICONS.search,
        title: 'Поиск по базе',
        text: 'bge-m3 + BM25, затем реранк',
        chip: '38 фрагментов',
    },
    {
        id: 'compose',
        icon: FLOW_ICONS.compose,
        title: 'Ответ',
        text: 'Каждый вывод со ссылкой на пункт и редакцию',
        chip: '5 сносок',
    },
    {
        id: 'selfcheck',
        icon: FLOW_ICONS.selfcheck,
        title: 'Самопроверка',
        text: 'Каждое утверждение сверяется с источником',
        chip: '5 из 5',
    },
]);

/** Условия между шагами. `branchId` — куда ведёт «нет». */
export const FLOW_GATES = Object.freeze([
    {id: 'context', afterId: 'parse', question: 'Хватает контекста?', branchId: 'clarify'},
    {id: 'threshold', afterId: 'search', question: 'Источники выше 0,80?', branchId: 'refusal'},
    {id: 'check', afterId: 'selfcheck', question: 'Всё подтверждено?', branchId: 'fix'},
]);

export const FLOW_OUTCOMES = Object.freeze({
    clarify: {
        id: 'clarify',
        kind: FLOW_NODE_KINDS.clarification,
        title: 'Уточняющий вопрос',
        text: '«Какой договор: П-17 или ПТ-05?»',
    },
    refusal: {
        id: 'refusal',
        kind: FLOW_NODE_KINDS.refusal,
        title: 'Обоснованный отказ',
        text: 'Что проверено и каких данных нет',
    },
    fix: {id: 'fix', kind: FLOW_NODE_KINDS.fix, title: 'нет: убрать утверждение и проверить'},
});

export const FLOW_FINISH = Object.freeze({
    id: 'finish',
    title: 'Ответ юристу',
    text: 'Сноски ведут к пунктам и редакции на дату события',
});

export const FLOW_GUARD = Object.freeze({
    id: 'guard',
    title: 'Защита роли на каждом шаге.',
    text: 'Команды вида [SYSTEM] внутри вопроса не исполняются.',
});

/** Сколько данных доходит до ответа в диалоге №412. */
export const FLOW_FUNNEL = Object.freeze({
    note: 'Пример: диалог №412, база из 21 документа',
    rows: [
        {id: 'found', value: 38, label: 'фрагментов нашёл поиск', tone: 'soft'},
        {id: 'ranked', value: 5, label: 'выше порога реранка 0,80', tone: 'violet'},
        {id: 'confirmed', value: 5, label: 'утверждений подтверждено', tone: 'cta'},
    ],
});

export const VERIFICATION_FACTS = Object.freeze([
    {id: 'threshold', value: '0,80', text: 'порог реранка: ниже него источник не используется'},
    {id: 'selfcheck', value: '1 : 1', text: 'каждое утверждение сверяется с пунктом'},
    {id: 'editions', value: 'на дату', text: 'редакция берётся на дату события, доп. соглашения учитываются'},
]);

/** Подписи узлов для вертикальной схемы на узких экранах. */
export const FLOW_NODES = Object.freeze([
    {id: 'question', kind: FLOW_NODE_KINDS.start, label: 'Вопрос юриста'},
    {id: 'parse', kind: FLOW_NODE_KINDS.action, label: 'Разбор: договор, дата события, тема'},
    {id: 'context', kind: FLOW_NODE_KINDS.decision, label: 'Хватает контекста?'},
    {id: 'search', kind: FLOW_NODE_KINDS.action, label: 'Поиск по базе: bge-m3 + BM25, реранк'},
    {id: 'threshold', kind: FLOW_NODE_KINDS.decision, label: 'Источники выше 0,80?'},
    {id: 'compose', kind: FLOW_NODE_KINDS.action, label: 'Ответ со ссылками на пункты и редакцию'},
    {id: 'selfcheck', kind: FLOW_NODE_KINDS.action, label: 'Самопроверка каждого утверждения'},
    {id: 'check', kind: FLOW_NODE_KINDS.decision, label: 'Всё подтверждено?'},
    {id: 'finish', kind: FLOW_NODE_KINDS.finish, label: 'Ответ юристу'},
    {id: 'clarify', kind: FLOW_NODE_KINDS.clarification, label: 'Уточняющий вопрос'},
    {id: 'refusal', kind: FLOW_NODE_KINDS.refusal, label: 'Обоснованный отказ'},
    {id: 'fix', kind: FLOW_NODE_KINDS.fix, label: 'Убрать неподтверждённое'},
    {id: 'guard', kind: FLOW_NODE_KINDS.guard, label: 'Защита роли'},
]);

export const FLOW_SCENARIOS = Object.freeze([
    {
        id: 'confirmed',
        label: 'Ответ со ссылками',
        dialogId: '412',
        nodeIds: ['question', 'parse', 'context', 'search', 'threshold', 'compose', 'selfcheck', 'check', 'finish'],
    },
    {
        id: 'refusal',
        label: 'Обоснованный отказ',
        dialogId: '411',
        nodeIds: ['question', 'parse', 'context', 'search', 'threshold', 'refusal'],
    },
    {
        id: 'clarification',
        label: 'Уточняющий вопрос',
        dialogId: '409',
        nodeIds: ['question', 'parse', 'context', 'clarify'],
    },
    {
        id: 'guard',
        label: 'Подмена роли',
        dialogId: '413',
        nodeIds: ['question', 'guard'],
    },
]);

export const FLOW_STEPS = Object.freeze([
    {nodeId: 'question', note: {nodeId: 'guard', text: 'Защита роли: [SYSTEM] от пользователя не исполняется'}},
    {nodeId: 'parse'},
    {nodeId: 'context', branch: {nodeId: 'clarify', label: 'нет', text: 'Уточняющий вопрос'}},
    {nodeId: 'search'},
    {nodeId: 'threshold', branch: {nodeId: 'refusal', label: 'нет', text: 'Обоснованный отказ'}},
    {nodeId: 'compose'},
    {nodeId: 'selfcheck'},
    {nodeId: 'check', branch: {nodeId: 'fix', label: 'нет', text: 'Убрать неподтверждённое и проверить снова'}},
    {nodeId: 'finish'},
]);
