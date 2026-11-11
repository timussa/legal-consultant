<script setup>
defineProps({
    /** @type {import('vue').PropType<'primary' | 'secondary' | 'quiet' | 'glass'>} */
    variant: {type: String, default: 'primary'},
    type: {type: String, default: 'button'},
    isSmall: {type: Boolean, default: false},
    isDisabled: {type: Boolean, default: false},
});
</script>

<template>
    <button
        :type="type"
        :disabled="isDisabled"
        :class="['ui-button', `ui-button--${variant}`, {'ui-button--small': isSmall}]"
    >
        <slot />
    </button>
</template>

<style lang="scss">
.ui-button {
    @include button-reset;
    @include focus-ring;

    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition:
        transform $duration-fast $ease-out,
        background $duration ease,
        box-shadow $duration ease,
        color $duration ease;
    border-radius: $radius-lg;
    font-size: $font-size-md;
    font-weight: $font-weight-bold;
    white-space: nowrap;
    gap: $indent-step * 2;

    @include padding('y', 2.5);
    @include padding('x', 4.5);

    &:disabled {
        opacity: 0.55;
        cursor: not-allowed;
    }

    @include press;

    &--small {
        border-radius: $radius-md;
        font-size: $font-size-sm;

        @include padding('y', 1.5);
        @include padding('x', 3);
    }

    &--primary {
        @include sheen;

        color: $color-white;
        background-color: $color-cta;
        box-shadow: 0 10px 22px -14px rgba($color-cta, 80%);

        &:not(:disabled) {
            @include hover {
                transform: translateY(-1px);
                box-shadow: 0 14px 26px -14px rgba($color-cta, 85%);
            }
        }
    }

    &--secondary {
        color: $color-navy;
        border: 1px solid $color-line;
        background: $color-surface;

        &:not(:disabled) {
            @include hover {
                border-color: $color-lavender-line;
                background: $color-lavender-soft;
            }
        }
    }

    &--quiet {
        color: $color-ink-soft;

        &:not(:disabled) {
            @include hover {
                color: $color-navy;
                background: $color-surface-muted;
            }
        }
    }

    &--glass {
        color: $color-white;
        backdrop-filter: blur(10px);

        @include glass;

        &:not(:disabled) {
            @include hover {
                background: rgba($color-white, 24%);
            }
        }
    }
}
</style>
