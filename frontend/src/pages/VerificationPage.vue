<script setup>
import {computed, ref} from 'vue';
import {ArrowRight, ShieldCheck} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';
import {FLOW_FUNNEL, FLOW_SCENARIOS, VERIFICATION_FACTS} from '@/core/data/verificationFlow';

import VerificationFlow from '@/components/Verification/VerificationFlow.vue';
import VerificationSteps from '@/components/Verification/VerificationSteps.vue';

const scenarioId = ref(null);

const funnelMax = Math.max(...FLOW_FUNNEL.rows.map((row) => row.value));

const scenario = computed(() => FLOW_SCENARIOS.find((item) => item.id === scenarioId.value) ?? null);

/** @param {string} id */
function handleScenarioClick(id) {
    scenarioId.value = scenarioId.value === id ? null : id;
}
</script>

<template>
    <div class="verification-page">
        <header class="verification-page__band">
            <span class="verification-page__icon">
                <ShieldCheck
                    :size="26"
                    aria-hidden="true"
                />
            </span>
            <div class="verification-page__intro">
                <h1 class="verification-page__title">Как проверяется каждый ответ</h1>
                <p class="verification-page__lead">
                    Ответ уходит юристу, только если каждое утверждение опирается на пункт документа в нужной редакции.
                    Иначе ассистент уточняет вопрос или честно отказывает.
                </p>
            </div>
        </header>

        <section class="verification-page__scheme">
            <div class="verification-page__scheme-head">
                <h2 class="verification-page__scheme-title">Схема проверки</h2>
                <div
                    class="verification-page__scenarios"
                    role="group"
                    aria-label="Подсветить сценарий"
                >
                    <button
                        v-for="item in FLOW_SCENARIOS"
                        :key="item.id"
                        :class="[
                            'verification-page__scenario',
                            {'verification-page__scenario--active': item.id === scenarioId},
                        ]"
                        type="button"
                        :aria-pressed="item.id === scenarioId"
                        @click="handleScenarioClick(item.id)"
                    >
                        {{ item.label }}
                    </button>
                </div>
            </div>

            <div class="verification-page__flow">
                <VerificationFlow :scenario="scenario" />
            </div>
            <div class="verification-page__steps">
                <VerificationSteps :scenario="scenario" />
            </div>

            <RouterLink
                v-if="scenario"
                class="verification-page__example"
                :to="{name: ROUTE_NAMES.dialogs, params: {dialogId: scenario.dialogId}}"
            >
                Посмотреть пример: диалог №{{ scenario.dialogId }}
                <ArrowRight
                    :size="16"
                    aria-hidden="true"
                />
            </RouterLink>
        </section>

        <div class="verification-page__summary">
            <section class="verification-page__funnel">
                <div class="verification-page__panel-head">
                    <h2 class="verification-page__panel-title">Сколько доходит до ответа</h2>
                    <span class="verification-page__panel-note">{{ FLOW_FUNNEL.note }}</span>
                </div>
                <ul class="verification-page__funnel-list">
                    <li
                        v-for="row in FLOW_FUNNEL.rows"
                        :key="row.id"
                        :class="['verification-page__funnel-row', `verification-page__funnel-row--${row.tone}`]"
                    >
                        <span class="verification-page__funnel-value">{{ row.value }}</span>
                        <span class="verification-page__funnel-track">
                            <span
                                class="verification-page__funnel-bar"
                                :style="{width: `${(row.value / funnelMax) * 100}%`}"
                            />
                        </span>
                        <span class="verification-page__funnel-label">{{ row.label }}</span>
                    </li>
                </ul>
            </section>

            <section class="verification-page__rules">
                <h2 class="verification-page__panel-title verification-page__panel-title--inverse">
                    Три правила, которые нельзя обойти
                </h2>
                <ul class="verification-page__facts">
                    <li
                        v-for="fact in VERIFICATION_FACTS"
                        :key="fact.id"
                        class="verification-page__fact"
                    >
                        <span class="verification-page__fact-value">{{ fact.value }}</span>
                        <span class="verification-page__fact-text">{{ fact.text }}</span>
                    </li>
                </ul>
            </section>
        </div>
    </div>
</template>

