<script setup>
import {computed} from 'vue';
import {
    Check,
    CircleHelp,
    CircleSlash,
    FileText,
    ListChecks,
    MessageSquareText,
    ScanText,
    Search,
    ShieldCheck,
} from 'lucide-vue-next';
import {
    FLOW_FINISH,
    FLOW_GATES,
    FLOW_GUARD,
    FLOW_ICONS,
    FLOW_OUTCOMES,
    FLOW_STAGES,
} from '@/core/data/verificationFlow';

const props = defineProps({
    /** @type {import('vue').PropType<(typeof import('@/core/data/verificationFlow').FLOW_SCENARIOS)[number] | null>} */
    scenario: {type: Object, default: null},
});

const STAGE_ICONS = Object.freeze({
    [FLOW_ICONS.question]: MessageSquareText,
    [FLOW_ICONS.parse]: ScanText,
    [FLOW_ICONS.search]: Search,
    [FLOW_ICONS.compose]: FileText,
    [FLOW_ICONS.selfcheck]: ListChecks,
});

const OUTCOME_ICONS = Object.freeze({
    [FLOW_OUTCOMES.clarify.id]: CircleHelp,
    [FLOW_OUTCOMES.refusal.id]: CircleSlash,
});

/**
 * Элементы основной линии по колонкам сетки: шаг, связка или условие, в конце — итог.
 * @typedef {{type: 'stage' | 'link' | 'gate' | 'finish', id: string, column: number, targetId?: string}} RailItem
 */
const railItems = computed(() => {
    /** @type {RailItem[]} */
    const items = [];

    FLOW_STAGES.forEach((stage, index) => {
        items.push({type: 'stage', id: stage.id, column: items.length + 1});

        const gate = FLOW_GATES.find((item) => item.afterId === stage.id);
        const nextId = FLOW_STAGES[index + 1]?.id ?? FLOW_FINISH.id;

        if (gate) {
            items.push({type: 'gate', id: gate.id, column: items.length + 1, targetId: nextId});
        } else if (index < FLOW_STAGES.length - 1) {
            items.push({type: 'link', id: `link-${nextId}`, column: items.length + 1, targetId: nextId});
        }
    });

    items.push({type: 'finish', id: FLOW_FINISH.id, column: items.length + 1});

    return items;
});

const columns = computed(() => Object.fromEntries(railItems.value.map((item) => [item.id, item.column])));

const branches = computed(() =>
    FLOW_GATES.filter((gate) => gate.branchId !== FLOW_OUTCOMES.fix.id).map((gate, index) => ({
        gate,
        outcome: FLOW_OUTCOMES[gate.branchId],
        column: columns.value[gate.id],
        side: index === 0 ? 'left' : 'right',
    })),
);

const loop = computed(() => {
    const gate = FLOW_GATES.find((item) => item.branchId === FLOW_OUTCOMES.fix.id);
    const composeId = FLOW_STAGES.find((stage) => stage.id === 'compose')?.id;

    return {from: columns.value[composeId], to: columns.value[gate.id] + 1};
});

/** @param {string} id */
function getState(id) {
    if (!props.scenario) {
        return '';
    }

    return props.scenario.nodeIds.includes(id) ? 'lit' : 'dim';
}

/** @param {string} id */
function findStage(id) {
    return FLOW_STAGES.find((stage) => stage.id === id);
}

/** @param {string} id */
function findGate(id) {
    return FLOW_GATES.find((gate) => gate.id === id);
}

/** @param {{side: string, column: number}} branch */
function getOutcomeColumn(branch) {
    return branch.side === 'left'
        ? `${branch.column - 1} / ${branch.column + 1}`
        : `${branch.column} / ${branch.column + 2}`;
}
</script>

