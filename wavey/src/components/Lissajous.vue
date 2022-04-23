<script setup lang="ts">
import { onMounted, ref } from 'vue';


var vert = `
attribute vec4 a_position;
varying vec4 v_color;

void main() {
  gl_Position = vec4(a_position.xy, 0.0, 1.0);
  v_color = gl_Position * 0.5 + 0.5;
}
`;
var frag = `
precision mediump float;

varying vec4 v_color;

uniform float time;
uniform vec2 freqUnscaled;

//void mainImage( out vec4 fragColor, in vec2 fragCoord )
void main()
{
    vec2 fragCoord = gl_FragCoord.xy;

    const float FREQ_X = 300.0;
    const float FREQ_Y = 200.0;

    vec2 iResolution = vec2(100, 100);
    
    float scale = 0.45 * min(iResolution.x, iResolution.y);
    vec2 uv = fragCoord/iResolution.xy;
    float x = fragCoord.x - iResolution.x * 0.5;
    float y = fragCoord.y - iResolution.y * 0.5;
    vec2 xy = vec2(x, y);

    //vec2 freq = 4.0 * normalize(vec2(FREQ_X, FREQ_Y));
    vec2 freq = 4.0 * normalize(freqUnscaled);
    vec3 col = vec3(0);
    
    const int LOOPS = 128;
    const float ISCALE = 2.0;
    
    for (int n = 0; n < LOOPS; n++) {
    float i = ISCALE * float(n) / float(LOOPS);
    float t = time - i*3.0;
    float fx = sin(freq.x*t) * scale;
    float fy = sin(freq.y*t) * scale;
    vec2 fxy = vec2(fx, fy);
    
    float gradx = cos(freq.x*t);
    float grady = cos(freq.y*t);
    float speed = length(vec2(gradx, grady));
    
    mat2 stretch = mat2(0.3, 0, 0, 1.5);
    mat2 rotate = mat2(gradx, grady, -grady, gradx)/speed;
    vec2 dist = fxy-xy;
    dist *= rotate;
    dist *= stretch;

    float strength = 1.0-smoothstep(0.02*scale, 0.075*scale, length(dist));
    col += strength * normalize(vec3(0.1,0.1,i*0.5)) * mix(0.8, 0.01, pow(i/ISCALE, 2.0));
    //col += strength * vec3(speed*0.01, speed*0.2, i*0.5) * (1.0/i);
    }

    // Output to screen
    gl_FragColor = vec4(col,1.0);
}

`;

const props = defineProps<{
    freq: [number, number],
}>()

const canvas = ref<HTMLCanvasElement|null>(null)
var gl: WebGLRenderingContext;
var program: WebGLProgram;
var timeLocation: WebGLUniformLocation
var freqLocation: WebGLUniformLocation
var positionAttributeLocation: number
var positionBuffer: WebGLBuffer

onMounted(() => {
    gl = canvas.value!.getContext('webgl')!;
    var vertexShader = createShader(gl, gl.VERTEX_SHADER, vert);
    var fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, frag);
    program = createProgram(gl, vertexShader, fragmentShader)!;
    timeLocation = gl.getUniformLocation(program, "time")!
    freqLocation = gl.getUniformLocation(program, "freqUnscaled")!
    positionAttributeLocation = gl.getAttribLocation(program, "a_position");
    positionBuffer = gl.createBuffer()!
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    var positions = [
    -1, -1,
    -1, 1,
    1, 1,
    1, 1,
    1, -1,
    -1, -1,
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
})

function render(time: number) {
  resizeCanvas(gl);
  gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
  gl.clearColor(0, 0, 0, 0);
  gl.clear(gl.COLOR_BUFFER_BIT);
  gl.useProgram(program);
  gl.enableVertexAttribArray(positionAttributeLocation);
  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
  // // Tell the attribute how to get data out of positionBuffer (ARRAY_BUFFER)
  var size = 2;          // 2 components per iteration
  var type = gl.FLOAT;   // the data is 32bit floats
  var normalize = false; // don't normalize the data
  var stride = 0;        // 0 = move forward size * sizeof(type) each iteration to get the next position
  var offset = 0;        // start at the beginning of the buffer
  gl.vertexAttribPointer(
      positionAttributeLocation, size, type, normalize, stride, offset)

  gl.uniform1f(timeLocation, time * 0.001);
  gl.uniform2f(freqLocation, props.freq[0], props.freq[1]);
  // // draw  
  var primitiveType = gl.TRIANGLES;
  var offset = 0;
  var count = 6;
  gl.drawArrays(primitiveType, offset, count);
  
  requestAnimationFrame(render);
}
requestAnimationFrame(render);

function resizeCanvas(gl: WebGLRenderingContext) {
  // not important for example
}

function createProgram(gl: WebGLRenderingContext, vs: WebGLShader, fs: WebGLShader) {
  const p = gl.createProgram()!
  gl.attachShader(p, vs);
  gl.attachShader(p, fs);
  gl.linkProgram(p);
  // should check for error here!
  return p;
}

function createShader(gl: WebGLRenderingContext, type: number, src: string) {
  const s = gl.createShader(type)!
  gl.shaderSource(s, src);
  gl.compileShader(s);
  // should check for error here
  return s;
}

</script>

<template>
<canvas ref="canvas" width="100" height="100"></canvas>
</template>