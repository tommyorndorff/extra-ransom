/* Synthesized V12 engine sound. No audio files: oscillators + filtered noise.
   Must be started from a user gesture (browser autoplay rules). */
(function () {
  const Engine = {
    ctx: null, master: null, nodes: null, enabled: true, running: false, rpm: 0, load: 0,

    ensure() {
      if (this.ctx) return true;
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return false;
      let ctx;
      try { ctx = new AC(); } catch (e) { return false; }
      const master = ctx.createGain();
      master.gain.value = 0;
      const comp = ctx.createDynamicsCompressor();
      comp.threshold.value = -18; comp.ratio.value = 4;
      master.connect(comp).connect(ctx.destination);

      // Firing pulses: a V12 fires 6 times per crank revolution.
      const lp = ctx.createBiquadFilter();
      lp.type = "lowpass"; lp.frequency.value = 600; lp.Q.value = 0.8;
      const shaper = ctx.createWaveShaper();
      const curve = new Float32Array(1024);
      for (let i = 0; i < 1024; i++) { const x = i / 512 - 1; curve[i] = Math.tanh(2.4 * x); }
      shaper.curve = curve;

      const fire = ctx.createOscillator(); fire.type = "sawtooth";
      const fireG = ctx.createGain(); fireG.gain.value = 0.5;
      const sub = ctx.createOscillator(); sub.type = "square";
      const subG = ctx.createGain(); subG.gain.value = 0.22;
      const harm = ctx.createOscillator(); harm.type = "triangle";
      const harmG = ctx.createGain(); harmG.gain.value = 0.18;

      // Lumpy amplitude at crank rate gives the "burble".
      const lfo = ctx.createOscillator(); lfo.type = "sine";
      const lfoG = ctx.createGain(); lfoG.gain.value = 0.25;
      const am = ctx.createGain(); am.gain.value = 0.75;
      lfo.connect(lfoG).connect(am.gain);

      fire.connect(fireG).connect(shaper);
      sub.connect(subG).connect(shaper);
      harm.connect(harmG).connect(shaper);
      shaper.connect(am).connect(lp).connect(master);

      // Exhaust / prop wash noise.
      const len = ctx.sampleRate * 2;
      const buf = ctx.createBuffer(1, len, ctx.sampleRate);
      const d = buf.getChannelData(0);
      let last = 0;
      for (let i = 0; i < len; i++) { last = (last + 0.04 * (Math.random() * 2 - 1)) / 1.04; d[i] = last * 3.2; }
      const noise = ctx.createBufferSource(); noise.buffer = buf; noise.loop = true;
      const nf = ctx.createBiquadFilter(); nf.type = "bandpass"; nf.frequency.value = 400; nf.Q.value = 0.6;
      const ng = ctx.createGain(); ng.gain.value = 0.25;
      noise.connect(nf).connect(ng).connect(master);

      [fire, sub, harm, lfo, noise].forEach(n => n.start());
      this.ctx = ctx; this.master = master;
      this.nodes = { fire, sub, harm, lfo, lp, nf, ng, am };
      this.set(0, 0);
      return true;
    },

    set(rpm, load) {
      this.rpm = rpm; this.load = load;
      if (!this.ctx) return;
      const t = this.ctx.currentTime;
      const crank = Math.max(rpm, 1) / 60;     // revolutions per second
      const firing = crank * 6;                 // V12 firing frequency
      const n = this.nodes;
      n.fire.frequency.setTargetAtTime(firing, t, 0.08);
      n.sub.frequency.setTargetAtTime(firing / 2, t, 0.08);
      n.harm.frequency.setTargetAtTime(firing * 1.5, t, 0.08);
      n.lfo.frequency.setTargetAtTime(crank / 2, t, 0.1);
      n.lp.frequency.setTargetAtTime(260 + rpm * 0.32 + load * 900, t, 0.1);
      n.nf.frequency.setTargetAtTime(220 + rpm * 0.18, t, 0.1);
      n.ng.gain.setTargetAtTime(0.12 + load * 0.35, t, 0.1);
      const on = this.enabled && this.running && rpm > 50;
      const vol = on ? 0.06 + Math.min(1, rpm / 3000) * 0.12 + load * 0.08 : 0;
      this.master.gain.setTargetAtTime(vol, t, 0.12);
    },

    start() {
      if (!this.ensure()) return;
      if (this.ctx.state === "suspended") this.ctx.resume();
      this.running = true;
      this.set(this.rpm, this.load);
    },

    stop() { this.running = false; this.set(0, 0); },

    setEnabled(on) {
      this.enabled = on;
      if (on && this.ctx && this.ctx.state === "suspended") this.ctx.resume();
      this.set(this.rpm, this.load);
    },

    /* A short cough as the engine catches. */
    cough() {
      if (!this.ctx || !this.enabled) return;
      const ctx = this.ctx, t = ctx.currentTime;
      for (let i = 0; i < 3; i++) {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = "sawtooth"; o.frequency.value = 55 + i * 12;
        g.gain.setValueAtTime(0, t + i * 0.16);
        g.gain.linearRampToValueAtTime(0.25, t + i * 0.16 + 0.02);
        g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.16 + 0.15);
        o.connect(g).connect(this.master.context.destination);
        o.start(t + i * 0.16); o.stop(t + i * 0.16 + 0.2);
      }
    }
  };
  /* One salvo of six .50 cal guns: a short filtered noise burst. */
  Engine.gun = function () {
    if (!this.enabled) return;
    if (!this.ensure()) return;
    const ctx = this.ctx, t = ctx.currentTime;
    if (!this._gunBuf) {
      const n = Math.floor(ctx.sampleRate * 0.09), buf = ctx.createBuffer(1, n, ctx.sampleRate), d = buf.getChannelData(0);
      for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / n, 3);
      this._gunBuf = buf;
    }
    const src = ctx.createBufferSource(); src.buffer = this._gunBuf;
    const f = ctx.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = 700 + Math.random() * 300; f.Q.value = 0.7;
    const g = ctx.createGain(); g.gain.value = 0.5;
    src.connect(f).connect(g).connect(ctx.destination);
    src.start(t);
  };
  window.EngineAudio = Engine;
})();
