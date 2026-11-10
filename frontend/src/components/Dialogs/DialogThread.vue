<script setup>
defineProps({
    path: {type: String, default: ''},
    width: {type: Number, default: 0},
    height: {type: Number, default: 0},
});
</script>

<template>
    <svg
        class="dialog-thread"
        :width="width"
        :height="height"
        :viewBox="`0 0 ${width} ${height}`"
        aria-hidden="true"
    >
        <defs>
            <linearGradient
                id="dialog-thread-gradient"
                x1="0"
                y1="0"
                x2="1"
                y2="0"
            >
                <stop
                    class="dialog-thread__stop dialog-thread__stop--start"
                    offset="0"
                />
                <stop
                    class="dialog-thread__stop dialog-thread__stop--middle"
                    offset="0.6"
                />
                <stop
                    class="dialog-thread__stop dialog-thread__stop--end"
                    offset="1"
                />
            </linearGradient>
        </defs>
        <path
            v-if="path"
            :key="path"
            class="dialog-thread__glow"
            :d="path"
        />
        <path
            v-if="path"
            :key="`${path}-line`"
            class="dialog-thread__line"
            :d="path"
            pathLength="1"
        />
    </svg>
</template>

<style lang="scss">
.dialog-thread {
    position: absolute;
    z-index: $ui-index-overlay;
    top: 0;
    left: 0;
    overflow: visible;
    pointer-events: none;

    &__stop {
        &--start {
            stop-color: $color-navy;
        }

        &--middle {
            stop-color: $color-violet-bright;
        }

        &--end {
            stop-color: $color-orange-soft;
        }
    }

    &__glow,
    &__line {
        fill: none;
        stroke: url('#dialog-thread-gradient');
        stroke-linecap: round;
    }

    &__glow {
        opacity: 0.18;
        stroke-width: 8;
    }

    &__line {
        stroke-width: 2;
        stroke-dasharray: 1;
        stroke-dashoffset: 1;
        animation: thread-draw $duration-slow $ease-out forwards;
    }
}
</style>
