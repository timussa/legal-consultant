import {onBeforeUnmount, onMounted} from 'vue';

/**
 * Вызывает обработчик при клике вне элемента и по Escape.
 * @param {import('vue').Ref<HTMLElement | null>} target
 * @param {() => void} handler
 */
export function useClickOutside(target, handler) {
    onMounted(() => {
        document.addEventListener('pointerdown', handlePointerDown);
        document.addEventListener('keydown', handleKeydown);
    });

    onBeforeUnmount(() => {
        document.removeEventListener('pointerdown', handlePointerDown);
        document.removeEventListener('keydown', handleKeydown);
    });

    /** @param {PointerEvent} event */
    function handlePointerDown(event) {
        if (target.value && !target.value.contains(event.target)) {
            handler();
        }
    }

    /** @param {KeyboardEvent} event */
    function handleKeydown(event) {
        if (event.key === 'Escape') {
            handler();
        }
    }
}
