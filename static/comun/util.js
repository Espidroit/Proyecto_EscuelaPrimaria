/* Utilidades compartidas por la interfaz de los chicos y la de la docente */
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const mezclar = a => { a = [...a]; for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const azar = a => a[Math.floor(Math.random() * a.length)];

/* Llamadas al servidor. Todas llevan la cabecera X-Isla (protección CSRF). */
async function api(url, {method = "GET", body} = {}) {
  const opts = {method, credentials: "same-origin", headers: {"X-Isla": "1"}};
  if (body !== undefined) { opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
  let r;
  try { r = await fetch(url, opts); }
  catch (e) { const err = new Error("No hay conexión con el servidor. ¿Está abierto el programa?"); err.status = 0; throw err; }
  let data = null;
  try { data = await r.json(); } catch (e) { /* sin cuerpo */ }
  if (!r.ok) { const err = new Error((data && data.error) || "Ocurrió un error."); err.status = r.status; throw err; }
  return data;
}

function fechaCorta(s) {
  if (!s) return "—";
  const d = new Date(s.replace(" ", "T"));
  return d.toLocaleDateString("es-AR", {day: "2-digit", month: "2-digit"});
}
function fechaHora(s) {
  if (!s) return "—";
  const d = new Date(s.replace(" ", "T"));
  return d.toLocaleDateString("es-AR", {day: "2-digit", month: "2-digit", year: "2-digit"}) + " " +
         d.toLocaleTimeString("es-AR", {hour: "2-digit", minute: "2-digit"});
}
function haceCuanto(s) {
  if (!s) return "nunca";
  const dias = Math.floor((Date.now() - new Date(s.replace(" ", "T")).getTime()) / 86400000);
  if (dias <= 0) return "hoy";
  if (dias === 1) return "ayer";
  if (dias < 7) return `hace ${dias} días`;
  if (dias < 30) return `hace ${Math.floor(dias / 7)} sem.`;
  return fechaCorta(s);
}
