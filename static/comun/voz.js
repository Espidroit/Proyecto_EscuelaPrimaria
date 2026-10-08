/* =========================================================
   Lectura en voz alta.
   Elige automáticamente la voz en español más natural y suave
   que tenga la computadora (preferentemente femenina y "Natural"),
   o la voz que haya elegido la docente en Ajustes.
   ========================================================= */
"use strict";

const Voz = (() => {
  let preferida = "";
  const FEMENINAS = /(elena|dalia|paloma|elvira|salom|camila|valentina|ximena|helena|sabina|laura|lupe|paulina|m[oó]nica|marisol|luc[ií]a|isabela|catalina|beatriz|larissa|karla|renata|tania|yolanda|abril|estrella|irene|triana|vera|google español)/i;
  const MASCULINAS = /(pablo|ra[uú]l|jorge|tom[aá]s|[aá]lvaro|gonzalo|gerardo|enrique|diego|mateo|lorenzo|andr[eé]s|jos[eé]|carlos|emilio|federico|liberto|dar[ií]o|juan|alonso|arnau|saul|sa[uú]l|teo|nil|marcelo|yago)/i;

  const disponible = () => "speechSynthesis" in window;
  const voces = () => disponible() ? speechSynthesis.getVoices().filter(v => /^es/i.test(v.lang)) : [];
  const esNatural = v => /natural|online|neural/i.test(v.name);

  function puntaje(v) {
    let p = 0;
    if (esNatural(v)) p += 50;                       // voces neuronales: mucho menos robóticas
    if (/google/i.test(v.name)) p += 10;
    if (/es[-_]AR/i.test(v.lang)) p += 20;
    else if (/es[-_](419|MX|US|CO|CL|UY|PE)/i.test(v.lang)) p += 12;
    if (FEMENINAS.test(v.name)) p += 18;
    if (MASCULINAS.test(v.name)) p -= 40;
    return p;
  }
  function elegir() {
    const vs = voces();
    if (preferida) { const v = vs.find(x => x.name === preferida); if (v) return v; }
    return [...vs].sort((a, b) => puntaje(b) - puntaje(a))[0] || null;
  }
  function etiqueta(v) {
    const genero = MASCULINAS.test(v.name) ? "voz masculina" : FEMENINAS.test(v.name) ? "voz femenina" : "";
    return `${v.name.replace(/^Microsoft\s+/, "").replace(/\s*-\s*Spanish.*$/i, "")} (${v.lang}${genero ? " · " + genero : ""}${esNatural(v) ? " · natural ⭐" : ""})`;
  }
  function callar() { if (disponible()) speechSynthesis.cancel(); }
  function hablar(texto, {lenta = false, fin = null, voz = null} = {}) {
    if (!disponible()) { fin && fin(); return; }
    const u = new SpeechSynthesisUtterance(String(texto).replace(/[—«»]/g, " ").replace(/\s+/g, " ").trim());
    const v = voz || elegir();
    if (v) { u.voice = v; u.lang = v.lang; } else u.lang = "es-AR";
    const natural = v && esNatural(v);
    // Las voces naturales suenan mejor a su velocidad; las clásicas, un poco más lentas y agudas = más suaves.
    u.rate = natural ? (lenta ? .82 : .95) : (lenta ? .72 : .85);
    u.pitch = natural ? 1 : 1.1;
    u.volume = 1;
    if (fin) u.onend = fin;
    speechSynthesis.speak(u);
  }
  if (disponible()) speechSynthesis.getVoices();

  return {
    voces, elegir, etiqueta, hablar, callar, esNatural, puntaje,
    set preferida(n) { preferida = n || ""; },
    get preferida() { return preferida; },
  };
})();
