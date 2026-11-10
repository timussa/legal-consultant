<script setup>
import {computed} from 'vue';
import {BadgeCheck, CircleHelp, OctagonX, PencilLine, TriangleAlert} from 'lucide-vue-next';
import {ANSWER_STATUS_LABELS, ANSWER_STATUSES} from '@/core/constants';

const STATUS_ICONS = Object.freeze({
    [ANSWER_STATUSES.confirmed]: BadgeCheck,
    [ANSWER_STATUSES.refusal]: OctagonX,
    [ANSWER_STATUSES.clarification]: CircleHelp,
    [ANSWER_STATUSES.correction]: PencilLine,
    [ANSWER_STATUSES.disputed]: TriangleAlert,
});

const props = defineProps({
    status: {type: String, required: true},
    label: {type: String, default: ''},
    isOnBrand: {type: Boolean, default: false},
});

const icon = computed(() => STATUS_ICONS[props.status] ?? BadgeCheck);
const text = computed(() => props.label || ANSWER_STATUS_LABELS[props.status]);
</script>

<template>
    <span :class="['ui-status-pill', `ui-status-pill--${status}`, {'ui-status-pill--on-brand': isOnBrand}]">
        <component
            :is="icon"
            :size="14"
            :stroke-width="2.2"
            aria-hidden="true"
        />
        {{ text }}
    </span>
</template>

<style lang="scss">
.ui-status-pill {
    @include pill;

    &--confirmed {
        color: $color-navy;
        background: $color-navy-tint;
    }

    &--refusal {
        color: $color-peach-ink;
        background: $color-peach;
    }

    &--clarification {
        color: $color-amber-ink;
        background: $color-amber;
    }

    &--correction {
        color: $color-violet;
        background: $color-lavender;
    }

    &--disputed {
        color: $color-peach-deep;
        background: $color-peach-soft;
        box-shadow: inset 0 0 0 1px $color-peach-line;
    }

    &--on-brand {
        color: $color-white;
        backdrop-filter: blur(8px);

        @include glass;
    }
}
</style>
