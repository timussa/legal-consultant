<script setup>
import {computed, ref, watch} from 'vue';
import {LoaderCircle, Send} from 'lucide-vue-next';

const props = defineProps({
    isAsking: {type: Boolean, default: false},
    placeholder: {type: String, default: 'Уточните вопрос или задайте новый'},
    initialText: {type: String, default: ''},
});

const emit = defineEmits(['ask']);

const text = ref(props.initialText);

const canSend = computed(() => text.value.trim().length > 0 && !props.isAsking);

watch(
    () => props.initialText,
    (value) => {
        text.value = value;
    },
);

function handleSubmit() {
    if (!canSend.value) {
        return;
    }

    emit('ask', text.value.trim());
    text.value = '';
}

/** @param {KeyboardEvent} event */
function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSubmit();
    }
}
</script>

<template>
    <form
        class="dialog-composer"
        @submit.prevent="handleSubmit"
    >
        <textarea
            v-model="text"
            class="dialog-composer__input"
            rows="1"
            :placeholder="placeholder"
            aria-label="Вопрос ассистенту"
            @keydown="handleKeydown"
        />
        <button
            class="dialog-composer__send"
            type="submit"
            :disabled="!canSend"
            aria-label="Спросить"
        >
            <LoaderCircle
                v-if="isAsking"
                class="dialog-composer__spinner"
                :size="18"
                aria-hidden="true"
            />
            <Send
                v-else
                :size="18"
                aria-hidden="true"
            />
            <span class="dialog-composer__send-label">Спросить</span>
        </button>
    </form>
</template>

<style lang="scss">
.dialog-composer {
    position: sticky;
    bottom: $indent-step * 4;
    display: flex;
    align-items: flex-end;
    transition: box-shadow $duration ease;
    border-radius: $radius-2xl;
    background: rgba($color-surface, 92%);
    box-shadow: $shadow-card;
    backdrop-filter: blur(12px);
    gap: $indent-step * 2;

    @include gradient-border(1px);
    @include padding('y', 2);
    @include padding('left', 4);
    @include padding('right', 2);

    &:focus-within {
        box-shadow:
            0 0 0 4px rgba($color-violet-bright, 12%),
            $shadow-card;
    }

    &__input {
        flex: 1;
        min-height: 40px;
        max-height: 160px;
        color: $color-ink;
        border: none;
        outline: none;
        background: transparent;
        font: inherit;
        font-size: $font-size-base;
        line-height: 1.5;
        resize: none;
        field-sizing: content;

        @include padding('y', 2);

        &::placeholder {
            color: $color-ink-faint;
        }
    }

    &__send {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        transition:
            opacity $duration ease,
            transform $duration-fast $ease-out;
        color: $color-white;
        border-radius: $radius-lg;
        background: $gradient-user;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include padding('y', 2.5);
        @include padding('x', 4);

        &:disabled {
            opacity: 0.5;
            cursor: default;
        }

        &:not(:disabled) {
            @include hover {
                transform: translateY(-1px);
            }
        }
    }

    &__spinner {
        animation: spin 0.9s linear infinite;
    }

    @include mobile {
        bottom: $indent-step * 20;

        &__send-label {
            display: none;
        }
    }
}
</style>
