
export interface WaveState {
    id: number
    playing: boolean
    gain: number
}

let waveId = 0

export class WaveCollection {
    waves: WaveState[]
    totalGain: number

    constructor(gain?: number) {
        this.waves = []
        this.totalGain = gain == undefined ? 1.0 : gain
    }


    protected calculateGain() {
        return this.totalGain * this.waves.map(({ playing }) => Number(playing)).reduce((a, b) => a + b)
    }

    public addWave() {
        const w = { id: waveId++, playing: false, gain: this.calculateGain() }
        this.waves.push(w)
    }

    public setPlaying(index: number, playing: boolean) {
        this.waves[index].playing = playing
        const newGain = this.calculateGain()
        this.waves.forEach(x => x.gain = newGain)
    }
}
