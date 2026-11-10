import {computed, onScopeDispose, ref, watch} from 'vue';
import {countCitations} from '@/core/utils/answer';

/** @typedef {import('@/core/types/assistant').Answer} Answer */

const STEP_DURATION_MS = 600;
const CITE_DURATION_MS = 380;

const shownAnswers = new WeakSet();

/**
 * Проигрывает ход проверки ответа: шаги пайплайна, затем поочерёдно сноски.
 * Уже показанный ответ раскрывается сразу.
 * @param {import('vue').Ref<Answer | null>} answer
 */
export function useAskPipeline(answer) {
    const activeStepIndex = ref(-1);
    const revealedCiteCount = ref(0);

    let timerId = null;

    const steps = computed(() => answer.value?.steps ?? []);
    const citeCount = computed(() => (answer.value ? countCitations(answer.value.paragraphs) : 0));
    const isStepsDone = computed(() => activeStepIndex.value >= steps.value.length);
    const isComplete = computed(() => isStepsDone.value && revealedCiteCount.value >= citeCount.value);
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
        revealedCiteCount.value = citeCount.value;
    }

    function revealCites() {
        stop();
        timerId = setInterval(() => {
            revealedCiteCount.value += 1;

            if (revealedCiteCount.value >= citeCount.value) {
                stop();
            }
        }, CITE_DURATION_MS);
    }

    function runSteps() {
        stop();
        activeStepIndex.value = 0;
        revealedCiteCount.value = 0;
        timerId = setInterval(() => {
            activeStepIndex.value += 1;

            if (activeStepIndex.value >= steps.value.length) {
                revealCites();
            }
        }, STEP_DURATION_MS);
    }

    function start() {
        if (!answer.value) {
            stop();
            activeStepIndex.value = -1;
            revealedCiteCount.value = 0;

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

    return {activeStepIndex, revealedCiteCount, isStepsDone, isComplete, progress, replay, finish};
}
