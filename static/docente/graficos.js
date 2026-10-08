/* Gráficos SVG simples para el panel docente (línea con tooltip y barras por tema). */
"use strict";

const Graficos = (() => {
  const datos = new Map();
  let n = 0;

  function nivel(p) {
    if (p === null || p === undefined) return {cls: "nd", txt: "Sin datos", ic: "—", color: "#c3c9d5"};
    if (p >= 80) return {cls: "ok", txt: "Logrado", ic: "✓", color: "#2e9b62"};
    if (p >= 50) return {cls: "warn", txt: "En proceso", ic: "◐", color: "#e0a419"};
    return {cls: "bad", txt: "A reforzar", ic: "!", color: "#d64a3a"};
  }
  function pill(p, conValor = true) {
    const e = nivel(p);
    return `<span class="estado e-${e.cls}"><span class="ic">${e.ic}</span>${conValor && p !== null && p !== undefined ? p + "% · " : ""}${e.txt}</span>`;
  }
  const semana = s => { const d = new Date(s + "T00:00"); return d.toLocaleDateString("es-AR", {day: "2-digit", month: "2-digit"}); };

  /* serie: [{semana:"2026-09-28", pct: 72, n: 18}] */
  function linea(serie, {alto = 230, titulo = "Porcentaje de respuestas correctas a la primera"} = {}) {
    if (!serie || !serie.length) return `<div class="vacio"><b>Todavía no hay datos</b>Cuando los chicos jueguen, acá vas a ver cómo evolucionan semana a semana.</div>`;
    const id = "g" + (++n);
    datos.set(id, serie);
    const W = 640, H = alto, L = 42, R = 22, T = 16, B = 30;
    const iw = W - L - R, ih = H - T - B;
    const x = i => serie.length === 1 ? L + iw / 2 : L + i * iw / (serie.length - 1);
    const y = v => T + ih - v / 100 * ih;
    const grid = [0, 25, 50, 75, 100].map(v => `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="${v === 0 ? "#cfd6e3" : "#eef1f6"}" stroke-width="1"/>` +
      (v % 50 === 0 ? `<text x="${L - 8}" y="${y(v) + 4}" text-anchor="end" font-size="11" fill="#76819a">${v}%</text>` : "")).join("");
    const paso = serie.length > 8 ? 2 : 1;
    const xs = serie.map((s, i) => (i % paso === 0 || i === serie.length - 1) ? `<text x="${x(i)}" y="${H - 8}" text-anchor="middle" font-size="11" fill="#76819a">${semana(s.semana)}</text>` : "").join("");
    const pts = serie.map((s, i) => `${x(i)},${y(s.pct)}`).join(" ");
    const area = serie.length > 1 ? `<polygon points="${x(0)},${y(0)} ${pts} ${x(serie.length - 1)},${y(0)}" fill="#2a78d6" opacity=".08"/>` : "";
    const ult = serie[serie.length - 1];
    const ancho = serie.length === 1 ? iw : iw / (serie.length - 1);
    const hits = serie.map((s, i) => `<rect x="${x(i) - ancho / 2}" y="${T}" width="${ancho}" height="${ih}" fill="transparent" data-i="${i}"/>`).join("");
    return `
    <div class="grafico" data-graf="${id}">
      <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${titulo}">
        ${grid}${xs}${area}
        ${serie.length > 1 ? `<polyline points="${pts}" fill="none" stroke="#2a78d6" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>` : ""}
        <line class="cruz" x1="0" x2="0" y1="${T}" y2="${T + ih}" stroke="#8a94a6" stroke-dasharray="3 3" opacity="0"/>
        ${serie.map((s, i) => `<circle cx="${x(i)}" cy="${y(s.pct)}" r="4.5" fill="#fff" stroke="#2a78d6" stroke-width="2"/>`).join("")}
        <text x="${x(serie.length - 1) + (serie.length === 1 ? 0 : -2)}" y="${y(ult.pct) - 12}" text-anchor="${serie.length === 1 ? "middle" : "end"}" font-size="12.5" font-weight="700" fill="#0f1b2d">${ult.pct}%</text>
        <g class="hits">${hits}</g>
      </svg>
      <div class="tt hidden"></div>
      <details class="ver-datos"><summary>Ver los datos en tabla</summary>
        <table><thead><tr><th>Semana del</th><th class="r">Correctas a la primera</th><th class="r">Respuestas</th></tr></thead>
        <tbody>${serie.map(s => `<tr><td>${semana(s.semana)}</td><td class="r num">${s.pct}%</td><td class="r num">${s.n}</td></tr>`).join("")}</tbody></table>
      </details>
    </div>`;
  }

  function activar(raiz = document) {
    raiz.querySelectorAll("[data-graf]").forEach(g => {
      if (g.dataset.on) return; g.dataset.on = "1";
      const serie = datos.get(g.dataset.graf), svg = g.querySelector("svg"), tt = g.querySelector(".tt"), cruz = g.querySelector(".cruz");
      const mostrar = i => {
        const s = serie[i], c = svg.querySelectorAll("circle")[i];
        const cx = +c.getAttribute("cx"), cy = +c.getAttribute("cy");
        const k = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
        cruz.setAttribute("x1", cx); cruz.setAttribute("x2", cx); cruz.setAttribute("opacity", "1");
        tt.innerHTML = `Semana del ${semana(s.semana)}<br><b>${s.pct}%</b> correctas a la primera · ${s.n} respuestas`;
        tt.style.left = cx * k + "px"; tt.style.top = cy * k + "px"; tt.classList.remove("hidden");
      };
      g.querySelectorAll(".hits rect").forEach(r => {
        r.addEventListener("mouseenter", () => mostrar(+r.dataset.i));
        r.addEventListener("touchstart", () => mostrar(+r.dataset.i), {passive: true});
      });
      svg.addEventListener("mouseleave", () => { tt.classList.add("hidden"); cruz.setAttribute("opacity", "0"); });
    });
  }

  /* filas: [{n, i, pct, cant}] */
  function barras(filas) {
    if (!filas.length) return `<div class="vacio">No hay temas activos.</div>`;
    return `<div class="barras">${filas.map(f => {
      const e = nivel(f.pct);
      return `<div class="fila-barra" title="${esc(f.n)}: ${f.pct === null ? "sin datos" : f.pct + "%"} (${f.cant || 0} respuestas)">
        <span class="n">${f.i || ""} ${esc(f.n)}</span>
        <span class="pista"><i style="width:${f.pct || 0}%;background:${e.color}"></i></span>
        <span class="v">${f.pct === null ? `<span class="muted">sin datos</span>` : `<b>${f.pct}%</b> <span class="muted">· ${f.cant}</span>`}</span>
      </div>`;
    }).join("")}</div>`;
  }

  return {linea, activar, barras, nivel, pill};
})();
