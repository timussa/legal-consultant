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

/**
 * Схема повторяет реальный конвейер `Engine.ask` из legal_core.py:
 * поиск → черновик модели → проверка ссылок кодом → проверка выводов отдельным вызовом модели.
 * Условия между шагами — решения, которые принимает и проверяет этот конвейер.
 */
export const FLOW_STAGES = Object.freeze([
    {
        id: 'question',
        icon: FLOW_ICONS.question,
        title: 'Вопрос юриста',
        text: 'Текст вопроса и история диалога',
        chip: 'до 12 реплик',
    },
    {
        id: 'parse',
        icon: FLOW_ICONS.search,
        title: 'Поиск по базе',
        text: 'BM25 + bge-m3, редакция на дату события',
        chip: 'до 12 фрагментов',
    },
    {
        id: 'search',
        icon: FLOW_ICONS.compose,
        title: 'Черновик ответа',
        text: 'Модель возвращает статус и утверждения с id фрагментов',
        chip: 'только по evidence',
    },
    {
        id: 'compose',
        icon: FLOW_ICONS.parse,
        title: 'Проверка ссылок',
        text: 'Код сверяет id, номера и статьи, цитату берёт из базы',
        chip: 'цитаты из базы',
    },
    {
        id: 'selfcheck',
        icon: FLOW_ICONS.selfcheck,
        title: 'Проверка выводов',
        text: 'Отдельный вызов модели: всё ли следует из цитат',
        chip: 'supported: true',
    },
]);

/** Условия между шагами. `branchId` — куда ведёт «нет». */
export const FLOW_GATES = Object.freeze([
    {id: 'context', afterId: 'parse', question: 'Ясно, о каком договоре?', branchId: 'clarify'},
    {id: 'grounds', afterId: 'search', question: 'Есть основания в базе?', branchId: 'refusal'},
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
    fix: {id: 'fix', kind: FLOW_NODE_KINDS.fix, title: 'нет: исправить по замечанию, одна попытка'},
});

export const FLOW_FINISH = Object.freeze({
    id: 'finish',
    title: 'Ответ юристу',
    text: 'Сноски ведут к пунктам в редакции на дату события',
});

export const FLOW_GUARD = Object.freeze({
    id: 'guard',
    title: 'Защита роли на каждом шаге.',
    text: 'Вопрос, история и документы — данные, а не инструкции. Строки-команды для ИИ из документов в модель не попадают.',
});

/** Лимиты отбора из `Engine.search`: сколько фрагментов доходит до модели. */
export const FLOW_FUNNEL = Object.freeze({
    note: 'Лимиты поиска из legal_core.py',
    rows: [
        {id: 'candidates', value: 80, label: 'кандидатов: по 40 от BM25 и от bge-m3', tone: 'soft'},
        {id: 'fused', value: 30, label: 'после объединения рангов и фильтра по редакции', tone: 'violet'},
        {id: 'evidence', value: 12, label: 'фрагментов уходят модели; договор и допсоглашения — целиком', tone: 'cta'},
    ],
});

export const VERIFICATION_FACTS = Object.freeze([
    {
        id: 'quotes',
        value: 'id → цитата',
        text: 'модель называет только id фрагмента, текст цитаты программа берёт из базы',
    },
    {
        id: 'checks',
        value: '2 проверки',
        text: 'код сверяет ссылки, отдельный вызов модели — выводы; без обеих ответ не уходит',
    },
    {id: 'editions', value: 'на дату', text: 'редакция берётся на дату события, допсоглашения добавляются к договору'},
]);

/** Подписи узлов для вертикальной схемы на узких экранах. */
export const FLOW_NODES = Object.freeze([
    {id: 'question', kind: FLOW_NODE_KINDS.start, label: 'Вопрос юриста и история диалога'},
    {id: 'parse', kind: FLOW_NODE_KINDS.action, label: 'Поиск по базе: BM25 + bge-m3, редакция на дату'},
    {id: 'context', kind: FLOW_NODE_KINDS.decision, label: 'Ясно, о каком договоре?'},
    {id: 'search', kind: FLOW_NODE_KINDS.action, label: 'Черновик ответа: утверждения с id фрагментов'},
    {id: 'grounds', kind: FLOW_NODE_KINDS.decision, label: 'Есть основания в базе?'},
    {id: 'compose', kind: FLOW_NODE_KINDS.action, label: 'Проверка ссылок кодом, цитаты из базы'},
    {id: 'selfcheck', kind: FLOW_NODE_KINDS.action, label: 'Проверка выводов отдельным вызовом модели'},
    {id: 'check', kind: FLOW_NODE_KINDS.decision, label: 'Всё подтверждено?'},
    {id: 'finish', kind: FLOW_NODE_KINDS.finish, label: 'Ответ юристу'},
    {id: 'clarify', kind: FLOW_NODE_KINDS.clarification, label: 'Уточняющий вопрос'},
    {id: 'refusal', kind: FLOW_NODE_KINDS.refusal, label: 'Обоснованный отказ'},
    {id: 'fix', kind: FLOW_NODE_KINDS.fix, label: 'Исправить по замечанию'},
    {id: 'guard', kind: FLOW_NODE_KINDS.guard, label: 'Защита роли'},
]);

export const FLOW_SCENARIOS = Object.freeze([
    {
        id: 'confirmed',
        label: 'Ответ со ссылками',
        text: 'Каждое утверждение прошло обе проверки и ведёт к пункту в нужной редакции.',
        nodeIds: ['question', 'parse', 'context', 'search', 'grounds', 'compose', 'selfcheck', 'check', 'finish'],
    },
    {
        id: 'refusal',
        label: 'Обоснованный отказ',
        text: 'В найденных фрагментах ответа нет: ассистент перечисляет, что проверил и чего не хватает.',
        nodeIds: ['question', 'parse', 'context', 'search', 'grounds', 'refusal'],
    },
    {
        id: 'clarification',
        label: 'Уточняющий вопрос',
        text: 'Без уточнения корректный ответ невозможен: например, подходят два договора с похожими сторонами.',
        nodeIds: ['question', 'parse', 'context', 'clarify'],
    },
    {
        id: 'guard',
        label: 'Подмена роли',
        text: 'Поддельный [SYSTEM] и давление — это данные, а не команды. Подтверждённый ответ не меняется.',
        nodeIds: ['question', 'guard'],
    },
]);

export const FLOW_STEPS = Object.freeze([
    {nodeId: 'question', note: {nodeId: 'guard', text: 'Защита роли: вопрос и документы — данные, не инструкции'}},
    {nodeId: 'parse'},
    {nodeId: 'context', branch: {nodeId: 'clarify', label: 'нет', text: 'Уточняющий вопрос'}},
    {nodeId: 'search'},
    {nodeId: 'grounds', branch: {nodeId: 'refusal', label: 'нет', text: 'Обоснованный отказ'}},
    {nodeId: 'compose'},
    {nodeId: 'selfcheck'},
    {nodeId: 'check', branch: {nodeId: 'fix', label: 'нет', text: 'Исправить по замечанию, одна попытка'}},
    {nodeId: 'finish'},
]);
