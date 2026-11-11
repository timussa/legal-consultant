<script setup>
import UiSkeleton from '@/components/Ui/UiSkeleton.vue';
</script>

<template>
    <div
        class="home-skeleton"
        role="status"
        aria-label="Открываю базу знаний"
    >
        <div class="home-skeleton__stats">
            <UiSkeleton
                v-for="index in 3"
                :key="index"
                height="96px"
                radius="18px"
            />
        </div>
        <UiSkeleton
            width="220px"
            height="22px"
        />
        <div class="home-skeleton__sections">
            <UiSkeleton
                height="360px"
                radius="20px"
            />
            <UiSkeleton
                height="360px"
                radius="20px"
            />
        </div>
    </div>
</template>

<style lang="scss">
.home-skeleton {
    @include column($indent-step * 6);

    &__stats {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: $indent-step * 4;
    }

    &__sections {
        display: grid;
        grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
        gap: $indent-step * 5;
    }

    @include tablet {
        &__stats,
        &__sections {
            grid-template-columns: minmax(0, 1fr);
        }
    }
}
</style>
