/* =========================================================
   La Isla de los Cuentos — panel docente
   ========================================================= */
"use strict";

let CAT = null, YO = null;
const UI = {buscar: "", grado: "", claves: false, tareasTab: "activas", actFiltro: "", tab: {}};
let BORRADOR = null;

/* ---------------- Íconos ---------------- */
const IC = {
  panel: '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
  alumnos: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  tareas: '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  actividades: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
  temas: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  ajustes: '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
  mas: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  imprimir: '<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
  bajar: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
  salir: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
  ojo: '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
  juego: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
  candado: '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  libro: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  lupa: '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
};
const ic = (k, cls = "") => `<svg viewBox="0 0 24 24" class="${cls}" aria-hidden="true">${IC[k]}</svg>`;

/* ---------------- Avisos y ventanas ---------------- */
function toast(t, err = false) {
  const d = document.createElement("div"); d.className = "toast" + (err ? " err" : ""); d.textContent = t;
  $("#toasts").appendChild(d); setTimeout(() => d.remove(), 3400);
}
function modal({titulo, cuerpo, botones, ...opc}) {
  return new Promise(res => {
    const capa = $("#capa-modal");
    capa.innerHTML = `<div class="fondo"><div class="modal ${opc.ancho ? "ancho" : ""}" role="dialog" aria-modal="true" aria-label="${esc(titulo)}">
      <div class="mh">${esc(titulo)}</div><div class="mb">${cuerpo}</div>
      <div class="mf">${botones.map((b, i) => `<button class="btn ${b.cls || ""}" data-m="${i}">${esc(b.txt)}</button>`).join("")}</div></div></div>`;
    const cerrar = v => { capa.innerHTML = ""; document.removeEventListener("keydown", tecla); res(v); };
    const tecla = e => { if (e.key === "Escape") cerrar(null); };
    document.addEventListener("keydown", tecla);
    capa.querySelectorAll("[data-m]").forEach(b => b.addEventListener("click", () => {
      const bt = botones[+b.dataset.m];
      cerrar(bt.valor === "form" ? Object.fromEntries([...capa.querySelectorAll("[name]")].map(i => [i.name, i.value])) : bt.valor);
    }));
    capa.querySelector(".fondo").addEventListener("click", e => { if (e.target.classList.contains("fondo")) cerrar(null); });
    const f = capa.querySelector("input,textarea,select,.btn:last-child"); if (f) f.focus();
  });
}
const confirmar = (titulo, msg, ok = "Confirmar", peligro = false) =>
  modal({titulo, cuerpo: `<p style="margin:0">${msg}</p>`, botones: [{txt: "Cancelar", cls: "sec", valor: false}, {txt: ok, cls: peligro ? "peligro lleno" : "", valor: true}]});

async function llamar(fn, okMsg) {
  try { const r = await fn(); if (okMsg) toast(okMsg); return r; }
  catch (e) {
    if (e.status === 401) { YO = null; toast("Tu sesión se cerró por seguridad. Volvé a ingresar.", true); navegar(); }
    else toast(e.message, true);
    return null;
  }
}

/* ---------------- Estructura de la página ---------------- */
const NAV = [["panel", "Panel general", "panel"], ["alumnos", "Alumnos", "alumnos"], ["tareas", "Misiones", "tareas"],
             ["cuentos", "Cuentos", "libro"], ["actividades", "Actividades", "actividades"], ["temas", "Temas y contenidos", "temas"], ["ajustes", "Ajustes", "ajustes"]];
function shell(seccion, titulo, cuerpo, {migas = "", acciones = ""} = {}) {
  return `<div class="shell">
    <aside class="side">
      <div class="marca"><div class="logo">🏝️</div><div><b>Isla de los Cuentos</b><small>Panel docente</small></div></div>
      <nav class="nav" aria-label="Secciones">
        <div class="sep">Seguimiento</div>
        ${NAV.slice(0, 3).map(([r, t, i]) => `<a href="#/${r}" class="${seccion === r ? "on" : ""}">${ic(i)}${t}</a>`).join("")}
        <div class="sep">Contenidos</div>
        ${NAV.slice(3).map(([r, t, i]) => `<a href="#/${r}" class="${seccion === r ? "on" : ""}">${ic(i)}${t}</a>`).join("")}
        <div class="sep">Juego</div>
        <a href="/" target="_blank" rel="noopener">${ic("juego")}Abrir el juego</a>
      </nav>
      <div class="side-pie"><div class="quien">${esc(YO.nombre)}</div><div>@${esc(YO.usuario)} · ${nombreGrados(misGrados())}</div>
        <button class="btn sec chico" data-act="salir">${ic("salir")}Cerrar sesión</button></div>
    </aside>
    <div class="main">
      <header class="barra"><div style="flex:1;min-width:0">${migas ? `<div class="migas">${migas}</div>` : ""}<h1>${titulo}</h1></div>
        <div class="buscador" role="search">${ic("lupa")}<input type="search" id="busqueda" placeholder="Buscar alumno, cuento, misión…" aria-label="Buscar en el panel" autocomplete="off" aria-controls="resBusqueda"><kbd>Ctrl K</kbd>
          <div id="resBusqueda" class="res-busqueda hidden" role="listbox"></div></div>
        <div class="acciones">${acciones}</div></header>
      <div class="contenido">${cuerpo}</div>
    </div></div>`;
}
/* ---------------- Grados de la docente ---------------- */
const GRADOS = [1, 2, 3];
const misGrados = () => (YO && YO.grados) || GRADOS;
const nombreGrados = gs => gs.length === 1 ? `${gs[0]}.º grado` : gs.slice(0, -1).map(x => x + ".º").join(", ") + " y " + gs[gs.length - 1] + ".º grado";
const opcionesGrado = (sel = null) => misGrados().map(x => `<option value="${x}" ${x === sel ? "selected" : ""}>${x}.º grado</option>`).join("");
const checksGrados = (marcados = []) => `<div class="grados-check">${GRADOS.map(x => `<label class="chip-grado"><input type="checkbox" name="grados" value="${x}" ${marcados.includes(x) ? "checked" : ""}><span>${x}.º grado</span></label>`).join("")}</div>`;

function pintar(html) { $("#raiz").innerHTML = html; Graficos.activar(); window.scrollTo({top: 0}); }
const persona = (a, s = 32) => `<span class="persona">${Avatar.svg(a.avatar, s, {mascota: false})}<span>${esc(a.nombre)}</span></span>`;
const tipoN = t => CAT.tipos[t] ? `${CAT.tipos[t].i} ${CAT.tipos[t].n}` : t;
const temaTag = t => CAT.temas[t] ? `<span class="tag">${CAT.temas[t].i} ${esc(CAT.temas[t].n)}</span>` : "";
const estrellas = n => n ? "★".repeat(n) + `<span class="muted">${"★".repeat(3 - n)}</span>` : `<span class="muted">—</span>`;
const vacio = (t, s = "") => `<div class="vacio"><b>${t}</b>${s}</div>`;
const leyenda = `<div class="leyenda"><span><i style="background:var(--ok-bg);border:1px solid #9fd6b7"></i>✓ Logrado (80% o más)</span><span><i style="background:var(--warn-bg);border:1px solid #f0cf7c"></i>◐ En proceso (50–79%)</span><span><i style="background:var(--bad-bg);border:1px solid #f1aaa3"></i>! A reforzar (menos de 50%)</span></div>`;
const celda = v => {
  if (!v) return `<td class="cel cel-nd">—</td>`;
  const e = Graficos.nivel(v.pct);
  return `<td class="cel cel-${e.cls}" title="${v.n} respuestas">${e.ic} ${v.pct}%</td>`;
};

