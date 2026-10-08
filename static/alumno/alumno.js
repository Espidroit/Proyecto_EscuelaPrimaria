/* =========================================================
   La Isla de los Cuentos — interfaz de los chicos
   ========================================================= */
"use strict";

let CAT = null;        // catálogo (avatar, temas, tipos, medallas)
let ING = null;        // datos de la pantalla de ingreso
let P = null;          // perfil del chico
let ACTS = [];         // actividades disponibles
let TAREAS = [];       // tareas de la seño
let pantalla = "carga", sub = {}, J = null, R = null;

const ELOGIOS = ["¡Muy bien! 🎉", "¡Genial! ⭐", "¡Excelente! 🙌", "¡Así se hace! 📖", "¡Bravo! 👏", "¡Sos un genio! 💡", "¡Perfecto! 🌈"];
const ANIMOS = ["¡Casi! Probá otra vez 💪", "¡Vos podés! Intentá de nuevo 🙂", "Mmm, no es esa. ¡Seguí probando! 🌟"];
const ZONA_INFO = {
  cuento:    {cls: "g-cuento",    txt: "Leé y respondé"},
  oraciones: {cls: "g-oraciones", txt: "Armá oraciones"},
  rimas:     {cls: "g-rimas",     txt: "Escuchá y encontrá"},
  palabras:  {cls: "g-palabras",  txt: "Escribí con letras"},
};

/* ---------------- Voz, sonido y festejos ---------------- */
function callar() { Voz.callar(); $$(".frase.leyendo").forEach(f => f.classList.remove("leyendo")); }
function decir(t, fin) {
  Voz.preferida = P ? P.cfg.voz : "";
  Voz.hablar(t, {lenta: !!(P && P.cfg.voz_lenta), fin});
}
let actx = null;
function sonar(tipo) {
  if (P && !P.cfg.sonido) return;
  try {
    actx ||= new (window.AudioContext || window.webkitAudioContext)();
    const notas = {ok: [660, 880], no: [300, 240], fin: [523, 659, 784, 1047], compra: [880, 1175], clic: [520]}[tipo] || [600];
    notas.forEach((f, i) => {
      const o = actx.createOscillator(), g = actx.createGain();
      o.type = tipo === "no" ? "triangle" : "sine"; o.frequency.value = f;
      const t = actx.currentTime + i * .12;
      g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.16, t + .02); g.gain.exponentialRampToValueAtTime(.0001, t + .22);
      o.connect(g).connect(actx.destination); o.start(t); o.stop(t + .25);
    });
  } catch (e) { /* sin audio */ }
}
function confeti(n = 40) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const fx = $("#fx"), em = ["⭐", "🎉", "✨", "🌟", "🎈", "💛", "🪙"];
  for (let i = 0; i < n; i++) {
    const s = document.createElement("span"); s.className = "conf"; s.textContent = azar(em);
    s.style.left = Math.random() * 100 + "vw"; s.style.animationDuration = (1.6 + Math.random() * 1.6) + "s";
    s.style.animationDelay = Math.random() * .5 + "s"; fx.appendChild(s); setTimeout(() => s.remove(), 4000);
  }
}
function toast(t) {
  const d = document.createElement("div"); d.className = "toast"; d.textContent = t; document.body.appendChild(d);
  setTimeout(() => d.remove(), 2600);
}

/* ---------------- Navegación ---------------- */
function ir(p, extra) {
  callar(); $("#fx").innerHTML = "";
  pantalla = p; if (extra) sub = {...sub, ...extra};
  render(); window.scrollTo({top: 0});
}
function render() {
  const app = $("#app");
  app.classList.toggle("mayus", !!(P && P.cfg.mayus));
  const v = {carga: () => `<p class="center">Cargando…</p>`, ingreso: vIngreso, clave: vClave, inicio: vInicio, zona: vZona,
             leer: vLeer, jugar: vJugar, premio: vPremio, tareas: vTareas, perfil: vPerfil}[pantalla] || vInicio;
  app.innerHTML = `<div class="entra">${v()}</div>`;
  if (pantalla === "leer" && P.cfg.auto_leer && sub.autoLeer) { sub.autoLeer = false; setTimeout(leerTodo, 450); }
  if (pantalla === "jugar" && P.cfg.auto_leer && !J.leida) { J.leida = true; setTimeout(leerConsigna, 350); }
}
async function seguro(fn) {
  try { return await fn(); }
  catch (e) {
    if (e.status === 401) { P = null; ING = await api("/api/ingreso"); ir("ingreso"); toast("Tu sesión terminó. Entrá de nuevo 🙂"); }
    else toast(e.message);
    return null;
  }
}
async function cargarTodo() {
  [P, ACTS, TAREAS] = await Promise.all([api("/api/alumno/perfil"), api("/api/alumno/actividades"), api("/api/alumno/tareas")]);
}

/* =========================================================
   Ingreso
   ========================================================= */
