<script setup>
import {computed, ref} from 'vue';
import {LoaderCircle, Send} from 'lucide-vue-next';
import {BRAND_IMAGE} from '@/assets/images';
import {getGreeting} from '@/core/utils/date';

const props = defineProps({
    userName: {type: String, required: true},
    /** @type {import('vue').PropType<string[]>} */
    examples: {type: Array, default: () => []},
    isAsking: {type: Boolean, default: false},
});

const emit = defineEmits(['ask']);

const question = ref('');

const firstName = computed(() => props.userName.split(' ')[0]);
const greeting = computed(() => `${getGreeting(new Date().getHours())}, ${firstName.value}`);
const canAsk = computed(() => question.value.trim().length > 0 && !props.isAsking);

function handleSubmit() {
    if (canAsk.value) {
        emit('ask', question.value.trim());
    }
}

/** @param {string} example */
function handleExampleClick(example) {
    question.value = example;
    emit('ask', example);
}
</script>

<template>
    <section class="home-hero">
        <div class="home-hero__content">
            <p class="home-hero__greeting">{{ greeting }}</p>
            <h1 class="home-hero__title">Ответ по базе знаний — со ссылкой на каждый пункт</h1>
            <p class="home-hero__lead">
                Договоры, регламенты и законы в нужной редакции. Если в документах ответа нет, ассистент скажет об этом
                прямо.
            </p>

            <form
                class="home-hero__panel"
                @submit.prevent="handleSubmit"
            >
                <label
                    class="home-hero__label"
                    for="home-question"
                >
                    Задайте вопрос
                </label>
                <div class="home-hero__field">
                    <input
                        id="home-question"
                        v-model="question"
                        class="home-hero__input"
                        type="text"
                        placeholder="Например: с кем согласовать договор П-17/2024?"
                        autocomplete="off"
                    />
                    <button
                        class="home-hero__send"
                        type="submit"
                        :disabled="!canAsk"
                    >
                        <LoaderCircle
                            v-if="isAsking"
                            class="home-hero__spinner"
                            :size="18"
                            aria-hidden="true"
                        />
                        <Send
                            v-else
                            :size="18"
                            aria-hidden="true"
                        />
                        Спросить
                    </button>
                </div>
                <div
                    v-if="examples.length"
                    class="home-hero__examples"
                >
                    <button
                        v-for="example in examples"
                        :key="example"
                        class="home-hero__example"
                        type="button"
                        :disabled="isAsking"
                        @click="handleExampleClick(example)"
                    >
                        {{ example }}
                    </button>
                </div>
            </form>
        </div>

        <img
            class="home-hero__art"
            :src="BRAND_IMAGE"
            alt=""
        />
    </section>
</template>

<style lang="scss">
.home-hero {
    @include brand-band;

    display: grid;
    align-items: center;
    border-radius: $radius-3xl;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: $indent-step * 6;

    @include padding('y', 9);
    @include padding('x', 10);

    &__content {
        position: relative;
        z-index: $ui-index-base;

        @include column($indent-step * 3);
    }

    &__greeting {
        margin: 0;
        color: $color-on-brand-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__title {
        max-width: 620px;
        line-height: 1.15;

        @include heading($font-size-4xl);
    }

    &__lead {
        max-width: 560px;
        margin: 0;
        color: $color-on-brand-muted;
        font-size: $font-size-base;
        line-height: 1.55;
    }

    &__panel {
        max-width: 680px;
        border-radius: $radius-2xl;
        backdrop-filter: blur(16px);

        @include glass;
        @include column($indent-step * 3);
        @include margin('top', 3);
        @include padding('y', 4);
        @include padding('x', 4);
    }

    &__label {
        color: $color-on-brand-soft;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
    }

    &__field {
        display: flex;
        border-radius: $radius-xl;
        background: $color-surface;
        box-shadow: $shadow-card;
        gap: $indent-step * 2;

        @include padding('y', 1.5);
        @include padding('left', 4);
        @include padding('right', 1.5);
    }

    &__input {
        flex: 1;
        min-width: 0;
        color: $color-ink;
        border: none;
        outline: none;
        background: transparent;
        font: inherit;
        font-size: $font-size-base;

        &::placeholder {
            color: $color-ink-faint;
        }
    }

    &__send {
        @include button-reset;
        @include focus-ring;
        @include sheen;
        @include press;

        display: inline-flex;
        align-items: center;
        transition:
            transform $duration-fast $ease-out,
            opacity $duration ease;
        color: $color-white;
        border-radius: $radius-lg;
        background: $color-action;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        @include padding('y', 2.5);
        @include padding('x', 4.5);

        &:disabled {
            opacity: 0.6;
            cursor: default;
        }

        &:not(:disabled) {
            @include hover {
                transform: translateY(-1px);
            }
        }
    }

    &__spinner {
        animation: spin 0.9s linear infinite;
    }

    &__examples {
        display: flex;
        flex-wrap: wrap;
        gap: $indent-step * 2;
    }

    &__example {
        @include button-reset;
        @include focus-ring;
        @include press;

        transition:
            background-color $duration ease,
            transform $duration-fast $ease-out;
        color: $color-white;
        border: 1px solid rgba($color-white, 28%);
        border-radius: $radius-pill;
        background: rgba($color-white, 10%);
        font-size: $font-size-xs;
        font-weight: $font-weight-semibold;

        @include padding('y', 1.5);
        @include padding('x', 3);

        @include hover {
            background: rgba($color-white, 22%);
        }
    }

    &__art {
        position: relative;
        z-index: $ui-index-base;
        width: 100%;
        filter: drop-shadow(0 30px 40px rgba($color-ink, 35%));
        animation: fade-up $duration-slow $ease-out both;
    }

    @include tablet {
        grid-template-columns: 1fr;

        @include padding('y', 7);
        @include padding('x', 6);

        &__art {
            display: none;
        }
    }

    @include mobile {
        border-radius: $radius-2xl;

        @include padding('y', 6);
        @include padding('x', 4);

        &__title {
            font-size: $font-size-3xl;
        }

        &__field {
            flex-direction: column;

            @include padding('x', 1.5);
        }

        &__input {
            @include padding('y', 2);
            @include padding('x', 2);
        }

        &__send {
            justify-content: center;
        }
    }
}
</style>