/* ---------------- Enrutador ---------------- */
async function navegar() {
  $("#capa-modal").innerHTML = "";
  INDICE = null;   // al cambiar de pantalla, el buscador vuelve a cargar los datos (por si algo cambió)
  if (!YO) {
    const est = await api("/api/docente/estado");
    if (!est.sesion) {
      if (location.hash === "#/registro" && est.registro) return vConfigurar(true, true);
      if (location.hash === "#/recuperar" && est.configurado) return vRecuperar();
      return est.configurado ? vIngreso(est) : vConfigurar(est.local);
    }
    YO = est.sesion;
  }
  if (YO.debe_cambiar) return vCambioObligatorio();
  const [r, a, b] = (location.hash.replace(/^#\/?/, "") || "panel").split("/");
  const rutas = {panel: pPanel, alumnos: pAlumnos, alumno: () => pAlumno(a, b), tarjetas: pTarjetas,
                 tareas: pTareas, tarea: () => pTarea(a), "tarea-nueva": pTareaNueva,
                 cuentos: pCuentos, actividades: pActividades, actividad: () => pActividad(a), "actividad-nueva": () => pEditor(a, null),
                 "actividad-editar": () => pEditor(null, a), temas: pTemas, ajustes: pAjustes};
  try { await (rutas[r] || pPanel)(); }
  catch (e) {
    if (e.status === 401) { YO = null; return navegar(); }
    pintar(shell("", "Ocurrió un problema", `<div class="panel"><div class="panel-b">${esc(e.message)}</div></div>`));
  }
}
window.addEventListener("hashchange", navegar);

/* =========================================================
   Buscador rápido (barra superior · Ctrl+K o «/»)
   Busca alumnos, cuentos, actividades, misiones, temas y secciones,
   sin importar mayúsculas ni tildes, y lleva directo a la pantalla.
   ========================================================= */
let INDICE = null, RES = [], SEL = 0;
const sinTildes = t => String(t || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
async function indiceBusqueda() {
  if (INDICE) return INDICE;
  const [alumnos, acts, misiones] = await Promise.all([api("/api/docente/alumnos"), api("/api/docente/actividades"), api("/api/docente/tareas")]);
  INDICE = [
    ...alumnos.map(a => ({g: "Alumnos", t: a.nombre, s: `${a.grado}.º grado${a.activo ? "" : " · inactivo"}${a.pct !== null ? ` · ${a.pct}% a la primera` : ""}`, h: `#/alumno/${a.id}`, av: a.avatar})),
    ...acts.map(a => ({g: a.tipo === "cuento" ? "Cuentos" : "Actividades", t: a.titulo, e: a.e,
                       s: `${tipoN(a.tipo)} · Nivel ${a.nivel}${a.estado === "borrador" ? " · borrador" : ""} · ${a.temas.map(x => CAT.temas[x] ? CAT.temas[x].n : x).join(", ")}`,
                       h: `#/actividad/${encodeURIComponent(a.id)}`})),
    ...misiones.map(t => ({g: "Misiones", t: t.titulo, e: "🎯", s: `${t.destino_n} · ${t.entregadas}/${t.asignados} terminaron${t.archivada ? " · archivada" : ""}`, h: `#/tarea/${t.id}`})),
    ...Object.values(CAT.temas).map(t => ({g: "Temas", t: t.n, e: t.i, s: t.area, h: "#/temas"})),
    ...[...NAV, ["tarea-nueva", "Nueva misión"], ["tarjetas", "Tarjetas de acceso"]].map(([r, t]) => ({g: "Secciones", t, e: "➡️", s: "Ir a la sección", h: "#/" + r})),
  ];
  INDICE.forEach(x => { x.n = sinTildes(x.t); x.todo = sinTildes(x.t + " " + x.s); });
  return INDICE;
}
async function buscar(q) {
  const caja = $("#resBusqueda"); if (!caja) return;
  const palabras = sinTildes(q).trim().split(/\s+/).filter(Boolean);
  if (!palabras.length) { caja.classList.add("hidden"); RES = []; return; }
  const idx = await indiceBusqueda();
  if (sinTildes($("#busqueda").value).trim() !== palabras.join(" ")) return;   // ya escribió otra cosa
  const orden = ["Alumnos", "Cuentos", "Actividades", "Misiones", "Temas", "Secciones"];
  RES = idx.filter(x => palabras.every(p => x.todo.includes(p)))
    .sort((a, b) => orden.indexOf(a.g) - orden.indexOf(b.g) || (b.n.startsWith(palabras[0]) - a.n.startsWith(palabras[0])) || a.n.localeCompare(b.n))
    .filter((x, i, l) => l.slice(0, i).filter(y => y.g === x.g).length < 5).slice(0, 14);
  SEL = 0;
  let grupo = "";
  caja.innerHTML = RES.length ? RES.map((x, i) => {
    const cab = x.g !== grupo ? `<div class="rb-grupo">${(grupo = x.g)}</div>` : "";
    return cab + `<a href="${x.h}" class="rb ${i === 0 ? "on" : ""}" role="option" data-i="${i}">
      <span class="rb-ic">${x.av ? Avatar.svg(x.av, 26, {mascota: false}) : x.e || ""}</span>
      <span class="rb-t"><b>${esc(x.t)}</b><small>${esc(x.s)}</small></span></a>`;
  }).join("") : `<div class="rb-vacio">No encontré nada con «${esc(q)}».</div>`;
  caja.classList.remove("hidden");
}
function marcarRes(i) {
  SEL = (i + RES.length) % RES.length;
  $$("#resBusqueda .rb").forEach((a, k) => a.classList.toggle("on", k === SEL));
  const el = $(`#resBusqueda .rb[data-i="${SEL}"]`); if (el) el.scrollIntoView({block: "nearest"});
}
let tBusq = null;
document.addEventListener("input", e => {
  if (e.target.id !== "busqueda") return;
  clearTimeout(tBusq); tBusq = setTimeout(() => buscar(e.target.value).catch(() => {}), 120);
});
document.addEventListener("keydown", e => {
  const enCampo = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
  if ((e.key === "k" && (e.ctrlKey || e.metaKey)) || (e.key === "/" && !enCampo)) {
    const b = $("#busqueda"); if (b) { e.preventDefault(); b.focus(); b.select(); }
    return;
  }
  if (e.target.id !== "busqueda") return;
  if (e.key === "ArrowDown" && RES.length) { e.preventDefault(); marcarRes(SEL + 1); }
  else if (e.key === "ArrowUp" && RES.length) { e.preventDefault(); marcarRes(SEL - 1); }
  else if (e.key === "Enter" && RES[SEL]) { e.preventDefault(); location.hash = RES[SEL].h; }
  else if (e.key === "Escape") { e.target.value = ""; $("#resBusqueda").classList.add("hidden"); e.target.blur(); }
});
document.addEventListener("focusout", e => {
  if (e.target.id === "busqueda") setTimeout(() => { const c = $("#resBusqueda"); if (c && !c.contains(document.activeElement)) c.classList.add("hidden"); }, 150);
});
document.addEventListener("focusin", e => { if (e.target.id === "busqueda" && e.target.value.trim()) buscar(e.target.value).catch(() => {}); });

/* =========================================================
   Ingreso y configuración inicial
   ========================================================= */
const campoPass = (name, label, auto, ayuda = "") => `
  <div class="campo"><label>${label}</label>
    <div class="pass-wrap"><input type="password" name="${name}" autocomplete="${auto}" maxlength="128" required>
      <button type="button" class="ver-pass" data-act="verPass" aria-label="Mostrar contraseña" title="Mostrar contraseña">${ic("ojo")}<span>Ver</span></button></div>
    ${ayuda ? `<small>${ayuda}</small>` : ""}</div>`;

function vIngreso(est = {}) {
  $("#raiz").innerHTML = `<div class="acceso"><form class="caja" data-form="ingresar" autocomplete="on">
    <div class="marca"><div class="logo">🏝️</div><div><b>Isla de los Cuentos</b><small class="muted">Panel docente</small></div></div>
    <h1>Ingresar</h1><p>Usá tu usuario y contraseña de docente.</p>
    <div class="campo"><label for="u">Usuario</label><input type="text" id="u" name="usuario" autocomplete="username" required autofocus></div>
    ${campoPass("password", "Contraseña", "current-password")}
    <div class="error-form" id="err"></div>
    <button class="btn" type="submit">Ingresar</button>
    <p style="margin:14px 0 0;text-align:center;font-size:13.5px"><a href="#/recuperar">¿Olvidaste tu contraseña?</a></p>
    ${est.registro ? `<p style="margin:16px 0 0;text-align:center;font-size:13.5px">¿Sos docente y todavía no tenés cuenta? <a href="#/registro">Crear mi cuenta</a></p>` : ""}
    <div class="candado">${ic("candado")}Por seguridad, la sesión se cierra sola después de 30 minutos sin uso.</div>
  </form></div>`;
}
function vRecuperar() {
  $("#raiz").innerHTML = `<div class="acceso"><form class="caja" data-form="recuperar" autocomplete="off">
    <div class="marca"><div class="logo">🏝️</div><div><b>Isla de los Cuentos</b><small class="muted">Recuperar el acceso</small></div></div>
    <h1>¿Olvidaste tu contraseña?</h1>
    <p>Escribí tu usuario y el <b>código de recuperación</b> que te mostró el panel al crear tu cuenta (empieza con ISLA-).</p>
    <div class="campo"><label>Usuario</label><input type="text" name="usuario" autocomplete="username" required></div>
    <div class="campo"><label>Código de recuperación</label><input type="text" name="codigo" placeholder="ISLA-XXXX-XXXX" required style="text-transform:uppercase;font-family:ui-monospace,monospace;letter-spacing:.06em"></div>
    <div class="f2">${campoPass("nueva", "Nueva contraseña", "new-password")}${campoPass("nueva2", "Repetir", "new-password")}</div>
    <div class="error-form" id="err"></div><button class="btn" type="submit">Cambiar contraseña y entrar</button>
    <div class="ayuda" style="margin-top:16px;font-size:13.5px"><b>¿No tenés el código?</b> Pedile a otra docente que entre al panel y toque <b>Ajustes → Docentes → Restablecer contraseña</b> en tu cuenta. Te va a dar una contraseña temporal.</div>
    <p style="margin:14px 0 0;text-align:center;font-size:13.5px"><a href="#/">Volver a ingresar</a></p>
  </form></div>`;
}
function vCambioObligatorio() {
  $("#raiz").innerHTML = `<div class="acceso"><form class="caja" data-form="cambioObligatorio" autocomplete="off">
    <div class="marca"><div class="logo">🏝️</div><div><b>Isla de los Cuentos</b><small class="muted">${esc(YO.nombre)}</small></div></div>
    <h1>Elegí una contraseña nueva</h1>
    <p>Entraste con una contraseña temporal. Antes de seguir, elegí una propia que solo vos sepas.</p>
    ${campoPass("nueva", "Nueva contraseña", "new-password", "Mínimo 8 caracteres, con letras y números.")}
    ${campoPass("nueva2", "Repetir contraseña", "new-password")}
    <div class="error-form" id="err"></div><button class="btn" type="submit">Guardar y entrar</button>
  </form></div>`;
}
// Muestra un código de recuperación (una sola vez) y espera a que la docente confirme que lo guardó
function mostrarCodigo(codigo, titulo = "Tu código de recuperación") {
  return modal({titulo, cuerpo: `
    <p style="margin-top:0">Si alguna vez te olvidás la contraseña, con este código la podés cambiar vos misma desde «¿Olvidaste tu contraseña?».</p>
    <div class="codigo-rec" id="codRec">${esc(codigo)}</div>
    <p class="muted" style="font-size:13px;margin-bottom:0"><b>Anotalo o sacale una foto ahora:</b> por seguridad no se vuelve a mostrar. Cada código sirve una sola vez; al usarlo te damos uno nuevo.</p>`,
    botones: [{txt: "Copiar", cls: "sec", valor: "copiar"}, {txt: "Ya lo guardé", valor: true}]}).then(async r => {
      if (r === "copiar") { try { await navigator.clipboard.writeText(codigo); toast("Código copiado."); } catch (e) { toast("No se pudo copiar: anotalo a mano.", true); } return mostrarCodigo(codigo, titulo); }
      return r;
    });
}

function vConfigurar(local, nueva = false) {
  $("#raiz").innerHTML = `<div class="acceso"><form class="caja" data-form="configurar" autocomplete="off">
    <div class="marca"><div class="logo">🏝️</div><div><b>Isla de los Cuentos</b><small class="muted">${nueva ? "Nueva cuenta docente" : "Primera configuración"}</small></div></div>
    <h1>${nueva ? "Crear mi cuenta docente" : "Crear la cuenta docente"}</h1>
    ${local ? `<p>${nueva ? "Vas a ver solo a los alumnos de los grados que elijas, con tu propio usuario y contraseña." : "Esta cuenta protege el panel donde vas a ver el progreso de los chicos y prepararles misiones."}</p>
    <div class="campo"><label>Tu nombre</label><input type="text" name="nombre" placeholder="Ej.: Seño Laura" required></div>
    <div class="campo"><label>Usuario</label><input type="text" name="usuario" placeholder="Ej.: laura" minlength="3" maxlength="30" pattern="[A-Za-z0-9._-]+" required><small>Sin espacios. Solo letras, números, punto o guion.</small></div>
    ${campoPass("password", "Contraseña", "new-password", "Mínimo 8 caracteres, con letras y números.")}
    ${campoPass("password2", "Repetir contraseña", "new-password")}
    <div class="campo"><label>¿De qué grados sos docente?</label>${checksGrados()}<small>Vas a ver solo a los alumnos de esos grados. Lo podés cambiar después en Ajustes.</small></div>
    <div class="error-form" id="err"></div><button class="btn" type="submit">Crear cuenta</button>
    ${nueva ? `<p style="margin:16px 0 0;text-align:center;font-size:13.5px"><a href="#/">Ya tengo cuenta, quiero ingresar</a></p>` : ""}`
    : `<p>La cuenta docente se crea desde la computadora donde está instalado el juego (abrí <b>http://localhost:5000/docente</b> en esa computadora).</p>`}
  </form></div>`;
}

/* =========================================================
   Panel general
   ========================================================= */
async function pPanel() {
  const d = await api("/api/docente/resumen");
  const k = d.kpis;
  const temasOn = d.temas;
  const cuerpo = `
  <div class="kpis">
    <div class="kpi"><div class="l">Alumnos activos</div><div class="v">${k.alumnos}</div><div class="s"><a href="#/alumnos">Ver la lista</a></div></div>
    <div class="kpi"><div class="l">Actividades · últimos 7 días</div><div class="v">${k.semana}</div><div class="s">cuentos y juegos terminados</div></div>
    <div class="kpi"><div class="l">Promedio del grupo</div><div class="v">${k.promedio === null ? "—" : k.promedio + "%"}</div><div class="s">respuestas correctas a la primera</div></div>
    <div class="kpi"><div class="l">Misiones en curso</div><div class="v">${k.tareas}</div><div class="s"><a href="#/tareas">Ver misiones</a></div></div>
  </div>
  <div class="grid g-7-5" style="margin-bottom:20px">
    <section class="panel"><div class="panel-h"><h2>Evolución del grupo</h2><span class="muted" style="font-size:12.5px">% de respuestas correctas a la primera, por semana</span></div>
      <div class="panel-b">${Graficos.linea(d.semanas)}</div></section>
    <section class="panel"><div class="panel-h"><h2>Para acompañar</h2><span class="estado ${d.alertas.length ? "e-warn" : "e-ok"}">${d.alertas.length}</span></div>
      <div class="panel-b sin">${d.alertas.length ? d.alertas.slice(0, 8).map(a => `
        <div class="alerta" data-act="ir" data-h="#/alumno/${a.id}"><span class="ic">!</span><div style="flex:1"><b>${esc(a.nombre)}</b><div class="muted" style="font-size:13px">${esc(a.motivo)}</div>
          ${(a.temas || []).length ? `<div class="refuerzos">${a.temas.map(t => `<button class="btn sec chico" data-act="refuerzo" data-id="${a.id}" data-t="${t}" data-n="${esc(a.nombre)}">＋ Asignar refuerzo: ${esc(CAT.temas[t].n)}</button>`).join("")}</div>` : ""}</div></div>`).join("")
        : vacio("Todo en orden", "No hay alumnos con temas por debajo del 50% ni inactivos.")}</div></section>
  </div>
  <div class="grid g-7-5" style="margin-bottom:20px">
    <section class="panel"><div class="panel-h"><h2>Comprensión por tema · todo el grupo</h2></div>
      <div class="panel-b">${Graficos.barras(temasOn.map(t => ({n: t.n, i: t.i, pct: t.pct, cant: t.cant})))}
      <div style="margin-top:14px">${leyenda}</div></div></section>
    <section class="panel"><div class="panel-h"><h2>Misiones en curso</h2><a class="btn sec chico" href="#/tarea-nueva">${ic("mas")}Nueva</a></div>
      <div class="panel-b sin">${d.tareas.length ? `<table><tbody>${d.tareas.map(t => `
        <tr class="clic" data-act="ir" data-h="#/tarea/${t.id}"><td><b>${esc(t.titulo)}</b><div class="muted" style="font-size:12.5px">${t.fecha_limite ? (t.vencida ? "Venció el " : "Hasta el ") + fechaCorta(t.fecha_limite) : "Sin fecha límite"}</div></td>
        <td style="width:45%"><div class="progreso"><span class="pista"><i style="width:${t.asignados ? Math.round(t.entregadas / t.asignados * 100) : 0}%"></i></span><span class="num">${t.entregadas}/${t.asignados}</span></div></td></tr>`).join("")}</tbody></table>`
        : vacio("Sin misiones", "Creá una misión para que los chicos practiquen en el aula.")}</div></section>
  </div>
  <section class="panel"><div class="panel-h"><h2>Mapa del grupo por tema</h2>${leyenda}</div>
    <div class="panel-b sin">${d.alumnos.length ? `<div class="tabla-wrap"><table class="calor"><thead><tr><th>Alumno</th>${temasOn.map(t => `<th class="c" title="${esc(t.n)}">${t.i}<br>${esc(t.n)}</th>`).join("")}<th class="c">General</th><th>Última vez</th></tr></thead>
      <tbody>${d.alumnos.map(a => `<tr class="clic" data-act="ir" data-h="#/alumno/${a.id}"><td>${persona(a, 28)}</td>${temasOn.map(t => celda(a.temas[t.id])).join("")}
        ${celda(a.pct === null ? null : {pct: a.pct, n: ""})}<td class="muted">${haceCuanto(a.ultima)}</td></tr>`).join("")}</tbody></table></div>`
      : vacio("Todavía no hay alumnos", `<a href="#/alumnos">Agregá a tus alumnos</a> para empezar.`)}</div></section>
  <section class="panel"><div class="panel-h"><h2>Actividad reciente</h2></div>
    <div class="panel-b sin">${d.recientes.length ? d.recientes.map(r => `
      <div class="reciente"><span class="em">${r.e}</span><div class="q"><div><b>${esc(r.alumno)}</b> terminó <b>${esc(r.titulo)}</b>${r.tarea ? ` <span class="tag">🎯 misión</span>` : ""}</div>
      <div class="muted" style="font-size:12.5px">${fechaHora(r.fecha)} · ${r.aciertos}/${r.total} a la primera</div></div><span style="color:#e0a419">${estrellas(r.estrellas)}</span></div>`).join("")
      : vacio("Sin actividad todavía")}</div></section>`;
  pintar(shell("panel", "Panel general", cuerpo, {acciones: `<a class="btn" href="#/tarea-nueva">${ic("mas")}Nueva misión</a>`}));
}

/* =========================================================
   Alumnos
   ========================================================= */
async function pAlumnos() {
  const l = await api("/api/docente/alumnos");
  const filtrados = l.filter(a => (!UI.grado || String(a.grado) === UI.grado) && a.nombre.toLowerCase().includes(UI.buscar.toLowerCase()));
  const cuerpo = `
  <section class="panel">
    <div class="panel-h">
      <input type="search" placeholder="Buscar alumno…" value="${esc(UI.buscar)}" data-input="buscar" style="max-width:260px">
      ${misGrados().length > 1 ? `<select data-input="grado" style="max-width:170px"><option value="">Todos mis grados</option>${misGrados().map(x => `<option value="${x}" ${UI.grado === String(x) ? "selected" : ""}>${x}.º grado</option>`).join("")}</select>` : ""}
      <span style="flex:1"></span>
      <button class="btn sec chico" data-act="verClaves">${ic("ojo")}${UI.claves ? "Ocultar claves" : "Mostrar claves"}</button>
    </div>
    <div class="panel-b sin">${filtrados.length ? `<div class="tabla-wrap"><table><thead><tr><th>Alumno</th><th>Grado</th><th>Clave de dibujos</th><th class="r">Nivel</th><th class="r">Actividades</th><th>Promedio</th><th>Última actividad</th><th>Estado</th></tr></thead>
      <tbody>${filtrados.map(a => `<tr class="clic" data-act="ir" data-h="#/alumno/${a.id}">
        <td>${persona(a)}</td><td>${a.grado}.º</td><td><span class="clave ${UI.claves ? "" : "oculta"}" aria-label="${UI.claves ? "Clave" : "Clave oculta"}">${a.clave.join("")}</span></td>
        <td class="r num">${a.nivel}</td><td class="r num">${a.actividades}</td><td>${Graficos.pill(a.pct)}</td><td class="muted">${haceCuanto(a.ultima)}</td>
        <td>${a.activo ? `<span class="estado e-ok">Activo</span>` : `<span class="estado e-nd">Inactivo</span>`}</td></tr>`).join("")}</tbody></table></div>`
      : vacio(l.length ? "No hay coincidencias" : "Todavía no cargaste alumnos", l.length ? "" : "Tocá «Agregar alumnos». Cada chico recibe una clave de 3 dibujos para entrar al juego.")}</div>
  </section>
  <div class="ayuda"><b>¿Cómo entran los chicos?</b> En la pantalla del juego eligen su nombre y tocan sus 3 dibujos secretos. Imprimí las tarjetas de acceso para repartirlas. Si un chico se olvida su clave, podés verla acá o generar una nueva desde su ficha.</div>`;
  pintar(shell("alumnos", "Alumnos", cuerpo, {acciones: `<a class="btn sec" href="#/tarjetas">${ic("imprimir")}Tarjetas de acceso</a><button class="btn" data-act="nuevoAlumno">${ic("mas")}Agregar alumnos</button>`}));
}

async function pTarjetas() {
  const l = (await api("/api/docente/alumnos")).filter(a => a.activo);
  const cuerpo = `<p class="muted no-print">Recortá cada tarjeta y entregásela a cada chico. Con su nombre y estos 3 dibujos entran a la isla.</p>
    <div class="tarjetas">${l.map(a => `<div class="tarjeta">${Avatar.svg(a.avatar, 84, {mascota: false})}<h3>${esc(a.nombre)}</h3><small>${a.grado}.º grado</small>
      <div class="dib">${a.clave.join("")}</div><small>Mis dibujos secretos para entrar a<br><b>La Isla de los Cuentos</b> 🏝️</small></div>`).join("") || vacio("No hay alumnos activos")}</div>`;
  pintar(shell("alumnos", "Tarjetas de acceso", cuerpo, {migas: `<a href="#/alumnos">Alumnos</a> /`, acciones: `<button class="btn" data-act="imprimir">${ic("imprimir")}Imprimir</button>`}));
}

async function pAlumno(id, tab = "evolucion") {
  const a = await api("/api/docente/alumnos/" + id);
  const tabs = [["evolucion", "Evolución"], ["temas", "Por tema"], ["historial", "Historial"], ["tareas", "Misiones"], ["observaciones", `Observaciones (${a.observaciones.length})`], ["acceso", "Acceso y datos"]];
  let panel = "";
  if (tab === "evolucion") {
    const s = a.semanas;
    let resumen = "Todavía no hay suficientes datos para ver una tendencia.";
    if (s.length >= 2) {
      const dif = s[s.length - 1].pct - s[0].pct;
      resumen = dif > 4 ? `Mejoró <b class="t-sube">+${dif} puntos</b> desde la semana del ${fechaCorta(s[0].semana)}.`
              : dif < -4 ? `Bajó <b class="t-baja">${dif} puntos</b> desde la semana del ${fechaCorta(s[0].semana)}.`
              : `Se mantiene estable desde la semana del ${fechaCorta(s[0].semana)}.`;
    }
    const conDatos = a.temas.filter(t => t.n);
    panel = `<div class="grid g-7-5">
      <section class="panel"><div class="panel-h"><h2>Evolución semanal</h2></div><div class="panel-b"><p style="margin:0 0 12px">${resumen}</p>${Graficos.linea(s)}</div></section>
      <section class="panel"><div class="panel-h"><h2>Tendencia por tema</h2></div><div class="panel-b sin">${conDatos.length ? `<table><thead><tr><th>Tema</th><th>Estado</th><th class="r">Cambio</th></tr></thead><tbody>
        ${conDatos.map(t => `<tr><td>${t.i} ${esc(t.n_tema)}<div class="muted" style="font-size:12px">${t.n} respuestas</div></td><td>${Graficos.pill(t.pct)}</td>
        <td class="r">${t.tendencia === null ? `<span class="muted" title="Se necesitan al menos 6 respuestas">—</span>` : t.tendencia > 4 ? `<span class="tendencia t-sube">▲ +${t.tendencia}</span>` : t.tendencia < -4 ? `<span class="tendencia t-baja">▼ ${t.tendencia}</span>` : `<span class="tendencia t-igual">● estable</span>`}</td></tr>`).join("")}
        </tbody></table><p class="muted" style="font-size:12.5px;padding:10px 20px;margin:0">El cambio compara la primera mitad de sus respuestas con la segunda mitad.</p>` : vacio("Sin datos todavía")}</div></section></div>`;
  } else if (tab === "temas") {
    const bajos = a.temas.filter(t => t.pct !== null && t.pct < 60);
    panel = `<div class="grid g2">
      <section class="panel"><div class="panel-h"><h2>Resultados por tema</h2></div><div class="panel-b">${Graficos.barras(a.temas.map(t => ({n: t.n_tema, i: t.i, pct: t.pct, cant: t.n})))}<div style="margin-top:14px">${leyenda}</div></div></section>
      <div class="pila">
        <section class="panel"><div class="panel-h"><h2>Para trabajar con ${esc(a.nombre)}</h2></div><div class="panel-b">${bajos.length ? `<ul style="margin:0;padding-left:18px">${bajos.map(t => `<li style="margin-bottom:10px"><b>${esc(t.n_tema)}</b> (${t.pct}%): ${esc(t.obj)}<br><button class="btn sec chico" style="margin-top:6px" data-act="refuerzo" data-id="${a.id}" data-t="${t.id}" data-n="${esc(a.nombre)}">＋ Asignar refuerzo</button></li>`).join("")}</ul>` : `<span class="muted">No hay temas por debajo del 60%.</span>`}</div></section>
        <section class="panel"><div class="panel-h"><h2>Preguntas donde más se equivoca</h2></div><div class="panel-b sin">${a.errores.length ? `<table><tbody>${a.errores.map(e => `<tr><td>${esc(e.texto)}<div class="muted" style="font-size:12.5px">${e.e} ${esc(e.titulo)} · ${temaTag(e.tema)}</div></td><td class="r num">${e.veces}×</td></tr>`).join("")}</tbody></table>` : vacio("Sin errores registrados")}</div></section>
      </div></div>`;
  } else if (tab === "historial") {
    panel = `<section class="panel"><div class="panel-b sin">${a.intentos.length ? `<div class="tabla-wrap"><table><thead><tr><th>Fecha</th><th>Actividad</th><th>Tipo</th><th class="r">A la primera</th><th>Estrellas</th><th class="r">Tiempo</th><th>Misión</th></tr></thead><tbody>
      ${a.intentos.map(i => `<tr><td class="num">${fechaHora(i.fecha)}</td><td>${i.e} ${esc(i.titulo)}</td><td class="muted">${tipoN(i.tipo)}</td><td class="r num">${i.aciertos}/${i.total}</td><td style="color:#e0a419">${estrellas(i.estrellas)}</td><td class="r num">${Math.max(1, Math.round(i.segundos / 60))} min</td><td>${i.tarea ? esc(i.tarea) : `<span class="muted">—</span>`}</td></tr>`).join("")}
      </tbody></table></div>` : vacio("Todavía no jugó ninguna actividad")}</div></section>`;
  } else if (tab === "tareas") {
    const cls = {entregada: "e-ok", pendiente: "e-info", vencida: "e-bad"};
    panel = `<section class="panel"><div class="panel-b sin">${a.tareas.length ? `<table><thead><tr><th>Misión</th><th>Fecha límite</th><th>Avance</th><th>Estado</th></tr></thead><tbody>
      ${a.tareas.map(t => `<tr><td><b>${esc(t.titulo)}</b></td><td>${t.fecha_limite ? fechaCorta(t.fecha_limite) : "—"}</td><td class="num">${t.hechas}/${t.total} actividades</td><td><span class="estado ${t.tarde ? "e-warn" : cls[t.estado]}">${t.estado === "entregada" ? (t.tarde ? "Terminada fuera de término " : "Terminada ") + fechaCorta(t.entregada) : t.estado === "vencida" ? "Vencida" : "Pendiente"}</span></td></tr>`).join("")}
      </tbody></table>` : vacio("No tiene misiones asignadas")}</div></section>`;
  } else if (tab === "observaciones") {
    panel = `<div class="grid g-7-5"><section class="panel"><div class="panel-h"><h2>Registro de observaciones</h2></div><div class="panel-b">
      ${a.observaciones.length ? a.observaciones.map(o => `<div class="obs"><div class="f"><span>${fechaHora(o.fecha)}</span><button class="btn fantasma chico" data-act="borrarObs" data-id="${o.id}" data-al="${a.id}">Borrar</button></div><p>${esc(o.texto)}</p></div>`).join("")
        : `<p class="muted" style="margin:0">Todavía no hay observaciones. Usalas para registrar avances, dificultades o acuerdos con la familia.</p>`}
      </div></section>
      <section class="panel"><div class="panel-h"><h2>Nueva observación</h2></div><form class="panel-b" data-form="observacion" data-id="${a.id}">
        <div class="campo"><textarea name="texto" maxlength="1000" placeholder="Ej.: Hoy reconoció sola al protagonista y pudo contar el final del cuento con sus palabras." required></textarea></div>
        <button class="btn" type="submit">Guardar observación</button></form></section></div>`;
  } else {
    panel = `<div class="grid g2">
      <section class="panel"><div class="panel-h"><h2>Clave para entrar al juego</h2></div><div class="panel-b">
        <div style="font-size:44px;letter-spacing:10px;margin-bottom:8px">${a.clave.join("")}</div>
        <p class="muted" style="margin:0 0 14px">Tiene que tocar estos 3 dibujos en este orden.</p>
        <button class="btn sec" data-act="nuevaClave" data-id="${a.id}">Generar una clave nueva</button></div></section>
      <section class="panel"><div class="panel-h"><h2>Datos del alumno</h2></div><form class="panel-b" data-form="editarAlumno" data-id="${a.id}">
        <div class="f2"><div class="campo"><label>Nombre</label><input type="text" name="nombre" value="${esc(a.nombre)}" maxlength="40" required></div>
        <div class="campo"><label>Grado</label><select name="grado">${opcionesGrado(a.grado)}</select></div></div>
        <div class="interruptor" style="padding-top:0"><div class="t"><b>Activo</b><small>Si lo desactivás, no aparece en el juego ni en las estadísticas del grupo, pero se guarda su historial.</small></div>
          <label class="sw"><input type="checkbox" name="activo" ${a.activo ? "checked" : ""}><span></span></label></div>
        <button class="btn" type="submit">Guardar cambios</button></form></section>
      <section class="panel" style="grid-column:1/-1"><div class="panel-h"><h2>Zona de cuidado</h2></div><div class="panel-b acciones">
        <button class="btn peligro" data-act="reiniciarAlumno" data-id="${a.id}">Reiniciar progreso</button>
        <button class="btn peligro lleno" data-act="borrarAlumno" data-id="${a.id}">Eliminar alumno</button>
        <span class="muted" style="font-size:13px">Estas acciones no se pueden deshacer. Te recomendamos descargar una copia de seguridad antes (en Ajustes).</span></div></section></div>`;
  }
  const n = a.nivel;
  const cuerpo = `
  <section class="panel"><div class="panel-b"><div class="ficha-cab">
    ${Avatar.svg(a.avatar, 92)}
    <div class="datos"><h2>${esc(a.nombre)} ${a.activo ? "" : `<span class="estado e-nd">Inactivo</span>`}</h2>
      <div class="muted">${a.grado}.º grado · ${n.i} Nivel ${n.num} (${esc(n.n)}) · en la isla desde el ${fechaCorta(a.creado)}</div>
      <div class="mini-kpis"><div><b>${a.pct === null ? "—" : a.pct + "%"}</b>correctas a la primera</div><div><b>${a.actividades}</b>actividades distintas</div>
        <div><b>${a.respuestas}</b>respuestas</div><div><b>${a.estrellas}</b>estrellas</div><div><b>${a.medallas}</b>medallas</div><div><b>${a.minutos}</b>minutos de juego</div></div></div>
  </div></div></section>
  <nav class="pestanas">${tabs.map(([k, t]) => `<a href="#/alumno/${a.id}/${k}" class="${k === tab ? "on" : ""}">${t}</a>`).join("")}</nav>
  ${panel}`;
  pintar(shell("alumnos", esc(a.nombre), cuerpo, {migas: `<a href="#/alumnos">Alumnos</a> /`, acciones: `<button class="btn sec" data-act="imprimir">${ic("imprimir")}Imprimir</button>`}));
}

/* =========================================================
   Tareas
   ========================================================= */
async function pTareas() {
  const l = await api("/api/docente/tareas");
  const vis = l.filter(t => UI.tareasTab === "activas" ? !t.archivada : t.archivada);
  const cuerpo = `
  <div style="margin-bottom:16px" class="segmento"><button class="${UI.tareasTab === "activas" ? "on" : ""}" data-act="tareasTab" data-t="activas">Activas (${l.filter(t => !t.archivada).length})</button><button class="${UI.tareasTab === "archivadas" ? "on" : ""}" data-act="tareasTab" data-t="archivadas">Archivadas (${l.filter(t => t.archivada).length})</button></div>
  <section class="panel"><div class="panel-b sin">${vis.length ? `<div class="tabla-wrap"><table><thead><tr><th>Misión</th><th>Para</th><th>Actividades</th><th>Fecha límite</th><th style="width:22%">Terminaron</th></tr></thead><tbody>
    ${vis.map(t => `<tr class="clic" data-act="ir" data-h="#/tarea/${t.id}"><td><b>${esc(t.titulo)}</b><div class="muted" style="font-size:12.5px">Creada el ${fechaCorta(t.creada)} · premio ${t.recompensa} 🪙</div></td>
      <td>${esc(t.destino_n)}</td><td style="font-size:20px">${t.actividades.map(a => `<span title="${esc(a.titulo)}">${a.e}</span>`).join(" ")}</td>
      <td>${t.fecha_limite ? `${fechaCorta(t.fecha_limite)} ${t.vencida && !t.archivada ? `<span class="estado e-bad">Vencida</span>` : ""}` : `<span class="muted">—</span>`}</td>
      <td><div class="progreso"><span class="pista"><i style="width:${t.asignados ? Math.round(t.entregadas / t.asignados * 100) : 0}%"></i></span><span class="num">${t.entregadas}/${t.asignados}</span></div></td></tr>`).join("")}
    </tbody></table></div>` : vacio(UI.tareasTab === "activas" ? "No hay misiones activas" : "No hay misiones archivadas", UI.tareasTab === "activas" ? "Creá una misión eligiendo cuentos o juegos para que los chicos practiquen en clase." : "")}</div></section>
  <div class="ayuda"><b>¿Cómo funcionan las misiones?</b> Son actividades que elegís para que los chicos hagan <b>en clase</b> (el juego se usa solo en el aula). Las ven en «Mis misiones» con tu consigna. Cuando terminan todas las actividades, la misión queda cumplida y reciben las monedas de premio. Acá ves quién terminó y con qué resultado.</div>`;
  pintar(shell("tareas", "Misiones", cuerpo, {acciones: `<a class="btn" href="#/tarea-nueva">${ic("mas")}Nueva misión</a>`}));
}

async function pTareaNueva() {
  const [todasActs, alumnos] = await Promise.all([api("/api/docente/actividades"), api("/api/docente/alumnos")]);
  const acts = todasActs.filter(a => a.estado !== "borrador");
  const activos = alumnos.filter(a => a.activo);
  const manana = new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
  const grupos = Object.keys(CAT.tipos).map(t => {
    const l = acts.filter(a => a.tipo === t);
    return l.length ? `<h3 style="font-size:14px;margin:16px 0 8px">${tipoN(t)}</h3><div class="check-lista">${l.map(a => `
      <label class="check"><input type="checkbox" name="act" value="${a.id}" data-act="marcarCheck"><span class="em">${a.e}</span><span><b>${esc(a.titulo)}</b><br>
      <span class="muted" style="font-size:12.5px">Nivel ${a.nivel}${a.visible ? "" : " · oculta en la isla"}</span><br>${a.temas.map(temaTag).join("")}</span></label>`).join("")}</div>` : "";
  }).join("");
  const cuerpo = `<form data-form="tarea">
  <div class="grid g-7-5">
    <section class="panel"><div class="panel-h"><h2>1. Datos de la misión</h2></div><div class="panel-b">
      <div class="campo"><label>Título</label><input type="text" name="titulo" maxlength="80" placeholder="Ej.: Practicamos personajes" required></div>
      <div class="campo"><label>Consigna para los chicos</label><textarea name="consigna" maxlength="400" placeholder="Ej.: Leé el cuento con atención y pensá quién es el protagonista. ¡Vos podés!"></textarea><small>Los chicos pueden escucharla en voz alta.</small></div>
      <div class="f2"><div class="campo"><label>Fecha límite</label><input type="date" name="fecha_limite" value="${manana}" min="${new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10)}"></div>
      <div class="campo"><label>Premio al terminar (monedas)</label><input type="number" name="recompensa" min="0" max="200" step="1" value="30" required></div></div>
    </div></section>
    <section class="panel"><div class="panel-h"><h2>2. ¿Para quién es?</h2></div><div class="panel-b">
      ${[["todos", misGrados().length > 1 ? `Todos mis grados (${nombreGrados(misGrados())})` : `Todo ${nombreGrados(misGrados())}`],
         ...(misGrados().length > 1 ? misGrados().map(x => ["grado" + x, `Solo ${x}.º grado`]) : []), ["elegidos", "Algunos alumnos"]].map(([v, t], i) => `
        <label class="check" style="margin-bottom:8px"><input type="radio" name="destino" value="${v}" ${i === 0 ? "checked" : ""} data-act="destino"><span><b>${t}</b></span></label>`).join("")}
      <div id="elegidos" class="hidden" style="margin-top:10px"><div class="check-lista">${activos.map(a => `<label class="check"><input type="checkbox" name="alumno" value="${a.id}" data-act="marcarCheck"><span>${persona(a, 26)}</span></label>`).join("") || `<span class="muted">No hay alumnos activos.</span>`}</div></div>
    </div></section>
  </div>
  <section class="panel" style="margin-top:20px"><div class="panel-h"><h2>3. Actividades</h2><span class="muted" id="cuentaAct">0 elegidas</span></div><div class="panel-b">
    <p class="muted" style="margin:0">Elegí entre 1 y 12. Las actividades de una misión se habilitan para los chicos aunque estén bloqueadas u ocultas en la isla.</p>${grupos}</div></section>
  <div class="error-form" id="err"></div>
  <div class="acciones"><a class="btn sec" href="#/tareas">Cancelar</a><button class="btn" type="submit">Crear misión</button></div></form>`;
  pintar(shell("tareas", "Nueva misión", cuerpo, {migas: `<a href="#/tareas">Misiones</a> /`}));
}

async function pTarea(id) {
  const t = await api("/api/docente/tareas/" + id);
  const ent = t.alumnos.filter(a => a.entregada).length;
  const hoy = new Date().toISOString().slice(0, 10);
  const cuerpo = `
  <div class="kpis">
    <div class="kpi"><div class="l">Terminaron</div><div class="v">${ent}/${t.alumnos.length}</div><div class="s">${t.alumnos.length ? Math.round(ent / t.alumnos.length * 100) : 0}% del grupo asignado</div></div>
    <div class="kpi"><div class="l">Fecha límite</div><div class="v" style="font-size:22px">${t.fecha_limite ? fechaCorta(t.fecha_limite) : "—"}</div><div class="s">${t.fecha_limite && t.fecha_limite < hoy ? "Vencida" : "En curso"}</div></div>
    <div class="kpi"><div class="l">Para</div><div class="v" style="font-size:18px">${esc(t.destino_n)}</div><div class="s">Premio: ${t.recompensa} monedas</div></div>
  </div>
  ${t.consigna ? `<div class="ayuda"><b>Consigna:</b> ${esc(t.consigna)}</div>` : ""}
  <section class="panel"><div class="panel-h"><h2>Resultados por alumno</h2><span class="muted" style="font-size:12.5px">★ estrellas obtenidas · % de respuestas correctas a la primera</span></div>
    <div class="panel-b sin">${t.alumnos.length ? `<div class="tabla-wrap"><table><thead><tr><th>Alumno</th>${t.actividades.map(a => `<th class="c">${a.e}<br>${esc(a.titulo)}</th>`).join("")}<th>Estado</th></tr></thead><tbody>
    ${t.alumnos.map(a => `<tr class="clic" data-act="ir" data-h="#/alumno/${a.id}"><td>${persona(a, 28)}</td>${a.actividades.map(r => r ? `<td class="c"><span style="color:#e0a419">${estrellas(r.estrellas)}</span><div class="muted num" style="font-size:12px">${r.pct}%</div></td>` : `<td class="c muted">—</td>`).join("")}
      <td>${a.entregada ? (a.tarde ? `<span class="estado e-warn" title="La terminó después de la fecha límite">✓ Terminó tarde (${fechaCorta(a.entregada)})</span>` : `<span class="estado e-ok">✓ Terminó ${fechaCorta(a.entregada)}</span>`) : t.fecha_limite && t.fecha_limite < hoy ? `<span class="estado e-bad">No la terminó</span>` : `<span class="estado e-nd">Pendiente</span>`}</td></tr>`).join("")}</tbody></table></div>` : vacio("No hay alumnos asignados")}</div></section>`;
  pintar(shell("tareas", esc(t.titulo), cuerpo, {migas: `<a href="#/tareas">Misiones</a> /`,
    acciones: `<button class="btn sec" data-act="imprimir">${ic("imprimir")}Imprimir</button><button class="btn sec" data-act="archivarTarea" data-id="${t.id}">${t.archivada ? "Desarchivar" : "Archivar"}</button><button class="btn peligro" data-act="borrarTarea" data-id="${t.id}">Eliminar</button>`}));
}

/* =========================================================
   Actividades
   ========================================================= */
async function pActividades() {
  const l = await api("/api/docente/actividades");
  const vis = l.filter(a => !UI.actFiltro || a.tipo === UI.actFiltro);
  const cuerpo = `
  <div class="acciones" style="margin-bottom:16px">
    <div class="segmento"><button class="${!UI.actFiltro ? "on" : ""}" data-act="actFiltro" data-t="">Todas (${l.length})</button>${Object.entries(CAT.tipos).map(([k, t]) => `<button class="${UI.actFiltro === k ? "on" : ""}" data-act="actFiltro" data-t="${k}">${t.i} ${esc(t.n)}</button>`).join("")}</div>
  </div>
  <section class="panel"><div class="panel-b sin"><div class="tabla-wrap"><table><thead><tr><th>Actividad</th><th>Tipo</th><th class="c">Nivel</th><th>Temas que trabaja</th><th class="r">Veces jugada</th><th>Resultado del grupo</th><th class="c">En la isla</th><th></th></tr></thead><tbody>
    ${vis.map(a => `<tr><td><span class="persona"><span style="font-size:22px">${a.e}</span><span>${esc(a.titulo)}<br><span class="muted" style="font-size:12px;font-weight:500">${a.base ? "Incluida" : "✍️ Creada por ustedes"} · ${a.n} ítems</span>${a.estado === "borrador" ? ` <span class="estado e-warn">Borrador</span>` : ""}</span></span></td>
      <td class="muted">${tipoN(a.tipo)}</td><td class="c">${a.nivel}</td><td>${a.temas.map(temaTag).join("")}</td><td class="r num">${a.veces}</td><td>${Graficos.pill(a.pct)}</td>
      <td class="c"><label class="sw" title="Mostrar en la isla"><input type="checkbox" data-act="visible" data-id="${a.id}" ${a.visible ? "checked" : ""}><span></span></label></td>
      <td class="r"><div class="acciones" style="justify-content:flex-end">${a.estado === "borrador" ? `<button class="btn chico" data-act="publicar" data-id="${a.id}">${ic("check")}Publicar</button>` : ""}<a class="btn sec chico" href="#/actividad/${a.id}">Ver</a>${a.base ? "" : `<a class="btn sec chico" href="#/actividad-editar/${a.id}">Editar</a><button class="btn peligro chico" data-act="borrarAct" data-id="${a.id}">Borrar</button>`}</div></td></tr>`).join("")}
  </tbody></table></div></div></section>
  <section class="panel"><div class="panel-h"><h2>Crear una actividad nueva</h2></div><div class="panel-b"><div class="check-lista">
    ${Object.entries(CAT.tipos).map(([k, t]) => `<a class="check" href="#/actividad-nueva/${k}" style="text-decoration:none;color:inherit"><span class="em">${t.i}</span><span><b>${esc(t.n)}</b><br><span class="muted" style="font-size:13px">${esc(t.desc)}</span></span></a>`).join("")}
  </div></div></section>`;
  pintar(shell("actividades", "Actividades", cuerpo, {acciones: `<button class="btn" data-act="nuevaActividad">${ic("mas")}Nueva actividad</button>`}));
}

function itemTexto(tipo, it) {
  const ops = o => `<span class="muted">(✓ ${esc(o[0])} · ✗ ${o.slice(1).map(esc).join(" · ✗ ")})</span>`;
  if (tipo === "oraciones") return esc(it.t);
  if (tipo === "palabras" || tipo === "silabas") return `<b>${esc(it.p)}</b>`;
  if (tipo === "rimas") return `<b>${esc(it.p)}</b> rima con <b>${esc(it.c.t)}</b> ${it.c.e || ""} <span class="muted">(no riman: ${it.x.map(x => esc(x.t)).join(", ")})</span>`;
  if (tipo === "completar") return `${esc(it.t).replace("_", "<b>___</b>")} ${ops(it.o)}`;
  if (tipo === "ortografia") return `<b>${esc(it.p).replace("_", "__")}</b> → <b>${esc(it.p.replace("_", it.o[0]))}</b> ${ops(it.o)}`;
  if (tipo === "opuestos") return `${it.r === "opuesto" ? "Lo contrario de" : "Parecida a"} <b>${esc(it.p)}</b> ${ops(it.o)}`;
  if (tipo === "clases") return `<b>${esc(it.p)}</b> → ${esc(CAT.clases[it.c] || "")}${it.t ? `<br><span class="muted">«${esc(it.t)}»</span>` : ""}`;
  return "";
}

async function pActividad(id) {
  const a = await api("/api/docente/actividades/" + encodeURIComponent(id));
  const res = i => { const r = a.resultados[i]; return r ? Graficos.pill(r.pct) + ` <span class="muted" style="font-size:12px">${r.n} resp.</span>` : `<span class="muted">sin datos</span>`; };
  let cuerpoItems;
  if (a.tipo === "cuento") {
    cuerpoItems = `<div class="panel-b" style="font-size:16px;line-height:1.7;border-bottom:1px solid var(--line2)">${esc(a.texto)}</div>
    <table><thead><tr><th>#</th><th>Pregunta</th><th>Tema</th><th>Resultado</th></tr></thead><tbody>${a.preguntas.map((q, i) => `<tr><td class="muted">${i + 1}</td><td>
      ${q.t === "e" ? `<b>${esc(q.p)}</b><br><span class="muted" style="font-size:13px">✓ ${esc(q.o[0])} · ✗ ${q.o.slice(1).map(esc).join(" · ✗ ")}</span>`
        : q.t === "vf" ? `<b>¿Verdadero o falso?</b> «${esc(q.p)}» → ${q.v ? "Verdadero" : "Falso"}`
        : `<b>Ordenar la secuencia:</b><br><span class="muted" style="font-size:13px">${q.items.map((x, k) => `${k + 1}. ${esc(x)}`).join(" · ")}</span>`}</td><td>${temaTag(q.tema)}</td><td>${res(i)}</td></tr>`).join("")}</tbody></table>`;
  } else {
    cuerpoItems = `<table><thead><tr><th>#</th><th>Ítem</th><th>Resultado</th></tr></thead><tbody>${a.items.map((it, i) => `<tr><td class="muted">${i + 1}</td><td><span style="font-size:20px">${it.e || ""}</span>
      ${itemTexto(a.tipo, it)}</td><td>${res(i)}</td></tr>`).join("")}</tbody></table>`;
  }
  const cuerpo = `<section class="panel"><div class="panel-h"><h2>${a.e} ${esc(a.titulo)}</h2><span class="tag">${tipoN(a.tipo)}</span><span class="tag">Nivel ${a.nivel}</span><span class="tag">Figurita ${a.sticker || "⭐"}</span></div>
    <div class="panel-b sin"><div class="tabla-wrap">${cuerpoItems}</div></div></section>`;
  pintar(shell("actividades", esc(a.titulo), cuerpo, {migas: `<a href="#/actividades">Actividades</a> /`,
    acciones: a.base ? "" : `<a class="btn sec" href="#/actividad-editar/${a.id}">Editar</a>`}));
}

/* =========================================================
   Cuentos: escribir, revisar, publicar y supervisar
   ========================================================= */
async function pCuentos() {
  const todos = (await api("/api/docente/actividades")).filter(a => a.tipo === "cuento");
  const revisar = todos.filter(a => a.estado === "borrador");
  const publicados = todos.filter(a => a.estado !== "borrador");
  const enIsla = publicados.filter(a => a.visible).length;
  const lecturas = todos.reduce((s, a) => s + a.veces, 0);
  const conRes = publicados.filter(a => a.pct !== null);
  const prom = conRes.length ? Math.round(conRes.reduce((s, a) => s + a.pct, 0) / conRes.length) : null;
  const quien = a => a.base ? "Incluido en el juego" : `Escrito por ${esc(a.autor || "una docente")}${a.editado_por && a.editado_por !== a.autor ? ` · editado por ${esc(a.editado_por)}` : ""}`;
  const cuerpo = `
  <div class="kpis">
    <div class="kpi"><div class="l">Cuentos en la isla</div><div class="v">${enIsla}</div><div class="s">publicados y visibles para los chicos</div></div>
    <div class="kpi"><div class="l">Para revisar</div><div class="v">${revisar.length}</div><div class="s">${revisar.length ? "esperando que los publiques" : "todo revisado"}</div></div>
    <div class="kpi"><div class="l">Lecturas</div><div class="v">${lecturas}</div><div class="s">veces que los chicos terminaron un cuento</div></div>
    <div class="kpi"><div class="l">Comprensión promedio</div><div class="v">${prom === null ? "—" : prom + "%"}</div><div class="s">respuestas correctas a la primera</div></div>
  </div>
  <section class="panel nuevo-cuento"><div class="panel-b">
    <div class="nc-icono">✍️</div>
    <div style="flex:1;min-width:240px"><h2 style="font-size:17px;margin-bottom:6px">Escribir un cuento nuevo</h2>
      <ol class="pasos"><li><b>Escribí</b> el cuento y sus preguntas.</li><li><b>Revisalo</b> con la vista previa, tal como lo van a ver los chicos.</li><li><b>Publicalo</b> y aparece en la isla.</li></ol></div>
    <a class="btn" href="#/actividad-nueva/cuento">${ic("mas")}Escribir cuento</a>
    <div class="otros-ej"><span class="muted">¿Otro tipo de ejercicio para practicar?</span>
      ${Object.entries(CAT.tipos).filter(([k]) => k !== "cuento").map(([k, t]) => `<a class="chip-ej" href="#/actividad-nueva/${k}"><span>${t.i}</span>${esc(t.n)}</a>`).join("")}</div>
  </div></section>
  ${revisar.length ? `
  <section class="panel"><div class="panel-h"><h2>Para revisar</h2><span class="estado e-warn">${revisar.length}</span>
    <span class="muted" style="font-size:12.5px">Los chicos todavía no ven estos cuentos</span></div>
    <div class="panel-b"><div class="tarjetas-cuento">${revisar.map(a => `
      <article class="t-cuento"><div class="tc-cab"><span class="tc-em">${a.e}</span><div><b>${esc(a.titulo)}</b><div class="muted" style="font-size:12.5px">${quien(a)}</div></div></div>
        <div class="tc-tags"><span class="tag">Nivel ${a.nivel}</span><span class="tag">${a.n} preguntas</span><span class="estado e-warn">Borrador</span></div>
        <div class="muted" style="font-size:12.5px">${a.actualizado ? "Última modificación: " + fechaHora(a.actualizado) : ""}</div>
        <div class="acciones"><button class="btn sec chico" data-act="vistaCuento" data-id="${a.id}">${ic("ojo")}Vista previa</button>
          <a class="btn sec chico" href="#/actividad-editar/${a.id}">Editar</a>
          <button class="btn chico" data-act="publicar" data-id="${a.id}">${ic("check")}Publicar</button>
          <button class="btn peligro chico" data-act="borrarAct" data-id="${a.id}">Borrar</button></div></article>`).join("")}</div></div></section>` : ""}
  <section class="panel"><div class="panel-h"><h2>Biblioteca de cuentos</h2><span class="muted" style="font-size:12.5px">${publicados.length} cuentos publicados</span></div>
    <div class="panel-b sin"><div class="tabla-wrap"><table><thead><tr><th>Cuento</th><th class="c">Nivel</th><th class="r">Preguntas</th><th class="r">Lecturas</th><th>Comprensión</th><th class="c">En la isla</th><th></th></tr></thead><tbody>
    ${publicados.map(a => `<tr><td><span class="persona"><span style="font-size:22px">${a.e}</span><span>${esc(a.titulo)}<br><span class="muted" style="font-size:12px;font-weight:500">${quien(a)}</span></span></span></td>
      <td class="c">${a.nivel}</td><td class="r num">${a.n}</td><td class="r num">${a.veces}</td><td>${Graficos.pill(a.pct)}</td>
      <td class="c"><label class="sw" title="Mostrar en la isla"><input type="checkbox" data-act="visible" data-id="${a.id}" ${a.visible ? "checked" : ""}><span></span></label></td>
      <td class="r"><div class="acciones" style="justify-content:flex-end">
        <button class="btn sec chico" data-act="vistaCuento" data-id="${a.id}">Vista previa</button>
        <a class="btn sec chico" href="#/actividad/${a.id}">Resultados</a>
        ${a.base ? "" : `<a class="btn sec chico" href="#/actividad-editar/${a.id}">Editar</a><button class="btn fantasma chico" data-act="despublicar" data-id="${a.id}">Pasar a borrador</button>`}</div></td></tr>`).join("")}
    </tbody></table></div></div></section>
  <div class="ayuda"><b>¿Cómo se supervisa?</b> Los cuentos nuevos quedan como <b>borrador</b> hasta que alguien los publica, así se pueden revisar antes de que los vean los chicos. En «Resultados» ves qué preguntas de cada cuento les cuestan más.</div>`;
  pintar(shell("cuentos", "Cuentos", cuerpo));
}

async function vistaCuento(id) {
  const a = await llamar(() => api("/api/docente/actividades/" + encodeURIComponent(id)));
  if (!a) return;
  const preguntas = a.preguntas.map((q, i) => `<li><span class="tag">${CAT.temas[q.tema]?.i || ""} ${esc(CAT.temas[q.tema]?.n || q.tema)}</span><br>
    ${q.t === "e" ? `<b>${esc(q.p)}</b><div class="opciones-prev">${q.o.map((o, k) => `<span class="${k === 0 ? "bien" : ""}">${k === 0 ? "✓ " : ""}${esc(o)}</span>`).join("")}</div>`
      : q.t === "vf" ? `<b>¿Es verdad? «${esc(q.p)}»</b><div class="opciones-prev"><span class="${q.v ? "bien" : ""}">👍 Sí</span><span class="${q.v ? "" : "bien"}">👎 No</span></div>`
      : `<b>Ordenar lo que pasó:</b><ol>${q.items.map(x => `<li>${esc(x)}</li>`).join("")}</ol>`}</li>`).join("");
  const r = await modal({ancho: true, titulo: "Vista previa · así lo ven los chicos", cuerpo: `
    <div class="prev-cuento"><div class="pc-em">${a.e}</div><h3>${esc(a.titulo)}</h3><p>${esc(a.texto)}</p></div>
    <h4 style="margin:16px 0 8px">Preguntas (${a.preguntas.length})</h4><ol class="prev-preguntas">${preguntas}</ol>
    <p class="muted" style="font-size:12.5px;margin-bottom:0">En 1.º grado se muestran 2 opciones por pregunta (la correcta y la primera incorrecta).</p>`,
    botones: [{txt: "Cerrar", cls: "sec", valor: null}, ...(a.base ? [] : [{txt: "Editar", cls: "sec", valor: "editar"}]),
              ...(!a.base && a.estado === "borrador" ? [{txt: "Publicar", valor: "publicar"}] : [])]});
  if (r === "editar") location.hash = "#/actividad-editar/" + id;
  if (r === "publicar") A.publicar({dataset: {id}});
}

/* ---------- Editor de actividades ---------- */
const COMPRENSION = () => Object.entries(CAT.temas).filter(([k, t]) => t.area === "Comprensión lectora" && k !== "secuencia");
function nuevoBorrador(tipo) {
  const base = {tipo, titulo: "", e: CAT.tipos[tipo].i, sticker: "⭐", nivel: "1"};
  if (tipo === "cuento") return {...base, texto: "", preguntas: [qVacia("personajes"), qVacia("detalles"), qVacia("emociones")], secuencia: ["", "", "", ""]};
  return {...base, items: [0, 1, 2].map(() => itemVacio(tipo))};
}
function qVacia(tema = "personajes") { return {t: "e", tema, p: "", o: ["", "", ""], v: true}; }
function rVacia() { return {p: "", e: "", c: {t: "", e: ""}, x: [{t: "", e: ""}, {t: "", e: ""}]}; }
const AYUDA_TIPO = {
  silabas: "Separá cada palabra con guiones: <b>ma-ri-po-sa</b>. Los chicos arman la palabra tocando las sílabas en orden. Desde 2.º grado aparece además una sílaba de otra palabra para despistar.",
  completar: "Escribí la oración con un guion bajo <b>_</b> donde va la palabra que falta. Poné la <b>correcta en el primer casillero</b>; el juego mezcla las opciones.",
  ortografia: "Escribí la palabra con un guion bajo <b>_</b> donde va la letra: <b>ca_a</b>. Poné la <b>letra correcta en el primer casillero</b> (puede ser de hasta 3 letras, como <b>ll</b> o <b>rr</b>).",
  opuestos: "Elegí si hay que buscar lo contrario o una palabra parecida. Poné la <b>correcta en el primer casillero</b>; el juego mezcla las opciones.",
  clases: "Los chicos eligen si la palabra <b>nombra algo</b> (sustantivo), <b>dice cómo es</b> (adjetivo) o <b>dice una acción</b> (verbo). Si escribís una oración de ejemplo, la palabra aparece resaltada.",
};
function itemVacio(tipo) {
  return {oraciones: {e: "", t: ""}, palabras: {e: "", p: ""}, silabas: {e: "", p: ""}, rimas: rVacia(),
          completar: {e: "", t: "", o: ["", "", ""]}, ortografia: {e: "", p: "", o: ["", "", ""]},
          opuestos: {e: "", p: "", r: "opuesto", o: ["", "", ""]}, clases: {e: "", p: "", c: "s", t: ""}}[tipo];
}

async function pEditor(tipo, id) {
  if (id) {
    const a = await api("/api/docente/actividades/" + encodeURIComponent(id));
    BORRADOR = {id, tipo: a.tipo, titulo: a.titulo, e: a.e, sticker: a.sticker, nivel: String(a.nivel), estado: a.estado};
    if (a.tipo === "cuento") {
      BORRADOR.texto = a.texto;
      BORRADOR.preguntas = a.preguntas.filter(q => q.t !== "o").map(q => ({...qVacia(), ...q, o: [...(q.o || []), "", "", ""].slice(0, 3)}));
      BORRADOR.secuencia = [...((a.preguntas.find(q => q.t === "o") || {}).items || []), "", "", "", ""].slice(0, 4);
    } else if (a.tipo === "rimas") {
      BORRADOR.items = a.items.map(it => ({...it, x: [...it.x, {t: "", e: ""}, {t: "", e: ""}].slice(0, 2)}));
    } else BORRADOR.items = a.items.map(it => ({...itemVacio(a.tipo), ...it, ...(it.o ? {o: [...it.o, "", ""].slice(0, 3)} : {})}));
  } else if (!BORRADOR || BORRADOR.tipo !== tipo || BORRADOR.id) {
    BORRADOR = nuevoBorrador(tipo);
  }
  dibujarEditor();
}
function dibujarEditor() {
  const b = BORRADOR, t = CAT.tipos[b.tipo];
  const inp = (bind, val, ph = "", extra = "") => `<input type="text" data-bind="${bind}" value="${esc(val)}" placeholder="${esc(ph)}" ${extra}>`;
  let especifico = "";
  if (b.tipo === "cuento") {
    especifico = `
    <section class="panel"><div class="panel-h"><h2>Texto del cuento</h2></div><div class="panel-b">
      <div class="campo"><textarea data-bind="texto" style="min-height:160px" placeholder="Había una vez…">${esc(b.texto)}</textarea>
      <small>Para 1.º grado: 3 a 5 oraciones cortas. Para 2.º grado: 5 a 8 oraciones. Para 3.º grado: 8 a 12 oraciones.</small></div></div></section>
    <section class="panel"><div class="panel-h"><h2>Preguntas de comprensión</h2><button type="button" class="btn sec chico" data-act="agregarQ">${ic("mas")}Agregar pregunta</button></div><div class="panel-b">
      <div class="ayuda">Escribí la <b>respuesta correcta en el primer casillero</b>. El juego mezcla las opciones. En 1.º grado se muestran solo 2 opciones (la correcta y la primera incorrecta).</div>
      ${b.preguntas.map((q, i) => `<div class="bloque-item"><div class="cab"><b>Pregunta ${i + 1}</b><button type="button" class="btn fantasma chico" data-act="quitar" data-lista="preguntas" data-i="${i}">Quitar</button></div>
        <div class="f2"><div class="campo"><label>Tema</label><select data-bind="preguntas.${i}.tema">${COMPRENSION().map(([k, tt]) => `<option value="${k}" ${k === q.tema ? "selected" : ""}>${tt.i} ${tt.n}</option>`).join("")}</select></div>
        <div class="campo"><label>Tipo</label><select data-bind="preguntas.${i}.t" data-redibujar="1"><option value="e" ${q.t === "e" ? "selected" : ""}>Elegir la respuesta</option><option value="vf" ${q.t === "vf" ? "selected" : ""}>Verdadero o falso</option></select></div></div>
        ${q.t === "e" ? `<div class="campo"><label>Pregunta</label>${inp(`preguntas.${i}.p`, q.p, "Ej.: ¿Quién es el personaje principal?")}</div>
          <div class="f3"><div class="campo"><label>✓ Correcta</label>${inp(`preguntas.${i}.o.0`, q.o[0])}</div><div class="campo"><label>✗ Incorrecta 1</label>${inp(`preguntas.${i}.o.1`, q.o[1])}</div><div class="campo"><label>✗ Incorrecta 2</label>${inp(`preguntas.${i}.o.2`, q.o[2])}</div></div>`
        : `<div class="f2"><div class="campo"><label>Oración</label>${inp(`preguntas.${i}.p`, q.p, "Ej.: El perro era muy grande.")}</div>
          <div class="campo"><label>Esa oración es…</label><select data-bind="preguntas.${i}.v"><option value="true" ${q.v ? "selected" : ""}>Verdadera</option><option value="false" ${!q.v ? "selected" : ""}>Falsa</option></select></div></div>`}
      </div>`).join("")}</div></section>
    <section class="panel"><div class="panel-h"><h2>Orden de los hechos <span class="muted" style="font-weight:500">(opcional)</span></h2></div><div class="panel-b">
      <p class="muted" style="margin-top:0">Escribí lo que pasa en el cuento, en orden. Completá al menos 3. Podés empezar cada parte con un emoji.</p>
      <div class="f2">${["Principio", "Después", "Después", "Final"].map((l, i) => `<div class="campo"><label>${i + 1}. ${l}</label>${inp(`secuencia.${i}`, b.secuencia[i])}</div>`).join("")}</div></div></section>`;
  } else {
    const filas = b.items.map((it, i) => {
      let campos;
      if (b.tipo === "oraciones") campos = `<div class="campo" style="max-width:110px"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, "🐱", 'maxlength="8"')}</div><div class="campo" style="flex:1"><label>Oración (3 a 10 palabras)</label>${inp(`items.${i}.t`, it.t, "El gato duerme en la cama")}</div>`;
      else if (b.tipo === "palabras") campos = `<div class="campo" style="max-width:110px"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, "☀️", 'maxlength="8"')}</div><div class="campo" style="flex:1"><label>Palabra (solo letras)</label>${inp(`items.${i}.p`, it.p, "sol", 'maxlength="10"')}</div>`;
      else if (b.tipo === "silabas") campos = `<div class="campo" style="max-width:110px"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, "🦋", 'maxlength="8"')}</div><div class="campo" style="flex:1"><label>Palabra separada en sílabas con guiones</label>${inp(`items.${i}.p`, it.p, "ma-ri-po-sa", 'maxlength="40"')}</div>`;
      else if (b.tipo === "completar" || b.tipo === "ortografia") {
        const orto = b.tipo === "ortografia", m = orto ? 'maxlength="3"' : 'maxlength="30"';
        campos = `<div style="flex:1"><div class="acciones" style="align-items:flex-start"><div class="campo" style="max-width:110px"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, orto ? "🏠" : "🐱", 'maxlength="8"')}</div>
          <div class="campo" style="flex:1"><label>${orto ? "Palabra con _ donde falta la letra" : "Oración con _ donde falta la palabra"}</label>${inp(`items.${i}.${orto ? "p" : "t"}`, orto ? it.p : it.t, orto ? "ca_a" : "El gato toma _", orto ? 'maxlength="16"' : 'maxlength="140"')}</div></div>
          <div class="f3"><div class="campo"><label>✓ Correcta</label>${inp(`items.${i}.o.0`, it.o[0], orto ? "s" : "leche", m)}</div><div class="campo"><label>✗ Incorrecta</label>${inp(`items.${i}.o.1`, it.o[1], orto ? "z" : "zapato", m)}</div><div class="campo"><label>✗ Otra (opcional)</label>${inp(`items.${i}.o.2`, it.o[2], "", m)}</div></div></div>`;
      } else if (b.tipo === "opuestos") campos = `<div style="flex:1"><div class="acciones" style="align-items:flex-start"><div class="campo" style="max-width:110px"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, "🐘", 'maxlength="8"')}</div>
          <div class="campo" style="flex:1"><label>Palabra</label>${inp(`items.${i}.p`, it.p, "grande", 'maxlength="30"')}</div>
          <div class="campo" style="flex:1"><label>Hay que buscar…</label><select data-bind="items.${i}.r"><option value="opuesto" ${it.r !== "parecido" ? "selected" : ""}>Lo contrario (antónimo)</option><option value="parecido" ${it.r === "parecido" ? "selected" : ""}>Una parecida (sinónimo)</option></select></div></div>
          <div class="f3"><div class="campo"><label>✓ Correcta</label>${inp(`items.${i}.o.0`, it.o[0], "chico", 'maxlength="30"')}</div><div class="campo"><label>✗ Incorrecta</label>${inp(`items.${i}.o.1`, it.o[1], "pesado", 'maxlength="30"')}</div><div class="campo"><label>✗ Otra (opcional)</label>${inp(`items.${i}.o.2`, it.o[2], "", 'maxlength="30"')}</div></div></div>`;
      else if (b.tipo === "clases") campos = `<div style="flex:1"><div class="acciones" style="align-items:flex-start"><div class="campo" style="max-width:110px"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, "🐶", 'maxlength="8"')}</div>
          <div class="campo" style="flex:1"><label>Palabra</label>${inp(`items.${i}.p`, it.p, "perro", 'maxlength="30"')}</div>
          <div class="campo" style="flex:1"><label>Clase de palabra</label><select data-bind="items.${i}.c">${Object.entries(CAT.clases).map(([k, t]) => `<option value="${k}" ${it.c === k ? "selected" : ""}>${esc(t)}</option>`).join("")}</select></div></div>
          <div class="campo"><label>Oración de ejemplo (opcional, debe contener la palabra)</label>${inp(`items.${i}.t`, it.t || "", "El perro ladra fuerte", 'maxlength="140"')}</div></div>`;
      else campos = `<div class="f4" style="flex:1">
        <div class="campo"><label>Palabra</label>${inp(`items.${i}.p`, it.p, "gato")}</div><div class="campo"><label>Dibujo</label>${inp(`items.${i}.e`, it.e, "🐱", 'maxlength="8"')}</div>
        <div class="campo"><label>✓ Rima con</label>${inp(`items.${i}.c.t`, it.c.t, "pato")}</div><div class="campo"><label>Dibujo</label>${inp(`items.${i}.c.e`, it.c.e, "🦆", 'maxlength="8"')}</div>
        <div class="campo"><label>✗ No rima 1</label>${inp(`items.${i}.x.0.t`, it.x[0].t, "mesa")}</div><div class="campo"><label>Dibujo</label>${inp(`items.${i}.x.0.e`, it.x[0].e, "", 'maxlength="8"')}</div>
        <div class="campo"><label>✗ No rima 2</label>${inp(`items.${i}.x.1.t`, it.x[1].t, "sol")}</div><div class="campo"><label>Dibujo</label>${inp(`items.${i}.x.1.e`, it.x[1].e, "", 'maxlength="8"')}</div></div>`;
      return `<div class="bloque-item"><div class="cab"><b>${i + 1}</b><button type="button" class="btn fantasma chico" data-act="quitar" data-lista="items" data-i="${i}">Quitar</button></div><div class="acciones" style="align-items:flex-start">${campos}</div></div>`;
    }).join("");
    especifico = `<section class="panel"><div class="panel-h"><h2>Contenido</h2><button type="button" class="btn sec chico" data-act="agregarItem">${ic("mas")}Agregar</button></div><div class="panel-b">${AYUDA_TIPO[b.tipo] ? `<div class="ayuda">${AYUDA_TIPO[b.tipo]}</div>` : ""}${filas}</div></section>`;
  }
  const cuerpo = `<form data-form="actividad">
    <section class="panel"><div class="panel-h"><h2>Datos generales</h2><span class="tag">${t.i} ${esc(t.n)}</span></div><div class="panel-b">
      <div class="campo"><label>Título</label>${inp("titulo", b.titulo, "Ej.: La vaca Lola", 'maxlength="60" required')}</div>
      <div class="f3"><div class="campo"><label>Dibujo (emoji)</label>${inp("e", b.e, "📖", 'maxlength="8"')}</div>
      <div class="campo"><label>Figurita del álbum</label>${inp("sticker", b.sticker, "⭐", 'maxlength="8"')}</div>
      <div class="campo"><label>Nivel</label><select data-bind="nivel"><option value="1" ${b.nivel === "1" ? "selected" : ""}>Nivel 1 (desde 1.º grado)</option><option value="2" ${b.nivel === "2" ? "selected" : ""}>Nivel 2 (desde 2.º grado)</option><option value="3" ${b.nivel === "3" ? "selected" : ""}>Nivel 3 (3.º grado)</option></select></div></div>
      <small class="muted">Para escribir un emoji en Windows: tecla Windows + punto ( . )</small></div></section>
    ${especifico}
    <div class="error-form" id="err"></div>
    ${b.tipo === "cuento" ? `<div class="ayuda">Si lo guardás como <b>borrador</b>, los chicos no lo ven hasta que lo publiques desde <a href="#/cuentos">Cuentos</a>.</div>` : ""}
    <div class="acciones"><a class="btn sec" href="${b.tipo === "cuento" ? "#/cuentos" : "#/actividades"}">Cancelar</a>
      <button class="btn sec" type="submit" value="borrador">Guardar como borrador</button>
      <button class="btn" type="submit" value="publicar">${ic("check")}Guardar y publicar</button></div></form>`;
  const seccion = b.tipo === "cuento" ? "cuentos" : "actividades";
  pintar(shell(seccion, b.id ? (b.tipo === "cuento" ? "Editar cuento" : "Editar actividad") : (b.tipo === "cuento" ? "Escribir un cuento nuevo" : "Nueva actividad: " + esc(t.n)), cuerpo,
    {migas: seccion === "cuentos" ? `<a href="#/cuentos">Cuentos</a> /` : `<a href="#/actividades">Actividades</a> /`}));
}
function fijar(obj, ruta, val) {
  const p = ruta.split("."); let o = obj;
  for (let i = 0; i < p.length - 1; i++) o = o[p[i]];
  o[p[p.length - 1]] = val === "true" ? true : val === "false" ? false : val;
}
function payloadActividad() {
  const b = BORRADOR, d = {tipo: b.tipo, titulo: b.titulo, e: b.e, sticker: b.sticker, nivel: b.nivel};
  if (b.tipo === "cuento") {
    d.texto = b.texto;
    d.preguntas = b.preguntas.map(q => q.t === "vf" ? {t: "vf", tema: q.tema, p: q.p, v: q.v} : {t: "e", tema: q.tema, p: q.p, o: q.o});
    const sec = b.secuencia.filter(s => s.trim());
    if (sec.length && sec.length < 3) throw new Error("Para el orden de los hechos completá al menos 3 partes (o dejalo vacío).");
    if (sec.length) d.preguntas.push({t: "o", tema: "secuencia", items: sec});
  } else d.items = b.items;
  return d;
}

/* =========================================================
   Temas y ajustes
   ========================================================= */
async function pTemas() {
  const {cfg, temas} = await api("/api/docente/config");
  const areas = [...new Set(temas.map(t => t.area))];
  const cuerpo = `
  <div class="ayuda">Cada pregunta y cada juego trabaja un tema del área de Lengua. <b>Desactivá</b> los temas que todavía no enseñaste: sus preguntas no aparecen en el juego. El porcentaje muestra cuántas respuestas del grupo fueron correctas a la primera.</div>
  ${areas.map(ar => `<section class="panel"><div class="panel-h"><h2>${esc(ar)}</h2></div><div class="panel-b sin"><table><thead><tr><th>Tema</th><th>Qué aprenden</th><th class="r">Ítems</th><th>Resultado del grupo</th><th class="c">Activo</th></tr></thead><tbody>
    ${temas.filter(t => t.area === ar).map(t => `<tr style="${t.activo ? "" : "opacity:.55"}"><td style="min-width:200px"><span class="persona"><span style="font-size:22px">${t.i}</span><span>${esc(t.n)}<br><span class="muted" style="font-size:12px;font-weight:500">Para los chicos: «${esc(t.kid)}»</span></span></span></td>
      <td style="min-width:280px">${esc(t.obj)}${t.ejemplo ? `<div class="muted" style="font-size:12.5px;margin-top:3px">Ej.: «${esc(t.ejemplo)}»</div>` : ""}</td>
      <td class="r num">${t.items}</td><td>${Graficos.pill(t.pct)}<div class="muted" style="font-size:12px;margin-top:2px">${t.cant} respuestas</div></td>
      <td class="c"><label class="sw"><input type="checkbox" data-act="tema" data-t="${t.id}" ${t.activo ? "checked" : ""}><span></span></label></td></tr>`).join("")}
  </tbody></table></div></section>`).join("")}`;
  pintar(shell("temas", "Temas y contenidos", cuerpo));
}

async function pAjustes() {
  const [{cfg}, aud, docentes] = await Promise.all([api("/api/docente/config"), api("/api/docente/auditoria"), api("/api/docente/docentes")]);
  const sw = (k, t, d) => `<div class="interruptor"><div class="t"><b>${t}</b><small>${d}</small></div><label class="sw"><input type="checkbox" data-act="cfg" data-k="${k}" ${cfg[k] ? "checked" : ""}><span></span></label></div>`;
  const cuerpo = `<div class="grid g2">
    <section class="panel"><div class="panel-h"><h2>Cómo se juega</h2><span class="muted" style="font-size:12.5px">Vale para todos los grados</span></div><div class="panel-b" style="padding-top:4px;padding-bottom:4px">
      ${sw("mayus_1", "Imprenta mayúscula en 1.º grado", "Los chicos de 1.º ven los textos en MAYÚSCULAS.")}
      ${sw("nivel2_para_1", "Actividades de nivel 2 para 1.º grado", "Útil para chicos de 1.º que ya leen con soltura.")}
      ${sw("nivel3_para_2", "Actividades de nivel 3 para 2.º grado", "Útil para chicos de 2.º que necesitan más desafío.")}
      ${sw("auto_leer", "Leer en voz alta automáticamente", "Cuentos, preguntas y consignas se leen solos al aparecer.")}
      ${sw("voz_lenta", "Voz más lenta", "La lectura en voz alta va más despacio.")}
      ${sw("voz_alegre", "Voz alegre", "La voz habla un poco más aguda y con más ritmo, como cuando se cuenta un cuento. Si la apagás, suena más tranquila.")}
      <div class="interruptor" style="flex-direction:column;align-items:stretch">
        <div class="t"><b>Voz de lectura</b><small>Las voces marcadas con ⭐ «natural» suenan mucho menos robóticas. Las mejores aparecen al abrir el juego con <strong>Microsoft Edge</strong> (por ejemplo «Elena», de Argentina). La lista depende de esta computadora y de este navegador.</small></div>
        <div class="acciones" style="margin-top:8px"><select id="selVoz" data-voz-actual="${esc(cfg.voz || "")}" style="flex:1;min-width:220px"></select>
          <button class="btn sec" type="button" data-act="probarVoz">🔊 Probar</button>
          <button class="btn" type="button" data-act="guardarVoz">Guardar voz</button></div>
      </div>
      ${sw("sonido", "Sonidos del juego", "Sonidos cortos al acertar y al equivocarse.")}
      ${sw("progresivo", "Desbloquear de a una", "Cada actividad se habilita al terminar la anterior, como en un videojuego.")}
    </div></section>
    <div class="pila">
      <section class="panel"><div class="panel-h"><h2>Mis grados</h2></div><form class="panel-b" data-form="misGrados">
        <p class="ink2" style="margin-top:0">Ves y manejás solo a los alumnos de estos grados. Así cada docente tiene su grupo y no se mezclan los datos.</p>
        ${checksGrados(misGrados())}
        <button class="btn" type="submit" style="margin-top:12px">Guardar mis grados</button></form></section>
      <section class="panel"><div class="panel-h"><h2>Mi cuenta</h2></div><form class="panel-b" data-form="password">
        ${campoPass("actual", "Contraseña actual", "current-password")}
        <div class="f2">${campoPass("nueva", "Nueva contraseña", "new-password")}${campoPass("nueva2", "Repetir", "new-password")}</div>
        <div class="error-form" id="err"></div><button class="btn" type="submit">Cambiar contraseña</button>
        <div class="interruptor" style="margin-top:18px;border-top:1px solid var(--line2);padding-top:14px"><div class="t"><b>Código de recuperación</b>
          <small>${YO.tiene_codigo ? "Ya tenés uno. Si lo perdiste, generá otro (el anterior deja de servir)." : "<b style='color:var(--warn)'>Todavía no tenés.</b> Generalo y guardalo: sirve para cambiar la contraseña si te la olvidás."}</small></div>
          <button class="btn sec chico" type="button" data-act="nuevoCodigo">${YO.tiene_codigo ? "Generar otro" : "Generar código"}</button></div></form></section>
      <section class="panel"><div class="panel-h"><h2>Datos y respaldo</h2></div><div class="panel-b">
        <p style="margin-top:0" class="ink2">Todo se guarda en la carpeta <b>datos</b> del programa, en esta computadora. Descargá una copia de vez en cuando.</p>
        <div class="acciones"><a class="btn sec" href="/api/docente/exportar.csv">${ic("bajar")}Resultados (Excel / CSV)</a><a class="btn sec" href="/api/docente/copia">${ic("bajar")}Copia de seguridad</a></div></div></section>
    </div></div>
  <section class="panel" style="margin-top:20px"><div class="panel-h"><h2>Docentes</h2><span class="muted" style="font-size:12.5px">Cada cuenta ve solo a los alumnos de sus grados</span></div>
    <div class="panel-b" style="padding-top:4px;padding-bottom:4px">${sw("registro_abierto", "Permitir que otros docentes se creen su cuenta", "Aparece «Crear mi cuenta» en la pantalla de ingreso. Por seguridad, solo funciona desde la computadora donde está instalado el juego. Desactivalo cuando ya estén todos.")}</div>
    <div class="panel-b sin"><table><thead><tr><th>Nombre</th><th>Usuario</th><th>Grados</th><th>Cuenta creada</th><th>Último ingreso</th><th></th></tr></thead><tbody>
    ${docentes.map(d => `<tr><td><b>${esc(d.nombre)}</b> ${d.yo ? `<span class="estado e-info">Vos</span>` : ""}</td><td>@${esc(d.usuario)}</td><td>${nombreGrados(d.grados)}</td><td class="num">${fechaCorta(d.creado)}</td><td class="muted">${haceCuanto(d.ultimo)}</td>
      <td class="r" style="white-space:nowrap">${d.yo ? "" : `<button class="btn sec chico" data-act="restablecer" data-id="${d.id}" data-n="${esc(d.nombre)}">Restablecer contraseña</button> <button class="btn peligro chico" data-act="borrarDocente" data-id="${d.id}" data-n="${esc(d.nombre)}">Eliminar</button>`}</td></tr>`).join("")}
    </tbody></table></div></section>
  <section class="panel" style="margin-top:20px"><div class="panel-h"><h2>Registro de accesos</h2><span class="muted" style="font-size:12.5px">Últimos 40 eventos de seguridad</span></div>
    <div class="panel-b sin"><div class="tabla-wrap"><table><thead><tr><th>Fecha</th><th>Evento</th><th>Usuario</th><th>Equipo (IP)</th></tr></thead><tbody>
    ${aud.map(e => `<tr><td class="num">${fechaHora(e.fecha)}</td><td>${/fallido/.test(e.evento) ? `<span class="estado e-bad">${esc(e.evento)}</span>` : esc(e.evento)}</td><td>${esc(e.usuario || "—")}</td><td class="muted num">${esc(e.ip || "")}</td></tr>`).join("")}
    </tbody></table></div></div></section>`;
  pintar(shell("ajustes", "Ajustes", cuerpo));
  llenarVoces();
  if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = llenarVoces;
}
function llenarVoces() {
  const sel = $("#selVoz"); if (!sel) return;
  const actual = sel.dataset.vozActual;
  const vs = Voz.voces().sort((a, b) => Voz.puntaje(b) - Voz.puntaje(a));
  Voz.preferida = "";
  const auto = Voz.elegir();
  sel.innerHTML = `<option value="">Automática (recomendada)${auto ? " — " + esc(Voz.etiqueta(auto)) : ""}</option>` +
    vs.map(v => `<option value="${esc(v.name)}" ${v.name === actual ? "selected" : ""}>${esc(Voz.etiqueta(v))}</option>`).join("");
  if (!vs.length) sel.innerHTML = `<option value="">Este navegador no tiene voces en español</option>`;
  if (actual && !vs.some(v => v.name === actual)) sel.insertAdjacentHTML("beforeend", `<option value="${esc(actual)}" selected>${esc(actual)} (no disponible en este navegador)</option>`);
}

/* =========================================================
   Acciones
   ========================================================= */
const A = {
  ir: el => { location.hash = el.dataset.h; },
  imprimir: () => window.print(),
  salir: async () => { await api("/api/docente/salir", {method: "POST"}).catch(() => {}); YO = null; location.hash = ""; navegar(); },
  verClaves: () => { UI.claves = !UI.claves; pAlumnos(); },
  nuevoAlumno: async () => {
    const r = await modal({titulo: "Agregar alumnos", cuerpo: `
      <div class="campo"><label>Nombres</label><textarea name="nombres" placeholder="Escribí un nombre por línea&#10;Ej.:&#10;Martina G.&#10;Thiago R."></textarea><small>Si hay dos chicos con el mismo nombre, agregá la inicial del apellido.</small></div>
      <div class="campo"><label>Grado</label><select name="grado">${opcionesGrado()}</select></div>`,
      botones: [{txt: "Cancelar", cls: "sec", valor: null}, {txt: "Agregar", valor: "form"}]});
    if (!r) return;
    const nombres = r.nombres.split("\n").map(s => s.trim()).filter(Boolean);
    const ok = await llamar(() => api("/api/docente/alumnos", {method: "POST", body: {nombres, grado: r.grado}}));
    if (ok) { toast(`Se agregaron ${ok.creados} alumnos. Cada uno tiene su clave de dibujos.`); pAlumnos(); }
  },
  nuevaClave: async el => {
    if (!await confirmar("Generar una clave nueva", "La clave anterior deja de funcionar. ¿Continuar?")) return;
    if (await llamar(() => api(`/api/docente/alumnos/${el.dataset.id}/clave`, {method: "POST"}), "Clave nueva generada.")) navegar();
  },
  reiniciarAlumno: async el => {
    if (!await confirmar("Reiniciar progreso", "Se borran sus resultados, estrellas, monedas, medallas y compras. Las observaciones se conservan.", "Reiniciar", true)) return;
    if (await llamar(() => api(`/api/docente/alumnos/${el.dataset.id}/reiniciar`, {method: "POST"}), "Progreso reiniciado.")) navegar();
  },
  borrarAlumno: async el => {
    if (!await confirmar("Eliminar alumno", "Se elimina el alumno con todo su historial y observaciones. Si solo deja de venir, mejor desactivalo.", "Eliminar", true)) return;
    if (await llamar(() => api(`/api/docente/alumnos/${el.dataset.id}`, {method: "DELETE"}), "Alumno eliminado.")) location.hash = "#/alumnos";
  },
  borrarObs: async el => {
    if (!await confirmar("Borrar observación", "¿Querés borrar esta observación?", "Borrar", true)) return;
    if (await llamar(() => api(`/api/docente/observaciones/${el.dataset.id}`, {method: "DELETE"}))) navegar();
  },
  tareasTab: el => { UI.tareasTab = el.dataset.t; pTareas(); },
  destino: () => { $("#elegidos").classList.toggle("hidden", $("[name=destino]:checked").value !== "elegidos"); },
  marcarCheck: el => {
    el.closest(".check").classList.toggle("on", el.checked);
    const n = $$("[name=act]:checked").length; if ($("#cuentaAct")) $("#cuentaAct").textContent = `${n} elegida${n === 1 ? "" : "s"}`;
  },
  archivarTarea: async el => { if (await llamar(() => api(`/api/docente/tareas/${el.dataset.id}/archivar`, {method: "POST"}), "Listo.")) navegar(); },
  borrarTarea: async el => {
    if (!await confirmar("Eliminar misión", "Se elimina la misión. Los resultados de los chicos se conservan en su historial.", "Eliminar", true)) return;
    if (await llamar(() => api(`/api/docente/tareas/${el.dataset.id}`, {method: "DELETE"}), "Misión eliminada.")) location.hash = "#/tareas";
  },
  actFiltro: el => { UI.actFiltro = el.dataset.t; pActividades(); },
  visible: async el => { await llamar(() => api(`/api/docente/actividades/${encodeURIComponent(el.dataset.id)}/visible`, {method: "POST", body: {visible: el.checked}}), el.checked ? "Ahora se ve en la isla." : "Oculta en la isla."); },
  borrarAct: async el => {
    if (!await confirmar("Borrar actividad", "Se borra la actividad y se quita de las misiones donde estaba.", "Borrar", true)) return;
    if (await llamar(() => api(`/api/docente/actividades/${encodeURIComponent(el.dataset.id)}`, {method: "DELETE"}), "Actividad borrada.")) navegar();
  },
  agregarQ: () => { BORRADOR.preguntas.push(qVacia("detalles")); dibujarEditor(); },
  agregarItem: () => { BORRADOR.items.push(itemVacio(BORRADOR.tipo)); dibujarEditor(); },
  quitar: el => { BORRADOR[el.dataset.lista].splice(+el.dataset.i, 1); dibujarEditor(); },
  tema: async el => {
    const {cfg} = await api("/api/docente/config");
    const off = new Set(cfg.temas_off); el.checked ? off.delete(el.dataset.t) : off.add(el.dataset.t);
    if (await llamar(() => api("/api/docente/config", {method: "PUT", body: {temas_off: [...off]}}), "Temas actualizados.")) pTemas(); else pTemas();
  },
  vistaCuento: el => vistaCuento(el.dataset.id),
  nuevaActividad: () => {
    modal({ancho: true, titulo: "¿Qué querés crear?", cuerpo: `<p class="muted" style="margin-top:0">Elegí el tipo de ejercicio. Después lo podés revisar y publicar.</p>
      <div class="elegir-tipo">${Object.entries(CAT.tipos).map(([k, t]) => `<a class="check" href="#/actividad-nueva/${k}"><span class="em">${t.i}</span><span><b>${esc(t.n)}</b><br><span class="muted" style="font-size:13px">${esc(t.desc)}</span></span></a>`).join("")}</div>`,
      botones: [{txt: "Cancelar", cls: "sec", valor: null}]});
  },
  refuerzo: async (el, e) => {
    e.stopPropagation();
    const tema = CAT.temas[el.dataset.t];
    if (!await confirmar("Asignar refuerzo", `Se crea una misión «Repaso: ${esc(tema.n)}» solo para <b>${esc(el.dataset.n)}</b>, con hasta 3 actividades de ese tema de su grado (primero las que menos estrellas tiene). Vence en 7 días.`, "Asignar")) return;
    const r = await llamar(() => api(`/api/docente/alumnos/${el.dataset.id}/refuerzo`, {method: "POST", body: {tema: el.dataset.t}}));
    if (r) { toast(`Misión creada: ${r.actividades.join(", ")}`); location.hash = "#/tarea/" + r.id; }
  },
  publicar: async el => {
    if (await llamar(() => api(`/api/docente/actividades/${encodeURIComponent(el.dataset.id)}/estado`, {method: "POST", body: {estado: "publicado"}}), "¡Publicado! Ya aparece en la isla.")) navegar();
  },
  despublicar: async el => {
    if (!await confirmar("Pasar a borrador", "Los chicos dejan de ver este cuento hasta que lo vuelvas a publicar. Sus resultados se conservan.")) return;
    if (await llamar(() => api(`/api/docente/actividades/${encodeURIComponent(el.dataset.id)}/estado`, {method: "POST", body: {estado: "borrador"}}), "Ahora es un borrador.")) navegar();
  },
  restablecer: async el => {
    if (!await confirmar("Restablecer contraseña", `Se genera una contraseña temporal para <b>${esc(el.dataset.n)}</b>. Su contraseña actual deja de funcionar y, al entrar con la temporal, va a tener que elegir una nueva.`, "Restablecer")) return;
    const r = await llamar(() => api(`/api/docente/docentes/${el.dataset.id}/restablecer`, {method: "POST"}));
    if (r) modal({titulo: "Contraseña temporal", cuerpo: `<p style="margin-top:0">Pasale estos datos a <b>${esc(el.dataset.n)}</b> (en persona o por un mensaje privado):</p>
      <p>Usuario: <b>@${esc(r.usuario)}</b></p><div class="codigo-rec">${esc(r.temporal)}</div>
      <p class="muted" style="font-size:13px;margin-bottom:0">No se vuelve a mostrar. Cuando entre, el panel le pide elegir una contraseña nueva.</p>`,
      botones: [{txt: "Listo", valor: true}]});
  },
  nuevoCodigo: async () => {
    if (YO.tiene_codigo && !await confirmar("Código de recuperación nuevo", "El código anterior deja de funcionar. ¿Generar uno nuevo?", "Generar")) return;
    const r = await llamar(() => api("/api/docente/codigo-recuperacion", {method: "POST"}));
    if (r) { YO.tiene_codigo = true; await mostrarCodigo(r.codigo); pAjustes(); }
  },
  verPass: el => {
    const i = el.parentElement.querySelector("input"), ver = i.type === "password";
    i.type = ver ? "text" : "password";
    el.querySelector("span").textContent = ver ? "Ocultar" : "Ver";
    el.setAttribute("aria-label", ver ? "Ocultar contraseña" : "Mostrar contraseña");
    el.classList.toggle("on", ver); i.focus();
  },
  borrarDocente: async el => {
    if (!await confirmar("Eliminar cuenta docente", `Se elimina la cuenta de ${esc(el.dataset.n)}. Los alumnos, misiones y resultados no se borran.`, "Eliminar", true)) return;
    if (await llamar(() => api(`/api/docente/docentes/${el.dataset.id}`, {method: "DELETE"}), "Cuenta eliminada.")) pAjustes();
  },
  probarVoz: () => {
    Voz.callar(); Voz.preferida = $("#selVoz").value;
    const sw = k => { const i = $(`[data-k="${k}"]`); return i ? i.checked : undefined; };
    Voz.hablar("¡Hola, chicos! Soy la voz de la Isla de los Cuentos. ¿Saben qué? Había una vez un perrito llamado Bobi que encontró una pelota roja en el jardín. ¡Qué contento se puso!",
               {lenta: !!sw("voz_lenta"), alegre: sw("voz_alegre") !== false});
  },
  guardarVoz: async () => { await llamar(() => api("/api/docente/config", {method: "PUT", body: {voz: $("#selVoz").value}}), "Voz guardada. Los chicos la van a escuchar en el juego."); },
  cfg: async el => { await llamar(() => api("/api/docente/config", {method: "PUT", body: {[el.dataset.k]: el.checked}}), "Ajuste guardado."); },
};

const FORM = {
  ingresar: async (f, d) => {
    try { await api("/api/docente/ingresar", {method: "POST", body: d}); YO = null; location.hash = "#/panel"; navegar(); }
    catch (e) { $("#err").textContent = e.message; f.password.value = ""; f.password.focus(); }
  },
  configurar: async (f, d) => {
    if (d.password !== d.password2) { $("#err").textContent = "Las contraseñas no coinciden."; return; }
    d.grados = $$("[name=grados]:checked", f).map(i => +i.value);
    if (!d.grados.length) { $("#err").textContent = "Elegí al menos un grado."; return; }
    const nueva = location.hash === "#/registro";
    try {
      const r = await api("/api/docente/configurar", {method: "POST", body: d});
      if (r.codigo) await mostrarCodigo(r.codigo);
      YO = null; location.hash = nueva ? "#/panel" : "#/alumnos"; navegar(); toast(nueva ? "¡Cuenta creada! Bienvenido/a al panel." : "¡Cuenta creada! Ahora agregá a tus alumnos.");
    }
    catch (e) { $("#err").textContent = e.message; }
  },
  observacion: async (f, d) => { if (await llamar(() => api(`/api/docente/alumnos/${f.dataset.id}/observaciones`, {method: "POST", body: d}), "Observación guardada.")) navegar(); },
  editarAlumno: async (f, d) => {
    d.activo = f.activo.checked;
    if (await llamar(() => api(`/api/docente/alumnos/${f.dataset.id}`, {method: "PUT", body: d}), "Datos guardados.")) navegar();
  },
  tarea: async f => {
    const d = Object.fromEntries(new FormData(f));
    d.actividades = $$("[name=act]:checked", f).map(i => i.value);
    d.alumnos = $$("[name=alumno]:checked", f).map(i => +i.value);
    try { const r = await api("/api/docente/tareas", {method: "POST", body: d}); toast("Misión creada. Los chicos ya la ven en «Mis misiones»."); location.hash = "#/tarea/" + r.id; }
    catch (e) { if (e.status === 401) return llamar(() => Promise.reject(e)); $("#err").textContent = e.message; }
  },
  actividad: async (f, _d, ev) => {
    try {
      const d = payloadActividad();
      d.publicar = !!(ev && ev.submitter && ev.submitter.value === "publicar");
      const r = BORRADOR.id ? await api("/api/docente/actividades/" + encodeURIComponent(BORRADOR.id), {method: "PUT", body: d})
                            : await api("/api/docente/actividades", {method: "POST", body: d});
      const id = BORRADOR.id || r.id, esCuento = BORRADOR.tipo === "cuento"; BORRADOR = null;
      toast(d.publicar ? "¡Publicado! Ya aparece en la isla." : "Guardado como borrador. Publicalo cuando esté listo.");
      location.hash = esCuento ? "#/cuentos" : "#/actividad/" + id;
    } catch (e) { if (e.status === 401) return llamar(() => Promise.reject(e)); $("#err").textContent = e.message; $("#err").scrollIntoView({block: "center"}); }
  },
  recuperar: async (f, d) => {
    if (d.nueva !== d.nueva2) { $("#err").textContent = "Las contraseñas nuevas no coinciden."; return; }
    try {
      const r = await api("/api/docente/recuperar", {method: "POST", body: d});
      await mostrarCodigo(r.codigo, "Listo. Este es tu código nuevo");
      YO = null; location.hash = "#/panel"; navegar(); toast("Contraseña cambiada. ¡Bienvenida de nuevo!");
    } catch (e) { $("#err").textContent = e.message; }
  },
  cambioObligatorio: async (f, d) => {
    if (d.nueva !== d.nueva2) { $("#err").textContent = "Las contraseñas no coinciden."; return; }
    try {
      await api("/api/docente/password", {method: "POST", body: {nueva: d.nueva}});
      YO.debe_cambiar = false; toast("Contraseña guardada.");
      if (!YO.tiene_codigo) { const r = await api("/api/docente/codigo-recuperacion", {method: "POST"}); YO.tiene_codigo = true; await mostrarCodigo(r.codigo); }
      navegar();
    } catch (e) { $("#err").textContent = e.message; }
  },
  misGrados: async f => {
    const grados = $$("[name=grados]:checked", f).map(i => +i.value);
    if (!grados.length) return toast("Elegí al menos un grado.", true);
    const r = await llamar(() => api("/api/docente/mis-grados", {method: "PUT", body: {grados}}), "Listo. Ahora ves " + nombreGrados(grados) + ".");
    if (r) { YO.grados = r.grados; UI.grado = ""; navegar(); }
  },
  password: async (f, d) => {
    if (d.nueva !== d.nueva2) { $("#err").textContent = "Las contraseñas nuevas no coinciden."; return; }
    try { await api("/api/docente/password", {method: "POST", body: d}); f.reset(); $("#err").textContent = ""; toast("Contraseña actualizada."); }
    catch (e) { $("#err").textContent = e.message; }
  },
};

document.addEventListener("click", e => {
  const el = e.target.closest("[data-act]");
  if (!el || (el.tagName === "INPUT" && el.type !== "button")) return;
  const f = A[el.dataset.act]; if (f) f(el, e);
});
document.addEventListener("change", e => {
  const el = e.target;
  if (el.matches("input[data-act]")) { const f = A[el.dataset.act]; if (f) f(el, e); return; }
  if (el.dataset.bind && BORRADOR) { fijar(BORRADOR, el.dataset.bind, el.value); if (el.dataset.redibujar) dibujarEditor(); }
  if (el.dataset.input) { UI[el.dataset.input] = el.value; pAlumnos(); }
});
let tBuscar = null;
document.addEventListener("input", e => {
  const el = e.target;
  if (el.dataset.bind && BORRADOR && el.tagName !== "SELECT") fijar(BORRADOR, el.dataset.bind, el.value);
  if (el.dataset.input === "buscar") {
    clearTimeout(tBuscar);
    tBuscar = setTimeout(async () => { UI.buscar = el.value; await pAlumnos(); const i = $("[data-input=buscar]"); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }, 250);
  }
});
document.addEventListener("submit", e => {
  const f = e.target.closest("[data-form]"); if (!f) return;
  e.preventDefault();
  FORM[f.dataset.form](f, Object.fromEntries(new FormData(f)), e);
});

(async () => {
  try { CAT = await cargarCatalogo(); Avatar.init(CAT.items); await navegar(); }
  catch (e) { $("#raiz").innerHTML = `<div class="acceso"><div class="caja"><h1>No se pudo abrir el panel</h1><p>${esc(e.message)}</p></div></div>`; }
})();
