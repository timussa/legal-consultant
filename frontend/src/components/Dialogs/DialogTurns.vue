<script setup>
import {ShieldAlert, ShieldCheck} from 'lucide-vue-next';

defineProps({
    /** @type {import('vue').PropType<import('@/core/types/assistant').Turn[]>} */
    turns: {type: Array, required: true},
});
</script>

<template>
    <ol class="dialog-turns">
        <li
            v-for="(turn, index) in turns"
            :key="index"
            :class="[
                'dialog-turns__turn',
                `dialog-turns__turn--${turn.role}`,
                {'dialog-turns__turn--injected': turn.isInjected},
            ]"
        >
            <template v-if="turn.role === 'user'">
                <span
                    v-if="turn.isInjected"
                    class="dialog-turns__warning"
                >
                    <ShieldAlert
                        :size="14"
                        aria-hidden="true"
                    />
                    Похоже на подмену роли
                </span>
                <p class="dialog-turns__bubble">{{ turn.text }}</p>
            </template>

            <div
                v-else
                class="dialog-turns__guard"
            >
                <span class="dialog-turns__shield">
                    <ShieldCheck
                        :size="18"
                        aria-hidden="true"
                    />
                </span>
                <div class="dialog-turns__guard-body">
                    <span
                        v-if="turn.badge"
                        class="dialog-turns__badge"
                    >
                        {{ turn.badge }}
                    </span>
                    <p class="dialog-turns__text">{{ turn.text }}</p>
                </div>
            </div>
        </li>
    </ol>
</template>

<style lang="scss">
.dialog-turns {
    margin: 0;
    padding: 0;
    list-style: none;

    @include column($indent-step * 4);

    &__turn {
        animation: fade-up $duration-slow $ease-out both;

        &--user {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: $indent-step * 1.5;
        }
    }

    &__bubble {
        max-width: 78%;
        margin: 0;
        color: $color-white;
        border-radius: $radius-2xl $radius-2xl $radius-xs $radius-2xl;
        background: $color-action;
        box-shadow: $shadow-bubble;
        font-size: $font-size-md;
        line-height: 1.55;

        @include padding('y', 3);
        @include padding('x', 4);
    }

    &__turn--injected &__bubble {
        color: $color-injected-ink;
        border: 1px dashed rgba($color-orange-soft, 60%);
        background: $color-injected-bg;
        font-family: $font-mono;
        font-size: $font-size-sm;
    }

    &__warning {
        @include pill($color-peach, $color-peach-ink);
    }

    &__guard {
        display: flex;
        align-items: flex-start;
        max-width: 86%;
        border: 1px solid $color-lavender-line;
        border-radius: $radius-2xl;
        background: $color-lavender-soft;
        gap: $indent-step * 3;

        @include padding('y', 3.5);
        @include padding('x', 4);
    }

    &__shield {
        @include flex-center;

        flex-shrink: 0;
        width: 34px;
        height: 34px;
        color: $color-white;
        border-radius: $radius-pill;
        background: $color-action;
        animation: shield-pulse 1.8s ease-out 3;
    }

    &__guard-body {
        @include column($indent-step * 1.5);
    }

    &__badge {
        align-self: flex-start;

        @include pill($color-surface, $color-violet);
    }

    &__text {
        margin: 0;
        color: $color-text-body;
        font-size: $font-size-md;
        line-height: 1.6;
    }

    @include mobile {
        &__bubble,
        &__guard {
            max-width: 100%;
        }
    }
}
</style>
