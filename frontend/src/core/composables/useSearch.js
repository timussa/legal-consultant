import {onScopeDispose, ref, watch} from 'vue';
import {searchKnowledgeBase} from '@/core/api/search';
import {getErrorMessage} from '@/core/helpers/getErrorMessage';

const DEBOUNCE_MS = 150;

/**
 * Поиск по базе с задержкой ввода. Устаревшие ответы отбрасываются.
 * @param {import('vue').Ref<string>} query
 */
export function useSearch(query) {
    const hits = ref(/** @type {import('@/core/utils/search').SearchHit[]} */ ([]));
    const isLoading = ref(false);
    const error = ref(/** @type {string | null} */ (null));

    let timerId = null;
    let requestId = 0;

    watch(query, schedule);

    onScopeDispose(() => clearTimeout(timerId));

    function schedule() {
        clearTimeout(timerId);
        timerId = setTimeout(run, DEBOUNCE_MS);
    }

    async function run() {
        requestId += 1;

        const currentId = requestId;
        const text = query.value.trim();

        if (!text) {
            hits.value = [];
            isLoading.value = false;

            return;
        }

        isLoading.value = true;
        error.value = null;

        try {
            const result = await searchKnowledgeBase(text);

            if (currentId === requestId) {
                hits.value = result;
            }
        } catch (searchError) {
            if (currentId === requestId) {
                error.value = getErrorMessage(searchError);
            }
        } finally {
            if (currentId === requestId) {
                isLoading.value = false;
            }
        }
    }

    return {hits, isLoading, error};
}
