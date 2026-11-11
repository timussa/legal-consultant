<script setup>
import {BookOpen, FileText, MessageSquareText, Settings, ShieldCheck} from 'lucide-vue-next';
import {useRoute} from 'vue-router';
import {DEFAULT_DOCUMENT_ID, ROUTE_NAMES} from '@/core/constants';
import {NAVIGATION_ITEMS} from '@/core/data/navigation';

const NAVIGATION_ICONS = Object.freeze({BookOpen, FileText, MessageSquareText, ShieldCheck});

const route = useRoute();

/**
 * @param {(typeof NAVIGATION_ITEMS)[number]} item
 * @returns {import('vue-router').RouteLocationRaw}
 */
function getTarget(item) {
    if (item.routeName === ROUTE_NAMES.document) {
        return {name: item.routeName, params: {documentId: DEFAULT_DOCUMENT_ID}};
    }

    return {name: item.routeName};
}

/** @param {(typeof NAVIGATION_ITEMS)[number]} item */
function isActive(item) {
    return route.name === item.routeName;
}
</script>

<template>
    <nav
        class="the-sidebar"
        aria-label="Разделы"
    >
        <RouterLink
            v-for="item in NAVIGATION_ITEMS"
            :key="item.id"
            :to="getTarget(item)"
            :class="['the-sidebar__item', {'the-sidebar__item--active': isActive(item)}]"
            :aria-label="item.ariaLabel"
            :aria-current="isActive(item) ? 'page' : undefined"
        >
            <span class="the-sidebar__icon">
                <component
                    :is="NAVIGATION_ICONS[item.icon]"
                    :size="22"
                    :stroke-width="1.8"
                    aria-hidden="true"
                />
            </span>
            <span class="the-sidebar__label">{{ item.label }}</span>
        </RouterLink>

        <RouterLink
            :to="{name: ROUTE_NAMES.settings}"
            :class="[
                'the-sidebar__item',
                'the-sidebar__item--bottom',
                {'the-sidebar__item--active': route.name === ROUTE_NAMES.settings},
            ]"
            :aria-current="route.name === ROUTE_NAMES.settings ? 'page' : undefined"
        >
            <span class="the-sidebar__icon">
                <Settings
                    :size="22"
                    :stroke-width="1.8"
                    aria-hidden="true"
                />
            </span>
            <span class="the-sidebar__label">Настройки</span>
        </RouterLink>
    </nav>
</template>

<style lang="scss">
.the-sidebar {
    $block: &;

    position: sticky;
    top: $header-height;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: $sidebar-width;
    height: calc(100vh - #{$header-height});
    border-right: 1px solid $color-line;
    background: $color-surface;
    gap: $indent-step * 2;

    @include padding('y', 4);

    &__item {
        @include button-reset;
        @include focus-ring;

        display: flex;
        flex-direction: column;
        align-items: center;
        width: 68px;
        transition: color $duration ease;
        color: $color-ink-muted;
        border-radius: $radius-lg;
        text-decoration: none;
        gap: $indent-step;

        @include padding('y', 2);

        @include hover {
            color: $color-navy;

            #{$block}__icon {
                background-color: $color-surface-muted;
            }
        }

        &--active {
            color: $color-navy;

            #{$block}__icon {
                color: $color-navy;

                &::before {
                    opacity: 1;
                }
            }
        }

        &--bottom {
            margin-top: auto;
        }
    }

    &__icon {
        @include flex-center;

        position: relative;
        width: 44px;
        height: 40px;
        transition:
            color $duration ease,
            background-color $duration ease,
            box-shadow $duration ease;
        border-radius: $radius-lg;
        isolation: isolate;

        &::before {
            position: absolute;
            z-index: -1;
            transition: opacity $duration ease;
            opacity: 0;
            border-radius: inherit;
            background-color: $color-lavender;
            content: '';
            inset: 0;
        }
    }

    &__label {
        font-size: $font-size-2xs;
        font-weight: $font-weight-bold;
    }

    @include mobile {
        position: fixed;
        z-index: $ui-index-header;
        top: auto;
        right: 0;
        bottom: 0;
        left: 0;
        flex-direction: row;
        justify-content: space-around;
        width: auto;
        height: auto;
        border-top: 1px solid $color-line;
        border-right: none;

        @include padding('y', 1.5);

        &__item--bottom {
            margin-top: 0;
        }
    }
}
</style>
