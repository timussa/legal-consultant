<script setup>
import {onMounted, watchEffect} from 'vue';
import {storeToRefs} from 'pinia';
import {useDialogsStore} from '@/core/stores/dialogs';
import {useNotificationsStore} from '@/core/stores/notifications';
import {useSettingsStore} from '@/core/stores/settings';

import TheHeader from '@/components/Header/TheHeader.vue';
import TheSidebar from '@/components/Sidebar/TheSidebar.vue';
import ToastContainer from '@/components/Toast/ToastContainer.vue';

const dialogsStore = useDialogsStore();
const notificationsStore = useNotificationsStore();
const {settings} = storeToRefs(useSettingsStore());

watchEffect(() => {
    document.documentElement.classList.toggle('is-motion-reduced', settings.value.isMotionReduced);
});

onMounted(() => {
    dialogsStore.load();
    notificationsStore.load();
});
</script>

<template>
    <div class="default-layout">
        <a
            class="default-layout__skip"
            href="#main"
        >
            Перейти к содержимому
        </a>
        <TheHeader />
        <div class="default-layout__body">
            <TheSidebar />
            <main
                id="main"
                class="default-layout__main"
                tabindex="-1"
            >
                <slot />
            </main>
        </div>
        <ToastContainer />
    </div>
</template>

<style lang="scss">
.default-layout {
    overflow-x: clip;
    min-height: 100vh;

    background-color: $color-page;

    &__skip {
        position: fixed;
        z-index: $ui-index-modal;
        top: $indent-step * 2;
        left: $indent-step * 2;
        transform: translateY(-200%);
        color: $color-white;
        border-radius: $radius-md;
        background-color: $color-navy;
        font-weight: $font-weight-bold;
        text-decoration: none;

        @include padding('y', 2);
        @include padding('x', 4);

        &:focus {
            transform: none;
        }
    }

    &__body {
        display: flex;
        align-items: flex-start;
    }

    &__main {
        flex: 1;
        min-width: 0;
        outline: none;

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
