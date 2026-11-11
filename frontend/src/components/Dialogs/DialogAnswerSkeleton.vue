<script setup>
import UiSkeleton from '@/components/Ui/UiSkeleton.vue';

const LINE_WIDTHS = Object.freeze(['94%', '86%', '72%']);
</script>

<template>
    <div
        class="dialog-answer-skeleton"
        role="status"
        aria-label="Составляю ответ"
    >
        <div class="dialog-answer-skeleton__head">
            <UiSkeleton
                width="34px"
                height="34px"
                radius="12px"
            />
            <UiSkeleton
                width="160px"
                height="14px"
            />
        </div>
        <UiSkeleton
            v-for="(width, index) in LINE_WIDTHS"
            :key="index"
            :width="width"
            height="16px"
        />
    </div>
</template>

<style lang="scss">
.dialog-answer-skeleton {
    @include card($radius-3xl);
    @include column($indent-step * 3.5);
    @include padding('y', 6);
    @include padding('x', 6);

    &__head {
        display: flex;
        align-items: center;
        gap: $indent-step * 3;

        @include margin('bottom', 1);
    }
}
</style>
