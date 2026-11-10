import {onBeforeUnmount, onMounted, ref} from 'vue';

const MIN_SELECTION_LENGTH = 3;

/**
 * @typedef {Object} TextSelection
 * @property {string} text
 * @property {string | null} clauseId Пункт, в котором выделен текст (`data-clause-id`)
 * @property {number} x Центр выделения относительно корня
 * @property {number} y Верх выделения относительно корня
 */

/**
 * @param {import('vue').Ref<HTMLElement | null>} root
 */
export function useTextSelection(root) {
    const selection = ref(/** @type {TextSelection | null} */ (null));

    onMounted(() => {
        document.addEventListener('mouseup', handleSelectionEnd);
        document.addEventListener('keyup', handleSelectionEnd);
    });

    onBeforeUnmount(() => {
        document.removeEventListener('mouseup', handleSelectionEnd);
        document.removeEventListener('keyup', handleSelectionEnd);
    });

    function clear() {
        selection.value = null;
    }

    function handleSelectionEnd() {
        const current = window.getSelection();
        const text = current?.toString().trim() ?? '';

        if (!root.value || !current || current.isCollapsed || text.length < MIN_SELECTION_LENGTH) {
            clear();

            return;
        }

        const range = current.getRangeAt(0);

        if (!root.value.contains(range.commonAncestorContainer)) {
            clear();

            return;
        }

        const rootRect = root.value.getBoundingClientRect();
        const rect = range.getBoundingClientRect();
        const element =
            range.commonAncestorContainer instanceof Element
                ? range.commonAncestorContainer
                : range.commonAncestorContainer.parentElement;

        selection.value = {
            text,
            clauseId: element?.closest('[data-clause-id]')?.getAttribute('data-clause-id') ?? null,
            x: rect.left + rect.width / 2 - rootRect.left,
            y: rect.top - rootRect.top,
        };
    }

    return {selection, clear};
}
