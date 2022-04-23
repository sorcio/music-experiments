<script setup lang="ts">
// import Wave from './components/Wave.vue';
import { ref } from 'vue';
import WaveSet from './components/WaveSet.vue';
import { WaveState } from './model'
import Foo from './components/Foo.vue';
import Lissajous from './components/Lissajous.vue';

const waves = ref<WaveState[]>([])

var id = 0;

</script>

<template>
  <button @click="waves.push({id: id++, playing: false})">+</button>
  <button @click="waves.pop()">-</button>
  <WaveSet :waves="waves"/>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