function vIngreso() {
  const al = ING.alumnos;
  const grados = [...new Set(al.map(a => a.grado))];
  return `
  <div class="logo"><div class="isla flota">🏝️</div><h1>La Isla de los Cuentos</h1><p class="kid">¿Quién va a jugar hoy?</p></div>
  ${al.length ? grados.map(g => `
    ${grados.length > 1 ? `<h2 class="grado-tit">${g}.º grado</h2>` : ""}
    <div class="chicos">${al.filter(a => a.grado === g).map(a => `
      <button class="chico" data-act="elegirChico" data-id="${a.id}">${Avatar.svg(a.avatar, 96, {mascota: false})}<span>${esc(a.nombre)}</span></button>`).join("")}
    </div>`).join("")
  : `<div class="card vacio center"><div style="font-size:3rem">👩‍🏫</div><h2>¡Todavía no hay chicos en la isla!</h2>
     <p style="font-size:1.2rem">La seño tiene que agregarlos desde su espacio.</p></div>`}
  <p class="center" style="margin-top:34px"><a href="/docente" class="muted" style="font-weight:700">Espacio docente</a></p>`;
}
function vClave() {
  const a = sub.alumno, c = sub.clave || [];
  return `
  <div class="card clave-box">
    ${Avatar.svg(a.avatar, 130)}
    <h2 style="font-size:2rem;margin-top:6px">¡Hola, ${esc(a.nombre)}!</h2>
    <p class="kid" style="font-size:1.3rem;margin:6px 0 0">Tocá tus <b>3 dibujos secretos</b>.</p>
    <div class="slots-clave" id="slotsClave">${[0, 1, 2].map(i => `<span class="${c[i] ? "f pop" : ""}">${c[i] ? "⭐" : ""}</span>`).join("")}</div>
    <div class="teclado">${ING.dibujos.map(d => `<button data-act="dibujo" data-d="${d}" aria-label="Dibujo ${d}">${d}</button>`).join("")}</div>
    <div class="err" id="errClave" aria-live="assertive">${esc(sub.errClave || "")}</div>
    <div class="row" style="justify-content:center;margin-top:8px">
      <button class="btn blanco" data-act="volverIngreso">⬅️ Volver</button>
      <button class="btn blanco" data-act="borrarClave">✖ Borrar</button>
    </div>
  </div>`;
}

/* =========================================================
   Inicio: la isla
   ========================================================= */
function barraTop() {
  const n = P.nivel;
  return `
  <header class="top">
    <button class="yo" data-act="ir" data-p="perfil" aria-label="Ver mi perfil">
      ${Avatar.svg(P.avatar, 68)}
      <span><span class="nom">${esc(P.nombre)}</span><br><span class="niv">${n.i} Nivel ${n.num}: ${esc(n.n)}</span>
        <span class="xpbar" style="display:block"><i style="width:${n.maximo ? 100 : Math.round(n.en_nivel / n.por_nivel * 100)}%"></i></span></span>
    </button>
    <span class="pill oro" title="Monedas">🪙 ${P.monedas}</span>
    <span class="pill" title="Estrellas">⭐ ${P.estrellas}</span>
    <button class="btn blanco chico" data-act="ir" data-p="inicio" aria-label="Inicio">🏝️</button>
    <button class="btn blanco chico" data-act="salir">🚪 Salir</button>
  </header>`;
}
function vInicio() {
  const pend = TAREAS.filter(t => !t.entregada);
  const zonas = Object.entries(CAT.tipos).map(([k, t]) => {
    const l = ACTS.filter(a => a.tipo === k);
    if (!l.length) return "";
    const hechas = l.filter(a => a.estrellas).length;
    return `<button class="zona" data-act="zona" data-t="${k}">
      <div class="cab ${ZONA_INFO[k].cls}"><span class="flota">${t.i}</span></div>
      <div class="pie"><h3 class="kid">${esc(t.n)}</h3><p class="kid">${ZONA_INFO[k].txt} · ${hechas}/${l.length} ✅</p></div></button>`;
  }).join("");
  const saludo = pend.length
    ? `<div class="aviso-tarea"><span style="font-size:2rem">📝</span><span class="kid" style="flex:1"><b style="display:inline;font-size:1.2rem">La seño te dejó ${pend.length === 1 ? "una tarea" : pend.length + " tareas"}.</b></span>
       <button class="btn sol chico" data-act="ir" data-p="tareas">Ver tareas ➡️</button></div>`
    : `<span class="kid">Elegí una zona de la isla para jugar.</span>`;
  return barraTop() + `
  <section class="hero">
    <div class="flota">${Avatar.svg(P.avatar, 150)}</div>
    <div class="burbuja"><b class="kid">¡Hola, ${esc(P.nombre)}!</b>${saludo}</div>
  </section>
  <div class="zonas">
    ${zonas}
    <button class="zona" data-act="ir" data-p="tareas">${pend.length ? `<span class="badge">${pend.length}</span>` : ""}
      <div class="cab g-tareas"><span class="flota">📝</span></div><div class="pie"><h3 class="kid">Mis tareas</h3><p class="kid">Lo que dejó la seño</p></div></button>
    <button class="zona" data-act="ir" data-p="perfil">
      <div class="cab g-perfil">${Avatar.svg(P.avatar, 92)}</div><div class="pie"><h3 class="kid">Mi perfil</h3><p class="kid">Avatar, medallas y álbum</p></div></button>
  </div>`;
}

