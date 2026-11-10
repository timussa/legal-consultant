<script setup>
import DefaultLayout from '@/layouts/DefaultLayout.vue';
</script>

<template>
    <DefaultLayout>
        <RouterView v-slot="{Component, route}">
            <Transition
                name="app__page"
                mode="out-in"
            >
                <component
                    :is="Component"
                    :key="route.name"
                />
            </Transition>
        </RouterView>
    </DefaultLayout>
</template>

<style lang="scss">
.app {
    &__page {
        &-enter-active,
        &-leave-active {
            transition:
                opacity $duration-fast ease,
                transform $duration-fast ease;
        }

        &-enter-from {
            transform: translateY(4px);
            opacity: 0;
        }

        &-leave-to {
            opacity: 0;
        }
    }
}
</style>
