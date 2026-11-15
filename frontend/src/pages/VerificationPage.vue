<script setup>
import {computed, ref} from 'vue';
import {ArrowRight, ShieldCheck} from 'lucide-vue-next';
import {VERIFICATION_IMAGES} from '@/assets/images';
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

        <section
            class="verification-page__scheme"
            :style="{'--scene-image': `url(${VERIFICATION_IMAGES.scene})`}"
        >
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
                        <span class="verification-page__funnel-body">
                            <span class="verification-page__funnel-label">{{ row.label }}</span>
                            <span class="verification-page__funnel-track">
                                <span
                                    class="verification-page__funnel-bar"
                                    :style="{width: `${Math.max((row.value / funnelMax) * 100, 4)}%`}"
                                />
                            </span>
                        </span>
                    </li>
                </ul>
            </section>

            <section
                class="verification-page__rules"
                :style="{'--scene-image': `url(${VERIFICATION_IMAGES.scene})`}"
            >
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
    $scene-glow: #b9a2ff;

    max-width: 1440px;
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

    // Тёмная сцена со стеклянной схемой
    &__scheme {
        position: relative;
        overflow: hidden;
        color: $color-white;
        border: 1px solid rgba($color-white, 12%);
        border-radius: $radius-3xl * 1.4;
        background:
            radial-gradient(120% 80% at 0% 0%, rgba($color-violet-bright, 35%), transparent 60%),
            linear-gradient(180deg, rgba($color-navy, 35%), rgba(#0d1250, 55%)),
            var(--scene-image) center / cover no-repeat,
            $color-navy;
        box-shadow: 0 40px 70px -40px rgba($color-navy, 85%);

        @include column($indent-step * 6);
        @include padding('y', 7);
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
        color: $color-white;

        @include heading($font-size-3xl);
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
            border-color $duration ease,
            box-shadow $duration ease,
            color $duration ease;
        color: $color-on-brand-muted;
        border: 1px solid rgba($color-white, 26%);
        border-radius: $radius-pill;
        background: rgba($color-white, 10%);
        backdrop-filter: blur(10px);
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;

        @include padding('y', 2);
        @include padding('x', 3.5);

        @include hover {
            color: $color-white;
            background: rgba($color-white, 20%);
        }

        &--active {
            color: $color-navy;
            border-color: $color-white;
            background: $color-white;
            box-shadow: 0 0 0 4px rgba($scene-glow, 35%);

            @include hover {
                color: $color-navy;
                background: $color-white;
            }
        }
    }

    &__steps {
        display: none;

        // вертикальная схема на тёмной сцене
        .verification-steps__label {
            color: $color-white;
        }

        .verification-steps__yes {
            color: $color-on-brand-soft;
        }

        .verification-steps__step:not(:last-child)::before {
            background-color: rgba($color-white, 25%);
        }

        .verification-steps__step--lit:not(:last-child)::before {
            background-color: $scene-glow;
        }

        .verification-steps__marker {
            border-color: rgba($color-white, 45%);
            background-color: rgba($color-white, 12%);
        }

        .verification-steps__step--start .verification-steps__marker,
        .verification-steps__step--finish .verification-steps__marker {
            border-color: $color-cta;
            background-color: $color-cta;
        }

        .verification-steps__branch {
            color: $color-white;
            border: 1px solid rgba($color-flash, 45%);
            background-color: rgba($color-orange, 22%);
        }

        .verification-steps__note {
            border: 1px solid rgba($color-white, 22%);
            background-color: rgba($color-white, 10%);
        }
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
        transition:
            transform $duration $ease-back-out,
            box-shadow $duration ease;
        border: 1px solid $color-line;
        border-radius: $radius-2xl;
        background: linear-gradient(90deg, $color-surface-soft, $color-surface);
        grid-template-columns: 76px minmax(0, 1fr);
        gap: $indent-step * 4;

        @include padding('y', 3);
        @include padding('x', 4);

        @include hover {
            transform: translateX(4px);
            box-shadow: $shadow-card;
        }

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

    &__funnel-body {
        min-width: 0;

        @include column($indent-step * 2);
    }

    &__funnel-track {
        overflow: hidden;
        height: 12px;
        border-radius: $radius-pill;
        background: $color-surface-muted;
        box-shadow: inset 0 1px 2px rgba($color-ink, 10%);
    }

    &__funnel-bar {
        display: block;
        height: 100%;
        transform-origin: left;
        border-radius: $radius-pill;
        background: linear-gradient(90deg, rgba($color-white, 35%), transparent 60%), var(--funnel-color);
        box-shadow: 0 0 12px -2px var(--funnel-color);
        animation: funnel-grow $duration-step $ease-out backwards;
    }

    &__funnel-label {
        color: $color-ink-soft;
        font-size: $font-size-md;
        line-height: 1.4;
    }

    &__rules {
        position: relative;
        overflow: hidden;
        color: $color-white;
        border: 1px solid rgba($color-white, 12%);
        border-radius: $radius-3xl * 1.4;
        background:
            linear-gradient(160deg, rgba($color-navy, 55%), rgba(#0d1250, 70%)),
            var(--scene-image) right center / cover no-repeat,
            $color-navy;
        box-shadow: 0 30px 60px -36px rgba($color-navy, 85%);

        @include column($indent-step * 5);
        @include padding('y', 6);
        @include padding('x', 6);
    }

    &__facts {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: minmax(0, 1fr);
        gap: $indent-step * 3;
    }

    // Правило — стеклянная плашка: значение слева, пояснение справа
    &__fact {
        display: grid;
        align-items: center;
        transition:
            transform $duration $ease-back-out,
            background $duration ease;
        border: 1px solid rgba($color-white, 20%);
        border-radius: $radius-2xl;
        background: linear-gradient(150deg, rgba($color-white, 16%), rgba($color-white, 6%));
        box-shadow: inset 0 1px 0 rgba($color-white, 25%);
        grid-template-columns: 104px minmax(0, 1fr);
        gap: $indent-step * 4;

        @include padding('y', 3.5);
        @include padding('x', 4);

        @include hover {
            transform: translateY(-3px);
            background: linear-gradient(150deg, rgba($color-white, 20%), rgba($color-white, 6%));
        }
    }

    &__fact-value {
        color: $color-orange-soft;
        white-space: nowrap;
        text-shadow: 0 0 18px rgba($color-orange, 55%);

        @include heading($font-size-3xl);
    }

    &__fact-text {
        color: rgba($color-white, 85%);
        font-size: $font-size-sm;
        line-height: 1.5;
    }

    &__example {
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        align-self: center;
        color: $color-white;
        border: 1px solid rgba($color-white, 30%);
        border-radius: $radius-pill;
        background: rgba($color-white, 12%);

        @include padding('y', 2);
        @include padding('x', 4);
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
            grid-template-columns: 52px minmax(0, 1fr);
            gap: $indent-step * 3;
        }

        &__fact {
            grid-template-columns: minmax(0, 1fr);
            gap: $indent-step;
        }

        &__scheme,
        &__rules {
            @include padding('x', 4);
        }
    }
}
</style>
