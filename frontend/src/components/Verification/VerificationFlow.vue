<script setup>
import {computed} from 'vue';
import {Check} from 'lucide-vue-next';
import {VERIFICATION_IMAGES} from '@/assets/images';
import {FLOW_FINISH, FLOW_GATES, FLOW_GUARD, FLOW_OUTCOMES, FLOW_STAGES} from '@/core/data/verificationFlow';

const props = defineProps({
    /** @type {import('vue').PropType<(typeof import('@/core/data/verificationFlow').FLOW_SCENARIOS)[number] | null>} */
    scenario: {type: Object, default: null},
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
                    <img
                        class="verification-flow__guard-icon"
                        :src="VERIFICATION_IMAGES.guard"
                        alt=""
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
                            <img
                                class="verification-flow__stage-icon"
                                :src="VERIFICATION_IMAGES.stages[findStage(item.id).icon]"
                                alt=""
                            />
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
                    >
                        <span
                            v-if="getState(item.targetId) === 'lit'"
                            class="verification-flow__spark"
                        />
                    </div>

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
                        <span
                            v-if="getState(item.id) === 'lit'"
                            class="verification-flow__spark"
                            aria-hidden="true"
                        />
                        <span class="verification-flow__gate-question">{{ findGate(item.id).question }}</span>
                        <span
                            class="verification-flow__diamond"
                            aria-hidden="true"
                        >
                            <img
                                class="verification-flow__diamond-image"
                                :src="
                                    findGate(item.id).branchId === FLOW_OUTCOMES.fix.id
                                        ? VERIFICATION_IMAGES.gateLoop
                                        : VERIFICATION_IMAGES.gate
                                "
                                alt=""
                            />
                            <span class="verification-flow__diamond-mark">?</span>
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
                        <img
                            class="verification-flow__outcome-icon"
                            :src="VERIFICATION_IMAGES.outcomes[branch.outcome.id]"
                            alt=""
                        />
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
// Схема рисуется на тёмной navy-сцене (фон задаёт страница): стеклянные плашки,
// светлые линии, 3D-иконки. Цвета — производные от брендовых токенов.
.verification-flow {
    $block: &;
    $gate: var(--flow-gate);
    $link: var(--flow-link);
    $rail: 2px;
    $diamond: 40px;
    $arrow: 6px;
    $outcome-width: 250px;
    $outcome-overlap: 52px;
    $glass-line: rgba($color-white, 22%);
    $glass-fill: rgba($color-white, 11%);
    $rail-color: rgba($color-white, 55%);
    $loop-color: #b9a2ff;
    $deep-shadow: #05082e;

    --flow-gate: 84px;
    --flow-link: 22px;

    &__scroller {
        overflow-x: auto;
        scrollbar-color: rgba($color-white, 30%) transparent;

        @include padding('bottom', 2);
    }

    &__grid {
        position: relative;
        display: grid;
        min-width: 1120px;
        grid-template-columns:
            minmax(0, 1fr) $link minmax(0, 1fr) $gate minmax(0, 1fr) $gate minmax(0, 1fr) $link minmax(0, 1fr)
            $gate minmax(0, 1.15fr);
        grid-template-rows: 56px 52px auto 20px 40px auto;

        @include padding('x', 4);
    }

    // Защищённый контур под всей основной линией
    &__guard {
        position: relative;
        z-index: 0;
        display: flex;
        align-items: flex-start;
        transition:
            background $duration ease,
            border-color $duration ease,
            opacity $duration ease;
        color: $color-on-brand-soft;
        border: 1px dashed rgba($color-white, 26%);
        border-radius: $radius-3xl * 1.6;
        background: linear-gradient(180deg, rgba($color-white, 7%), rgba($color-white, 2%));
        font-size: $font-size-sm;
        line-height: 1.45;
        grid-column: 1 / -1;
        grid-row: 2 / 5;
        gap: $indent-step * 2;

        @include margin('x', -4);
        @include padding('top', 2);
        @include padding('x', 4);

        span {
            @include padding('top', 2);
        }

        b {
            color: $color-white;
        }

        &--lit {
            border-style: solid;
            border-color: rgba($loop-color, 70%);
            background: linear-gradient(180deg, rgba($loop-color, 18%), rgba($loop-color, 4%));
        }

        &--dim {
            opacity: 0.4;
        }
    }

    &__guard-icon {
        flex-shrink: 0;
        width: 34px;
        height: 34px;
        filter: drop-shadow(0 4px 8px rgba($color-ink, 40%));
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
        border: $rail solid $loop-color;
        border-bottom: none;
        border-radius: $radius-3xl $radius-3xl 0 0;
        box-shadow: 0 -2px 14px -4px rgba($loop-color, 70%);

        &::after {
            position: absolute;
            bottom: -$arrow;
            left: -$arrow - $rail * 0.5;
            width: 0;
            height: 0;
            border: $arrow solid transparent;
            border-top-color: $loop-color;
            content: '';
        }
    }

    &__loop-label {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        color: $color-white;
        border: 1px solid rgba($loop-color, 60%);
        border-radius: $radius-pill;
        background: rgba(mix($color-violet, $color-navy, 60%), 85%);
        box-shadow: 0 8px 20px -10px rgba($loop-color, 80%);
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        line-height: 1;
        white-space: nowrap;

        @include padding('y', 2);
        @include padding('x', 3.5);
    }

    // Шаги основной линии — стеклянные плашки
    &__stage {
        position: relative;
        z-index: 2;
        display: flex;
        flex-direction: column;
        min-width: 0;
        transition:
            opacity $duration ease,
            transform $duration $ease-back-out,
            box-shadow $duration ease,
            border-color $duration ease,
            background $duration ease;
        border: 1px solid $glass-line;
        border-radius: $radius-3xl;
        background:
            linear-gradient(155deg, rgba($color-white, 16%) 0%, rgba($color-white, 4%) 55%),
            $glass-fill;
        box-shadow:
            inset 0 1px 0 rgba($color-white, 30%),
            0 22px 40px -26px rgba($deep-shadow, 90%);
        animation: fade-up $duration-slow $ease-out backwards;
        animation-delay: calc(var(--stage-index) * 60ms);
        grid-row: 3;
        gap: $indent-step * 1.5;

        @include padding('top', 3);
        @include padding('bottom', 3.5);
        @include padding('x', 3.5);

        @include hover {
            transform: translateY(-4px);
            border-color: rgba($color-white, 40%);
        }

        &--lit {
            border-color: rgba($loop-color, 85%);
            background:
                linear-gradient(155deg, rgba($loop-color, 30%) 0%, rgba($color-white, 6%) 60%),
                $glass-fill;
            box-shadow:
                inset 0 1px 0 rgba($color-white, 40%),
                0 0 0 1px rgba($loop-color, 35%),
                0 24px 44px -20px rgba($loop-color, 75%);
        }

        &--dim {
            opacity: 0.32;
        }
    }

    &__stage-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
    }

    &__stage-icon {
        width: 52px;
        height: 52px;
        margin: (-$indent-step) 0 0 (-$indent-step);
        transition: transform $duration $ease-back-out;
        filter: drop-shadow(0 8px 12px rgba($deep-shadow, 55%));
    }

    &__stage:hover &__stage-icon {
        transform: translateY(-3px) rotate(-4deg);
    }

    &__stage-number {
        color: rgba($color-white, 45%);
        font-size: $font-size-xs;
        font-weight: $font-weight-extrabold;
        font-variant-numeric: tabular-nums;
        letter-spacing: 0.06em;
    }

    &__stage-title {
        color: $color-white;
        font-size: $font-size-base;
        font-weight: $font-weight-extrabold;
        line-height: 1.25;
        text-wrap: balance;
    }

    &__stage-text {
        color: $color-on-brand-soft;
        font-size: $font-size-xs;
        line-height: 1.45;
    }

    &__stage-chip {
        align-self: flex-start;
        max-width: 100%;
        margin-top: auto;
        color: $color-white;
        border: 1px solid rgba($color-white, 26%);
        border-radius: $radius-pill;
        background: rgba($color-white, 12%);
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
        border-radius: $radius-pill;
        background: $rail-color;
        content: '';
    }

    // Подсвеченный путь: яркая линия + «искра», которая едет только через transform
    &__link--lit::before,
    &__gate--lit::before,
    &__gate--lit::after {
        background: rgba($color-white, 85%);
        box-shadow: 0 0 8px rgba($loop-color, 90%);
    }

    &__link--lit::after,
    &__gate--lit &__gate-head {
        border-left-color: $color-white;
    }

    &__spark {
        position: absolute;
        z-index: 1;
        top: 50%;
        right: $arrow;
        left: 0;
        overflow: hidden;
        height: $rail * 3;
        margin-top: -$rail * 1.5;
        pointer-events: none;

        &::before {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(closest-side, $color-white, rgba($loop-color, 60%) 45%, transparent);
            background-size: 28px 100%;
            background-repeat: no-repeat;
            background-position: center;
            animation: verification-flow-run 1.4s linear infinite;
            content: '';
            will-change: transform;
        }
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
            border-left-color: $rail-color;
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
        transition: transform $duration $ease-back-out;

        @include flex-center;
    }

    &__gate:hover &__diamond {
        transform: translate(-50%, -50%) scale(1.12);
    }

    &__diamond-image {
        position: absolute;
        top: -6px;
        left: -6px;
        width: calc(100% + 12px);
        height: calc(100% + 12px);
        filter: drop-shadow(0 6px 10px rgba($deep-shadow, 60%));
    }

    &__diamond-mark {
        position: relative;
        color: $color-white;
        font-size: $font-size-md;
        font-weight: $font-weight-extrabold;
        text-shadow: 0 1px 4px rgba($color-ink, 60%);
    }

    &__gate--lit &__diamond-image {
        filter: drop-shadow(0 0 12px rgba($loop-color, 90%));
    }

    &__gate-yes {
        position: absolute;
        top: 50%;
        right: $indent-step * 2;
        transform: translateY(calc(-100% - #{$indent-step * 1.5}));
        color: rgba($color-white, 75%);
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
        border-left-color: $rail-color;
    }

    &__gate-question {
        position: absolute;
        left: 50%;
        width: calc(#{$gate} + #{$indent-step * 2});
        transform: translateX(-50%);
        color: $color-white;
        font-size: $font-size-2xs;
        font-weight: $font-weight-bold;
        line-height: 1.3;
        text-align: center;
        text-wrap: balance;
    }

    &__gate--branch &__gate-question {
        bottom: calc(50% + #{$diamond * 0.6 + $indent-step * 2});
    }

    &__gate--loop &__gate-question {
        top: calc(50% + #{$diamond * 0.6 + $indent-step * 2});
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
        background: $color-orange-soft;
    }

    &__gate--loop &__gate-stem {
        top: 0;
        bottom: 50%;
        background: $loop-color;
    }

    &__gate--clarify &__gate-stem {
        background: $color-highlighter-amber;
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
            background: $color-orange-soft;
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
            border-top-color: $color-orange-soft;
            content: '';
        }

        &--clarification::before {
            background: $color-highlighter-amber;
        }

        &--clarification::after {
            border-top-color: $color-highlighter-amber;
        }

        &--dim {
            opacity: 0.3;
        }
    }

    &__branch-label {
        position: absolute;
        top: $indent-step * 3.5;
        left: calc(50% + #{$indent-step * 2});
        color: $color-flash;
        font-size: $font-size-xs;
        font-weight: $font-weight-extrabold;
    }

    &__branch--clarification &__branch-label {
        color: $color-highlighter-amber;
    }

    &__outcome {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        width: $outcome-width;
        transition:
            opacity $duration ease,
            transform $duration $ease-back-out;
        color: $color-white;
        border: 1px solid var(--outcome-line);
        border-radius: $radius-3xl;
        background: linear-gradient(150deg, var(--outcome-fill) 0%, rgba($color-white, 4%) 70%);
        box-shadow:
            inset 0 1px 0 rgba($color-white, 25%),
            0 22px 40px -24px var(--outcome-glow);
        font-size: $font-size-sm;
        line-height: 1.4;
        grid-row: 6;
        gap: $indent-step * 3;

        @include padding('y', 3.5);
        @include padding('left', 3);
        @include padding('right', 4);

        @include hover {
            transform: translateY(-3px);
        }

        &--left {
            justify-self: end;
            margin-right: calc(#{$gate} / 2 - #{$outcome-overlap});
        }

        &--right {
            justify-self: start;
            margin-left: calc(#{$gate} / 2 - #{$outcome-overlap});
        }

        &--clarification {
            --outcome-line: #{rgba($color-highlighter-amber, 55%)};
            --outcome-fill: #{rgba($color-gold, 34%)};
            --outcome-glow: #{rgba($color-gold, 70%)};
        }

        &--refusal {
            --outcome-line: #{rgba($color-flash, 55%)};
            --outcome-fill: #{rgba($color-orange, 34%)};
            --outcome-glow: #{rgba($color-orange, 70%)};
        }

        &--dim {
            opacity: 0.3;
        }
    }

    &__outcome-icon {
        flex-shrink: 0;
        width: 52px;
        height: 52px;
        filter: drop-shadow(0 8px 12px rgba($deep-shadow, 55%));
    }

    &__outcome-body {
        color: rgba($color-white, 82%);

        @include column($indent-step * 0.5);
    }

    &__outcome-title {
        color: $color-white;
        font-size: $font-size-base;
    }

    // Итог — главный акцент схемы
    &__finish {
        position: relative;
        z-index: 2;
        display: flex;
        overflow: hidden;
        flex-direction: column;
        transition:
            opacity $duration ease,
            transform $duration $ease-back-out;
        color: $color-white;
        border: 1px solid rgba($color-flash, 60%);
        border-radius: $radius-3xl * 1.3;
        background: linear-gradient(150deg, $color-orange-soft 0%, $color-cta 55%, $color-cta-hover 100%);
        box-shadow:
            inset 0 1px 0 rgba($color-white, 45%),
            0 0 0 6px rgba($color-cta, 18%),
            0 28px 50px -20px rgba($color-cta, 90%);
        animation: fade-up $duration-slow $ease-out backwards;
        animation-delay: calc(var(--stage-index) * 60ms);
        grid-row: 3;
        gap: $indent-step * 2;

        @include padding('y', 5);
        @include padding('x', 4.5);
        @include margin('y', -2.5);

        // блик по стеклу
        &::after {
            position: absolute;
            top: -40%;
            left: 0;
            width: 50%;
            height: 180%;
            transform: translateX(-120%) rotate(20deg);
            background: linear-gradient(90deg, transparent, rgba($color-white, 28%), transparent);
            animation: verification-flow-shine 4.5s $ease-in-out infinite;
            content: '';
            pointer-events: none;
            will-change: transform;
        }

        @include hover {
            transform: translateY(-4px);
        }

        &--dim {
            opacity: 0.35;
        }
    }

    &__finish-icon {
        @include flex-center;

        width: 44px;
        height: 44px;
        border: 1px solid rgba($color-white, 45%);
        border-radius: $radius-pill;
        background: rgba($color-white, 22%);
    }

    &__finish-title {
        font-size: $font-size-2xl;
        font-weight: $font-weight-extrabold;
        line-height: 1.2;
        text-wrap: balance;

        @include margin('top', 1);
    }

    &__finish-text {
        font-size: $font-size-sm;
        line-height: 1.45;
        opacity: 0.95;
    }

    @include laptop {
        --flow-gate: 76px;
        --flow-link: 18px;

        &__stage {
            @include padding('x', 3);
        }

        &__stage-title {
            font-size: $font-size-md;
        }
    }
}

@keyframes verification-flow-run {
    from {
        transform: translateX(-100%);
    }

    to {
        transform: translateX(100%);
    }
}

@keyframes verification-flow-shine {
    0%,
    55% {
        transform: translateX(-120%) rotate(20deg);
    }

    100% {
        transform: translateX(300%) rotate(20deg);
    }
}
</style>
