<script setup>
import {BRAND_MARK} from '@/assets/images';

defineProps({
    size: {type: Number, default: 40},
});
</script>

<template>
    <img
        class="ui-brand-mark"
        :src="BRAND_MARK"
        :width="size"
        :height="size"
        alt=""
    />
</template>

<style lang="scss">
.ui-brand-mark {
    flex-shrink: 0;
    filter: drop-shadow(0 6px 10px rgba($color-indigo, 30%));
}
</style>
