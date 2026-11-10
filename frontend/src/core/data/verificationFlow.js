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

export const FLOW_CANVAS = Object.freeze({width: 1140, height: 620});

export const FLOW_NODES = Object.freeze([
    {id: 'question', kind: FLOW_NODE_KINDS.start, label: 'Вопрос юриста', x: 40, y: 52, width: 180, height: 56},
    {
        id: 'parse',
        kind: FLOW_NODE_KINDS.action,
        label: 'Разбор: договор, дата события, тема',
        x: 280,
        y: 48,
        width: 200,
        height: 64,
    },
    {
        id: 'context',
        kind: FLOW_NODE_KINDS.decision,
        label: 'Хватает контекста?',
        x: 540,
        y: 20,
        width: 120,
        height: 120,
    },
    {
        id: 'search',
        kind: FLOW_NODE_KINDS.action,
        label: 'Гибридный поиск bge-m3 + BM25, реранк',
        x: 720,
        y: 48,
        width: 200,
        height: 64,
    },
    {
        id: 'clarify',
        kind: FLOW_NODE_KINDS.clarification,
        label: 'Уточняющий вопрос',
        x: 520,
        y: 220,
        width: 160,
        height: 60,
    },
    {
        id: 'threshold',
        kind: FLOW_NODE_KINDS.decision,
        label: 'Источники выше 0,80?',
        x: 760,
        y: 200,
        width: 120,
        height: 120,
    },
    {
        id: 'refusal',
        kind: FLOW_NODE_KINDS.refusal,
        label: 'Обоснованный отказ',
        x: 940,
        y: 230,
        width: 160,
        height: 60,
    },
    {
        id: 'compose',
        kind: FLOW_NODE_KINDS.action,
        label: 'Ответ со ссылками на пункты и редакцию',
        x: 720,
        y: 360,
        width: 200,
        height: 64,
    },
    {
        id: 'selfcheck',
        kind: FLOW_NODE_KINDS.decision,
        label: 'Самопроверка пройдена?',
        x: 760,
        y: 460,
        width: 120,
        height: 120,
    },
    {id: 'fix', kind: FLOW_NODE_KINDS.fix, label: 'Убрать неподтверждённое', x: 520, y: 490, width: 160, height: 60},
    {id: 'finish', kind: FLOW_NODE_KINDS.finish, label: 'Ответ юристу', x: 940, y: 492, width: 160, height: 56},
    {
        id: 'guard',
        kind: FLOW_NODE_KINDS.guard,
        label: 'Защита роли: [SYSTEM] от пользователя не исполняется',
        x: 40,
        y: 200,
        width: 180,
        height: 84,
    },
]);

export const FLOW_LINES = Object.freeze([
    {id: 'question-parse', direction: 'right', x: 220, y: 79, length: 52},
    {id: 'parse-context', direction: 'right', x: 480, y: 79, length: 54},
    {id: 'context-search', direction: 'right', x: 660, y: 79, length: 52, label: 'да'},
    {id: 'context-clarify', direction: 'down', x: 599, y: 140, length: 72, label: 'нет', isBranch: true},
    {id: 'search-threshold', direction: 'down', x: 819, y: 112, length: 82},
    {id: 'threshold-refusal', direction: 'right', x: 880, y: 259, length: 52, label: 'нет', isBranch: true},
    {id: 'threshold-compose', direction: 'down', x: 819, y: 320, length: 32, label: 'да'},
    {id: 'compose-selfcheck', direction: 'down', x: 819, y: 424, length: 30},
    {id: 'selfcheck-finish', direction: 'right', x: 880, y: 519, length: 52, label: 'да'},
    {id: 'selfcheck-fix', direction: 'left', x: 688, y: 519, length: 72, label: 'нет', isBranch: true},
    {id: 'fix-up', direction: 'up', x: 599, y: 392, length: 98, isBranch: true, hasArrow: false},
    {id: 'fix-compose', direction: 'right', x: 599, y: 391, length: 113, isBranch: true},
]);

export const FLOW_GUARD_LINK = Object.freeze({x: 129, y: 108, length: 92});

export const FLOW_LEGEND = Object.freeze([
    {kind: FLOW_NODE_KINDS.start, label: 'Начало'},
    {kind: FLOW_NODE_KINDS.action, label: 'Действие'},
    {kind: FLOW_NODE_KINDS.decision, label: 'Условие'},
    {kind: FLOW_NODE_KINDS.refusal, label: 'Отказ'},
    {kind: FLOW_NODE_KINDS.guard, label: 'Защита'},
    {kind: FLOW_NODE_KINDS.finish, label: 'Завершение'},
]);

export const VERIFICATION_FACTS = Object.freeze([
    {id: 'threshold', label: 'Порог реранка', value: '0,80', text: 'Ниже порога фрагмент в ответ не попадает'},
    {
        id: 'selfcheck',
        label: 'Самопроверка',
        value: 'каждое утверждение',
        text: 'Без подтверждающего пункта утверждение удаляется',
    },
    {
        id: 'editions',
        label: 'Редакции',
        value: 'на дату события',
        text: 'Для договоров учитываются ДС, законы — в действующей редакции',
    },
]);

export const FLOW_SCENARIOS = Object.freeze([
    {
        id: 'confirmed',
        label: 'Ответ со ссылками',
        dialogId: '412',
        nodeIds: ['question', 'parse', 'context', 'search', 'threshold', 'compose', 'selfcheck', 'finish'],
        lineIds: [
            'question-parse',
            'parse-context',
            'context-search',
            'search-threshold',
            'threshold-compose',
            'compose-selfcheck',
            'selfcheck-finish',
        ],
    },
    {
        id: 'refusal',
        label: 'Обоснованный отказ',
        dialogId: '411',
        nodeIds: ['question', 'parse', 'context', 'search', 'threshold', 'refusal'],
        lineIds: ['question-parse', 'parse-context', 'context-search', 'search-threshold', 'threshold-refusal'],
    },
    {
        id: 'clarification',
        label: 'Уточняющий вопрос',
        dialogId: '409',
        nodeIds: ['question', 'parse', 'context', 'clarify'],
        lineIds: ['question-parse', 'parse-context', 'context-clarify'],
    },
    {
        id: 'guard',
        label: 'Подмена роли',
        dialogId: '413',
        nodeIds: ['question', 'guard'],
        lineIds: [],
        hasGuardLink: true,
    },
]);
