<script setup lang="ts">
import { onMounted, ref, shallowRef, watch } from 'vue';
import Wave from './Wave.vue';
import { WaveState } from '../model'
import Oscilloscope from './Oscilloscope.vue';

const props = defineProps<{
    waves: WaveState[]
}>()

// @ts-ignore (webkitAudioContext needed for compatibility?)
const audioCtx = new(window.AudioContext || window.webkitAudioContext)()

const sink = shallowRef<GainNode>()
const showScope = ref(false)

const startTime = 0
const frequency = ref(440)

function handleFrequencyUpdate(f: number, w: WaveState) {
    if (w.id == props.waves[0].id) {
        frequency.value = f
    }
}

watch(props, () => {
    const playingWaves = props.waves.reduce((a, b) => a + (b.playing ? 1 : 0), 0)
    if (sink.value) {
        sink.value.gain.value = playingWaves > 0 ? 1 / playingWaves : 0
    }
})

onMounted(() => {
    sink.value = audioCtx.createGain()
    sink.value.connect(audioCtx.destination)
})
</script>

<template>
    <div v-for="w in waves">
        <input type="checkbox" v-model="w.playing">
        <Wave 
            :playing="w.playing"
            :audio-ctx="audioCtx"
            :destination="sink"
            :gain="1"
            @update="(f) => handleFrequencyUpdate(f, w)"
        ></Wave>
    </div>
    <div>
        <label>
        <input type="checkbox" v-model="showScope">
        Show oscilloscope
        </label>
        <Oscilloscope v-show="showScope" :source="sink" :start-time="startTime" :frequency="frequency"/>
    </div>
</template>