function vZona() {
  const t = CAT.tipos[sub.tipo];
  const l = ACTS.filter(a => a.tipo === sub.tipo);
  return barraTop() + `
  <div class="encab"><h2 class="kid">${t.i} ${esc(t.n)}</h2><button class="btn blanco" data-act="ir" data-p="inicio">⬅️ Volver a la isla</button></div>
  <div class="islas">${l.map((a, i) => `
    <button class="islita ${a.bloqueada ? "lock" : ""}" data-act="${a.bloqueada ? "bloqueada" : "abrir"}" data-id="${a.id}">
      <span class="num">${i + 1}</span>${a.en_tarea ? `<span class="tag">📝 Tarea</span>` : ""}
      <div class="em">${a.e}</div><div class="t kid">${esc(a.titulo)}</div>
      <div class="st" aria-label="${a.estrellas} estrellas">${"⭐".repeat(a.estrellas)}${"☆".repeat(3 - a.estrellas)}</div></button>`).join("")}
  </div>`;
}

/* =========================================================
   Preparar y jugar una actividad
   ========================================================= */
async function abrir(id, tareaId = null) {
  const act = await seguro(() => api("/api/alumno/actividad/" + encodeURIComponent(id)));
  if (!act) return;
  J = prepararJuego(act, tareaId);
  if (act.tipo === "cuento") { sub.autoLeer = true; ir("leer"); } else ir("jugar");
}
function prepararJuego(act, tarea) {
  const g1 = P.grado === 1;
  let items;
  if (act.tipo === "cuento") {
    items = act.preguntas.map(q => {
      if (q.t === "e") return {...q, ops: mezclar((g1 ? q.o.slice(0, 2) : q.o.slice(0, 3)).map((t, i) => ({t, ok: i === 0})))};
      if (q.t === "o") {
        let it = q.items;
        if (g1 && it.length > 3) it = [it[0], it[Math.floor(it.length / 2)], it[it.length - 1]];
        return {...q, items: it, pool: mezclar(it.map((t, i) => ({t, i})))};
      }
      return q;
    }).sort((a, b) => (a.t === "o") - (b.t === "o"));
  } else if (act.tipo === "oraciones") {
    items = act.items.map(it => { const pal = it.t.split(" "); return {...it, tema: "oraciones", pal, pool: mezclar(pal.map((w, i) => ({w, i})))}; });
  } else if (act.tipo === "rimas") {
    items = act.items.map(it => ({...it, tema: "rimas", ops: mezclar([{...it.c, ok: true}, ...it.x.slice(0, g1 ? 1 : 2).map(x => ({...x, ok: false}))])}));
  } else {
    items = act.items.map(it => ({...it, tema: "escritura", pool: mezclar(it.p.split("").map((l, i) => ({l, i})))}));
  }
  return {act, tipo: act.tipo, tarea, items, i: 0, err: 0, res: [], bloq: false, pos: 0, puestos: [], t0: Date.now(), leida: false};
}

