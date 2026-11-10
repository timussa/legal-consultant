<script setup>
import {CircleCheck} from 'lucide-vue-next';
import {storeToRefs} from 'pinia';
import {useToastStore} from '@/core/stores/toast';

const toastStore = useToastStore();
const {toasts} = storeToRefs(toastStore);
</script>

<template>
    <div
        class="toast-container"
        aria-live="polite"
    >
        <TransitionGroup name="toast-container__toast">
            <div
                v-for="toast in toasts"
                :key="toast.id"
                class="toast-container__toast"
            >
                <CircleCheck
                    :size="18"
                    aria-hidden="true"
                />
                {{ toast.text }}
            </div>
        </TransitionGroup>
    </div>
</template>

<style lang="scss">
.toast-container {
    position: fixed;
    z-index: $ui-index-overlay;
    bottom: $indent-step * 6;
    left: 50%;
    transform: translateX(-50%);
    pointer-events: none;

    @include column($indent-step * 2);

    &__toast {
        display: flex;
        align-items: center;
        color: $color-white;
        border-radius: $radius-pill;
        background: $color-ink;
        box-shadow: $shadow-card;
        font-size: $font-size-sm;
        font-weight: $font-weight-semibold;
        gap: $indent-step * 2;

        @include padding('y', 2.5);
        @include padding('x', 4.5);

        &-enter-active,
        &-leave-active {
            transition:
                opacity $duration ease,
                transform $duration $ease-out;
        }

        &-enter-from,
        &-leave-to {
            transform: translateY(8px);
            opacity: 0;
        }
    }

    @include mobile {
        bottom: $indent-step * 22;
    }
}
</style>