<style lang="scss">
.verification-page {
    max-width: 1280px;
    margin: 0 auto;

    @include column($indent-step * 5);

    &__band {
        @include light-band;
        @include padding('y', 7);
        @include padding('x', 8);

        display: flex;
        align-items: flex-start;
        border-radius: $radius-3xl;
        gap: $indent-step * 5;
    }

    &__icon {
        @include flex-center;

        flex-shrink: 0;
        width: 56px;
        height: 56px;
        color: $color-navy;
        border-radius: $radius-xl;
        background-color: $color-navy-tint;
    }

    &__intro {
        @include column($indent-step * 2);
    }

    &__title {
        @include heading($font-size-3xl);
    }

    &__lead {
        max-width: 720px;
        margin: 0;
        color: $color-ink-soft;
        font-size: $font-size-base;
        line-height: 1.6;
    }

    &__scheme {
        box-shadow: $shadow-card;

        @include card($radius-3xl);
        @include column($indent-step * 5);
        @include padding('y', 6);
        @include padding('x', 6);
    }

    &__scheme-head {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: $indent-step * 3;
    }

    &__scheme-title {
        @include heading;
    }

    &__scenarios {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 2;
    }

    &__scenario {
        @include button-reset;
        @include focus-ring;

        transition:
            background $duration ease,
            color $duration ease;
        color: $color-ink-soft;
        border: 1px solid $color-line;
        border-radius: $radius-pill;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;

        @include padding('y', 2);
        @include padding('x', 3.5);

        @include hover {
            color: $color-navy;
            border-color: $color-lavender-line;
        }

        &--active {
            color: $color-white;
            border-color: transparent;
            background: $color-action;

            @include hover {
                color: $color-white;
            }
        }
    }

    &__steps {
        display: none;
    }

    &__summary {
        display: grid;
        grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
        gap: $indent-step * 5;
    }

    &__funnel {
        box-shadow: $shadow-card;

        @include card($radius-3xl);
        @include column($indent-step * 5);
        @include padding('y', 6);
        @include padding('x', 7);
    }

    &__panel-head {
        display: flex;
        flex-wrap: wrap;
        align-items: baseline;
        justify-content: space-between;
        gap: $indent-step * 2;
    }

    &__panel-title {
        @include heading;

        &--inverse {
            color: $color-white;
        }
    }

    &__panel-note {
        color: $color-ink-muted;
        font-size: $font-size-sm;
    }

    &__funnel-list {
        margin: 0;
        padding: 0;
        list-style: none;

        @include column($indent-step * 3);
    }

    &__funnel-row {
        display: grid;
        align-items: center;
        grid-template-columns: 64px minmax(0, 1.4fr) minmax(0, 1fr);
        gap: $indent-step * 5;

        --funnel-color: #{$color-lavender-line};
        --funnel-ink: #{$color-indigo};

        &--violet {
            --funnel-color: #{$color-violet};
            --funnel-ink: #{$color-violet};
        }

        &--cta {
            --funnel-color: #{$color-cta};
            --funnel-ink: #{$color-cta};
        }
    }

    &__funnel-value {
        color: var(--funnel-ink);
        text-align: right;

        @include heading($font-size-4xl);
    }

    &__funnel-track {
        overflow: hidden;
        height: 14px;
        border-radius: $radius-pill;
        background: $color-page;
    }

    &__funnel-bar {
        display: block;
        height: 100%;
        transform-origin: left;
        border-radius: $radius-pill;
        background: var(--funnel-color);
        animation: funnel-grow $duration-step $ease-out backwards;
    }

    &__funnel-label {
        color: $color-ink-soft;
        font-size: $font-size-md;
        line-height: 1.4;
    }

    &__rules {
        color: $color-white;
        border-radius: $radius-3xl * 1.4;
        background: $color-navy;
        box-shadow: $shadow-bubble;

        @include column($indent-step * 5);
        @include padding('y', 6);
        @include padding('x', 7);
    }

    &__facts {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: $indent-step * 5;
    }

    &__fact {
        @include column($indent-step * 2);
    }

    &__fact-value {
        color: $color-orange-soft;

        @include heading($font-size-3xl);
    }

    &__fact-text {
        color: rgba($color-white, 82%);
        font-size: $font-size-sm;
        line-height: 1.5;
    }

    &__example {
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        align-self: center;
        color: $color-violet;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        text-decoration: none;
        gap: $indent-step * 2;

        @include hover {
            text-decoration: underline;
        }
    }

    @include laptop {
        &__summary {
            grid-template-columns: minmax(0, 1fr);
        }
    }

    @include tablet {
        &__flow {
            display: none;
        }

        &__steps {
            display: block;
        }

        &__summary {
            grid-template-columns: minmax(0, 1fr);
        }

        &__funnel,
        &__rules {
            @include padding('x', 5);
        }

        &__band {
            @include padding('y', 6);
            @include padding('x', 5);
        }

        &__scheme {
            @include padding('x', 4);
        }
    }

    @include mobile {
        &__facts {
            grid-template-columns: minmax(0, 1fr);
        }

        &__funnel-row {
            grid-template-columns: 48px minmax(0, 1fr);
        }

        &__funnel-label {
            grid-column: 2;
        }
    }
}
</style>
