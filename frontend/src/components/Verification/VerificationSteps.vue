<script setup>
import {computed} from 'vue';
import {CornerDownRight, ShieldCheck} from 'lucide-vue-next';
import {FLOW_NODE_KINDS, FLOW_NODES, FLOW_STEPS} from '@/core/data/verificationFlow';

const props = defineProps({
    /** @type {import('vue').PropType<(typeof import('@/core/data/verificationFlow').FLOW_SCENARIOS)[number] | null>} */
    scenario: {type: Object, default: null},
});

const steps = computed(() =>
    FLOW_STEPS.map((step) => ({
        ...step,
        node: FLOW_NODES.find((node) => node.id === step.nodeId),
        state: getState(step.nodeId),
        branchState: step.branch ? getState(step.branch.nodeId) : '',
        noteState: step.note ? getState(step.note.nodeId) : '',
    })),
);

/** @param {string} nodeId */
function getState(nodeId) {
    if (!props.scenario) {
        return '';
    }

    return props.scenario.nodeIds.includes(nodeId) ? 'lit' : 'dim';
}
</script>

<template>
    <ol class="verification-steps">
        <li
            v-for="step in steps"
            :key="step.nodeId"
            :class="[
                'verification-steps__step',
                `verification-steps__step--${step.node.kind}`,
                step.state && `verification-steps__step--${step.state}`,
            ]"
        >
            <span
                class="verification-steps__marker"
                aria-hidden="true"
            />
            <div class="verification-steps__body">
                <span class="verification-steps__label">{{ step.node.label }}</span>
                <span
                    v-if="step.node.kind === FLOW_NODE_KINDS.decision"
                    class="verification-steps__yes"
                >
                    да — дальше по шагам
                </span>

                <span
                    v-if="step.branch"
                    :class="[
                        'verification-steps__branch',
                        step.branchState && `verification-steps__branch--${step.branchState}`,
                    ]"
                >
                    <CornerDownRight
                        :size="15"
                        aria-hidden="true"
                    />
                    {{ step.branch.label }} → {{ step.branch.text }}
                </span>

                <span
                    v-if="step.note"
                    :class="['verification-steps__note', step.noteState && `verification-steps__note--${step.noteState}`]"
                >
                    <ShieldCheck
                        :size="15"
                        aria-hidden="true"
                    />
                    {{ step.note.text }}
                </span>
            </div>
        </li>
    </ol>
</template>

<style lang="scss">
.verification-steps {
    $block: &;
    $marker-size: 22px;

    margin: 0;
    padding: 0;
    list-style: none;

    &__step {
        position: relative;
        display: flex;
        align-items: flex-start;
        transition: opacity $duration ease;
        gap: $indent-step * 3;

        @include padding('bottom', 5);

        &:not(:last-child)::before {
            position: absolute;
            top: $marker-size + $indent-step;
            bottom: $indent-step;
            left: $marker-size * 0.5 - 1px;
            width: 2px;
            border-radius: $radius-pill;
            background-color: $color-line-strong;
            content: '';
        }

        &--dim {
            opacity: 0.35;
        }

        &--lit:not(:last-child)::before {
            background-color: $color-violet-bright;
        }
    }

    &__marker {
        flex-shrink: 0;
        width: $marker-size;
        height: $marker-size;
        border: 2px solid $color-lavender-line;
        border-radius: $radius-pill;
        background-color: $color-surface;
    }

    &__step--start &__marker,
    &__step--finish &__marker {
        border-color: $color-navy;
        background-color: $color-navy;
    }

    &__step--decision &__marker {
        transform: rotate(45deg) scale(0.82);
        border-radius: $radius-xs;
        background-color: $color-lavender;
    }

    &__step--lit &__marker {
        border-color: $color-violet-bright;
        box-shadow: 0 0 0 4px rgba($color-violet-bright, 15%);
    }

    &__body {
        min-width: 0;

        @include column($indent-step * 1.5);
    }

    &__label {
        color: $color-ink;
        font-size: $font-size-md;
        font-weight: $font-weight-bold;
        line-height: 1.4;
    }

    &__yes {
        color: $color-ink-muted;
        font-size: $font-size-xs;
    }

    &__branch,
    &__note {
        display: inline-flex;
        align-items: flex-start;
        align-self: flex-start;
        transition: opacity $duration ease;
        border-radius: $radius-lg;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        line-height: 1.4;
        gap: $indent-step * 1.5;

        @include padding('y', 1.5);
        @include padding('x', 2.5);

        svg {
            flex-shrink: 0;
            margin-top: 2px;
        }

        &--dim {
            opacity: 0.45;
        }
    }

    &__branch {
        color: $color-peach-ink;
        background-color: $color-peach-soft;
    }

    &__note {
        color: $color-white;
        background-color: $color-injected-bg;
    }
}
</style>
