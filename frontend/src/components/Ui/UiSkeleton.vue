<script setup>
defineProps({
    width: {type: String, default: '100%'},
    height: {type: String, default: '16px'},
    radius: {type: String, default: '8px'},
});
</script>

<template>
    <span
        class="ui-skeleton"
        :style="{'--skeleton-width': width, '--skeleton-height': height, '--skeleton-radius': radius}"
        aria-hidden="true"
    />
</template>

<style lang="scss">
.ui-skeleton {
    display: block;
    overflow: hidden;
    width: var(--skeleton-width);
    height: var(--skeleton-height);
    border-radius: var(--skeleton-radius);
    background-color: $color-surface-muted;
    background-image: linear-gradient(90deg, transparent, rgba($color-white, 70%), transparent);
    background-repeat: no-repeat;
    background-size: 40% 100%;
    animation: skeleton-shimmer 1.4s ease-in-out infinite;
}
</style>
