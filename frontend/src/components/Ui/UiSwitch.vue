<script setup>
defineProps({
    label: {type: String, required: true},
    hint: {type: String, default: ''},
    isDisabled: {type: Boolean, default: false},
});

const model = defineModel({type: Boolean, default: false});
</script>

<template>
    <label :class="['ui-switch', {'ui-switch--disabled': isDisabled}]">
        <span class="ui-switch__text">
            <span class="ui-switch__label">{{ label }}</span>
            <span
                v-if="hint"
                class="ui-switch__hint"
            >
                {{ hint }}
            </span>
        </span>
        <button
            :class="['ui-switch__track', {'ui-switch__track--on': model}]"
            type="button"
            role="switch"
            :aria-checked="model"
            :aria-label="label"
            :disabled="isDisabled"
            @click="model = !model"
        >
            <span class="ui-switch__thumb" />
        </button>
    </label>
</template>

<style lang="scss">
.ui-switch {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    gap: $indent-step * 4;

    &--disabled {
        opacity: 0.55;
        cursor: not-allowed;
    }

    &__text {
        @include column($indent-step * 0.5);
    }

    &__label {
        color: $color-ink;
        font-size: $font-size-md;
        font-weight: $font-weight-semibold;
    }

    &__hint {
        color: $color-ink-muted;
        font-size: $font-size-sm;
        line-height: 1.45;
    }

    &__track {
        @include button-reset;
        @include focus-ring;

        position: relative;
        flex-shrink: 0;
        width: 44px;
        height: 26px;
        transition: background-color $duration ease;
        border-radius: $radius-pill;
        background-color: $color-line-strong;

        &--on {
            background-color: $color-action;
        }

        &:disabled {
            cursor: not-allowed;
        }
    }

    &__thumb {
        position: absolute;
        top: 3px;
        left: 3px;
        width: 20px;
        height: 20px;
        transition: transform $duration $ease-out;
        border-radius: $radius-pill;
        background-color: $color-white;
        box-shadow: $shadow-soft;
    }

    &__track--on &__thumb {
        transform: translateX(18px);
    }
}
</style>
