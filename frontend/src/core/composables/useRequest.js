import {ref, toValue, watch} from 'vue';
import {getErrorMessage} from '@/core/helpers/getErrorMessage';

/**
 * Загружает данные и перезагружает их при смене параметра.
 * @template T, P
 * @param {(parameter: P) => Promise<T>} request
 * @param {import('vue').MaybeRefOrGetter<P>} [parameter]
 */
export function useRequest(request, parameter) {
    const data = ref(/** @type {T | null} */ (null));
    const isLoading = ref(false);
    const error = ref(/** @type {string | null} */ (null));

    let requestId = 0;

    watch(() => toValue(parameter), load, {immediate: true});

    async function load() {
        requestId += 1;

        const currentId = requestId;

        isLoading.value = true;
        error.value = null;

        try {
            const result = await request(toValue(parameter));

            if (currentId === requestId) {
                data.value = result;
            }
        } catch (requestError) {
            if (currentId === requestId) {
                error.value = getErrorMessage(requestError);
            }
        } finally {
            if (currentId === requestId) {
                isLoading.value = false;
            }
        }
    }

    return {data, isLoading, error, reload: load};
}
