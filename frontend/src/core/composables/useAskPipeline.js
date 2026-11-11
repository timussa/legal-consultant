import {computed, onScopeDispose, ref, toValue, watch} from 'vue';
import {getPartOffsets} from '@/core/utils/answer';

/** @typedef {import('@/core/types/assistant').Answer} Answer */

const STEP_DURATION_MS = 600;
const TYPE_TICK_MS = 30;
const CHARS_PER_TICK = 9;

const shownAnswers = new WeakSet();

/**
 * Проигрывает ход проверки ответа: шаги пайплайна, затем печатает текст, сноски появляются по ходу.
 * Уже показанный ответ раскрывается сразу.
 * @param {import('vue').Ref<Answer | null>} answer
 * @param {{isStreaming?: import('vue').MaybeRefOrGetter<boolean>}} [options]
 */
export function useAskPipeline(answer, options = {}) {
    const activeStepIndex = ref(-1);
    const revealedChars = ref(0);

    let timerId = null;

    const steps = computed(() => answer.value?.steps ?? []);
    const offsets = computed(() => getPartOffsets(answer.value?.paragraphs ?? []));
    const isStepsDone = computed(() => activeStepIndex.value >= steps.value.length);
    const isTextComplete = computed(() => revealedChars.value >= offsets.value.total);
    const isStreamingText = computed(() => isStepsDone.value && !isTextComplete.value);
    const isComplete = computed(() => isStepsDone.value && isTextComplete.value);
    const revealedCiteCount = computed(() =>
        isStepsDone.value ? offsets.value.citeOffsets.filter((offset) => offset <= revealedChars.value).length : 0,
    );
    const progress = computed(() =>
        steps.value.length ? Math.min(1, Math.max(0, activeStepIndex.value) / steps.value.length) : 0,
    );

    watch(answer, start, {immediate: true});

    onScopeDispose(stop);

    function stop() {
        clearInterval(timerId);
        timerId = null;
    }

    function finish() {
        stop();
        activeStepIndex.value = steps.value.length;
        revealedChars.value = offsets.value.total;
    }

    function typeText() {
        stop();

        if (toValue(options.isStreaming) === false) {
            revealedChars.value = offsets.value.total;

            return;
        }

        timerId = setInterval(() => {
            revealedChars.value = Math.min(offsets.value.total, revealedChars.value + CHARS_PER_TICK);

            if (revealedChars.value >= offsets.value.total) {
                stop();
            }
        }, TYPE_TICK_MS);
    }

    function runSteps() {
        stop();
        activeStepIndex.value = 0;
        revealedChars.value = 0;
        timerId = setInterval(() => {
            activeStepIndex.value += 1;

            if (activeStepIndex.value >= steps.value.length) {
                typeText();
            }
        }, STEP_DURATION_MS);
    }

    function start() {
        if (!answer.value) {
            stop();
            activeStepIndex.value = -1;
            revealedChars.value = 0;

            return;
        }

        if (shownAnswers.has(answer.value)) {
            finish();

            return;
        }

        shownAnswers.add(answer.value);
        runSteps();
    }

    function replay() {
        if (answer.value) {
            runSteps();
        }
    }

    return {
        activeStepIndex,
        revealedChars,
        revealedCiteCount,
        isStepsDone,
        isTextComplete,
        isStreamingText,
        isComplete,
        progress,
        replay,
        finish,
    };
}
