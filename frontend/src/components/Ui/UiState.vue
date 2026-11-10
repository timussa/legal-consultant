<script setup>
import {LoaderCircle, WifiOff} from 'lucide-vue-next';

defineProps({
    isLoading: {type: Boolean, default: false},
    error: {type: String, default: null},
    loadingText: {type: String, default: 'Загружаем…'},
});

const emit = defineEmits(['retry']);
</script>

<template>
    <div
        :class="['ui-state', {'ui-state--error': error}]"
        :role="error ? 'alert' : 'status'"
    >
        <template v-if="error">
            <WifiOff
                :size="28"
                aria-hidden="true"
            />
            <p class="ui-state__text">{{ error }}</p>
            <button
                class="ui-state__retry"
                type="button"
                @click="emit('retry')"
            >
                Повторить
            </button>
        </template>
        <template v-else-if="isLoading">
            <LoaderCircle
                class="ui-state__spinner"
                :size="28"
                aria-hidden="true"
            />
            <p class="ui-state__text">{{ loadingText }}</p>
        </template>
        <slot v-else />
    </div>
</template>

<style lang="scss">
.ui-state {
    @include flex-center;
    @include column($indent-step * 3);

    align-items: center;
    min-height: 240px;
    color: $color-ink-muted;
    text-align: center;

    &--error {
        color: $color-peach-ink;
    }

    &__text {
        max-width: 360px;
        margin: 0;
        font-size: $font-size-md;
    }

    &__spinner {
        color: $color-violet;
        animation: spin 0.9s linear infinite;
    }

    &__retry {
        @include button-reset;
        @include focus-ring;

        color: $color-navy;
        border: 1px solid $color-line;
        border-radius: $radius-lg;
        background: $color-surface;
        font-weight: $font-weight-bold;

        @include padding('y', 2);
        @include padding('x', 4);
    }
}
</style>
