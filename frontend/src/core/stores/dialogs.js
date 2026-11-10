import {defineStore} from 'pinia';
import {computed, ref} from 'vue';
import {askQuestion, getDialogs, reviewAnswer, sendFeedback} from '@/core/api/dialogs';
import {ANSWER_STATUSES} from '@/core/constants';
import {getErrorMessage} from '@/core/helpers/getErrorMessage';

/** @typedef {import('@/core/types/assistant').Dialog} Dialog */

const NEW_DIALOG_TITLE_LENGTH = 48;

/**
 * @param {string} question
 * @returns {string}
 */
function makeTitle(question) {
    const trimmed = question.trim().replace(/\?$/, '');

    return trimmed.length > NEW_DIALOG_TITLE_LENGTH ? `${trimmed.slice(0, NEW_DIALOG_TITLE_LENGTH)}…` : trimmed;
}

export const useDialogsStore = defineStore('dialogs', () => {
    const dialogs = ref(/** @type {Dialog[]} */ ([]));
    const isLoading = ref(false);
    const isLoaded = ref(false);
    const loadError = ref(/** @type {string | null} */ (null));
    const askingDialogId = ref(/** @type {string | null} */ (null));
    const askError = ref(/** @type {string | null} */ (null));
    const feedback = ref(/** @type {Record<string, string | null>} */ ({}));
    const reviews = ref(/** @type {Record<string, string>} */ ({}));

    const nextNumber = computed(() => {
        const numbers = dialogs.value.map((dialog) => Number(dialog.id)).filter(Number.isFinite);

        return numbers.length ? Math.max(...numbers) + 1 : 1;
    });

    /**
     * @param {string | undefined} dialogId
     * @returns {Dialog | undefined}
     */
    function getDialog(dialogId) {
        return dialogs.value.find((dialog) => dialog.id === dialogId);
    }

    let loadPromise = null;

    /** @returns {Promise<void>} */
    function load() {
        if (isLoaded.value) {
            return Promise.resolve();
        }

        loadPromise ??= fetchDialogs().finally(() => {
            loadPromise = null;
        });

        return loadPromise;
    }

    async function fetchDialogs() {
        isLoading.value = true;
        loadError.value = null;

        try {
            const loaded = await getDialogs();
            const loadedIds = new Set(loaded.map((dialog) => dialog.id));
            const created = dialogs.value.filter((dialog) => !loadedIds.has(dialog.id));

            dialogs.value = [...created, ...loaded];
            isLoaded.value = true;
        } catch (error) {
            loadError.value = getErrorMessage(error);
        } finally {
            isLoading.value = false;
        }
    }

    /**
     * @param {string} question
     * @returns {Dialog}
     */
    function createDialog(question) {
        const id = String(nextNumber.value);
        const dialog = {
            id,
            number: `№${id}`,
            title: makeTitle(question),
            documentLabel: 'определяется',
            timeLabel: 'сейчас',
            status: ANSWER_STATUSES.clarification,
            question,
            answer: null,
        };

        dialogs.value.unshift(dialog);

        return getDialog(id);
    }

    /**
     * @param {Dialog} dialog
     * @param {string} question
     */
    function moveToHistory(dialog, question) {
        if (!dialog.answer || dialog.question === question) {
            return;
        }

        dialog.history = {
            summary: `предыдущий вопрос · ${dialog.answer.verdict.toLowerCase()}`,
            question: dialog.question,
            answer: dialog.answer.verdict,
        };
        dialog.question = question;
    }

    /**
     * @param {string} question
     * @param {{dialogId?: string, documentId?: string, eventDate?: string}} [options]
     * @returns {Promise<string>} id диалога, в котором задан вопрос
     */
    async function ask(question, options = {}) {
        await load();

        const dialog = getDialog(options.dialogId) ?? createDialog(question);

        moveToHistory(dialog, question);
        askingDialogId.value = dialog.id;
        askError.value = null;

        try {
            const answer = await askQuestion({
                question,
                dialogId: dialog.id,
                documentId: options.documentId,
                eventDate: options.eventDate ?? dialog.eventDate,
            });

            dialog.answer = answer;
            dialog.status = answer.status;
            dialog.documentLabel = answer.context[0]?.value ?? dialog.documentLabel;
        } catch (error) {
            askError.value = getErrorMessage(error);
        } finally {
            askingDialogId.value = null;
        }

        return dialog.id;
    }

    /**
     * @param {string} dialogId
     * @param {string} eventDate
     */
    async function changeEventDate(dialogId, eventDate) {
        const dialog = getDialog(dialogId);

        if (!dialog || dialog.eventDate === eventDate) {
            return;
        }

        dialog.eventDate = eventDate;
        await ask(dialog.question, {dialogId, eventDate});
    }

    /**
     * @param {string} dialogId
     * @param {string} value
     * @returns {Promise<boolean>} удалось ли сохранить отметку
     */
    async function setFeedback(dialogId, value) {
        const previous = feedback.value[dialogId] ?? null;
        const next = previous === value ? null : value;

        feedback.value[dialogId] = next;

        try {
            await sendFeedback(dialogId, next);

            return true;
        } catch (error) {
            feedback.value[dialogId] = previous;
            askError.value = getErrorMessage(error);

            return false;
        }
    }

    /**
     * @param {{id: string, dialogId: string}} answer
     * @param {string} decision
     * @returns {Promise<boolean>} удалось ли сохранить решение
     */
    async function review(answer, decision) {
        reviews.value[answer.id] = decision;

        try {
            await reviewAnswer(answer.dialogId, decision);

            return true;
        } catch (error) {
            delete reviews.value[answer.id];
            askError.value = getErrorMessage(error);

            return false;
        }
    }

    return {
        dialogs,
        isLoading,
        loadError,
        askingDialogId,
        askError,
        feedback,
        reviews,
        getDialog,
        load,
        ask,
        changeEventDate,
        setFeedback,
        review,
    };
});
