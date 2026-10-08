/* =========================================================
   Dibujo del avatar en SVG (capas: fondo, capa, pelo de atrás,
   cuerpo, cabeza, pelo, cara, anteojos, gorro, mascota y marco).
   Avatar.init(catalogo.items) debe llamarse una vez.
   ========================================================= */
"use strict";

const Avatar = (() => {
  let porId = {};
  let n = 0;

  function init(items) { porId = {}; items.forEach(it => { porId[it.id] = it; }); }
  const item = (cat, v) => porId[cat + ":" + v] || {};

  function sombra(hex, f) {
    const h = (hex || "#999999").replace("#", "");
    const c = [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16));
    const r = c.map(x => Math.max(0, Math.min(255, Math.round(f < 0 ? x * (1 + f) : x + (255 - x) * f))));
    return "#" + r.map(x => x.toString(16).padStart(2, "0")).join("");
  }

  function svg(av, size = 120, {mascota = true} = {}) {
    const id = "av" + (++n);
    const piel = item("piel", av.piel).color || "#f6c9a0";
    const pelo = item("colorPelo", av.colorPelo).color || "#6b4226";
    const ropa = av.ropa === "guardapolvo" ? "#ffffff" : (item("colorRopa", av.colorRopa).color || "#3d8bfd");
    const acento = item("colorRopa", av.colorRopa).color || "#3d8bfd";
    const fondo = item("fondo", av.fondo);
    const pielOsc = sombra(piel, -0.18);
    const p = [];

    p.push(`<svg viewBox="0 0 200 200" width="${size}" height="${size}" role="img" aria-label="Avatar" xmlns="http://www.w3.org/2000/svg" class="avatar-svg">`);
    p.push(`<defs>
      <clipPath id="${id}c"><circle cx="100" cy="100" r="96"/></clipPath>
      <linearGradient id="${id}f" x1="0" y1="0" x2="0" y2="1">${av.fondo === "arcoiris"
        ? `<stop offset="0" stop-color="#ff9a9e"/><stop offset=".3" stop-color="#fecf71"/><stop offset=".55" stop-color="#a8e6a1"/><stop offset=".8" stop-color="#8fd3fe"/><stop offset="1" stop-color="#c3a6ff"/>`
        : `<stop offset="0" stop-color="${fondo.c1 || "#bfe6ff"}"/><stop offset="1" stop-color="${fondo.c2 || "#8fd0ff"}"/>`}</linearGradient>
      <linearGradient id="${id}r" x1="0" x2="1"><stop offset="0" stop-color="#ff6b6b"/><stop offset=".25" stop-color="#ffd166"/><stop offset=".5" stop-color="#06d6a0"/><stop offset=".75" stop-color="#4dabf7"/><stop offset="1" stop-color="#b197fc"/></linearGradient>
      <clipPath id="${id}s"><path d="M38 210 C40 162 66 144 100 144 C134 144 160 162 162 210Z"/></clipPath>
    </defs>`);

    // ---------- fondo ----------
    p.push(`<g clip-path="url(#${id}c)"><rect width="200" height="200" fill="url(#${id}f)"/>`);
    if (av.fondo === "espacio") p.push([[40, 40], [150, 30], [30, 120], [168, 110], [120, 20], [70, 170]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="2" fill="#fff" opacity=".9"/>`).join(""));
    if (av.fondo === "mar") p.push(`<path d="M0 170 Q25 160 50 170 T100 170 T150 170 T200 170 V200 H0Z" fill="#ffffff" opacity=".35"/>`);
    if (av.fondo === "bosque") p.push(`<path d="M0 175 L20 140 L40 175Z M160 175 L180 135 L200 175Z" fill="#2e8b57" opacity=".45"/>`);
    if (av.fondo === "atardecer") p.push(`<circle cx="160" cy="50" r="18" fill="#fff3b0" opacity=".8"/>`);
    if (av.fondo === "cielo") p.push(`<g fill="#fff" opacity=".7"><ellipse cx="40" cy="45" rx="18" ry="8"/><ellipse cx="160" cy="60" rx="16" ry="7"/></g>`);

    // ---------- capa (detrás) ----------
    if (av.ropa === "capa") p.push(`<path d="M58 150 L36 205 L164 205 L142 150Z" fill="#e8505b"/>`);

    // ---------- pelo de atrás ----------
    if (av.pelo === "largo") p.push(`<path d="M54 98 C48 44 152 44 146 98 L154 172 C132 184 68 184 46 172Z" fill="${pelo}"/>`);
    if (av.pelo === "colitas") p.push(`<circle cx="50" cy="104" r="19" fill="${pelo}"/><circle cx="150" cy="104" r="19" fill="${pelo}"/><circle cx="62" cy="96" r="5" fill="#ff6fa5"/><circle cx="138" cy="96" r="5" fill="#ff6fa5"/>`);
    if (av.pelo === "rodete") p.push(`<circle cx="100" cy="40" r="19" fill="${pelo}"/>`);

    // ---------- cuerpo ----------
    p.push(`<rect x="87" y="120" width="26" height="30" rx="9" fill="${pielOsc}"/>`);
    p.push(`<path d="M38 210 C40 162 66 144 100 144 C134 144 160 162 162 210Z" fill="${ropa}" ${av.ropa === "guardapolvo" ? 'stroke="#d5dbe5" stroke-width="2"' : ""}/>`);
    p.push(`<path d="M86 146 Q100 160 114 146" fill="none" stroke="${sombra(ropa, -0.25)}" stroke-width="4" stroke-linecap="round"/>`);
    const deco = {
      rayas: `<g clip-path="url(#${id}s)" fill="#ffffff" opacity=".45"><rect x="30" y="162" width="140" height="7"/><rect x="30" y="178" width="140" height="7"/><rect x="30" y="194" width="140" height="7"/></g>`,
      estrella: `<path d="M100 160 L105 172 L118 172 L108 180 L112 193 L100 185 L88 193 L92 180 L82 172 L95 172Z" fill="#fff" opacity=".85"/>`,
      corazon: `<path d="M100 192 C80 178 84 162 94 164 C98 165 100 169 100 171 C100 169 102 165 106 164 C116 162 120 178 100 192Z" fill="#fff" opacity=".85"/>`,
      rayo: `<path d="M104 158 L90 178 L100 178 L94 196 L112 172 L102 172 L108 158Z" fill="#ffd23f" stroke="#fff" stroke-width="1.5"/>`,
      capa: `<circle cx="100" cy="176" r="12" fill="#ffd23f"/><text x="100" y="182" font-size="15" text-anchor="middle" font-weight="bold" fill="#e8505b" font-family="sans-serif">★</text>`,
      guardapolvo: `<path d="M100 148 L88 196 M100 148 L112 196" stroke="#d5dbe5" stroke-width="2"/><path d="M90 150 L100 158 L110 150 L100 164Z" fill="${acento}"/>`,
    };
    p.push(deco[av.ropa] || "");

    // ---------- cabeza ----------
    p.push(`<circle cx="57" cy="100" r="10" fill="${piel}"/><circle cx="143" cy="100" r="10" fill="${piel}"/>`);
    p.push(`<ellipse cx="100" cy="94" rx="43" ry="45" fill="${piel}"/>`);

    // ---------- pelo de adelante ----------
    const peinados = {
      corto: `<path d="M56 94 C52 50 80 38 100 38 C124 38 150 52 144 94 C139 74 128 63 112 61 C102 71 84 73 70 69 C63 76 59 84 56 94Z" fill="${pelo}"/>`,
      largo: `<path d="M55 100 C50 50 82 38 100 38 C120 38 150 50 145 100 C140 78 130 66 118 62 C108 70 88 72 74 66 C64 76 58 86 55 100Z" fill="${pelo}"/>`,
      colitas: `<path d="M56 94 C52 50 80 38 100 38 C124 38 150 52 144 94 C138 72 120 60 100 60 C80 60 62 72 56 94Z" fill="${pelo}"/>`,
      rodete: `<path d="M57 90 C57 54 82 46 100 46 C120 46 143 54 143 90 C134 70 118 62 100 62 C82 62 66 70 57 90Z" fill="${pelo}"/>`,
      rulos: [[-170, 15], [-150, 15], [-130, 15], [-110, 15], [-90, 15], [-70, 15], [-50, 15], [-30, 15], [-10, 15]].map(([g, r]) => {
        const a = g * Math.PI / 180;
        return `<circle cx="${(100 + 44 * Math.cos(a)).toFixed(1)}" cy="${(88 + 44 * Math.sin(a)).toFixed(1)}" r="${r}" fill="${pelo}"/>`;
      }).join("") + `<circle cx="84" cy="56" r="14" fill="${pelo}"/><circle cx="116" cy="56" r="14" fill="${pelo}"/>`,
      punk: `<path d="M86 64 L88 18 L98 40 L104 14 L110 40 L120 22 L116 64 C106 58 96 58 86 64Z" fill="${pelo}"/>`,
      pelado: `<path d="M60 84 C62 50 138 50 140 84 C128 66 72 66 60 84Z" fill="${pelo}" opacity=".55"/>`,
    };
    p.push(peinados[av.pelo] || peinados.corto);

    // ---------- cara ----------
    p.push(`<path d="M76 82 Q84 77 92 82 M108 82 Q116 77 124 82" stroke="${sombra(pelo, -0.1)}" stroke-width="3.5" fill="none" stroke-linecap="round"/>`);
    const ojoN = (x) => `<circle cx="${x}" cy="97" r="6" fill="#2b2b3a"/><circle cx="${x + 2}" cy="95" r="2" fill="#fff"/>`;
    const ojoF = (x) => `<path d="M${x - 7} 99 Q${x} 90 ${x + 7} 99" stroke="#2b2b3a" stroke-width="3.8" fill="none" stroke-linecap="round"/>`;
    const ojos = {
      normal: ojoN(84) + ojoN(116),
      felices: ojoF(84) + ojoF(116),
      grandes: [84, 116].map(x => `<ellipse cx="${x}" cy="96" rx="9" ry="10" fill="#fff" stroke="#2b2b3a" stroke-width="1.5"/><circle cx="${x}" cy="97" r="6.5" fill="#3b2a1e"/><circle cx="${x + 2.5}" cy="94" r="2.6" fill="#fff"/><circle cx="${x - 2}" cy="100" r="1.2" fill="#fff"/>`).join(""),
      guino: ojoN(84) + ojoF(116),
    };
    p.push(ojos[av.ojos] || ojos.normal);
    p.push(`<ellipse cx="74" cy="112" rx="7.5" ry="4.5" fill="#ff7a7a" opacity=".35"/><ellipse cx="126" cy="112" rx="7.5" ry="4.5" fill="#ff7a7a" opacity=".35"/>`);
    p.push(`<path d="M97 106 Q100 109 103 106" stroke="${pielOsc}" stroke-width="2.5" fill="none" stroke-linecap="round"/>`);
    const bocas = {
      sonrisa: `<path d="M88 116 Q100 127 112 116" stroke="#7a2f2f" stroke-width="3.6" fill="none" stroke-linecap="round"/>`,
      contenta: `<path d="M86 114 Q100 134 114 114Z" fill="#7a2f2f"/><path d="M89 115 L111 115 L109 119 L91 119Z" fill="#fff"/>`,
      lengua: `<path d="M88 115 Q100 126 112 115" stroke="#7a2f2f" stroke-width="3.6" fill="none" stroke-linecap="round"/><path d="M95 120 Q100 132 105 120Z" fill="#ff7b93"/>`,
      sorpresa: `<ellipse cx="100" cy="119" rx="6" ry="8" fill="#7a2f2f"/>`,
    };
    p.push(bocas[av.boca] || bocas.sonrisa);

    // ---------- anteojos ----------
    const lentes = {
      redondos: `<g stroke="#2b2b3a" stroke-width="3" fill="#ffffff" fill-opacity=".2"><circle cx="84" cy="97" r="13"/><circle cx="116" cy="97" r="13"/></g><path d="M97 96 Q100 93 103 96" stroke="#2b2b3a" stroke-width="3" fill="none"/>`,
      sol: `<rect x="68" y="88" width="30" height="20" rx="8" fill="#1f2433"/><rect x="102" y="88" width="30" height="20" rx="8" fill="#1f2433"/><path d="M98 95 L102 95" stroke="#1f2433" stroke-width="3"/><path d="M74 93 L82 93" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".6"/>`,
      corazon: [84, 116].map(x => `<path d="M${x} 108 C${x - 16} 98 ${x - 12} 84 ${x - 5} 86 C${x - 2} 87 ${x} 90 ${x} 92 C${x} 90 ${x + 2} 87 ${x + 5} 86 C${x + 12} 84 ${x + 16} 98 ${x} 108Z" fill="#ff4f8b" opacity=".9"/>`).join("") + `<path d="M96 95 L104 95" stroke="#ff4f8b" stroke-width="3"/>`,
    };
    p.push(lentes[av.anteojos] || "");

    // ---------- gorros ----------
    const gorros = {
      gorra: `<path d="M55 78 C55 34 145 34 145 78Z" fill="${acento}"/><path d="M118 74 C140 68 168 72 174 82 C152 86 130 84 118 80Z" fill="${sombra(acento, -0.2)}"/><circle cx="100" cy="40" r="5" fill="${sombra(acento, -0.2)}"/>`,
      mono: `<path d="M128 50 L106 36 L108 64Z" fill="#ff6fa5"/><path d="M128 50 L150 36 L148 64Z" fill="#ff6fa5"/><circle cx="128" cy="50" r="7" fill="#e84f8a"/>`,
      flores: [[66, 64], [80, 50], [100, 44], [120, 50], [134, 64]].map(([x, y], i) => {
        const col = ["#ff8fab", "#ffd166", "#a0c4ff", "#ff8fab", "#ffd166"][i];
        return `<g>${[0, 72, 144, 216, 288].map(g => `<circle cx="${(x + 6 * Math.cos(g * Math.PI / 180)).toFixed(1)}" cy="${(y + 6 * Math.sin(g * Math.PI / 180)).toFixed(1)}" r="5" fill="${col}"/>`).join("")}<circle cx="${x}" cy="${y}" r="3.5" fill="#fff3b0"/></g>`;
      }).join(""),
      auriculares: `<path d="M54 96 C52 30 148 30 146 96" stroke="#3b3f52" stroke-width="8" fill="none" stroke-linecap="round"/><rect x="44" y="84" width="18" height="30" rx="8" fill="${acento}"/><rect x="138" y="84" width="18" height="30" rx="8" fill="${acento}"/>`,
      mago: `<path d="M64 62 L102 -4 L136 62Z" fill="#5b3fc4"/><ellipse cx="100" cy="62" rx="50" ry="9" fill="#4a2fb0"/><text x="92" y="40" font-size="14" fill="#ffd23f" font-family="sans-serif">★</text><text x="108" y="22" font-size="10" fill="#ffd23f" font-family="sans-serif">★</text>`,
      corona: `<path d="M64 60 L68 26 L86 44 L100 20 L114 44 L132 26 L136 60Z" fill="#ffcf33" stroke="#e0a800" stroke-width="2.5" stroke-linejoin="round"/><circle cx="100" cy="48" r="5" fill="#e8505b"/><circle cx="80" cy="52" r="3.5" fill="#3d8bfd"/><circle cx="120" cy="52" r="3.5" fill="#3bb273"/>`,
      astronauta: `<circle cx="100" cy="94" r="64" fill="#bfe6ff" fill-opacity=".22" stroke="#e8eef6" stroke-width="7"/><path d="M58 70 Q66 46 90 38" stroke="#fff" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/><rect x="66" y="148" width="68" height="14" rx="7" fill="#d9e1ea"/>`,
    };
    p.push(gorros[av.gorro] || "");
    p.push(`</g>`);

    // ---------- marco ----------
    const marcos = {
      ninguno: `<circle cx="100" cy="100" r="96" fill="none" stroke="#26324a" stroke-width="5"/>`,
      plata: `<circle cx="100" cy="100" r="95" fill="none" stroke="#aeb7c4" stroke-width="9"/><circle cx="100" cy="100" r="95" fill="none" stroke="#eef1f5" stroke-width="3"/>`,
      oro: `<circle cx="100" cy="100" r="95" fill="none" stroke="#e0a800" stroke-width="10"/><circle cx="100" cy="100" r="95" fill="none" stroke="#ffe27a" stroke-width="4"/>`,
      estrellas: `<circle cx="100" cy="100" r="95" fill="none" stroke="#5b3fc4" stroke-width="9"/>` +
        [0, 45, 90, 135, 180, 225, 270, 315].map(g => `<text x="${(100 + 95 * Math.cos(g * Math.PI / 180)).toFixed(1)}" y="${(100 + 95 * Math.sin(g * Math.PI / 180) + 5).toFixed(1)}" font-size="16" text-anchor="middle" fill="#ffd23f" font-family="sans-serif">★</text>`).join(""),
      arcoiris: `<circle cx="100" cy="100" r="95" fill="none" stroke="url(#${id}r)" stroke-width="10"/>`,
    };
    p.push(marcos[av.marco] || marcos.ninguno);

    // ---------- mascota ----------
    const pet = item("mascota", av.mascota).e;
    if (mascota && pet) p.push(`<circle cx="163" cy="166" r="26" fill="#ffffff" stroke="#26324a" stroke-width="3"/><text x="163" y="178" font-size="32" text-anchor="middle">${pet}</text>`);

    p.push(`</svg>`);
    return p.join("");
  }

  return {init, svg, item};
})();
