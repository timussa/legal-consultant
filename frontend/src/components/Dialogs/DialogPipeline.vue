<script setup>
import {computed, ref, watch} from 'vue';
import {Check, ChevronDown, LoaderCircle, RotateCcw} from 'lucide-vue-next';
import {pluralize} from '@/core/utils/plural';

const props = defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').PipelineStep[]>} */
    steps: {type: Array, default: () => []},
    activeStepIndex: {type: Number, default: -1},
    progress: {type: Number, default: 0},
    totalDurationLabel: {type: String, default: ''},
    isWaiting: {type: Boolean, default: false},
    isDone: {type: Boolean, default: false},
});

const emit = defineEmits(['replay']);

const isExpanded = ref(!props.isDone);

const summary = computed(() => {
    const count = props.steps.length;

    return `Ход проверки · ${count} ${pluralize(count, ['шаг', 'шага', 'шагов'])} · ${props.totalDurationLabel}`;
});

watch(
    () => props.isDone,
    (isDone) => {
        isExpanded.value = !isDone;
    },
);

/** @param {number} index */
function getStepState(index) {
    if (props.isDone || index < props.activeStepIndex) {
        return 'done';
    }

    return index === props.activeStepIndex ? 'active' : 'pending';
}

function handleReplay() {
    isExpanded.value = true;
    emit('replay');
}
</script>

<template>
    <section
        :class="['dialog-pipeline', {'dialog-pipeline--done': isDone}]"
        aria-live="polite"
    >
        <div
            v-if="isWaiting"
            class="dialog-pipeline__waiting"
        >
            <LoaderCircle
                class="dialog-pipeline__spinner"
                :size="18"
                aria-hidden="true"
            />
            Ищем в базе знаний и выбираем редакции документов…
        </div>

        <template v-else>
            <div class="dialog-pipeline__head">
                <button
                    class="dialog-pipeline__toggle"
                    type="button"
                    :aria-expanded="isExpanded"
                    :disabled="!isDone"
                    @click="isExpanded = !isExpanded"
                >
                    <span
                        v-if="!isDone"
                        class="dialog-pipeline__live"
                    />
                    <Check
                        v-else
                        class="dialog-pipeline__done-icon"
                        :size="16"
                        aria-hidden="true"
                    />
                    {{ isDone ? summary : 'Проверяем ответ по документам' }}
                    <ChevronDown
                        v-if="isDone"
                        :class="['dialog-pipeline__chevron', {'dialog-pipeline__chevron--open': isExpanded}]"
                        :size="16"
                        aria-hidden="true"
                    />
                </button>
                <button
                    v-if="isDone"
                    class="dialog-pipeline__replay"
                    type="button"
                    @click="handleReplay"
                >
                    <RotateCcw
                        :size="14"
                        aria-hidden="true"
                    />
                    Показать заново
                </button>
            </div>

            <div class="dialog-pipeline__track">
                <span
                    class="dialog-pipeline__progress"
                    :style="{'--pipeline-progress': isDone ? 1 : progress}"
                />
            </div>

            <ol
                v-if="isExpanded"
                class="dialog-pipeline__steps"
            >
                <li
                    v-for="(step, index) in steps"
                    :key="step.title"
                    :class="['dialog-pipeline__step', `dialog-pipeline__step--${getStepState(index)}`]"
                >
                    <span class="dialog-pipeline__marker">
                        <Check
                            v-if="getStepState(index) === 'done'"
                            :size="13"
                            :stroke-width="3"
                            aria-hidden="true"
                        />
                        <LoaderCircle
                            v-else-if="getStepState(index) === 'active'"
                            class="dialog-pipeline__spinner"
                            :size="13"
                            aria-hidden="true"
                        />
                        <template v-else>{{ index + 1 }}</template>
                    </span>
                    <span class="dialog-pipeline__step-text">
                        <span class="dialog-pipeline__step-title">{{ step.title }}</span>
                        <span class="dialog-pipeline__step-detail">{{ step.detail }}</span>
                    </span>
                    <span class="dialog-pipeline__step-time">{{ step.durationLabel }}</span>
                </li>
            </ol>
        </template>
    </section>
</template>

<style lang="scss">
.dialog-pipeline {
    $block: &;

    @include card($radius-2xl);
    @include column($indent-step * 3);
    @include padding('y', 4);
    @include padding('x', 5);

    &__waiting {
        display: flex;
        align-items: center;
        color: $color-ink-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        gap: $indent-step * 2.5;
    }

    &__spinner {
        color: $color-violet;
        animation: spin 0.9s linear infinite;
    }

    &__head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: $indent-step * 3;
    }

    &__toggle {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        color: $color-ink;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        gap: $indent-step * 2;

        &:disabled {
            cursor: default;
        }
    }

    &__live {
        width: 8px;
        height: 8px;
        border-radius: $radius-pill;
        background: $color-violet-bright;
        animation: shield-pulse 1.2s ease-out infinite;
    }

    &__done-icon {
        color: $color-violet;
    }

    &__chevron {
        transition: transform $duration $ease-out;
        color: $color-ink-muted;

        &--open {
            transform: rotate(180deg);
        }
    }

    &__replay {
        @include button-reset;
        @include focus-ring;

        display: inline-flex;
        align-items: center;
        color: $color-ink-muted;
        font-size: $font-size-xs;
        font-weight: $font-weight-bold;
        gap: $indent-step * 1.5;

        @include hover {
            color: $color-violet;
        }
    }

    &__track {
        overflow: hidden;
        height: 4px;
        border-radius: $radius-pill;
        background: $color-surface-muted;
    }

    &__progress {
        display: block;
        height: 100%;
        transform: scaleX(var(--pipeline-progress));
        transform-origin: left;
        transition: transform $duration-step $ease-out;
        border-radius: inherit;
        background: $gradient-thread;
    }

    &__steps {
        display: grid;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: $indent-step * 2 $indent-step * 5;
    }

    &__step {
        display: flex;
        align-items: flex-start;
        transition: opacity $duration ease;
        gap: $indent-step * 2.5;

        &--pending {
            opacity: 0.45;
        }

        &--active #{$block}__marker {
            color: $color-violet;
            background: $color-lavender;
        }

        &--done #{$block}__marker {
            color: $color-white;
            background: $gradient-user;
        }
    }

    &__marker {
        @include flex-center;

        flex-shrink: 0;
        width: 22px;
        height: 22px;
        color: $color-ink-muted;
        border-radius: $radius-pill;
        background: $color-surface-muted;
        font-size: $font-size-2xs;
        font-weight: $font-weight-extrabold;
    }

    &__step-text {
        flex: 1;
        min-width: 0;

        @include column(0);
    }

    &__step-title {
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__step-detail {
        color: $color-ink-muted;
        font-size: $font-size-xs;
        line-height: 1.45;
    }

    &__step-time {
        color: $color-ink-faint;
        font-family: $font-mono;
        font-size: $font-size-2xs;
    }

    @include mobile {
        @include padding('x', 4);

        &__steps {
            grid-template-columns: 1fr;
        }

        &__replay {
            display: none;
        }
    }
}
</style>
