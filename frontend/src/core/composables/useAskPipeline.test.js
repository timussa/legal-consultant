import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {effectScope, nextTick, ref} from 'vue';
import {useAskPipeline} from '@/core/composables/useAskPipeline';

/** @returns {import('@/core/types/assistant').Answer} */
function makeAnswer() {
    return {
        steps: [{title: 'Поиск'}, {title: 'Проверка'}],
        paragraphs: [[{text: 'Вывод по договору'}, {cite: 1}, {text: ' и по регламенту'}, {cite: 2}]],
        sources: [],
    };
}

describe('useAskPipeline', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('проходит шаги, затем печатает текст, и сноски появляются по ходу', () => {
        const scope = effectScope();
        const pipeline = scope.run(() => useAskPipeline(ref(makeAnswer())));

        expect(pipeline.activeStepIndex.value).toBe(0);

        vi.advanceTimersByTime(1200);
        expect(pipeline.isStepsDone.value).toBe(true);
        expect(pipeline.revealedCiteCount.value).toBe(0);

        vi.advanceTimersByTime(60);
        expect(pipeline.revealedCiteCount.value).toBe(1);
        expect(pipeline.isTextComplete.value).toBe(false);

        vi.advanceTimersByTime(90);
        expect(pipeline.revealedCiteCount.value).toBe(2);
        expect(pipeline.isComplete.value).toBe(true);

        scope.stop();
    });

    it('без потоковой печати показывает текст сразу после шагов', () => {
        const scope = effectScope();
        const pipeline = scope.run(() => useAskPipeline(ref(makeAnswer()), {isStreaming: false}));

        vi.advanceTimersByTime(1200);
        expect(pipeline.isComplete.value).toBe(true);

        scope.stop();
    });

    it('сразу показывает уже просмотренный ответ', async () => {
        const answer = ref(makeAnswer());
        const scope = effectScope();
        const pipeline = scope.run(() => useAskPipeline(answer));
        const sameAnswer = answer.value;

        answer.value = null;
        await nextTick();
        answer.value = sameAnswer;
        await nextTick();

        expect(pipeline.isComplete.value).toBe(true);

        scope.stop();
    });

    it('сбрасывает состояние, пока ответа нет', () => {
        const scope = effectScope();
        const pipeline = scope.run(() => useAskPipeline(ref(null)));

        expect(pipeline.activeStepIndex.value).toBe(-1);
        expect(pipeline.progress.value).toBe(0);

        scope.stop();
    });
});
