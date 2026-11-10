<script setup>
import {computed} from 'vue';
import {Ban, Check, Ellipsis, Flag, PenLine, X} from 'lucide-vue-next';
import {ANSWER_STATUS_LABELS, ANSWER_STATUSES} from '@/core/constants';

const STATUS_ICONS = Object.freeze({
    [ANSWER_STATUSES.confirmed]: Check,
    [ANSWER_STATUSES.refusal]: X,
    [ANSWER_STATUSES.clarification]: Ellipsis,
    [ANSWER_STATUSES.correction]: PenLine,
    [ANSWER_STATUSES.disputed]: Flag,
    [ANSWER_STATUSES.offTopic]: Ban,
});

const props = defineProps({
    status: {type: String, required: true},
    label: {type: String, default: ''},
    isOnBrand: {type: Boolean, default: false},
});

const icon = computed(() => STATUS_ICONS[props.status] ?? Check);
const text = computed(() => props.label || ANSWER_STATUS_LABELS[props.status]);
</script>

<template>
    <span :class="['ui-status-pill', `ui-status-pill--${status}`, {'ui-status-pill--on-brand': isOnBrand}]">
        <span class="ui-status-pill__mark">
            <component
                :is="icon"
                :size="12"
                :stroke-width="2.6"
                aria-hidden="true"
            />
        </span>
        {{ text }}
    </span>
</template>

<style lang="scss">
$status-tones: (
    confirmed: (
        $color-navy,
        $color-navy-tint,
        $color-navy,
    ),
    refusal: (
        $color-orange,
        $color-peach,
        $color-peach-ink,
    ),
    clarification: (
        $color-gold,
        $color-amber,
        $color-amber-ink,
    ),
    correction: (
        $color-violet,
        $color-lavender,
        $color-violet,
    ),
    disputed: (
        $color-orange-soft,
        $color-peach-soft,
        $color-peach-deep,
    ),
    off-topic: (
        $color-ink-muted,
        $color-surface-muted,
        $color-ink-soft,
    ),
);

.ui-status-pill {
    $block: &;

    display: inline-flex;
    align-items: center;
    border-radius: $radius-pill;
    font-size: $font-size-xs;
    font-weight: $font-weight-bold;
    white-space: nowrap;
    gap: $indent-step * 1.5;

    @include padding('y', 0.75);
    @include padding('left', 0.75);
    @include padding('right', 2.5);

    &__mark {
        @include flex-center;

        flex-shrink: 0;
        width: 20px;
        height: 20px;
        color: $color-white;
        border-radius: $radius-pill;
    }

    @each $status, $tone in $status-tones {
        $solid: nth($tone, 1);
        $tint: nth($tone, 2);
        $ink: nth($tone, 3);

        &--#{$status} {
            color: $ink;
            background: $tint;
            box-shadow: inset 0 0 0 1px rgba($solid, 18%);

            #{$block}__mark {
                background: $solid;
                box-shadow:
                    0 2px 6px -2px rgba($solid, 70%),
                    inset 0 1px 0 rgba($color-white, 30%);
            }
        }
    }

    &--on-brand {
        color: $color-white;
        background: rgba($color-white, 14%);
        box-shadow: inset 0 0 0 1px rgba($color-white, 30%);
        backdrop-filter: blur(8px);

        #{$block}__mark {
            color: $color-navy;
            background: $color-white;
            box-shadow: none;
        }
    }
}
</style>
