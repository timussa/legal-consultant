import {defineStore} from 'pinia';
import {ref} from 'vue';

const TOAST_LIFETIME_MS = 2600;

export const useToastStore = defineStore('toast', () => {
    const toasts = ref([]);

    let nextId = 0;

    /** @param {string} text */
    function show(text) {
        nextId += 1;

        const id = nextId;

        toasts.value.push({id, text});
        setTimeout(() => dismiss(id), TOAST_LIFETIME_MS);
    }

    /** @param {number} id */
    function dismiss(id) {
        toasts.value = toasts.value.filter((toast) => toast.id !== id);
    }

    return {toasts, show, dismiss};
});
