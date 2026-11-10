<script setup>
defineProps({
    /** @type {import('vue').PropType<{value: string, label: string, hint?: string}[]>} */
    options: {type: Array, required: true},
    label: {type: String, required: true},
    isOnBrand: {type: Boolean, default: false},
    isDisabled: {type: Boolean, default: false},
});

const model = defineModel({type: String, required: true});
</script>

<template>
    <div
        :class="['ui-segmented', {'ui-segmented--on-brand': isOnBrand}]"
        role="radiogroup"
        :aria-label="label"
    >
        <button
            v-for="option in options"
            :key="option.value"
            type="button"
            role="radio"
            :aria-checked="model === option.value"
            :disabled="isDisabled"
            :class="['ui-segmented__option', {'ui-segmented__option--active': model === option.value}]"
            @click="model = option.value"
        >
            {{ option.label }}
            <span
                v-if="option.hint"
                class="ui-segmented__hint"
            >
                {{ option.hint }}
            </span>
        </button>
    </div>
</template>

<style lang="scss">
.ui-segmented {
    $block: &;

    display: inline-flex;
    border-radius: $radius-pill;
    background: $color-surface-muted;
    gap: $indent-step;

    @include padding('y', 1);
    @include padding('x', 1);

    &__option {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: baseline;
        transition:
            background $duration ease,
            color $duration ease,
            box-shadow $duration ease;
        color: $color-ink-muted;
        border-radius: $radius-pill;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        white-space: nowrap;
        gap: $indent-step * 1.5;

        @include padding('y', 1.5);
        @include padding('x', 3.5);

        @include hover {
            color: $color-ink;
        }

        &:disabled {
            cursor: progress;
        }

        &--active {
            color: $color-navy;
            background: $color-surface;
            box-shadow: $shadow-soft;

            @include hover {
                color: $color-navy;
            }
        }
    }

    &__hint {
        opacity: 0.7;
        font-size: $font-size-2xs;
        font-weight: $font-weight-semibold;
    }

    &--on-brand {
        backdrop-filter: blur(10px);

        @include glass;

        #{$block}__option {
            color: $color-on-brand-muted;

            @include hover {
                color: $color-white;
            }

            &--active {
                color: $color-navy;
                background: $color-white;

                @include hover {
                    color: $color-navy;
                }
            }
        }
    }
}
</style>