function frasesDe(t) { return (t.match(/[^.!?…]+[.!?…]+[»"]?|[^.!?…]+$/g) || [t]).map(s => s.trim()).filter(Boolean); }
function vLeer() {
  const c = J.act;
  return `
  <div class="juego"><div class="card">
    <div class="cuento-em flota">${c.e}</div>
    <h2 class="cuento-tit kid">${esc(c.titulo)}</h2>
    <div class="tip kid">👀 Leé el cuento con atención. Tocá una oración para escucharla.</div>
    <p class="texto kid" id="texto">${frasesDe(c.texto).map((f, i) => `<span class="frase" data-act="leerFrase" data-i="${i}">${esc(f)}</span>`).join(" ")}</p>
    <div class="row" style="justify-content:center">
      <button class="btn blanco" data-act="leerTodo">🔊 Escuchar el cuento</button>
      <button class="btn blanco" data-act="callar">⏹️ Parar</button>
    </div>
    <div class="row" style="justify-content:center;margin-top:12px">
      <button class="btn blanco" data-act="salirJuego">⬅️ Volver</button>
      <button class="btn verde" data-act="empezarPreguntas">¡Ya lo leí! A las preguntas ➡️</button>
    </div>
  </div></div>`;
}
function leerTodo() {
  callar();
  const spans = $$("#texto .frase"); let i = 0;
  const sig = () => {
    spans.forEach(s => s.classList.remove("leyendo"));
    if (i >= spans.length || pantalla !== "leer") return;
    const s = spans[i++]; s.classList.add("leyendo"); decir(s.textContent, sig);
  };
  sig();
}

function etiquetasOrden(n) {
  return Array.from({length: n}, (_, i) => i === 0 ? "1️⃣ Principio" : i === n - 1 ? `${n}️⃣ Final` : `${i + 1}️⃣ Después`);
}
function vJugar() {
  const q = J.items[J.i];
  const T = CAT.temas[q.tema] || CAT.temas.detalles;
  const puntos = J.items.map((_, k) => k < J.i ? `<i class="${J.res[k].primer ? "ok" : "med"}"></i>` : k === J.i ? `<i class="ya"></i>` : `<i></i>`).join("");
  let cuerpo = "";
  const parlante = `<button class="btn blanco chico" data-act="leerConsigna" aria-label="Escuchar">🔊</button>`;
  if (J.tipo === "cuento") {
    if (q.t === "e") {
      cuerpo = `<p class="q kid">${esc(q.p)} ${parlante}</p>
        <div class="opts">${q.ops.map((o, k) => `<button class="opt kid" data-act="elegir" data-k="${k}">${esc(o.t)}</button>`).join("")}</div>`;
    } else if (q.t === "vf") {
      cuerpo = `<p class="q kid">¿Es verdad lo que dice esta oración? ${parlante}</p>
        <p class="q kid" style="background:#fff;border:3px solid var(--ink);border-radius:16px;padding:12px 16px;margin-top:0">«${esc(q.p)}»</p>
        <div class="opts dos"><button class="opt kid" data-act="vf" data-v="1"><span class="big">👍</span>Sí, es verdad</button><button class="opt kid" data-act="vf" data-v="0"><span class="big">👎</span>No, no es así</button></div>`;
    } else {
      const et = etiquetasOrden(q.items.length);
      cuerpo = `<p class="q kid">¿En qué orden pasaron las cosas? Tocá lo que pasó primero. ${parlante}</p>
        <div class="slots">${q.items.map((_, k) => `<div class="slot ${k < J.pos ? "f" : ""}" id="sl${k}"><b>${et[k]}</b><span class="kid">${k < J.pos ? esc(q.items[k]) : ""}</span></div>`).join("")}</div>
        <div class="pool">${q.pool.map((o, k) => `<button class="pieza kid" data-act="pieza" data-k="${k}" ${o.i < J.pos ? "disabled" : ""}>${esc(o.t)}</button>`).join("")}</div>`;
    }
  } else if (J.tipo === "oraciones") {
    cuerpo = `<div class="pic">${q.e}</div><p class="q kid center">Tocá las palabras en orden para armar la oración. ${parlante}</p>
      <div class="linea" id="linea">${J.puestos.map(w => `<span class="puesta kid">${esc(w)}</span>`).join("")}</div>
      <div class="fichas">${q.pool.map((o, k) => `<button class="ficha kid" data-act="palabra" data-k="${k}">${esc(o.w)}</button>`).join("")}</div>`;
  } else if (J.tipo === "rimas") {
    cuerpo = `<div class="pic">${q.e}</div><div class="palabra-grande kid">${esc(q.p)}</div>
      <p class="q kid center">¿Qué palabra rima con <u>${esc(q.p)}</u>? ${parlante}</p>
      <div class="opts" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr))">${q.ops.map((o, k) => `<button class="opt kid" style="text-align:center" data-act="rima" data-k="${k}"><span class="big">${o.e}</span>${esc(o.t)}</button>`).join("")}</div>`;
  } else {
    cuerpo = `<div class="pic">${q.e}</div><p class="q kid center">Tocá las letras en orden para escribir la palabra. ${parlante}</p>
      <div class="casillas">${q.p.split("").map((_, k) => `<div class="casilla ${k < J.pos ? "f" : ""}" id="cs${k}">${k < J.pos ? esc(q.p[k]) : ""}</div>`).join("")}</div>
      <div class="fichas">${q.pool.map((o, k) => `<button class="letra" data-act="letra" data-k="${k}">${esc(o.l)}</button>`).join("")}</div>`;
  }
  return `
  <div class="juego"><div class="card">
    <div class="jbar"><div class="puntos" aria-label="Paso ${J.i + 1} de ${J.items.length}">${puntos}</div><span class="tema-chip kid">${T.i} ${esc(T.kid)}</span></div>
    ${cuerpo}
    <div class="msg kid" id="msg" aria-live="polite"></div>
    ${J.tipo === "cuento" ? `<div class="row" style="justify-content:center;margin-top:8px"><button class="btn blanco chico" data-act="mirar">📖 Mirar el cuento</button></div>
      <div class="mirar kid hidden" id="mirar"><b>${esc(J.act.titulo)}</b><br>${esc(J.act.texto)}</div>` : ""}
  </div>
  <div class="center" style="margin-top:16px"><button class="btn blanco chico" data-act="salirJuego">⬅️ Salir</button></div></div>`;
}
function leerConsigna() {
  const q = J.items[J.i]; callar();
  if (J.tipo === "cuento") {
    if (q.t === "e") decir(q.p + ". " + q.ops.map(o => o.t).join(". ¿O "));
    else if (q.t === "vf") decir("¿Es verdad lo que dice esta oración? " + q.p);
    else decir("¿En qué orden pasaron las cosas? Tocá lo que pasó primero.");
  } else if (J.tipo === "oraciones") decir(q.t);
  else if (J.tipo === "rimas") decir("¿Qué palabra rima con " + q.p + "? " + q.ops.map(o => o.t).join(", "));
  else decir(q.p);
}
function marcar(ok) {
  const q = J.items[J.i], T = CAT.temas[q.tema] || CAT.temas.detalles;
  if (ok) {
    if (J.bloq) return; J.bloq = true;
    const primer = J.err === 0;
    J.res.push({idx: q.idx, intentos: J.err + 1, primer});
    sonar("ok"); $("#msg").textContent = primer ? azar(ELOGIOS) : "¡Bien! Lo lograste 👍";
    if (primer) confeti(12);
    if (J.tipo === "oraciones") decir(q.t); if (J.tipo === "palabras") decir(q.p);
    setTimeout(() => {
      J.i++; J.err = 0; J.bloq = false; J.pos = 0; J.puestos = []; J.leida = false;
      if (J.i < J.items.length) ir("jugar"); else enviar();
    }, 1500);
  } else {
    J.err++; sonar("no");
    $("#msg").textContent = J.err >= 2 ? T.pista : azar(ANIMOS);
    if (J.err >= 2 && $("#mirar")) $("#mirar").classList.remove("hidden");
  }
}
function sacudir(el) { el.classList.remove("shake"); void el.offsetWidth; el.classList.add("shake"); }

async function enviar() {
  $("#app").innerHTML = `<div class="card center juego"><div class="copa flota" style="font-size:4rem">⏳</div><h2>Guardando tus estrellas…</h2></div>`;
  const body = {actividad_id: J.act.id, tarea_id: J.tarea, segundos: Math.round((Date.now() - J.t0) / 1000),
                respuestas: J.res.map(r => ({idx: r.idx, intentos: r.intentos}))};
  const res = await seguro(() => api("/api/alumno/intento", {method: "POST", body}));
  if (!res) return;
  R = res;
  await seguro(cargarTodo);
  sonar("fin"); confeti(70);
  ir("premio");
}

function vPremio() {
  const frase = R.estrellas === 3 ? "¡Lo hiciste perfecto!" : R.estrellas === 2 ? "¡Muy buen trabajo!" : "¡Terminaste! Si jugás otra vez, podés ganar más estrellas.";
  return `
  <div class="card premio">
    <div class="copa flota">🏆</div>
    <h2 class="cuento-tit kid">${frase}</h2>
    <div class="estrellas">${[1, 2, 3].map(n => `<span style="animation-delay:${n * .25}s">${n <= R.estrellas ? "⭐" : "☆"}</span>`).join("")}</div>
    <p class="kid" style="font-size:1.25rem;font-weight:700">Lo hiciste bien a la primera ${R.aciertos} de ${R.total} veces.</p>
    ${R.tarea ? `<div class="subio kid">📝 ¡Terminaste la tarea «${esc(R.tarea.titulo)}»! +${R.tarea.recompensa} 🪙 de premio</div>` : ""}
    ${R.subio ? `<div class="subio kid">🎊 ¡Subiste al nivel ${R.nivel.num}: ${R.nivel.i} ${esc(R.nivel.n)}!</div>` : ""}
    <div class="reco-grid">
      <div class="reco"><span class="e">🪙</span>+${R.monedas} monedas</div>
      <div class="reco"><span class="e">✨</span>+${R.monedas} de experiencia</div>
      ${R.sticker_nuevo ? `<div class="reco pop"><span class="e">${R.sticker_nuevo}</span>¡Figurita nueva para tu álbum!</div>` : ""}
      ${R.medallas.map(m => `<div class="reco pop"><span class="e">${m.i}</span>Medalla:<br><b>${esc(m.n)}</b></div>`).join("")}
    </div>
    <div class="row" style="justify-content:center">
      <button class="btn blanco" data-act="otraVez">🔁 Jugar otra vez</button>
      ${J.tarea ? `<button class="btn sol" data-act="ir" data-p="tareas">📝 Mis tareas</button>` : `<button class="btn verde" data-act="zona" data-t="${J.tipo}">🏝️ Seguir jugando</button>`}
      <button class="btn violeta" data-act="ir" data-p="perfil">🎨 Mi perfil</button>
      <button class="btn blanco" data-act="ir" data-p="inicio">🏝️ Inicio</button>
    </div>
  </div>`;
}

/* =========================================================
   Tareas
   ========================================================= */
function vTareas() {
  const pend = TAREAS.filter(t => !t.entregada), hechas = TAREAS.filter(t => t.entregada);
  const hoy = new Date().toISOString().slice(0, 10);
  const tarjeta = t => {
    const urge = t.fecha_limite && t.fecha_limite <= hoy && !t.entregada;
    return `
    <article class="card tarea ${t.entregada ? "hecha-t" : ""}">
      <div class="cab-t"><h3 class="kid">${t.entregada ? "✅" : "📝"} ${esc(t.titulo)}</h3>
        ${t.fecha_limite ? `<span class="fecha ${urge ? "urge" : ""}">📅 Para el ${fechaCorta(t.fecha_limite)}</span>` : ""}
        <span class="fecha">🪙 +${t.recompensa}</span></div>
      ${t.consigna ? `<div class="seno"><span class="cara">👩‍🏫</span><span class="kid" style="flex:1"><b>La seño dice:</b> ${esc(t.consigna)}</span>
        <button class="btn blanco chico" data-act="leerTexto" data-t="${esc(t.consigna)}" aria-label="Escuchar">🔊</button></div>` : ""}
      <div class="lista-act">${t.actividades.map(a => `
        <div class="act-t ${a.estrellas ? "hecha" : ""}"><span class="e">${a.e}</span>
          <span class="n kid">${esc(a.titulo)}<br><small class="muted">${CAT.tipos[a.tipo].i} ${esc(CAT.tipos[a.tipo].n)}</small></span>
          ${a.estrellas ? `<span style="font-size:1.3rem">${"⭐".repeat(a.estrellas)}</span><button class="btn blanco chico" data-act="abrirTarea" data-id="${a.id}" data-t="${t.id}">🔁</button>`
                        : `<button class="btn verde chico" data-act="abrirTarea" data-id="${a.id}" data-t="${t.id}">¡Empezar! ▶</button>`}
        </div>`).join("")}</div>
    </article>`;
  };
  return barraTop() + `
  <div class="encab"><h2 class="kid">📝 Mis tareas</h2><button class="btn blanco" data-act="ir" data-p="inicio">⬅️ Volver a la isla</button></div>
  ${pend.length ? pend.map(tarjeta).join("") : `<div class="card center"><div style="font-size:3.5rem">🎉</div><h3 class="kid" style="font-size:1.7rem">¡No tenés tareas pendientes!</h3><p class="kid" style="font-size:1.2rem">Podés seguir jugando en la isla.</p></div>`}
  ${hechas.length ? `<h3 class="kid" style="font-size:1.5rem;margin:26px 0 12px">✅ Tareas terminadas</h3>${hechas.map(tarjeta).join("")}` : ""}`;
}

/* =========================================================
   Perfil: avatar, armario, medallas y álbum
   ========================================================= */
function avatarConPrueba() {
  return sub.probando ? {...P.avatar, [sub.probando.cat]: sub.probando.v} : P.avatar;
}
function vPerfil() {
  sub.ptab ||= "armario"; sub.cat ||= "pelo";
  const ganadas = P.medallas.filter(m => m.fecha).length;
  const figus = P.album.filter(a => a.estrellas).length;
  let panel = "";
  if (sub.ptab === "armario") {
    const items = CAT.items.filter(i => i.cat === sub.cat);
    const swatch = ["piel", "colorPelo", "colorRopa", "fondo"].includes(sub.cat);
    panel = `
      <div class="cats">${CAT.categorias.map(c => `<button class="cat ${c.id === sub.cat ? "on" : ""}" data-act="cat" data-c="${c.id}">${c.i} ${esc(c.n)}</button>`).join("")}</div>
      <div class="items">${items.map(it => {
        const st = P.items[it.id], puesto = P.avatar[it.cat] === it.v, conf = sub.confirmar === it.id;
        const prev = swatch
          ? `<div class="swatch prev" style="background:${it.c1 ? `linear-gradient(${it.c1},${it.c2})` : it.color}"></div>`
          : `<span class="prev">${Avatar.svg({...P.avatar, [it.cat]: it.v}, 92, {mascota: it.cat === "mascota"})}</span>`;
        let estado;
        if (st.tiene) estado = puesto ? `<span class="estado" style="color:var(--blue2)">Puesto</span>` : `<span class="estado muted">Tocá para usar</span>`;
        else if (st.req) estado = `<span class="estado muted">🔒 ${esc(st.req)}</span>`;
        else estado = `<button class="btn ${conf ? "verde" : "sol"} chico" data-act="comprar" data-id="${it.id}" ${P.monedas < it.precio ? "disabled" : ""}>${conf ? "¿Seguro? ✔" : "🪙 " + it.precio}</button>`;
        return `<div class="it ${puesto ? "puesto" : ""} ${st.tiene ? "" : "no"}" data-act="item" data-id="${it.id}" role="button" tabindex="0">${prev}<span class="n kid">${esc(it.n)}</span>${estado}</div>`;
      }).join("")}</div>`;
  } else if (sub.ptab === "medallas") {
    panel = `<div class="medallas">${P.medallas.map(m => `<div class="med ${m.fecha ? "" : "no"}"><span class="e">${m.fecha ? m.i : "🔒"}</span><span class="n kid">${esc(m.n)}</span><small class="kid">${esc(m.d)}</small></div>`).join("")}</div>`;
  } else {
    panel = `<p class="kid muted" style="font-weight:700">Cada actividad que terminás te da una figurita. Tenés ${figus} de ${P.album.length}.</p>
      <div class="medallas">${P.album.map(a => `<div class="med ${a.estrellas ? "" : "no"}"><span class="e">${a.estrellas ? a.sticker : "❓"}</span><span class="n kid">${a.estrellas ? esc(a.titulo) : "???"}</span><small>${"⭐".repeat(a.estrellas)}</small></div>`).join("")}</div>`;
  }
  const n = P.nivel;
  return barraTop() + `
  <div class="perfil">
    <aside class="card vitrina">
      ${Avatar.svg(avatarConPrueba(), 250)}
      ${sub.probando ? `<div class="tip kid" style="margin-top:8px">👀 Así te quedaría. <button class="btn blanco chico" data-act="dejarProbar">Listo</button></div>` : ""}
      <h2 class="kid">${esc(P.nombre)}</h2>
      <span class="nivel-chip">${n.i} Nivel ${n.num} · ${esc(n.n)}</span>
      <div class="xpbar" style="width:100%;margin:6px 0"><i style="width:${n.maximo ? 100 : Math.round(n.en_nivel / n.por_nivel * 100)}%"></i></div>
      <small class="muted" style="font-weight:700">${n.maximo ? "¡Nivel máximo!" : `Te faltan ${n.por_nivel - n.en_nivel} ✨ para el nivel ${n.num + 1}`}</small>
      <div class="mini-stats">
        <div><b>🪙 ${P.monedas}</b>monedas</div><div><b>⭐ ${P.estrellas}</b>estrellas</div>
        <div><b>🏅 ${ganadas}</b>medallas</div><div><b>📒 ${figus}</b>figuritas</div>
      </div>
    </aside>
    <section class="card">
      <div class="tabs">
        <button class="tab ${sub.ptab === "armario" ? "on" : ""}" data-act="ptab" data-t="armario">🎨 Mi armario</button>
        <button class="tab ${sub.ptab === "medallas" ? "on" : ""}" data-act="ptab" data-t="medallas">🏅 Medallas</button>
        <button class="tab ${sub.ptab === "album" ? "on" : ""}" data-act="ptab" data-t="album">📒 Álbum</button>
      </div>
      ${panel}
    </section>
  </div>`;
}

/* =========================================================
   Acciones
   ========================================================= */
const A = {
  ir: el => { sub.probando = null; sub.confirmar = null; ir(el.dataset.p); },
  elegirChico: el => { sub.alumno = ING.alumnos.find(a => String(a.id) === el.dataset.id); sub.clave = []; sub.errClave = ""; ir("clave"); },
  volverIngreso: () => ir("ingreso"),
  borrarClave: () => { sub.clave = []; sub.errClave = ""; render(); },
  dibujo: async el => {
    if (sub.clave.length >= 3) return;
    sonar("clic"); sub.clave.push(el.dataset.d); sub.errClave = ""; render();
    if (sub.clave.length === 3) {
      try {
        await api("/api/alumno/ingresar", {method: "POST", body: {id: sub.alumno.id, clave: sub.clave}});
        await cargarTodo(); sonar("fin"); confeti(30); ir("inicio");
      } catch (e) {
        sonar("no"); sub.clave = []; sub.errClave = e.message; render(); sacudir($("#slotsClave"));
      }
    }
  },
  salir: async () => { await api("/api/alumno/salir", {method: "POST"}).catch(() => {}); P = null; ING = await api("/api/ingreso"); sub = {}; ir("ingreso"); },
  zona: el => { sub.tipo = el.dataset.t; ir("zona"); },
  bloqueada: el => { sonar("no"); sacudir(el); toast("Primero terminá la actividad anterior 🔒"); },
  abrir: el => abrir(el.dataset.id),
  abrirTarea: el => abrir(el.dataset.id, +el.dataset.t),
  otraVez: () => abrir(J.act.id, J.tarea),
  salirJuego: () => { const t = J.tarea; sub.tipo = J.tipo; J = null; if (t) ir("tareas"); else ir("zona"); },
  leerFrase: el => { callar(); el.classList.add("leyendo"); decir(el.textContent, () => el.classList.remove("leyendo")); },
  leerTodo: () => leerTodo(),
  callar: () => callar(),
  leerTexto: el => { callar(); decir(el.dataset.t); },
  empezarPreguntas: () => { J.t0 = J.t0 || Date.now(); ir("jugar"); },
  leerConsigna: () => leerConsigna(),
  mirar: () => $("#mirar").classList.toggle("hidden"),
  elegir: el => {
    if (J.bloq || el.classList.contains("no")) return;
    const o = J.items[J.i].ops[+el.dataset.k];
    el.classList.add(o.ok ? "ok" : "no", o.ok ? "pop" : "shake"); marcar(o.ok);
  },
  vf: el => {
    if (J.bloq || el.classList.contains("no")) return;
    const ok = (el.dataset.v === "1") === !!J.items[J.i].v;
    el.classList.add(ok ? "ok" : "no", ok ? "pop" : "shake"); marcar(ok);
  },
  rima: el => {
    if (J.bloq || el.classList.contains("no")) return;
    const o = J.items[J.i].ops[+el.dataset.k]; decir(o.t);
    el.classList.add(o.ok ? "ok" : "no", o.ok ? "pop" : "shake"); marcar(o.ok);
  },
  pieza: el => {
    const q = J.items[J.i], o = q.pool[+el.dataset.k];
    if (J.bloq) return;
    if (o.i === J.pos) {
      const sl = $("#sl" + J.pos); sl.classList.add("f", "pop"); sl.querySelector("span").textContent = o.t;
      el.disabled = true; J.pos++; sonar("clic");
      if (J.pos === q.items.length) marcar(true); else $("#msg").textContent = "¡Sí! ¿Y después qué pasó? 🤔";
    } else { sacudir(el); marcar(false); }
  },
  palabra: el => {
    const q = J.items[J.i], o = q.pool[+el.dataset.k];
    if (J.bloq || el.disabled) return;
    if (o.w.toLowerCase() === q.pal[J.pos].toLowerCase()) {
      const w = q.pal[J.pos];
      J.puestos.push(w); J.pos++; el.disabled = true; sonar("clic");
      const s = document.createElement("span"); s.className = "puesta kid pop"; s.textContent = w; $("#linea").appendChild(s);
      $("#msg").textContent = "";
      if (J.pos === q.pal.length) marcar(true);
    } else { sacudir(el); marcar(false); if (J.err < 2) $("#msg").textContent = "Esa palabra va después. ¡Probá otra! 🙂"; }
  },
  letra: el => {
    const q = J.items[J.i], o = q.pool[+el.dataset.k];
    if (J.bloq || el.disabled) return;
    if (o.l === q.p[J.pos]) {
      const c = $("#cs" + J.pos); c.textContent = o.l; c.classList.add("f", "pop");
      el.disabled = true; J.pos++; sonar("clic");
      if (J.pos === q.p.length) marcar(true);
    } else { sacudir(el); marcar(false); }
  },
  ptab: el => { sub.ptab = el.dataset.t; sub.probando = null; render(); },
  cat: el => { sub.cat = el.dataset.c; sub.confirmar = null; render(); },
  dejarProbar: () => { sub.probando = null; render(); },
  item: async el => {
    const it = CAT.items.find(i => i.id === el.dataset.id), st = P.items[it.id];
    sub.confirmar = null;
    if (!st.tiene) { sub.probando = {cat: it.cat, v: it.v}; render(); return; }
    sub.probando = null;
    const anterior = P.avatar[it.cat];
    P.avatar = {...P.avatar, [it.cat]: it.v}; sonar("clic"); render();
    const r = await seguro(() => api("/api/alumno/avatar", {method: "POST", body: {avatar: {[it.cat]: it.v}}}));
    if (!r) { P.avatar[it.cat] = anterior; render(); }
  },
  comprar: async (el, ev) => {
    ev.stopPropagation();
    const it = CAT.items.find(i => i.id === el.dataset.id);
    if (sub.confirmar !== it.id) { sub.confirmar = it.id; sub.probando = {cat: it.cat, v: it.v}; render(); return; }
    const r = await seguro(() => api("/api/alumno/comprar", {method: "POST", body: {item: it.id}}));
    sub.confirmar = null;
    if (!r) return;
    await seguro(() => api("/api/alumno/avatar", {method: "POST", body: {avatar: {[it.cat]: it.v}}}));
    P = await api("/api/alumno/perfil");
    sub.probando = null; sonar("compra"); confeti(30); toast(`¡Conseguiste: ${it.n}! 🎉`); render();
  },
};

document.addEventListener("click", e => {
  const el = e.target.closest("[data-act]");
  if (!el) return;
  const f = A[el.dataset.act];
  if (f) f(el, e);
});
document.addEventListener("keydown", e => {
  if ((e.key === "Enter" || e.key === " ") && e.target.matches("[role=button][data-act]")) { e.preventDefault(); e.target.click(); }
});

/* ---------------- Arranque ---------------- */
(async () => {
  try {
    CAT = await api("/api/catalogo");
    Avatar.init(CAT.items);
    ING = await api("/api/ingreso");
    if (ING.sesion) { await cargarTodo(); ir("inicio"); } else ir("ingreso");
  } catch (e) {
    $("#app").innerHTML = `<div class="card center" style="max-width:560px;margin:60px auto"><h2>No se pudo abrir la isla 😕</h2><p>${esc(e.message)}</p></div>`;
  }
})();
