<script setup>
defineProps({
    size: {type: Number, default: 40},
});
</script>

<template>
    <span
        class="ui-brand-mark"
        :style="{'--brand-mark-size': `${size}px`}"
        aria-hidden="true"
    >
        §
    </span>
</template>

<style lang="scss">
.ui-brand-mark {
    flex-shrink: 0;
    width: var(--brand-mark-size);
    height: var(--brand-mark-size);
    color: $color-white;
    border-radius: calc(var(--brand-mark-size) * 0.3);
    background: $gradient-brand;
    box-shadow:
        inset 0 1px 0 rgba($color-white, 35%),
        $shadow-raised;
    font-size: calc(var(--brand-mark-size) * 0.55);
    font-weight: $font-weight-extrabold;
    line-height: 1;

    @include flex-center;
}
</style>
