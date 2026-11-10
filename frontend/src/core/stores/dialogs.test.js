import {createPinia, setActivePinia} from 'pinia';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {askQuestion, getDialogs, reviewAnswer, sendFeedback} from '@/core/api/dialogs';
import {ANSWER_STATUSES} from '@/core/constants';
import {useDialogsStore} from '@/core/stores/dialogs';

vi.mock('@/core/api/dialogs', () => ({
    getDialogs: vi.fn(),
    askQuestion: vi.fn(),
    sendFeedback: vi.fn(),
    reviewAnswer: vi.fn(),
}));

const ANSWER = {
    status: ANSWER_STATUSES.confirmed,
    verdict: 'Проверено 1 из 1',
    context: [{label: 'Договор', value: 'П-17/2024'}],
    paragraphs: [],
    sources: [],
    steps: [],
};

const DIALOG = {
    id: '412',
    number: '№412',
    title: 'Согласование',
    documentLabel: 'П-17/2024',
    question: 'С кем согласовать?',
    eventDate: '2026-11-10',
    status: ANSWER_STATUSES.confirmed,
    answer: ANSWER,
};

describe('dialogs store', () => {
    beforeEach(() => {
        setActivePinia(createPinia());
        vi.clearAllMocks();
        getDialogs.mockResolvedValue([structuredClone(DIALOG)]);
        askQuestion.mockResolvedValue(structuredClone(ANSWER));
        sendFeedback.mockResolvedValue(undefined);
        reviewAnswer.mockResolvedValue(undefined);
    });

    it('загружает диалоги один раз', async () => {
        const store = useDialogsStore();

        await store.load();
        await store.load();

        expect(getDialogs).toHaveBeenCalledTimes(1);
        expect(store.dialogs).toHaveLength(1);
    });

    it('сохраняет текст ошибки загрузки', async () => {
        getDialogs.mockRejectedValue(new Error('offline'));

        const store = useDialogsStore();

        await store.load();

        expect(store.loadError).toBeTruthy();
    });

    it('создаёт новый диалог со следующим номером', async () => {
        const store = useDialogsStore();

        await store.load();

        const dialogId = await store.ask('Срок оплаты по договору?');

        expect(dialogId).toBe('413');
        expect(store.getDialog('413').answer.verdict).toBe('Проверено 1 из 1');
    });

    it('не теряет вопрос, заданный до окончания загрузки', async () => {
        const store = useDialogsStore();
        const loading = store.load();
        const dialogId = await store.ask('Срок оплаты?');

        await loading;

        expect(getDialogs).toHaveBeenCalledTimes(1);
        expect(store.getDialog(dialogId)).toBeTruthy();
        expect(store.dialogs).toHaveLength(2);
    });

    it('переносит прошлый вопрос в историю при уточнении', async () => {
        const store = useDialogsStore();

        await store.load();
        await store.ask('А срок согласования?', {dialogId: '412'});

        expect(store.getDialog('412').history.question).toBe('С кем согласовать?');
    });

    it('перезапрашивает ответ при смене даты события', async () => {
        const store = useDialogsStore();

        await store.load();
        await store.changeEventDate('412', '2024-02-12');

        expect(askQuestion).toHaveBeenCalledWith(expect.objectContaining({eventDate: '2024-02-12'}));
    });

    it('снимает отметку при повторном нажатии и откатывает при ошибке', async () => {
        const store = useDialogsStore();

        await store.setFeedback('412', 'correct');
        expect(store.feedback['412']).toBe('correct');

        await store.setFeedback('412', 'correct');
        expect(store.feedback['412']).toBeNull();

        sendFeedback.mockRejectedValue(new Error('offline'));
        await store.setFeedback('412', 'wrong');
        expect(store.feedback['412']).toBeNull();
    });

    it('сохраняет решение руководителя и откатывает при ошибке', async () => {
        const store = useDialogsStore();
        const answer = {id: 'team-418', dialogId: '418'};

        expect(await store.review(answer, 'approved')).toBe(true);
        expect(store.reviews['team-418']).toBe('approved');
        expect(reviewAnswer).toHaveBeenCalledWith('418', 'approved');

        reviewAnswer.mockRejectedValue(new Error('offline'));
        expect(await store.review({id: 'team-406', dialogId: '406'}, 'needs-fix')).toBe(false);
        expect(store.reviews['team-406']).toBe(undefined);
    });
});
