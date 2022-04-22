<script setup lang="ts">
import { reactive } from 'vue';
import Wave from './Wave.vue';
import { WaveState } from '../model'

defineProps<{
    waves: WaveState[]
}>()

</script>

<template>
    <div v-for="w in waves">
        <input type="checkbox" v-model="w.playing">
        <Wave :playing="w.playing"></Wave>
    </div>
</template>
