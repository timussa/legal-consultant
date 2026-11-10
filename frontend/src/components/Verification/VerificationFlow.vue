<script setup>
import {computed} from 'vue';
import {
    FLOW_CANVAS,
    FLOW_GUARD_LINK,
    FLOW_LEGEND,
    FLOW_LINES,
    FLOW_NODE_KINDS,
    FLOW_NODES,
} from '@/core/data/verificationFlow';

const props = defineProps({
    /** @type {import('vue').PropType<(typeof import('@/core/data/verificationFlow').FLOW_SCENARIOS)[number] | null>} */
    scenario: {type: Object, default: null},
});

const activeNodeIds = computed(() => props.scenario?.nodeIds ?? []);
const activeLineIds = computed(() => props.scenario?.lineIds ?? []);

/**
 * @param {(typeof FLOW_NODES)[number]} node
 * @param {number} index
 */
function getNodeStyle(node, index) {
    return {
        '--node-x': `${node.x}px`,
        '--node-y': `${node.y}px`,
        '--node-width': `${node.width}px`,
        '--node-height': `${node.height}px`,
        '--node-index': index,
    };
}

/** @param {(typeof FLOW_LINES)[number]} line */
function getLineStyle(line) {
    return {'--line-x': `${line.x}px`, '--line-y': `${line.y}px`, '--line-length': `${line.length}px`};
}

/** @param {string} id */
function getNodeState(id) {
    if (!props.scenario) {
        return '';
    }

    return activeNodeIds.value.includes(id) ? 'lit' : 'dim';
}

/** @param {string} id */
function getLineState(id) {
    if (!props.scenario) {
        return '';
    }

    return activeLineIds.value.includes(id) ? 'lit' : 'dim';
}
</script>

<template>
    <div class="verification-flow">
        <div class="verification-flow__scroller">
            <div
                class="verification-flow__canvas"
                :style="{'--canvas-width': `${FLOW_CANVAS.width}px`, '--canvas-height': `${FLOW_CANVAS.height}px`}"
            >
                <span
                    v-for="line in FLOW_LINES"
                    :key="line.id"
                    :class="[
                        'verification-flow__line',
                        `verification-flow__line--${line.direction}`,
                        getLineState(line.id) && `verification-flow__line--${getLineState(line.id)}`,
                        {
                            'verification-flow__line--branch': line.isBranch,
                            'verification-flow__line--plain': line.hasArrow === false,
                        },
                    ]"
                    :style="getLineStyle(line)"
                >
                    <span
                        v-if="line.label"
                        class="verification-flow__line-label"
                    >
                        {{ line.label }}
                    </span>
                </span>

                <span
                    :class="[
                        'verification-flow__guard-link',
                        {
                            'verification-flow__guard-link--lit': scenario?.hasGuardLink,
                            'verification-flow__guard-link--dim': scenario && !scenario.hasGuardLink,
                        },
                    ]"
                    :style="{
                        '--line-x': `${FLOW_GUARD_LINK.x}px`,
                        '--line-y': `${FLOW_GUARD_LINK.y}px`,
                        '--line-length': `${FLOW_GUARD_LINK.length}px`,
                    }"
                />

                <div
                    v-for="(node, index) in FLOW_NODES"
                    :key="node.id"
                    :class="[
                        'verification-flow__node',
                        `verification-flow__node--${node.kind}`,
                        getNodeState(node.id) && `verification-flow__node--${getNodeState(node.id)}`,
                    ]"
                    :style="getNodeStyle(node, index)"
                >
                    <span
                        v-if="node.kind === FLOW_NODE_KINDS.decision"
                        class="verification-flow__diamond"
                        aria-hidden="true"
                    />
                    <span class="verification-flow__label">{{ node.label }}</span>
                </div>
            </div>
        </div>

        <ul class="verification-flow__legend">
            <li
                v-for="item in FLOW_LEGEND"
                :key="item.kind"
                class="verification-flow__legend-item"
            >
                <span :class="['verification-flow__swatch', `verification-flow__swatch--${item.kind}`]" />
                {{ item.label }}
            </li>
        </ul>
    </div>
</template>

