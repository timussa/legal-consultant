<script setup>
defineProps({
    number: {type: Number, required: true},
    isActive: {type: Boolean, default: false},
    isRevealed: {type: Boolean, default: true},
});

const emit = defineEmits(['activate', 'deactivate', 'select']);
</script>

<template>
    <button
        type="button"
        :class="['ui-cite-badge', {'ui-cite-badge--active': isActive, 'ui-cite-badge--hidden': !isRevealed}]"
        :data-cite-anchor="number"
        :aria-label="`Источник ${number}`"
        :tabindex="isRevealed ? 0 : -1"
        @mouseenter="emit('activate', number)"
        @mouseleave="emit('deactivate', number)"
        @focus="emit('activate', number)"
        @blur="emit('deactivate', number)"
        @click="emit('select', number)"
    >
        {{ number }}
    </button>
</template>

<style lang="scss">
.ui-cite-badge {
    @include button-reset;
    @include flex-center;
    @include focus-ring;

    display: inline-flex;
    min-width: 20px;
    height: 20px;
    vertical-align: 2px;
    transition:
        transform $duration-fast $ease-out,
        background $duration ease,
        color $duration ease;
    color: $color-violet;
    border-radius: $radius-pill;
    background: $color-lavender;
    font-size: $font-size-2xs;
    font-weight: $font-weight-extrabold;
    animation: cite-pop $duration-slow $ease-back-out both;

    @include margin('x', 0.5);
    @include padding('x', 1.5);

    @include hover {
        transform: translateY(-1px);
    }

    &--active {
        color: $color-white;
        background: $gradient-thread;
        box-shadow: $shadow-raised;
    }

    &--hidden {
        visibility: hidden;
        animation: none;
    }
}
</style>
