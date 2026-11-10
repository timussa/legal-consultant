import {nextTick, onBeforeUnmount, onMounted, ref, watch} from 'vue';
import {buildThreadPath} from '@/core/utils/answer';

/**
 * Нить доказательства: кривая от сноски в ответе к карточке источника.
 * Сноска помечается `data-cite-anchor`, карточка — `data-source-anchor` с тем же номером.
 * @param {import('vue').Ref<HTMLElement | null>} container
 * @param {import('vue').Ref<number | null>} activeCite
 */
export function useEvidenceThread(container, activeCite) {
    const path = ref('');
    const size = ref({width: 0, height: 0});

    let frameId = 0;
    let resizeObserver = null;

    watch(activeCite, () => nextTick(measure));

    onMounted(() => {
        resizeObserver = new ResizeObserver(scheduleMeasure);

        if (container.value) {
            resizeObserver.observe(container.value);
        }

        window.addEventListener('scroll', scheduleMeasure, {passive: true, capture: true});
        window.addEventListener('resize', scheduleMeasure);
    });

    onBeforeUnmount(() => {
        resizeObserver?.disconnect();
        cancelAnimationFrame(frameId);
        window.removeEventListener('scroll', scheduleMeasure, {capture: true});
        window.removeEventListener('resize', scheduleMeasure);
    });

    function measure() {
        const root = container.value;
        const cite = activeCite.value;

        if (!root || cite === null) {
            path.value = '';

            return;
        }

        const from = root.querySelector(`[data-cite-anchor="${cite}"]`);
        const to = root.querySelector(`[data-source-anchor="${cite}"]`);

        if (!from || !to) {
            path.value = '';

            return;
        }

        const rootRect = root.getBoundingClientRect();
        const fromRect = from.getBoundingClientRect();
        const toRect = to.getBoundingClientRect();
        const start = {x: fromRect.right - rootRect.left, y: fromRect.top + fromRect.height / 2 - rootRect.top};
        const end = {x: toRect.left - rootRect.left, y: toRect.top + Math.min(toRect.height / 2, 28) - rootRect.top};

        size.value = {width: rootRect.width, height: rootRect.height};
        path.value = end.x > start.x ? buildThreadPath(start, end) : '';
    }

    function scheduleMeasure() {
        cancelAnimationFrame(frameId);
        frameId = requestAnimationFrame(measure);
    }

    return {path, size, measure};
}
