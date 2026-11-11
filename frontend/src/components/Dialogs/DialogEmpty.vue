<script setup>
import {ArrowRight} from 'lucide-vue-next';
import {NEW_DIALOG_STARTERS} from '@/core/data/dialogs';

import UiBrandMark from '@/components/Ui/UiBrandMark.vue';

const emit = defineEmits(['ask']);
</script>

<template>
    <section class="dialog-empty">
        <UiBrandMark :size="56" />
        <h1 class="dialog-empty__title">Новый вопрос</h1>
        <p class="dialog-empty__text">
            Назовите договор и, если важно, дату события — так ассистент выберет нужную редакцию документов.
        </p>
        <ul class="dialog-empty__starters">
            <li
                v-for="starter in NEW_DIALOG_STARTERS"
                :key="starter.id"
            >
                <button
                    class="dialog-empty__starter"
                    type="button"
                    @click="emit('ask', starter.question)"
                >
                    <span class="dialog-empty__tag">{{ starter.tag }}</span>
                    <span class="dialog-empty__question">{{ starter.question }}</span>
                    <ArrowRight
                        class="dialog-empty__arrow"
                        :size="16"
                        aria-hidden="true"
                    />
                </button>
            </li>
        </ul>
    </section>
</template>

<style lang="scss">
.dialog-empty {
    $block: &;

    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: $indent-step * 3;

    @include padding('y', 10);

    &__title {
        @include heading($font-size-3xl);
    }

    &__text {
        max-width: 460px;
        margin: 0;
        color: $color-ink-soft;
        font-size: $font-size-md;
        line-height: 1.6;
    }

    &__starters {
        display: grid;
        width: 100%;
        max-width: 760px;
        margin: 0;
        padding: 0;
        list-style: none;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: $indent-step * 3;

        @include margin('top', 3);
    }

    &__starter {
        @include button-reset;
        @include card($radius-xl);
        @include focus-ring;
        @include column($indent-step * 2);
        @include padding('y', 4);
        @include padding('x', 4);

        position: relative;
        width: 100%;
        height: 100%;
        transition:
            transform $duration $ease-out,
            box-shadow $duration ease;
        text-align: left;

        @include hover {
            transform: translateY(-2px);
            box-shadow: $shadow-card;

            #{$block}__arrow {
                color: $color-violet;
                transform: translateX(2px);
            }
        }
    }

    &__tag {
        align-self: flex-start;

        @include pill($color-lavender, $color-violet);
    }

    &__question {
        color: $color-ink;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
        line-height: 1.45;

        @include padding('right', 5);
    }

    &__arrow {
        position: absolute;
        right: $indent-step * 4;
        bottom: $indent-step * 4;
        transition:
            color $duration ease,
            transform $duration $ease-out;
        color: $color-ink-decor;
    }

    @include tablet {
        &__starters {
            grid-template-columns: minmax(0, 1fr);
        }
    }
}
</style>
