<script setup>
import UiSkeleton from '@/components/Ui/UiSkeleton.vue';

const LINE_WIDTHS = Object.freeze(['96%', '88%', '92%', '60%', '94%', '82%', '90%', '48%']);
</script>

<template>
    <div
        class="document-skeleton"
        role="status"
        aria-label="Открываю документ"
    >
        <UiSkeleton
            height="140px"
            radius="20px"
        />
        <div class="document-skeleton__grid">
            <UiSkeleton
                class="document-skeleton__toc"
                height="300px"
                radius="18px"
            />
            <div class="document-skeleton__paper">
                <UiSkeleton
                    width="40%"
                    height="22px"
                />
                <UiSkeleton
                    v-for="(width, index) in LINE_WIDTHS"
                    :key="index"
                    :width="width"
                    height="14px"
                />
            </div>
        </div>
    </div>
</template>

<style lang="scss">
.document-skeleton {
    @include column($indent-step * 5);

    &__grid {
        display: grid;
        align-items: start;
        grid-template-columns: 240px minmax(0, 1fr);
        gap: $indent-step * 5;
    }

    &__paper {
        @include card($radius-md);
        @include column($indent-step * 4);
        @include padding('y', 12);
        @include padding('x', 14);
    }

    @include tablet {
        &__grid {
            grid-template-columns: minmax(0, 1fr);
        }

        &__toc {
            display: none;
        }

        &__paper {
            @include padding('x', 6);
        }
    }
}
</style>
