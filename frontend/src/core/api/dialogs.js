import {http} from '@/core/api/client';
import {resolveMock, USE_MOCKS} from '@/core/api/mocks';
import {APPROVAL_ANSWERS, DIALOGS} from '@/core/data/dialogs';
import {MOCK_ANSWER_KEYWORDS, MOCK_ANSWERS} from '@/core/data/mockAnswers';
import {findMockAnswerKey} from '@/core/utils/mockAnswer';

/** @typedef {import('@/core/types/assistant').Dialog} Dialog */
/** @typedef {import('@/core/types/assistant').Answer} Answer */
/** @typedef {import('@/core/types/assistant').AskRequest} AskRequest */

/** @returns {Promise<Dialog[]>} */
export function getDialogs() {
    if (USE_MOCKS) {
        return resolveMock([...DIALOGS]);
    }

    return http.get('/v1/dialogs');
}

/**
 * @param {AskRequest} request
 * @returns {Answer}
 */
function getMockAnswer(request) {
    const dialog = DIALOGS.find((item) => item.id === request.dialogId);
    const answerKey = findMockAnswerKey(request.question, MOCK_ANSWER_KEYWORDS);

    if (dialog && request.eventDate && APPROVAL_ANSWERS[request.eventDate] && dialog.eventDates) {
        return APPROVAL_ANSWERS[request.eventDate];
    }

    if (answerKey === 'approval') {
        return Object.values(APPROVAL_ANSWERS)[0];
    }

    return MOCK_ANSWERS[answerKey] ?? dialog?.answer ?? MOCK_ANSWERS.notFound;
}

/**
 * @param {AskRequest} request
 * @returns {Promise<Answer>}
 */
export function askQuestion(request) {
    if (USE_MOCKS) {
        return resolveMock(getMockAnswer(request));
    }

    return http.post('/v1/ask', request);
}

/**
 * @param {string} dialogId
 * @param {string | null} value
 * @returns {Promise<void>}
 */
export function sendFeedback(dialogId, value) {
    if (USE_MOCKS) {
        return resolveMock(undefined);
    }

    return http.post(`/v1/dialogs/${dialogId}/feedback`, {value});
}

/**
 * @param {string} dialogId
 * @param {string} decision
 * @returns {Promise<void>}
 */
export function reviewAnswer(dialogId, decision) {
    if (USE_MOCKS) {
        return resolveMock(undefined);
    }

    return http.post(`/v1/dialogs/${dialogId}/review`, {decision});
}