<template>
    <div class="verification-flow">
        <div class="verification-flow__scroller">
            <div class="verification-flow__grid">
                <div
                    :class="[
                        'verification-flow__guard',
                        getState(FLOW_GUARD.id) && `verification-flow__guard--${getState(FLOW_GUARD.id)}`,
                    ]"
                >
                    <ShieldCheck
                        :size="18"
                        aria-hidden="true"
                    />
                    <span>
                        <b>{{ FLOW_GUARD.title }}</b>
                        {{ FLOW_GUARD.text }}
                    </span>
                </div>

                <div
                    :class="[
                        'verification-flow__loop',
                        getState(FLOW_OUTCOMES.fix.id) && `verification-flow__loop--${getState(FLOW_OUTCOMES.fix.id)}`,
                    ]"
                    :style="{gridColumn: `${loop.from} / ${loop.to}`}"
                    aria-hidden="true"
                >
                    <span class="verification-flow__loop-path" />
                    <span class="verification-flow__loop-label">{{ FLOW_OUTCOMES.fix.title }}</span>
                </div>

                <template
                    v-for="(item, index) in railItems"
                    :key="item.id"
                >
                    <div
                        v-if="item.type === 'stage'"
                        :class="[
                            'verification-flow__stage',
                            getState(item.id) && `verification-flow__stage--${getState(item.id)}`,
                        ]"
                        :style="{gridColumn: item.column, '--stage-index': index}"
                    >
                        <div class="verification-flow__stage-head">
                            <span class="verification-flow__stage-icon">
                                <component
                                    :is="STAGE_ICONS[findStage(item.id).icon]"
                                    :size="19"
                                    aria-hidden="true"
                                />
                            </span>
                            <span class="verification-flow__stage-number">
                                {{ FLOW_STAGES.indexOf(findStage(item.id)) + 1 }}
                            </span>
                        </div>
                        <span class="verification-flow__stage-title">{{ findStage(item.id).title }}</span>
                        <span class="verification-flow__stage-text">{{ findStage(item.id).text }}</span>
                        <span class="verification-flow__stage-chip">{{ findStage(item.id).chip }}</span>
                    </div>

                    <div
                        v-else-if="item.type === 'link'"
                        :class="[
                            'verification-flow__link',
                            getState(item.targetId) && `verification-flow__link--${getState(item.targetId)}`,
                        ]"
                        :style="{gridColumn: item.column}"
                        aria-hidden="true"
                    />

                    <div
                        v-else-if="item.type === 'gate'"
                        :class="[
                            'verification-flow__gate',
                            findGate(item.id).branchId === FLOW_OUTCOMES.fix.id
                                ? 'verification-flow__gate--loop'
                                : 'verification-flow__gate--branch',
                            `verification-flow__gate--${findGate(item.id).branchId}`,
                            getState(item.id) && `verification-flow__gate--${getState(item.id)}`,
                        ]"
                        :style="{gridColumn: item.column}"
                    >
                        <span
                            class="verification-flow__gate-stem"
                            aria-hidden="true"
                        />
                        <span class="verification-flow__gate-question">{{ findGate(item.id).question }}</span>
                        <span
                            class="verification-flow__diamond"
                            aria-hidden="true"
                        >
                            ?
                        </span>
                        <span class="verification-flow__gate-yes">да</span>
                        <span
                            class="verification-flow__gate-head"
                            aria-hidden="true"
                        />
                    </div>

                    <div
                        v-else
                        :class="[
                            'verification-flow__finish',
                            getState(item.id) && `verification-flow__finish--${getState(item.id)}`,
                        ]"
                        :style="{gridColumn: item.column, '--stage-index': index}"
                    >
                        <span class="verification-flow__finish-icon">
                            <Check
                                :size="24"
                                :stroke-width="3"
                                aria-hidden="true"
                            />
                        </span>
                        <span class="verification-flow__finish-title">{{ FLOW_FINISH.title }}</span>
                        <span class="verification-flow__finish-text">{{ FLOW_FINISH.text }}</span>
                    </div>
                </template>

                <template
                    v-for="branch in branches"
                    :key="branch.gate.id"
                >
                    <div
                        :class="[
                            'verification-flow__branch',
                            `verification-flow__branch--${branch.outcome.kind}`,
                            getState(branch.outcome.id) && `verification-flow__branch--${getState(branch.outcome.id)}`,
                        ]"
                        :style="{gridColumn: branch.column}"
                        aria-hidden="true"
                    >
                        <span class="verification-flow__branch-label">нет</span>
                    </div>
                    <div
                        :class="[
                            'verification-flow__outcome',
                            `verification-flow__outcome--${branch.outcome.kind}`,
                            `verification-flow__outcome--${branch.side}`,
                            getState(branch.outcome.id) && `verification-flow__outcome--${getState(branch.outcome.id)}`,
                        ]"
                        :style="{gridColumn: getOutcomeColumn(branch)}"
                    >
                        <span class="verification-flow__outcome-icon">
                            <component
                                :is="OUTCOME_ICONS[branch.outcome.id]"
                                :size="20"
                                aria-hidden="true"
                            />
                        </span>
                        <span class="verification-flow__outcome-body">
                            <b class="verification-flow__outcome-title">{{ branch.outcome.title }}</b>
                            <span>{{ branch.outcome.text }}</span>
                        </span>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.verification-flow {
    $block: &;
    $gate: var(--flow-gate);
    $link: var(--flow-link);
    $rail: 3px;
    $diamond: 26px;
    $arrow: 6px;
    $outcome-width: 236px;
    $outcome-overlap: 48px;

    --flow-gate: 96px;
    --flow-link: 32px;

    &__scroller {
        overflow-x: auto;

        @include padding('bottom', 2);
    }

    &__grid {
        position: relative;
        display: grid;
        min-width: 1080px;
        grid-template-columns:
            minmax(0, 1fr) $link minmax(0, 1fr) $gate minmax(0, 1fr) $gate minmax(0, 1fr) $link minmax(0, 1fr)
            $gate minmax(0, 1.2fr);
        grid-template-rows: 56px 48px auto 20px 40px auto;

        @include padding('x', 5);
    }

    // Защита роли — подложка под всей основной линией
    &__guard {
        position: relative;
        z-index: 0;
        display: flex;
        align-items: flex-start;
        transition:
            background $duration ease,
            opacity $duration ease;
        color: $color-violet;
        border: 1.5px dashed $color-lavender-line;
        border-radius: $radius-3xl * 1.6;
        background: rgba($color-lavender, 60%);
        font-size: $font-size-sm;
        line-height: 1.45;
        grid-column: 1 / -1;
        grid-row: 2 / 5;
        gap: $indent-step * 2;

        @include margin('x', -5);
        @include padding('top', 3.5);
        @include padding('x', 5);

        svg {
            flex-shrink: 0;
        }

        &--lit {
            border-style: solid;
            border-color: $color-violet-bright;
            background: $color-lavender;
        }

        &--dim {
            opacity: 0.45;
        }
    }

    // Возврат на исправление: дуга над шагами «Ответ» и «Самопроверка»
    &__loop {
        position: relative;
        z-index: 1;
        transition: opacity $duration ease;
        grid-row: 1 / 3;

        &--dim {
            opacity: 0.3;
        }
    }

    &__loop-path {
        position: absolute;
        top: $indent-step * 4;
        right: calc(#{$gate} / 2 - #{$rail} / 2);
        bottom: 0;
        left: calc((100% - #{$link} - #{$gate}) / 4 - #{$rail} / 2);
        border: $rail solid $color-violet-bright;
        border-bottom: none;
        border-radius: $radius-3xl $radius-3xl 0 0;

        &::after {
            position: absolute;
            bottom: -$arrow;
            left: -$arrow - $rail * 0.5;
            width: 0;
            height: 0;
            border: $arrow solid transparent;
            border-top-color: $color-violet-bright;
            content: '';
        }
    }

    &__loop-label {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        color: $color-violet;
        border: 1.5px solid $color-lavender-line;
        border-radius: $radius-pill;
        background: $color-surface;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        line-height: 1;
        white-space: nowrap;

        @include padding('y', 2);
        @include padding('x', 4);
    }

    // Шаги основной линии
    &__stage {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        transition:
            opacity $duration ease,
            box-shadow $duration ease,
            border-color $duration ease;
        border: 1px solid $color-line;
        border-radius: $radius-3xl * 1.1;
        background: $color-surface;
        box-shadow: $shadow-card;
        animation: fade-up $duration-slow $ease-out backwards;
        animation-delay: calc(var(--stage-index) * 50ms);
        grid-row: 3;
        gap: $indent-step * 1.5;

        @include padding('y', 4);
        @include padding('x', 3);

        &--lit {
            border-color: $color-lavender-line;
            box-shadow: $shadow-raised;
        }

        &--dim {
            opacity: 0.3;
        }
    }

    &__stage-head {
        display: flex;
        align-items: center;
        justify-content: space-between;

        @include margin('bottom', 1);
    }

    &__stage-icon {
        @include flex-center;

        width: 36px;
        height: 36px;
        color: $color-indigo;
        border-radius: $radius-lg;
        background: $color-lavender;
    }

    &__stage-number {
        color: $color-ink-decor;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__stage-title {
        color: $color-ink;
        font-size: $font-size-base;
        font-weight: $font-weight-extrabold;
        line-height: 1.25;
        hyphens: auto;
    }

    &__stage-text {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        line-height: 1.4;
    }

    &__stage-chip {
        align-self: flex-start;
        margin-top: auto;
        color: $color-navy;
        border-radius: $radius-pill;
        background: $color-navy-tint;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        line-height: 1.3;

        @include padding('y', 1);
        @include padding('x', 2.5);
        @include margin('top', 2);
    }

    // Связка между шагами и линия через условие
    &__link,
    &__gate {
        position: relative;
        z-index: 1;
        transition: opacity $duration ease;
        grid-row: 3;

        &--dim {
            opacity: 0.3;
        }
    }

    &__link::before,
    &__gate::before,
    &__gate::after {
        position: absolute;
        top: 50%;
        height: $rail;
        margin-top: -$rail * 0.5;
        background: $color-navy;
        content: '';
    }

    &__link {
        &::before {
            right: $arrow;
            left: 0;
        }

        &::after {
            position: absolute;
            top: 50%;
            right: 0;
            width: 0;
            height: 0;
            margin-top: -$arrow;
            border: $arrow solid transparent;
            border-right: none;
            border-left-color: $color-navy;
            content: '';
        }
    }

    &__gate {
        &::before {
            right: 50%;
            left: 0;
        }

        &::after {
            right: $arrow;
            left: 50%;
        }
    }

    &__diamond {
        position: absolute;
        z-index: 1;
        top: 50%;
        left: 50%;
        width: $diamond;
        height: $diamond;
        transform: translate(-50%, -50%);
        color: $color-navy;
        font-size: $font-size-md;
        font-weight: $font-weight-extrabold;

        @include flex-center;

        &::before {
            position: absolute;
            z-index: -1;
            inset: 0;
            transform: rotate(45deg);
            border: $rail solid $color-navy;
            border-radius: $radius-sm * 0.8;
            background: $color-surface;
            content: '';
        }
    }

    &__gate--lit &__diamond::before {
        background: $color-lavender;
    }

    &__gate-yes {
        position: absolute;
        top: 50%;
        right: $indent-step * 2.5;
        transform: translateY(calc(-100% - #{$indent-step * 1.5}));
        color: $color-navy;
        font-size: $font-size-2xs;
        font-weight: $font-weight-bold;
    }

    &__gate-head {
        position: absolute;
        top: 50%;
        right: 0;
        width: 0;
        height: 0;
        margin-top: -$arrow;
        border: $arrow solid transparent;
        border-right: none;
        border-left-color: $color-navy;
    }

    &__gate-question {
        position: absolute;
        left: 50%;
        width: calc(#{$gate} - #{$indent-step * 2});
        transform: translateX(-50%);
        color: $color-ink;
        font-size: $font-size-2xs;
        font-weight: $font-weight-bold;
        line-height: 1.3;
        text-align: center;
    }

    &__gate--branch &__gate-question {
        bottom: calc(50% + #{$diamond * 0.75 + $indent-step * 2});
    }

    &__gate--loop &__gate-question {
        top: calc(50% + #{$diamond * 0.75 + $indent-step * 2});
    }

    // вертикальная линия от условия: вниз к исходу или вверх к дуге
    &__gate-stem {
        position: absolute;
        left: 50%;
        width: $rail;
        margin-left: -$rail * 0.5;
    }

    &__gate--branch &__gate-stem {
        top: 50%;
        bottom: 0;
        background: $color-orange;
    }

    &__gate--loop &__gate-stem {
        top: 0;
        bottom: 50%;
        background: $color-violet-bright;
    }

    &__gate--clarify &__gate-stem {
        background: $color-gold;
    }

    // Ветка «нет» и исходы
    &__branch {
        position: relative;
        z-index: 1;
        transition: opacity $duration ease;
        grid-row: 4 / 6;

        &::before {
            position: absolute;
            top: 0;
            bottom: $arrow;
            left: 50%;
            width: $rail;
            margin-left: -$rail * 0.5;
            background: $color-orange;
            content: '';
        }

        &::after {
            position: absolute;
            bottom: 0;
            left: 50%;
            width: 0;
            height: 0;
            margin-left: -$arrow;
            border: $arrow solid transparent;
            border-bottom: none;
            border-top-color: $color-orange;
            content: '';
        }

        &--clarification::before {
            background: $color-gold;
        }

        &--clarification::after {
            border-top-color: $color-gold;
        }

        &--dim {
            opacity: 0.3;
        }
    }

    &__branch-label {
        position: absolute;
        top: $indent-step * 4;
        left: calc(50% + #{$indent-step * 2});
        color: $color-peach-ink;
        font-size: $font-size-xs;
        font-weight: $font-weight-extrabold;
    }

    &__branch--clarification &__branch-label {
        color: $color-amber-ink;
    }

    &__outcome {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        width: $outcome-width;
        transition: opacity $duration ease;
        border-radius: $radius-3xl;
        font-size: $font-size-sm;
        line-height: 1.4;
        grid-row: 6;
        gap: $indent-step * 3;

        @include padding('y', 4);
        @include padding('x', 4);

        &--left {
            justify-self: end;
            margin-right: calc(#{$gate} / 2 - #{$outcome-overlap});
        }

        &--right {
            justify-self: start;
            margin-left: calc(#{$gate} / 2 - #{$outcome-overlap});
        }

        &--clarification {
            color: $color-amber-ink;
            background: $color-amber;
        }

        &--refusal {
            color: $color-peach-ink;
            background: $color-peach;
        }

        &--dim {
            opacity: 0.3;
        }
    }

    &__outcome-icon {
        @include flex-center;

        flex-shrink: 0;
        width: 40px;
        height: 40px;
        color: $color-white;
        border-radius: $radius-pill;
    }

    &__outcome--clarification &__outcome-icon {
        background: $color-gold;
    }

    &__outcome--refusal &__outcome-icon {
        background: $color-orange;
    }

    &__outcome-body {
        @include column($indent-step * 0.5);
    }

    &__outcome-title {
        color: inherit;
        font-size: $font-size-base;
    }

    // Итог
    &__finish {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        transition: opacity $duration ease;
        color: $color-white;
        border-radius: $radius-3xl * 1.3;
        background: $color-cta;
        box-shadow: 0 24px 44px -24px rgba($color-cta, 85%);
        animation: fade-up $duration-slow $ease-out backwards;
        animation-delay: calc(var(--stage-index) * 50ms);
        grid-row: 3;
        gap: $indent-step * 2;

        @include padding('y', 5);
        @include padding('x', 4.5);
        @include margin('y', -2.5);

        &--dim {
            opacity: 0.35;
        }
    }

    &__finish-icon {
        @include flex-center;

        width: 44px;
        height: 44px;
        border-radius: $radius-pill;
        background: rgba($color-white, 22%);
    }

    &__finish-title {
        font-size: $font-size-2xl;
        font-weight: $font-weight-extrabold;
        line-height: 1.2;

        @include margin('top', 1);
    }

    &__finish-text {
        font-size: $font-size-sm;
        line-height: 1.45;
        opacity: 0.92;
    }

    @include laptop {
        --flow-gate: 84px;
        --flow-link: 24px;

        &__stage {
            @include padding('x', 2.5);
        }

        &__stage-title {
            font-size: $font-size-md;
        }
    }
}
</style>
