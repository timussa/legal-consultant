<script setup>
import {useRoute} from 'vue-router';

import DefaultLayout from '@/layouts/DefaultLayout.vue';

const route = useRoute();
</script>

<template>
    <RouterView
        v-if="route.meta.isPublic"
        v-slot="{Component}"
    >
        <component :is="Component" />
    </RouterView>
    <DefaultLayout v-else-if="route.matched.length">
        <RouterView v-slot="{Component, route: pageRoute}">
            <Transition
                name="app__page"
                mode="out-in"
            >
                <component
                    :is="Component"
                    :key="pageRoute.name"
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