<style lang="scss">
.verification-flow {
    $block: &;
    $line-width: 2px;
    $arrow-size: 6px;

    @include column($indent-step * 4);

    &__scroller {
        overflow-x: auto;

        @include padding('bottom', 2);
    }

    &__canvas {
        position: relative;
        width: var(--canvas-width);
        height: var(--canvas-height);
        margin: 0 auto;
    }

    &__node {
        position: absolute;
        top: var(--node-y);
        left: var(--node-x);
        width: var(--node-width);
        height: var(--node-height);
        transition:
            opacity $duration ease,
            transform $duration $ease-out,
            box-shadow $duration ease;
        color: $color-ink;
        border: 1px solid $color-line;
        border-radius: $radius-xl;
        background: $color-surface;
        box-shadow: $shadow-soft;
        text-align: center;
        animation: fade-up $duration-slow $ease-out backwards;
        animation-delay: calc(var(--node-index) * 60ms);

        @include flex-center;
        @include padding('x', 3);

        &--start,
        &--finish {
            color: $color-white;
            border: none;
            border-radius: $radius-pill;
            background: $gradient-user;
            box-shadow: $shadow-bubble;
        }

        &--finish {
            background: $gradient-thread;
        }

        &--action {
            @include gradient-border(1px);
        }

        &--decision {
            border: none;
            background: transparent;
            box-shadow: none;

            &#{$block}__node--lit {
                box-shadow: none;
            }

            @include padding('x', 5);
        }

        &--clarification {
            color: $color-amber-ink;
            border-color: transparent;
            background: $color-amber;
        }

        &--refusal {
            color: $color-peach-ink;
            border-color: $color-peach-line;
            background: $color-peach;
        }

        &--fix {
            color: $color-violet;
            border-style: dashed;
            border-color: $color-lavender-line;
            background: $color-lavender-soft;
        }

        &--guard {
            color: $color-white;
            border: none;
            background: $color-injected-bg;
            box-shadow: $shadow-bubble;
        }

        &--lit {
            transform: scale(1.04);
            box-shadow: $shadow-raised;
        }

        &--dim {
            opacity: 0.3;
        }
    }

    &__diamond {
        position: absolute;
        inset: 17%;
        transform: rotate(45deg);
        border-radius: $radius-lg;
        background: $color-lavender;
        box-shadow: inset 0 0 0 1px $color-lavender-line;
    }

    &__node--lit &__diamond {
        background: $gradient-selected;
        box-shadow: inset 0 0 0 1.5px $color-violet-bright;
    }

    &__label {
        position: relative;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        line-height: 1.35;
    }

    &__line {
        position: absolute;
        top: var(--line-y);
        left: var(--line-x);
        transition: opacity $duration ease;
        background: $color-line-strong;

        &::after {
            position: absolute;
            width: 0;
            height: 0;
            border: $arrow-size solid transparent;
            content: '';
        }

        &--right,
        &--left {
            width: var(--line-length);
            height: $line-width;
            margin-top: -$line-width * 0.5;
        }

        &--down,
        &--up {
            width: $line-width;
            height: var(--line-length);
            margin-left: -$line-width * 0.5;
        }

        &--right::after {
            top: -$arrow-size + $line-width * 0.5;
            right: -$arrow-size;
            border-left-color: $color-line-strong;
        }

        &--left::after {
            top: -$arrow-size + $line-width * 0.5;
            left: -$arrow-size;
            border-right-color: $color-line-strong;
        }

        &--down::after {
            bottom: -$arrow-size;
            left: -$arrow-size + $line-width * 0.5;
            border-top-color: $color-line-strong;
        }

        &--up::after {
            top: -$arrow-size;
            left: -$arrow-size + $line-width * 0.5;
            border-bottom-color: $color-line-strong;
        }

        &--plain::after {
            display: none;
        }

        &--branch {
            background: $color-orange-soft;

            &#{$block}__line--right::after {
                border-left-color: $color-orange-soft;
            }

            &#{$block}__line--left::after {
                border-right-color: $color-orange-soft;
            }

            &#{$block}__line--down::after {
                border-top-color: $color-orange-soft;
            }
        }

        &--lit {
            background: $color-violet-bright;

            &#{$block}__line--right::after {
                border-left-color: $color-violet-bright;
            }

            &#{$block}__line--left::after {
                border-right-color: $color-violet-bright;
            }

            &#{$block}__line--down::after {
                border-top-color: $color-violet-bright;
            }
        }

        &--dim {
            opacity: 0.25;
        }
    }

    &__line-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, calc(-100% - #{$indent-step}));
        color: $color-ink-muted;
        border-radius: $radius-pill;
        background: $color-page;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
        white-space: nowrap;

        @include padding('x', 1.5);
    }

    &__line--down &__line-label,
    &__line--up &__line-label {
        transform: translate($indent-step * 2, -50%);
    }

    &__guard-link {
        position: absolute;
        top: var(--line-y);
        left: var(--line-x);
        width: 0;
        height: var(--line-length);
        transition: opacity $duration ease;
        border-left: $line-width dashed $color-violet-bright;

        &--lit {
            border-left-style: solid;
        }

        &--dim {
            opacity: 0.25;
        }
    }

    &__legend {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        margin: 0;
        padding: 0;
        list-style: none;
        gap: $indent-step * 5;
    }

    &__legend-item {
        display: flex;
        align-items: center;
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;
        gap: $indent-step * 2;
    }

    &__swatch {
        width: 14px;
        height: 14px;
        border-radius: $radius-xs;

        &--start,
        &--finish {
            border-radius: $radius-pill;
            background: $gradient-user;
        }

        &--action {
            @include gradient-border(1.5px);
        }

        &--decision {
            transform: rotate(45deg) scale(0.8);
            background: $color-lavender;
            box-shadow: inset 0 0 0 1px $color-lavender-line;
        }

        &--refusal {
            background: $color-peach;
        }

        &--guard {
            background: $color-injected-bg;
        }
    }
}
</style>
