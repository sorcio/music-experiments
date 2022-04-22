<script setup lang="ts">
import { ref, computed, onMounted, watchEffect, watch } from 'vue'

const props = defineProps<{
    playing: boolean
}>()

const cents = ref<number>(0)
const minCents = -1200 * 2;
const maxCents = 1200 * 3;
const centerValue = 440;

function centsToHertz(c: number): number {
    return centerValue * Math.pow(2, c / 1200)
}

const modulo = (x: number, n: number) => ((x % n) + n) % n

const frequency = computed<number>({
    get() { return Math.round(centsToHertz(cents.value)) },
    set(newValue) {
        cents.value = Math.log2(newValue / 440) * 1200
    }
})

const note = computed<string>(() => {
    const scale = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    const absCents = cents.value - minCents
    const semitones = Math.round(absCents / 100)
    const detune = Math.round(absCents - semitones * 100)
    if (Math.abs(detune) < 20) {
        const octave = Math.trunc(semitones / 12)
        const index = modulo(semitones, 12)
        const noteName = scale[index]
        const prettyDetune = (detune == 0 ? '' : (detune > 0 ? ' +' + detune : ' ' + detune))
        return noteName + String(octave) +  prettyDetune
    }
    return ''
})

// @ts-ignore (webkitAudioContext needed for compatibility?)
const audioCtx = new(window.AudioContext || window.webkitAudioContext)()

class OscillatorState {
    private _oscillator?: OscillatorNode
    private _frequency?: number
    
    get frequency() { return this._frequency }
    
    set frequency(v: number|undefined) {
        if (v && this._oscillator) {
            this._oscillator.frequency.setValueAtTime(v, audioCtx.currentTime)
        }
        this._frequency = v;
    }

    get isPlaying(): boolean {
        return this._oscillator != undefined
    }

    play(this: OscillatorState) {
        if (this._frequency == undefined) {
            throw "frequency is not set"
        }
        const freq = this._frequency
        if (this._oscillator != undefined) {
            throw "already playing"
        }
        const oscillator = audioCtx.createOscillator()
        oscillator.type = 'sine'
        oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime)
        oscillator.connect(audioCtx.destination)
        oscillator.start()
        this._oscillator = oscillator
    }

    stop(this: OscillatorState) {
        if (this._oscillator == undefined) {
            throw "not playing"
        }
        this._oscillator.stop()
        this._oscillator = undefined
    }

}
let oscState = new OscillatorState();

watch(
    () => props.playing,
    (newValue, oldValue) => {
        if (newValue == oldValue) {
            return
        }
        if (newValue) {
            oscState.play()
        } else {
            oscState.stop()
        }
    }
), 

watchEffect(() => {
    console.log("setting frequency", frequency.value)
    oscState.frequency = frequency.value
})

onMounted(() => {
    cents.value = 0
})
</script>

<template>
    <input type="range"
    :min="minCents" :max="maxCents" step="1"
    v-model.number="cents" list="tickmarks">
    <datalist ref="tickmarks">
        <option value="-2400" label="A"></option>
        <option value="-1200" label="A"></option>
        <option value="0" label="A"></option>
        <option value="1200" label="A"></option>
        <option value="2400" label="A"></option>
        <option value="3600" label="A"></option>
    </datalist>
    <!-- <button v-if="playing" @click="stopPlaying">Stop</button>
    <button v-else="playing" @click="startPlaying">Play</button> -->
    <input v-model.lazy.number="frequency" type="number" step="1">
    <p>{{frequency}} Hz <span v-if="note">({{ note }})</span></p>
</template>

<style scoped>
input[type="range"] {
    width: 100%;
}
</style>
