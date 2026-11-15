<script setup>
import {ref} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {ROUTE_NAMES} from '@/core/constants';
import {getErrorMessage} from '@/core/helpers/getErrorMessage';
import {useSessionStore} from '@/core/stores/session';

import UiBrandMark from '@/components/Ui/UiBrandMark.vue';
import UiButton from '@/components/Ui/UiButton.vue';

const route = useRoute();
const router = useRouter();
const sessionStore = useSessionStore();

const login = ref('');
const password = ref('');
const error = ref(/** @type {string | null} */ (null));
const isSubmitting = ref(false);

/** Возвращаем только на внутренние страницы приложения. */
function redirectTarget() {
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '';

    return redirect.startsWith('/') && !redirect.startsWith('//') ? redirect : {name: ROUTE_NAMES.home};
}

async function handleSubmit() {
    if (!login.value.trim() || !password.value) {
        error.value = 'Введите логин и пароль';
        return;
    }

    isSubmitting.value = true;
    error.value = null;

    try {
        await sessionStore.login(login.value.trim(), password.value);
        password.value = '';
        await router.replace(redirectTarget());
    } catch (loginError) {
        error.value = getErrorMessage(loginError);
    } finally {
        isSubmitting.value = false;
    }
}
</script>

<template>
    <main class="login-page">
        <form
            class="login-page__card"
            novalidate
            @submit.prevent="handleSubmit"
        >
            <div class="login-page__brand">
                <UiBrandMark :size="44" />
                <span class="login-page__brand-text">
                    <span class="login-page__brand-name">Юрассистент</span>
                    <span class="login-page__brand-caption">база знаний юристов</span>
                </span>
            </div>

            <h1 class="login-page__title">Вход</h1>

            <label class="login-page__field">
                <span class="login-page__label">Логин</span>
                <input
                    v-model="login"
                    class="login-page__input"
                    name="username"
                    autocomplete="username"
                    autocapitalize="none"
                    spellcheck="false"
                    required
                />
            </label>

            <label class="login-page__field">
                <span class="login-page__label">Пароль</span>
                <input
                    v-model="password"
                    class="login-page__input"
                    type="password"
                    name="password"
                    autocomplete="current-password"
                    required
                />
            </label>

            <p
                v-if="error"
                class="login-page__error"
                role="alert"
            >
                {{ error }}
            </p>

            <UiButton
                class="login-page__submit"
                type="submit"
                :is-disabled="isSubmitting"
            >
                {{ isSubmitting ? 'Входим…' : 'Войти' }}
            </UiButton>

            <p class="login-page__note">Учётные записи выдаёт руководитель юридического отдела.</p>
        </form>
    </main>
</template>

<style lang="scss">
.login-page {
    @include flex-center;

    min-height: 100vh;
    background-color: $color-page;

    @include padding('x', 4);

    &__card {
        @include card($radius-2xl);
        @include column($indent-step * 4);

        width: 100%;
        max-width: 400px;

        @include padding('y', 7);
        @include padding('x', 7);
    }

    &__brand {
        display: flex;
        align-items: center;
        gap: $indent-step * 3;
    }

    &__brand-text {
        @include column(0);
    }

    &__brand-name {
        color: $color-ink;
        font-size: $font-size-lg;
        font-weight: $font-weight-extrabold;
    }

    &__brand-caption {
        color: $color-ink-muted;
        font-size: $font-size-xs;
    }

    &__title {
        @include heading($font-size-2xl);
    }

    &__field {
        @include column($indent-step * 1.5);
    }

    &__label {
        color: $color-ink-soft;
        font-size: $font-size-sm;
        font-weight: $font-weight-bold;
    }

    &__input {
        height: 44px;
        color: $color-ink;
        border: 1px solid $color-line-strong;
        border-radius: $radius-md;
        background-color: $color-surface;
        font: inherit;
        font-size: $font-size-md;
        transition: border-color $duration ease;

        @include padding('x', 3);

        &:focus-visible {
            border-color: $color-action;
            outline: 2px solid $color-lavender-line;
            outline-offset: 1px;
        }
    }

    &__error {
        margin: 0;
        color: $color-peach-ink;
        border-radius: $radius-md;
        background-color: $color-peach-soft;
        font-size: $font-size-sm;

        @include padding('y', 2);
        @include padding('x', 3);
    }

    &__submit {
        width: 100%;
    }

    &__note {
        margin: 0;
        color: $color-ink-faint;
        font-size: $font-size-xs;
        text-align: center;
    }

    @include mobile {
        &__card {
            @include padding('y', 6);
            @include padding('x', 5);
        }
    }
}
</style>
