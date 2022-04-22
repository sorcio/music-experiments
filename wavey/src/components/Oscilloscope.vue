<script setup lang="ts">

import { ref, onMounted, watch } from 'vue'


const props = defineProps<{
    source?: AudioNode,
    startTime: number,
    frequency: number,
}>()

interface State {
    audioCtx: BaseAudioContext,
    source: AudioNode,
    analyser: AnalyserNode,
    bufferLength: number,
    dataArray: Float32Array,
}
var state: State | undefined

function configure() {
    if (!props.source) {
        state = undefined
        return
    }

    const { source } = props
    const audioCtx = source.context
    const analyser = audioCtx.createAnalyser()
    analyser.fftSize = 2048
    source.connect(analyser)

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Float32Array(bufferLength);

    state = {
        audioCtx, source, analyser, bufferLength, dataArray
    }
}

var canvas = ref<HTMLCanvasElement | null>(null)
var canvasCtx: CanvasRenderingContext2D | null = null
var offscreenCanvas = document.createElement("canvas")
offscreenCanvas.width = 600
offscreenCanvas.height = 300
var offscreenCtx = offscreenCanvas.getContext("2d")

var frameCount = 0;

function draw() {
    if (!canvasCtx || !canvas.value) return

    requestAnimationFrame(draw)

    // const skipFrame = (frameCount % 1 != 0)
    // frameCount++
    // if (skipFrame) return

    if (!state) return

    const el = canvas.value
    const {audioCtx, analyser, dataArray, bufferLength} = state

    analyser.getFloatTimeDomainData(dataArray)

    const framesInAPeriod = audioCtx.sampleRate / props.frequency
    const sliceWidth = el.width * 1.0 / bufferLength

    const sampleTime = audioCtx.sampleRate * (audioCtx.currentTime - props.startTime)
    const sampleOffset = Math.trunc(sampleTime % framesInAPeriod)

    const ctx = offscreenCtx!
    ctx.fillStyle = "rgb(200, 200, 200)"
    // ctx.globalAlpha = 0.8
    ctx.fillRect(sampleOffset * sliceWidth, 0, el.width, el.height)
    ctx.globalAlpha = 1

    ctx.fillStyle = "rgb(100, 0, 0)"
    for (var i = 1; i * framesInAPeriod < bufferLength; i++){
        ctx.fillRect(i*framesInAPeriod * sliceWidth - 1, 0, 2, 20)
    }

    // ctx.font = '20px sans-serif';
    // ctx.fillText(`${framesInAPeriod}/${bufferLength}`, 20, 20)

    ctx.lineWidth = 1
    ctx.strokeStyle = "rgb(160, 160, 160)"
    ctx.beginPath()
    ctx.moveTo(0, el.height / 2)
    ctx.lineTo(el.width, el.height / 2)
    ctx.stroke()

    ctx.lineWidth = 2
    ctx.strokeStyle = "rgb(0, 0, 0)"
    // ctx.beginPath()
    // for (var i = 0; i < sampleOffset; i++) {
    //     const x = i * sliceWidth

    //     const idx = (i + bufferLength - sampleOffset)
    //     const v = dataArray[idx]
    //     const y = (1 - v*0.8) * el.height / 2;

    //     if (i === 0) {
    //         ctx.moveTo(x, y)
    //     } else {
    //         ctx.lineTo(x, y)
    //     }
    // }
    // ctx.stroke()
    ctx.beginPath()
    for (var i = 0; i < bufferLength - sampleOffset; i++) {
        const x = (i + sampleOffset) * sliceWidth

        const idx = i
        const v = dataArray[idx]
        const y = (1 - v*0.8) * el.height / 2;
        ctx.lineTo(x, y)
    }

    // ctx.lineTo(el.width, el.height / 2)
    ctx.stroke()

    canvasCtx.drawImage(offscreenCanvas, 0, 0)
}

onMounted(() => {
    const el = canvas.value!
    canvasCtx = el.getContext("2d")
    draw()
})

watch(props, () => {
    configure()
})
</script>

<template>
    <canvas ref="canvas" width="600" height="300"></canvas>
</template>

<style scoped>
canvas {
    border: 1px black solid
}
</style>