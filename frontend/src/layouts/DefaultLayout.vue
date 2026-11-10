<script setup>
import {onMounted} from 'vue';
import {useDialogsStore} from '@/core/stores/dialogs';

import TheHeader from '@/components/Header/TheHeader.vue';
import TheSidebar from '@/components/Sidebar/TheSidebar.vue';
import ToastContainer from '@/components/Toast/ToastContainer.vue';

const dialogsStore = useDialogsStore();

onMounted(dialogsStore.load);
</script>

<template>
    <div class="default-layout">
        <TheHeader />
        <div class="default-layout__body">
            <TheSidebar />
            <main class="default-layout__main">
                <slot />
            </main>
        </div>
        <ToastContainer />
    </div>
</template>

<style lang="scss">
.default-layout {
    min-height: 100vh;

    @include soft-glows;

    &__body {
        display: flex;
        align-items: flex-start;
    }

    &__main {
        flex: 1;
        min-width: 0;

        @include padding('y', 6);
        @include padding('x', 7);
    }

    @include tablet {
        &__main {
            @include padding('y', 5);
            @include padding('x', 4);
        }
    }

    @include mobile {
        &__main {
            @include padding('bottom', 24);
        }
    }
}
</style>
