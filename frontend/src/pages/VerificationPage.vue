<script setup>
import {computed, ref} from 'vue';
import {ArrowRight, ShieldCheck} from 'lucide-vue-next';
import {ROUTE_NAMES} from '@/core/constants';
import {FLOW_SCENARIOS, VERIFICATION_FACTS} from '@/core/data/verificationFlow';

import VerificationFlow from '@/components/Verification/VerificationFlow.vue';

const scenarioId = ref(FLOW_SCENARIOS[0].id);

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
                    Ответ уходит юристу, только если каждое утверждение подтверждено пунктом документа в нужной
                    редакции. Иначе — уточняющий вопрос или обоснованный отказ.
                </p>
            </div>
        </header>

        <ul class="verification-page__facts">
            <li
                v-for="fact in VERIFICATION_FACTS"
                :key="fact.id"
                class="verification-page__fact"
            >
                <span class="verification-page__fact-label">{{ fact.label }}</span>
                <span class="verification-page__fact-value">{{ fact.value }}</span>
                <span class="verification-page__fact-text">{{ fact.text }}</span>
            </li>
        </ul>

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

            <VerificationFlow :scenario="scenario" />

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
    </div>
</template>

<style lang="scss">
.verification-page {
    max-width: 1280px;
    margin: 0 auto;

    @include column($indent-step * 5);

    &__band {
        @include brand-band;
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
        border-radius: $radius-xl;
        backdrop-filter: blur(10px);

        @include glass;
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
        color: $color-on-brand-muted;
        font-size: $font-size-base;
        line-height: 1.6;
    }

    &__facts {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: $indent-step * 4;
    }

    &__fact {
        box-shadow: $shadow-card;

        @include card($radius-2xl);
        @include column($indent-step);
        @include padding('y', 4);
        @include padding('x', 5);
    }

    &__fact-label {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
    }

    &__fact-value {
        color: $color-navy;

        @include heading($font-size-2xl);
    }

    &__fact-text {
        color: $color-ink-soft;
        font-size: $font-size-sm;
        line-height: 1.5;
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

    @include tablet {
        &__facts {
            grid-template-columns: 1fr;
        }

        &__band {
            @include padding('y', 6);
            @include padding('x', 5);
        }

        &__scheme {
            @include padding('x', 4);
        }
    }
}
</style>
