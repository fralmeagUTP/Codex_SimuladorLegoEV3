/* Control de audio del brick separado de la orquestacion de la simulacion. */
window.EV3SpeakerAudio = (() => {
  const MAX_DURATION_MS = 3000;
  let context = null;
  let unlocked = false;
  let lastSignature = "";

  function ensureContext() {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return null;
    context ||= new Ctx();
    if (unlocked && context.state === "suspended") context.resume().catch(() => {});
    return context;
  }

  function unlock() {
    unlocked = true;
    const audio = ensureContext();
    if (audio?.state === "suspended") audio.resume().catch(() => {});
  }

  function bindUnlockGesture() {
    const handler = () => {
      unlock();
      window.removeEventListener("pointerdown", handler, true);
      window.removeEventListener("keydown", handler, true);
    };
    window.addEventListener("pointerdown", handler, true);
    window.addEventListener("keydown", handler, true);
  }

  function handleSpeaker(speaker) {
    if (!speaker) {
      lastSignature = "";
      return;
    }
    const signature = [speaker.freq, speaker.duration_ms, speaker.volume, speaker.started_at_ms ?? speaker.tick]
      .map((value) => Math.round(Number(value ?? 0)))
      .join("|");
    if (!signature || signature === lastSignature) return;
    lastSignature = signature;
    const audio = ensureContext();
    const frequency = Number(speaker.freq);
    if (!audio || !unlocked || !Number.isFinite(frequency) || frequency <= 0) return;
    const duration = Math.max(10, Math.min(MAX_DURATION_MS, Number(speaker.duration_ms) || 120));
    const gain = Math.max(0, Math.min(1, (Number(speaker.volume) || 50) / 100)) * 0.2;
    const oscillator = audio.createOscillator();
    const volume = audio.createGain();
    const now = audio.currentTime;
    const stopAt = now + duration / 1000;
    oscillator.type = "square";
    oscillator.frequency.setValueAtTime(frequency, now);
    volume.gain.setValueAtTime(Math.max(0.0001, gain), now);
    oscillator.connect(volume);
    volume.connect(audio.destination);
    oscillator.start(now);
    oscillator.stop(stopAt);
    oscillator.onended = () => { oscillator.disconnect(); volume.disconnect(); };
  }

  return { bindUnlockGesture, handleSpeaker, unlock };
})();
