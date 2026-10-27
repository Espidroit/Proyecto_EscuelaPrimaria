"""
La Isla de los Cuentos — servidor (Python + Flask + SQLite)

  Chicos:   http://localhost:5000/
  Docente:  http://localhost:5000/docente

Uso:
  python app.py                 -> solo en esta computadora
  python app.py --red           -> también desde otras computadoras de la misma red (aula)
  python app.py --puerto 8080   -> otro puerto
"""
import argparse
import csv
import io
import json
import os
import re
import secrets
import socket
import sqlite3
import tempfile
import threading
import time
import webbrowser
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, abort, g, jsonify, request, send_file, send_from_directory, session

import contenido as C
import database as db
import seguridad as seg

BASE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(BASE, "static")

app = Flask(__name__, static_folder=STATIC, static_url_path="/static")
app.config.update(
    SECRET_KEY=seg.clave_secreta(db.CARPETA_DATOS),
    SESSION_COOKIE_NAME="isla_sesion",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
    JSON_AS_ASCII=False,
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)
app.json.ensure_ascii = False

LIMITE_DOCENTE = seg.LimiteIntentos(maximo=5, ventana=600, bloqueo=600)
LIMITE_ALUMNO = seg.LimiteIntentos(maximo=6, ventana=300, bloqueo=120)
INACTIVIDAD = {"docente": 30 * 60, "alumno": 3 * 60 * 60}
ESPERA_INTENTO = 3  # segundos mínimos entre dos resultados guardados por el mismo chico
ORDEN_TIPOS = list(C.TIPOS.keys())


# =================================================================
# Infraestructura
# =================================================================
def con_db():
    return db.conectar()


def existe(con, tabla, id_):
    return con.execute(f"SELECT 1 FROM {tabla} WHERE id=?", (id_,)).fetchone() is not None


def error(msg, codigo=400):
    return jsonify({"error": msg}), codigo


def ip():
    return request.remote_addr or "?"


@app.before_request
def proteger():
    if not request.path.startswith("/api/"):
        return None
    # Protección contra pedidos falsificados desde otros sitios (CSRF)
    if request.method in ("POST", "PUT", "DELETE"):
        if request.headers.get("X-Isla") != "1":
            return error("Pedido no permitido.", 403)
        origen = request.headers.get("Origin")
        if origen and origen.split("://", 1)[-1] != request.host:
            return error("Origen no permitido.", 403)
    # Cierre de sesión por inactividad
    rol = session.get("rol")
    if rol:
        if time.time() - session.get("t", 0) > INACTIVIDAD.get(rol, 0):
            session.clear()
        else:
            session["t"] = time.time()
    return None


@app.after_request
def despues(resp):
    return seg.cabeceras(resp)


def requiere(rol):
    def deco(f):
        @wraps(f)
        def envuelta(*a, **k):
            if session.get("rol") != rol or not session.get("uid"):
                return error("Necesitás iniciar sesión.", 401)
            return f(*a, **k)
        return envuelta
    return deco


# -----------------------------------------------------------------
# Grados de la docente: cada una ve y maneja solo a los alumnos de sus grados
# -----------------------------------------------------------------
def leer_grados(v):
    """Lista de grados elegidos ([1, 3]) → "1,3". Lanza ValueError si no sirve."""
    if not isinstance(v, list) or not v or any(str(x) not in ("1", "2", "3") for x in v):
        raise ValueError("Elegí al menos un grado (1.º, 2.º o 3.º).")
    return ",".join(sorted({str(x) for x in v}))


def mis_grados(con):
    """Grados a cargo de la docente que tiene la sesión abierta, como tupla (1, 2)."""
    if "grados" not in g:
        r = con.execute("SELECT grados FROM docentes WHERE id=?", (session.get("uid"),)).fetchone()
        g.grados = tuple(int(x) for x in (r[0] if r and r[0] else "1,2,3").split(","))
    return g.grados


def sql_grados(con, col="grado"):
    """Filtro SQL «grado IN (…)» con los grados de la docente, y sus parámetros."""
    gs = mis_grados(con)
    return f"{col} IN ({','.join('?' * len(gs))})", gs


def sql_mios(con, col="alumno_id"):
    """Filtro SQL para tablas con alumno_id: solo alumnos de los grados de la docente."""
    gs = mis_grados(con)
    return f"{col} IN (SELECT id FROM alumnos WHERE grado IN ({','.join('?' * len(gs))}))", gs


def alumno_mio(con, aid):
    """El alumno, si es de un grado de la docente; si no, None (como si no existiera)."""
    f, p = sql_grados(con)
    r = con.execute(f"SELECT * FROM alumnos WHERE id=? AND {f}", (aid, *p)).fetchone()
    return dict(r) if r else None


def tarea_mia(con, t):
    """La tarea es de alguno de mis grados (las viejas, sin grados, las ven todas)."""
    return not t["grados"] or bool(set(int(x) for x in t["grados"].split(",")) & set(mis_grados(con)))


def nombre_grados(gs):
    gs = [f"{x}.º" for x in gs]
    return gs[0] + " grado" if len(gs) == 1 else ", ".join(gs[:-1]) + " y " + gs[-1] + " grado"


def cuerpo():
    d = request.get_json(silent=True)
    return d if isinstance(d, dict) else {}


def texto(v, maximo=200):
    return str(v or "").strip()[:maximo]


def entero(v, minimo, maximo):
    """Número entero dentro del rango, o None si no lo es (no acepta True/False ni decimales)."""
    if isinstance(v, bool):
        return None
    try:
        n = int(str(v).strip())
    except (TypeError, ValueError):
        return None
    return n if minimo <= n <= maximo else None


def si_no(d, clave, actual):
    """Valor de un interruptor: tiene que venir como true o false."""
    v = d.get(clave, actual)
    if not isinstance(v, bool):
        raise ValueError("Valor inválido para «%s»." % clave)
    return v


LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"
RE_NOMBRE = re.compile(rf"[{LETRAS}][{LETRAS} .'-]*")


def nombre_alumno(v):
    """Nombre limpio, o lanza ValueError con el motivo."""
    n = re.sub(r"\s+", " ", str(v or "")).strip()
    if len(n) > 40:
        raise ValueError(f"El nombre «{n[:40]}…» es muy largo (máximo 40 letras).")
    if not RE_NOMBRE.fullmatch(n):
        raise ValueError(f"El nombre «{n}» solo puede tener letras, espacios, puntos o guiones.")
    return n


def fecha_limite(v):
    """Fecha AAAA-MM-DD que existe y no es anterior a hoy, o None si viene vacía."""
    s = texto(v, 10)
    if not s:
        return None
    try:
        f = date.fromisoformat(s) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s) else None
    except ValueError:
        f = None
    if not f:
        raise ValueError("La fecha límite no es válida.")
    if f < date.today():
        raise ValueError("La fecha límite no puede ser anterior a hoy.")
    if f > date.today() + timedelta(days=366):
        raise ValueError("La fecha límite no puede ser dentro de más de un año.")
    return s


# =================================================================
# Actividades (base + creadas por la docente)
# =================================================================
def todas_actividades(con):
    acts = [dict(a) for a in C.ACTIVIDADES_BASE]
    for r in con.execute("SELECT id, tipo, datos, creado FROM actividades_custom ORDER BY creado"):
        d = json.loads(r["datos"])
        d.setdefault("estado", "publicado")
        d.update({"id": r["id"], "tipo": r["tipo"], "base": False, "creado": r["creado"]})
        acts.append(d)
    return acts


def actividad(con, aid):
    return next((a for a in todas_actividades(con) if a["id"] == aid), None)


def items_validos(act, cfg):
    """Devuelve {idx: tema} con los ítems que se juegan según los temas activos."""
    off = set(cfg["temas_off"])
    if act["tipo"] == "cuento":
        todos = {i: q["tema"] for i, q in enumerate(act["preguntas"])}
        activos = {i: t for i, t in todos.items() if t not in off}
        return activos or todos
    tema = C.TIPOS[act["tipo"]]["tema"]
    return {i: tema for i in range(len(act["items"]))}


def tema_juego_activo(act, cfg):
    off = set(cfg["temas_off"])
    if act["tipo"] == "cuento":
        # Si la docente apagó los temas de todas sus preguntas, el cuento no aparece en el juego libre
        return any(q["tema"] not in off for q in act["preguntas"])
    return C.TIPOS[act["tipo"]]["tema"] not in off


def niveles_para(grado, cfg):
    if grado == 1:
        return (1, 2) if cfg["nivel2_para_1"] else (1,)
    if grado == 2:
        return (1, 2, 3) if cfg["nivel3_para_2"] else (1, 2)
    return (1, 2, 3)


def visibles_para(con, alumno, cfg):
    niveles = niveles_para(alumno["grado"], cfg)
    acts = [a for a in todas_actividades(con)
            if a["id"] not in cfg["ocultas"] and int(a["nivel"]) in niveles and tema_juego_activo(a, cfg)
            and a.get("estado", "publicado") == "publicado"]
    acts.sort(key=lambda a: (ORDEN_TIPOS.index(a["tipo"]), int(a["nivel"])))
    return acts


def mejores_estrellas(con, alumno_id):
    return {r[0]: r[1] for r in con.execute(
        "SELECT actividad_id, MAX(estrellas) FROM intentos WHERE alumno_id=? GROUP BY actividad_id", (alumno_id,))}


def texto_item(act, idx):
    try:
        if act["tipo"] == "cuento":
            q = act["preguntas"][idx]
            return ("Ordenar la secuencia del cuento" if q["t"] == "o"
                    else f"¿Verdadero o falso? «{q['p']}»" if q["t"] == "vf" else q["p"])
        it = act["items"][idx]
        if act["tipo"] == "oraciones":
            return f"Ordenar: «{it['t']}»"
        if act["tipo"] == "rimas":
            return f"¿Qué rima con «{it['p']}»?"
        if act["tipo"] == "silabas":
            return f"Armar con sílabas «{it['p']}»"
        if act["tipo"] == "completar":
            return f"Completar: «{it['t'].replace('_', '___')}»"
        if act["tipo"] == "opuestos":
            return f"{'Lo contrario de' if it['r'] == 'opuesto' else 'Parecida a'} «{it['p']}»"
        if act["tipo"] == "ortografia":
            return f"¿Qué letra falta? «{it['p'].replace('_', '__')}»"
        if act["tipo"] == "clases":
            return f"¿Qué clase de palabra es «{it['p']}»?"
        return f"Escribir «{it['p']}»"
    except (IndexError, KeyError):
        return "(ítem modificado)"


def resumen_actividad(act):
    temas = sorted({q["tema"] for q in act["preguntas"]}) if act["tipo"] == "cuento" else [C.TIPOS[act["tipo"]]["tema"]]
    n = len(act["preguntas"] if act["tipo"] == "cuento" else act["items"])
    return {"id": act["id"], "tipo": act["tipo"], "titulo": act["titulo"], "e": act.get("e", "📖"),
            "sticker": act.get("sticker", "⭐"), "nivel": int(act["nivel"]), "temas": temas, "n": n,
            "base": act.get("base", False), "estado": act.get("estado", "publicado"), "autor": act.get("autor"),
            "editado_por": act.get("editado_por"), "creado": act.get("creado"), "actualizado": act.get("actualizado")}


# =================================================================
# Tareas
# =================================================================
def asignados(con, tarea):
    if tarea["destino"] == "todos":
        gs = [int(x) for x in (tarea.get("grados") or "1,2,3").split(",")]
        q = con.execute(f"SELECT id FROM alumnos WHERE activo=1 AND grado IN ({','.join('?' * len(gs))})", gs)
    elif tarea["destino"] in ("grado1", "grado2", "grado3"):
        q = con.execute("SELECT id FROM alumnos WHERE activo=1 AND grado=?", (int(tarea["destino"][-1]),))
    else:
        q = con.execute("SELECT a.id FROM tarea_alumnos ta JOIN alumnos a ON a.id=ta.alumno_id "
                        "WHERE ta.tarea_id=? AND a.activo=1", (tarea["id"],))
    return [r[0] for r in q]


def actividades_tarea(con, tarea_id, acts_por_id):
    ids = [r[0] for r in con.execute(
        "SELECT actividad_id FROM tarea_actividades WHERE tarea_id=? ORDER BY orden", (tarea_id,))]
    return [acts_por_id[i] for i in ids if i in acts_por_id]


def tareas_de_alumno(con, alumno, solo_activas=True):
    # Las actividades que volvieron a borrador no se muestran a los chicos (tampoco dentro de las tareas)
    acts_por_id = {a["id"]: a for a in todas_actividades(con) if a.get("estado", "publicado") == "publicado"}
    res = []
    for t in con.execute("SELECT * FROM tareas WHERE archivada=0 ORDER BY creada DESC"):
        t = dict(t)
        if alumno["id"] not in asignados(con, t):
            continue
        acts = actividades_tarea(con, t["id"], acts_por_id)
        if not acts:
            continue
        hechas = {r[0]: r[1] for r in con.execute(
            "SELECT actividad_id, MAX(estrellas) FROM intentos WHERE alumno_id=? AND tarea_id=? GROUP BY actividad_id",
            (alumno["id"], t["id"]))}
        entrega = con.execute("SELECT fecha FROM tarea_entregas WHERE tarea_id=? AND alumno_id=?",
                              (t["id"], alumno["id"])).fetchone()
        res.append({"id": t["id"], "titulo": t["titulo"], "consigna": t["consigna"], "fecha_limite": t["fecha_limite"],
                    "recompensa": t["recompensa"], "entregada": entrega[0] if entrega else None,
                    "actividades": [{**resumen_actividad(a), "estrellas": hechas.get(a["id"], 0)} for a in acts]})
    return res


# =================================================================
# Medallas, avatar y perfil
# =================================================================
def evaluar_medallas(con, alumno_id):
    acts = {a["id"]: a for a in todas_actividades(con)}
    mejores = mejores_estrellas(con, alumno_id)
    cuentos = sum(1 for a in mejores if a in acts and acts[a]["tipo"] == "cuento")
    juegos = sum(1 for a in mejores if a in acts and acts[a]["tipo"] != "cuento")
    perfectos = sum(1 for v in mejores.values() if v >= 3)
    n_int = con.execute("SELECT COUNT(*) FROM intentos WHERE alumno_id=?", (alumno_id,)).fetchone()[0]
    tareas = con.execute("SELECT COUNT(*) FROM tarea_entregas WHERE alumno_id=?", (alumno_id,)).fetchone()[0]
    por_tema = {r[0]: r[1] or 0 for r in con.execute(
        "SELECT tema, SUM(primera) FROM respuestas WHERE alumno_id=? GROUP BY tema", (alumno_id,))}
    cumple = {"m1": cuentos >= 1, "m3": cuentos >= 3, "m6": cuentos >= 6, "j3": juegos >= 3,
              "perf": perfectos >= 1, "perf3": perfectos >= 5, "rep": n_int > len(mejores),
              "t1": tareas >= 1, "t5": tareas >= 5}
    for k in C.TEMAS:
        cumple["tema-" + k] = por_tema.get(k, 0) >= 5
    tiene = {r[0] for r in con.execute("SELECT medalla_id FROM medallas WHERE alumno_id=?", (alumno_id,))}
    nuevas = []
    for mid, ok in cumple.items():
        if ok and mid not in tiene:
            con.execute("INSERT INTO medallas VALUES(?,?,?)", (alumno_id, mid, db.ahora()))
            nuevas.append(C.MEDALLAS_POR_ID[mid])
    return nuevas


def medallas_posibles(con, alumno, cfg):
    """Medallas que este chico puede ganar con las actividades que tiene a su alcance."""
    vis = visibles_para(con, alumno, cfg) + [x for t in tareas_de_alumno(con, alumno) for x in t["actividades"]]
    acts = {a["id"]: a for a in todas_actividades(con)}
    vis = [acts[a["id"]] for a in vis if a["id"] in acts]
    ids = {a["id"] for a in vis}
    juegos = len({a["id"] for a in vis if a["tipo"] != "cuento"})
    cuentos = len({a["id"] for a in vis if a["tipo"] == "cuento"})
    off = set(cfg["temas_off"])
    temas = set()
    for a in vis:
        if a["tipo"] == "cuento":
            temas |= {q["tema"] for q in a["preguntas"] if q["tema"] not in off}
        else:
            temas.add(C.TIPOS[a["tipo"]]["tema"])
    posibles = {"m1": cuentos >= 1, "m3": cuentos >= 3, "m6": cuentos >= 6, "j3": juegos >= 3,
                "perf": bool(ids), "perf3": len(ids) >= 5, "rep": bool(ids), "t1": True, "t5": True}
    posibles.update({"tema-" + k: k in temas for k in C.TEMAS})
    return {k for k, v in posibles.items() if v}


def estado_items(con, alumno):
    inv = {r[0] for r in con.execute("SELECT item_id FROM inventario WHERE alumno_id=?", (alumno["id"],))}
    meds = {r[0] for r in con.execute("SELECT medalla_id FROM medallas WHERE alumno_id=?", (alumno["id"],))}
    nivel = C.nivel_de(alumno["xp"]) + 1
    estados = {}
    for it in C.CATALOGO:
        if it["medalla"]:
            ok = it["medalla"] in meds
            req = f"Medalla «{C.MEDALLAS_POR_ID[it['medalla']]['n']}»"
        elif it["nivel"]:
            ok = nivel >= it["nivel"]
            req = f"Nivel {it['nivel']}"
        elif it["precio"]:
            ok = it["id"] in inv
            req = None
        else:
            ok, req = True, None
        estados[it["id"]] = {"tiene": ok, "req": None if ok else req}
    return estados


def avatar_de(alumno):
    try:
        av = json.loads(alumno["avatar"])
    except (ValueError, TypeError):
        av = {}
    return {**C.AVATAR_INICIAL, **{k: v for k, v in av.items() if k in C.AVATAR_INICIAL}}


def info_nivel(xp):
    n = C.nivel_de(xp)
    maximo = n >= len(C.NIVELES) - 1
    return {"num": n + 1, **C.NIVELES[n], "xp": xp, "en_nivel": C.XP_NIVEL if maximo else xp % C.XP_NIVEL,
            "por_nivel": C.XP_NIVEL, "maximo": maximo}


def alumno_actual(con):
    a = con.execute("SELECT * FROM alumnos WHERE id=? AND activo=1", (session.get("uid"),)).fetchone()
    if not a:
        session.clear()
        abort(401)
    return dict(a)


# =================================================================
# Páginas
# =================================================================
@app.route("/")
def pagina_alumnos():
    return send_from_directory(os.path.join(STATIC, "alumno"), "index.html")


@app.route("/docente")
def pagina_docente():
    return send_from_directory(os.path.join(STATIC, "docente"), "index.html")


@app.errorhandler(401)
def no_autorizado(_):
    return error("Necesitás iniciar sesión.", 401)


# =================================================================
# API pública (pantalla de ingreso de los chicos)
# =================================================================
@app.get("/api/ingreso")
def api_ingreso():
    con = con_db()
    alumnos = [{"id": r["id"], "nombre": r["nombre"], "grado": r["grado"], "avatar": avatar_de(r)}
               for r in con.execute("SELECT * FROM alumnos WHERE activo=1 ORDER BY grado, nombre COLLATE NOCASE")]
    con.close()
    return jsonify({"alumnos": alumnos, "dibujos": C.DIBUJOS_CLAVE,
                    "sesion": session.get("uid") if session.get("rol") == "alumno" else None})


@app.get("/api/catalogo")
def api_catalogo():
    return jsonify({"items": C.CATALOGO, "categorias": C.CATEGORIAS_AVATAR, "temas": C.TEMAS,
                    "tipos": C.TIPOS, "clases": C.CLASES, "orden": {"tipos": list(C.TIPOS), "clases": list(C.CLASES)}, "medallas": C.MEDALLAS, "niveles": C.NIVELES})


# =================================================================
# API de los chicos
# =================================================================
@app.post("/api/alumno/ingresar")
def api_alumno_ingresar():
    d = cuerpo()
    aid = entero(d.get("id"), 1, 10 ** 9)
    if aid is None:
        return error("Datos incompletos.")
    clave = d.get("clave")
    if not isinstance(clave, list) or len(clave) != 3 or any(x not in C.DIBUJOS_CLAVE for x in clave):
        return error("Tocá tus 3 dibujos secretos.")
    llave = f"al{aid}|{ip()}"
    espera = LIMITE_ALUMNO.bloqueado(llave)
    if espera:
        return error(f"Esperá {espera} segundos y probá de nuevo.", 429)
    con = con_db()
    a = con.execute("SELECT * FROM alumnos WHERE id=? AND activo=1", (aid,)).fetchone()
    if not a or not isinstance(clave, list) or json.loads(a["clave"]) != clave:
        LIMITE_ALUMNO.fallo(llave)
        con.close()
        return error("Esos dibujos no son. ¡Probá otra vez!", 403)
    LIMITE_ALUMNO.exito(llave)
    con.close()
    session.clear()  # si había una sesión docente abierta, se cierra
    session.update({"rol": "alumno", "uid": aid, "t": time.time()})
    return jsonify({"ok": True})


@app.post("/api/alumno/salir")
def api_alumno_salir():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/alumno/perfil")
@requiere("alumno")
def api_alumno_perfil():
    con = con_db()
    a = alumno_actual(con)
    cfg = db.leer_config(con)
    mejores = mejores_estrellas(con, a["id"])
    acts = {x["id"]: x for x in todas_actividades(con)}
    meds = {r[0]: r[1] for r in con.execute("SELECT medalla_id, fecha FROM medallas WHERE alumno_id=?", (a["id"],))}
    vis = visibles_para(con, a, cfg)
    album_ids = [x["id"] for x in vis] + [i for i in mejores if i in acts and i not in {v["id"] for v in vis}]
    album = [{"id": i, "titulo": acts[i]["titulo"], "sticker": acts[i].get("sticker", "⭐"), "tipo": acts[i]["tipo"],
              "estrellas": mejores.get(i, 0)} for i in album_ids]
    pendientes = sum(1 for t in tareas_de_alumno(con, a) if not t["entregada"])
    posibles = medallas_posibles(con, a, cfg)
    out = {
        "id": a["id"], "nombre": a["nombre"], "grado": a["grado"], "monedas": a["monedas"],
        "nivel": info_nivel(a["xp"]), "avatar": avatar_de(a), "items": estado_items(con, a),
        "estrellas": sum(mejores.values()), "hechas": len(mejores), "tareas_pendientes": pendientes,
        # Solo se muestran las medallas que ya ganó o que puede ganar con lo que tiene para jugar
        "medallas": [{**m, "fecha": meds.get(m["id"])} for m in C.MEDALLAS
                     if m["id"] in meds or m["id"] in posibles], "album": album,
        "cfg": {"mayus": a["grado"] == 1 and cfg["mayus_1"], "auto_leer": cfg["auto_leer"],
                "voz_lenta": cfg["voz_lenta"], "voz_alegre": cfg["voz_alegre"], "sonido": cfg["sonido"], "voz": cfg["voz"]},
    }
    con.close()
    return jsonify(out)


@app.get("/api/alumno/actividades")
@requiere("alumno")
def api_alumno_actividades():
    con = con_db()
    a = alumno_actual(con)
    cfg = db.leer_config(con)
    mejores = mejores_estrellas(con, a["id"])
    en_tarea = {x["id"] for t in tareas_de_alumno(con, a) if not t["entregada"] for x in t["actividades"]}
    out = []
    previo = {}
    for act in visibles_para(con, a, cfg):
        r = resumen_actividad(act)
        tipo = act["tipo"]
        libre = (not cfg["progresivo"] or tipo not in previo or mejores.get(previo[tipo], 0) > 0
                 or mejores.get(act["id"], 0) > 0 or act["id"] in en_tarea)
        previo[tipo] = act["id"]
        out.append({**r, "estrellas": mejores.get(act["id"], 0), "bloqueada": not libre, "en_tarea": act["id"] in en_tarea})
    con.close()
    return jsonify(out)


@app.get("/api/alumno/actividad/<aid>")
@requiere("alumno")
def api_alumno_actividad(aid):
    con = con_db()
    a = alumno_actual(con)
    cfg = db.leer_config(con)
    act = actividad(con, aid)
    permitidas = {x["id"] for x in visibles_para(con, a, cfg)} | {
        x["id"] for t in tareas_de_alumno(con, a) for x in t["actividades"]}
    con.close()
    if not act or aid not in permitidas:
        return error("Esa actividad no está disponible.", 404)
    validos = items_validos(act, cfg)
    salida = {k: act[k] for k in ("id", "tipo", "titulo", "e", "sticker", "nivel") if k in act}
    if act["tipo"] == "cuento":
        salida["texto"] = act["texto"]
        salida["preguntas"] = [{**q, "idx": i} for i, q in enumerate(act["preguntas"]) if i in validos]
    else:
        salida["items"] = [{**it, "idx": i} for i, it in enumerate(act["items"])]
    salida["temas"] = {k: {"n": v["n"], "i": v["i"], "kid": v["kid"], "pista": v["pista"]} for k, v in C.TEMAS.items()}
    return jsonify(salida)


@app.post("/api/alumno/intento")
@requiere("alumno")
def api_alumno_intento():
    d = cuerpo()
    con = con_db()
    a = alumno_actual(con)
    cfg = db.leer_config(con)
    act = actividad(con, texto(d.get("actividad_id"), 40))
    if not act:
        con.close()
        return error("Actividad inexistente.", 404)
    tareas = tareas_de_alumno(con, a)
    tarea = None
    if d.get("tarea_id") is not None:
        tarea = next((t for t in tareas if t["id"] == d.get("tarea_id")
                      and any(x["id"] == act["id"] for x in t["actividades"])), None)
    permitidas = {x["id"] for x in visibles_para(con, a, cfg)} | {x["id"] for t in tareas for x in t["actividades"]}
    if act["id"] not in permitidas:
        con.close()
        return error("Esa actividad no está disponible.", 403)
    # Nadie termina una actividad en menos de 3 segundos: evita envíos repetidos (doble clic o programas)
    ultimo = con.execute("SELECT MAX(fecha) FROM intentos WHERE alumno_id=?", (a["id"],)).fetchone()[0]
    if ultimo and datetime.now() - datetime.strptime(ultimo, "%Y-%m-%d %H:%M:%S") < timedelta(seconds=ESPERA_INTENTO):
        con.close()
        return error("Esperá un momento antes de guardar otra vez.", 429)

    validos = items_validos(act, cfg)
    resp = d.get("respuestas")
    if not isinstance(resp, list):
        con.close()
        return error("Respuestas inválidas.")
    vistos, limpias = set(), []
    for r in resp:
        try:
            idx, n = int(r.get("idx")), int(r.get("intentos"))
        except (TypeError, ValueError, AttributeError):
            con.close()
            return error("Respuestas inválidas.")
        if idx not in validos or idx in vistos:
            con.close()
            return error("Respuestas inválidas.")
        vistos.add(idx)
        limpias.append((idx, max(1, min(n, 20))))
    if vistos != set(validos):
        con.close()
        return error("La actividad no está completa.")

    total = len(limpias)
    aciertos = sum(1 for _, n in limpias if n == 1)
    pct = aciertos / total
    estrellas = 3 if pct >= 0.9 else 2 if pct >= 0.6 else 1
    previas = mejores_estrellas(con, a["id"]).get(act["id"], 0)
    por_bien, por_mal = (10, 4) if act["tipo"] == "cuento" else (6, 3)
    monedas = sum(por_bien if n == 1 else por_mal for _, n in limpias)
    if previas:
        monedas = (monedas + 1) // 2
    bonus = 15 if estrellas == 3 and previas < 3 else 0
    monedas += bonus
    segundos = entero(d.get("segundos") or 0, 0, 10 ** 9)
    segundos = min(segundos, 3 * 3600) if segundos is not None else 0
    ahora = db.ahora()

    cur = con.execute("INSERT INTO intentos(alumno_id, actividad_id, tarea_id, fecha, aciertos, total, estrellas, monedas, segundos) "
                      "VALUES(?,?,?,?,?,?,?,?,?)",
                      (a["id"], act["id"], tarea["id"] if tarea else None, ahora, aciertos, total, estrellas, monedas, segundos))
    for idx, n in limpias:
        con.execute("INSERT INTO respuestas(intento_id, alumno_id, actividad_id, item_idx, tema, primera, intentos, fecha) "
                    "VALUES(?,?,?,?,?,?,?,?)", (cur.lastrowid, a["id"], act["id"], idx, validos[idx], int(n == 1), n, ahora))

    # ¿Se completó una tarea?
    tarea_completa = None
    if tarea and not tarea["entregada"]:
        hechas = {r[0] for r in con.execute(
            "SELECT DISTINCT actividad_id FROM intentos WHERE alumno_id=? AND tarea_id=?", (a["id"], tarea["id"]))}
        if all(x["id"] in hechas for x in tarea["actividades"]):
            con.execute("INSERT OR IGNORE INTO tarea_entregas VALUES(?,?,?)", (tarea["id"], a["id"], ahora))
            monedas += tarea["recompensa"]
            tarea_completa = {"titulo": tarea["titulo"], "recompensa": tarea["recompensa"]}

    nivel_antes = C.nivel_de(a["xp"])
    con.execute("UPDATE alumnos SET monedas=monedas+?, xp=xp+? WHERE id=?", (monedas, monedas, a["id"]))
    nuevas = evaluar_medallas(con, a["id"])
    con.commit()
    xp = a["xp"] + monedas
    out = {"estrellas": estrellas, "aciertos": aciertos, "total": total, "monedas": monedas, "bonus": bonus,
           "sticker_nuevo": act.get("sticker") if not previas else None, "medallas": nuevas, "mejora": estrellas > previas,
           "nivel": info_nivel(xp), "subio": C.nivel_de(xp) > nivel_antes, "tarea": tarea_completa}
    con.close()
    return jsonify(out)


@app.get("/api/alumno/tareas")
@requiere("alumno")
def api_alumno_tareas():
    con = con_db()
    a = alumno_actual(con)
    t = tareas_de_alumno(con, a)
    con.close()
    return jsonify(t)


@app.post("/api/alumno/comprar")
@requiere("alumno")
def api_alumno_comprar():
    item = C.CATALOGO_POR_ID.get(texto(cuerpo().get("item"), 40))
    if not item or not item["precio"] or item["nivel"] or item["medalla"]:
        return error("Eso no se puede comprar.")
    con = con_db()
    a = alumno_actual(con)
    if con.execute("SELECT 1 FROM inventario WHERE alumno_id=? AND item_id=?", (a["id"], item["id"])).fetchone():
        con.close()
        return error("¡Ya lo tenés!")
    if a["monedas"] < item["precio"]:
        con.close()
        return error("Te faltan monedas. ¡Seguí jugando para ganar más!")
    con.execute("UPDATE alumnos SET monedas=monedas-? WHERE id=?", (item["precio"], a["id"]))
    con.execute("INSERT INTO inventario VALUES(?,?,?)", (a["id"], item["id"], db.ahora()))
    con.commit()
    con.close()
    return jsonify({"ok": True, "monedas": a["monedas"] - item["precio"]})


@app.post("/api/alumno/avatar")
@requiere("alumno")
def api_alumno_avatar():
    nuevo = cuerpo().get("avatar")
    if not isinstance(nuevo, dict):
        return error("Datos inválidos.")
    con = con_db()
    a = alumno_actual(con)
    estados = estado_items(con, a)
    av = avatar_de(a)
    for cat in C.AVATAR_INICIAL:
        if cat in nuevo:
            iid = f"{cat}:{nuevo[cat]}"
            if iid not in C.CATALOGO_POR_ID or not estados[iid]["tiene"]:
                con.close()
                return error("Todavía no tenés ese objeto.", 403)
            av[cat] = nuevo[cat]
    con.execute("UPDATE alumnos SET avatar=? WHERE id=?", (json.dumps(av), a["id"]))
    con.commit()
    con.close()
    return jsonify({"ok": True, "avatar": av})


# =================================================================
# API docente: acceso
# =================================================================
def problema_password(pw):
    """Motivo por el que la contraseña no sirve, o None si está bien."""
    if len(pw) < 8 or len(pw) > 128:
        return "La contraseña debe tener entre 8 y 128 caracteres."
    if not re.search(r"\d", pw) or not re.search(r"[^\W\d_]", pw):
        return "La contraseña debe tener letras y números."
    return None


CABECERAS_PROXY = ("X-Forwarded-For", "X-Real-IP", "Forwarded", "CF-Connecting-IP", "True-Client-IP")


def es_local():
    # Con un túnel (Cloudflare, ngrok) los pedidos de internet llegan desde 127.0.0.1,
    # pero el túnel agrega estas cabeceras: si están, el pedido NO viene de esta computadora.
    if any(request.headers.get(h) for h in CABECERAS_PROXY):
        return False
    return ip() in ("127.0.0.1", "::1", "localhost")


@app.get("/api/docente/estado")
def api_docente_estado():
    con = con_db()
    n = con.execute("SELECT COUNT(*) FROM docentes").fetchone()[0]
    yo = None
    if session.get("rol") == "docente":
        r = con.execute("SELECT nombre, usuario, grados FROM docentes WHERE id=?", (session["uid"],)).fetchone()
        yo = {**dict(r), "grados": [int(x) for x in (r["grados"] or "1,2,3").split(",")]} if r else None
    abierto = db.leer_config(con)["registro_abierto"]
    con.close()
    return jsonify({"configurado": n > 0, "sesion": yo, "local": es_local(),
                    "registro": n > 0 and abierto and es_local()})


@app.post("/api/docente/configurar")
def api_docente_configurar():
    """Crea la primera cuenta docente, o una cuenta nueva si el registro está habilitado."""
    d = cuerpo()
    con = con_db()
    hay = con.execute("SELECT COUNT(*) FROM docentes").fetchone()[0] > 0
    if hay and not db.leer_config(con)["registro_abierto"]:
        con.close()
        return error("El registro de docentes nuevos está desactivado. Pedile a otra docente que lo habilite en Ajustes.", 403)
    if not es_local():
        con.close()
        return error("Las cuentas docentes se crean desde la computadora donde está instalado el juego.", 403)
    nombre = re.sub(r"\s+", " ", str(d.get("nombre") or "")).strip()
    usuario, pw = str(d.get("usuario") or "").strip().lower(), str(d.get("password") or "")
    if not nombre:
        con.close()
        return error("Escribí tu nombre.")
    if len(nombre) > 60 or not re.search(rf"[{LETRAS}]", nombre) or re.search(r"[<>\x00-\x1f]", nombre):
        con.close()
        return error("Tu nombre puede tener hasta 60 letras y no puede llevar los signos < o >.")
    if not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
        con.close()
        return error("El usuario debe tener entre 3 y 30 letras o números, sin espacios.")
    if problema_password(pw):
        con.close()
        return error(problema_password(pw))
    try:
        grados = leer_grados(d.get("grados"))
    except ValueError as e:
        con.close()
        return error(str(e))
    if con.execute("SELECT 1 FROM docentes WHERE usuario=?", (usuario,)).fetchone():
        con.close()
        return error("Ese usuario ya existe. Elegí otro.")
    cur = con.execute("INSERT INTO docentes(usuario, nombre, pass_hash, creado, grados) VALUES(?,?,?,?,?)",
                      (usuario, nombre, seg.hashear(pw), db.ahora(), grados))
    db.registrar(con, "Cuenta docente creada", usuario, ip())
    con.close()
    session.clear()
    session.update({"rol": "docente", "uid": cur.lastrowid, "t": time.time()})
    return jsonify({"ok": True})


@app.post("/api/docente/ingresar")
def api_docente_ingresar():
    d = cuerpo()
    usuario, pw = texto(d.get("usuario"), 30).lower(), str(d.get("password") or "")
    llave = ip()
    espera = LIMITE_DOCENTE.bloqueado(llave)
    if espera:
        return error(f"Demasiados intentos. Esperá {espera // 60 + 1} minutos.", 429)
    con = con_db()
    r = con.execute("SELECT * FROM docentes WHERE usuario=?", (usuario,)).fetchone()
    if not r or len(pw) > 128 or not seg.verificar(pw, r["pass_hash"]):
        LIMITE_DOCENTE.fallo(llave)
        db.registrar(con, "Intento de ingreso fallido", usuario, ip())
        con.close()
        return error("Usuario o contraseña incorrectos.", 403)
    LIMITE_DOCENTE.exito(llave)
    db.registrar(con, "Ingreso correcto", usuario, ip())
    con.close()
    session.clear()
    session.update({"rol": "docente", "uid": r["id"], "t": time.time()})
    return jsonify({"ok": True})


@app.post("/api/docente/salir")
def api_docente_salir():
    session.clear()
    return jsonify({"ok": True})


@app.post("/api/docente/password")
@requiere("docente")
def api_docente_password():
    d = cuerpo()
    con = con_db()
    r = con.execute("SELECT * FROM docentes WHERE id=?", (session["uid"],)).fetchone()
    if len(str(d.get("actual") or "")) > 128 or not seg.verificar(str(d.get("actual") or ""), r["pass_hash"]):
        con.close()
        return error("La contraseña actual no es correcta.", 403)
    nueva = str(d.get("nueva") or "")
    if problema_password(nueva):
        con.close()
        return error("La nueva contraseña no sirve: " + problema_password(nueva)[0].lower() + problema_password(nueva)[1:])
    if seg.verificar(nueva, r["pass_hash"]):
        con.close()
        return error("La nueva contraseña tiene que ser distinta de la actual.")
    con.execute("UPDATE docentes SET pass_hash=? WHERE id=?", (seg.hashear(nueva), r["id"]))
    db.registrar(con, "Cambio de contraseña", r["usuario"], ip())
    con.close()
    return jsonify({"ok": True})


# =================================================================
# API docente: estadísticas
# =================================================================
def entrega_tarde(entregada, limite):
    """True si la tarea se terminó después del día límite."""
    return bool(entregada and limite and entregada[:10] > limite)


def pct(ok, n):
    return round(ok * 100 / n) if n else None


def stats_temas(con, alumno_id=None):
    if alumno_id:
        filtro, params = "alumno_id=?", (alumno_id,)
    else:
        filtro, params = sql_mios(con)
    sql = f"SELECT tema, SUM(primera), COUNT(*) FROM respuestas WHERE {filtro} GROUP BY tema"
    return {r[0]: {"pct": pct(r[1], r[2]), "n": r[2]} for r in con.execute(sql, params)}


def semanas(con, alumno_id=None, tema=None, cuantas=10):
    filtros, params = [], []
    if alumno_id:
        filtros.append("alumno_id=?"); params.append(alumno_id)
    else:
        f, p = sql_mios(con)
        filtros.append(f); params.extend(p)
    if tema:
        filtros.append("tema=?"); params.append(tema)
    where = (" WHERE " + " AND ".join(filtros)) if filtros else ""
    filas = con.execute("SELECT strftime('%Y-%W', fecha) s, MIN(date(fecha)), SUM(primera), COUNT(*) FROM respuestas"
                        + where + " GROUP BY s ORDER BY s", params).fetchall()[-cuantas:]
    out = []
    for s, desde, ok, n in filas:
        d = datetime.strptime(desde, "%Y-%m-%d").date()
        lunes = d - timedelta(days=d.weekday())
        out.append({"semana": lunes.isoformat(), "pct": pct(ok, n), "n": n})
    return out


def tendencia(con, alumno_id, tema):
    vals = [r[0] for r in con.execute(
        "SELECT primera FROM respuestas WHERE alumno_id=? AND tema=? ORDER BY fecha, id", (alumno_id, tema))]
    if len(vals) < 6:
        return None
    mitad = len(vals) // 2
    antes, despues = vals[:mitad], vals[mitad:]
    return round(sum(despues) * 100 / len(despues)) - round(sum(antes) * 100 / len(antes))


def nombre_act(acts, aid):
    a = acts.get(aid)
    return {"titulo": a["titulo"], "e": a.get("e", "📖"), "tipo": a["tipo"]} if a else {"titulo": "(actividad borrada)", "e": "❔", "tipo": "?"}


@app.get("/api/docente/resumen")
@requiere("docente")
def api_docente_resumen():
    con = con_db()
    cfg = db.leer_config(con)
    acts = {a["id"]: a for a in todas_actividades(con)}
    fg, pg = sql_grados(con)
    fm, pm = sql_mios(con)
    alumnos = [dict(r) for r in con.execute(f"SELECT * FROM alumnos WHERE activo=1 AND {fg} ORDER BY nombre COLLATE NOCASE", pg)]
    hace7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    semana = con.execute(f"SELECT COUNT(*) FROM intentos WHERE fecha>=? AND {fm}", (hace7, *pm)).fetchone()[0]
    tot = con.execute(f"SELECT SUM(primera), COUNT(*) FROM respuestas WHERE {fm}", pm).fetchone()
    temas_on = [t for t in C.TEMAS if t not in cfg["temas_off"]]
    grupo = stats_temas(con)
    mapa = {r[0]: {} for r in con.execute("SELECT id FROM alumnos")}
    for r in con.execute("SELECT alumno_id, tema, SUM(primera), COUNT(*) FROM respuestas GROUP BY alumno_id, tema"):
        mapa.setdefault(r[0], {})[r[1]] = {"pct": pct(r[2], r[3]), "n": r[3]}
    ultimo = {r[0]: r[1] for r in con.execute("SELECT alumno_id, MAX(fecha) FROM intentos GROUP BY alumno_id")}
    filas, alertas = [], []
    for a in alumnos:
        st = mapa.get(a["id"], {})
        ok_n = con.execute("SELECT SUM(primera), COUNT(*) FROM respuestas WHERE alumno_id=?", (a["id"],)).fetchone()
        filas.append({"id": a["id"], "nombre": a["nombre"], "grado": a["grado"], "avatar": avatar_de(a),
                      "temas": {t: st.get(t) for t in temas_on}, "pct": pct(ok_n[0] or 0, ok_n[1]),
                      "ultima": ultimo.get(a["id"])})
        bajos = [t for t in temas_on if st.get(t) and st[t]["n"] >= 3 and st[t]["pct"] < 50]
        if bajos:
            alertas.append({"id": a["id"], "nombre": a["nombre"], "temas": bajos,
                            "motivo": "Le cuesta: " + ", ".join(C.TEMAS[t]["n"] for t in bajos)})
        if not ultimo.get(a["id"]):
            alertas.append({"id": a["id"], "nombre": a["nombre"], "motivo": "Todavía no jugó ninguna actividad"})
        elif ultimo[a["id"]] < hace7:
            alertas.append({"id": a["id"], "nombre": a["nombre"], "motivo": "Hace más de una semana que no juega"})
    recientes = [{"alumno": r["nombre"], "alumno_id": r["alumno_id"], **nombre_act(acts, r["actividad_id"]),
                  "fecha": r["fecha"], "estrellas": r["estrellas"], "aciertos": r["aciertos"], "total": r["total"],
                  "tarea": r["tarea_id"] is not None}
                 for r in con.execute("SELECT i.*, a.nombre FROM intentos i JOIN alumnos a ON a.id=i.alumno_id "
                                      f"WHERE a.{fg} ORDER BY i.fecha DESC, i.id DESC LIMIT 8", pg)]
    hoy = date.today().isoformat()
    tareas = []
    for t in [t for t in con.execute("SELECT * FROM tareas WHERE archivada=0 ORDER BY creada DESC") if tarea_mia(con, t)][:6]:
        asig = asignados(con, dict(t))
        ent = con.execute("SELECT COUNT(*) FROM tarea_entregas WHERE tarea_id=? AND alumno_id IN (%s)" %
                          ",".join("?" * len(asig)), (t["id"], *asig)).fetchone()[0] if asig else 0
        tareas.append({"id": t["id"], "titulo": t["titulo"], "fecha_limite": t["fecha_limite"], "asignados": len(asig),
                       "entregadas": ent, "vencida": bool(t["fecha_limite"] and t["fecha_limite"] < hoy)})
    out = {"kpis": {"alumnos": len(alumnos), "semana": semana, "promedio": pct(tot[0] or 0, tot[1]),
                    "tareas": sum(1 for t in tareas if not t["vencida"])},
           "semanas": semanas(con), "temas": [{"id": t, **C.TEMAS[t], "pct": (grupo.get(t) or {}).get("pct"),
                                                "cant": (grupo.get(t) or {}).get("n", 0)} for t in temas_on],
           "alumnos": filas, "alertas": alertas, "recientes": recientes, "tareas": tareas}
    con.close()
    return jsonify(out)


# =================================================================
# API docente: alumnos
# =================================================================
def clave_nueva():
    return secrets.SystemRandom().sample(C.DIBUJOS_CLAVE, 3)


@app.get("/api/docente/alumnos")
@requiere("docente")
def api_docente_alumnos():
    con = con_db()
    ultimo = {r[0]: r[1] for r in con.execute("SELECT alumno_id, MAX(fecha) FROM intentos GROUP BY alumno_id")}
    cuenta = {r[0]: r[1] for r in con.execute("SELECT alumno_id, COUNT(*) FROM intentos GROUP BY alumno_id")}
    prom = {r[0]: pct(r[1], r[2]) for r in con.execute("SELECT alumno_id, SUM(primera), COUNT(*) FROM respuestas GROUP BY alumno_id")}
    out = [{"id": r["id"], "nombre": r["nombre"], "grado": r["grado"], "activo": bool(r["activo"]),
            "clave": json.loads(r["clave"]), "avatar": avatar_de(r), "nivel": info_nivel(r["xp"])["num"],
            "monedas": r["monedas"], "actividades": cuenta.get(r["id"], 0), "pct": prom.get(r["id"]),
            "ultima": ultimo.get(r["id"])}
           for r in con.execute(f"SELECT * FROM alumnos WHERE {sql_grados(con)[0]} "
                                "ORDER BY activo DESC, grado, nombre COLLATE NOCASE", mis_grados(con))]
    con.close()
    return jsonify(out)


@app.post("/api/docente/alumnos")
@requiere("docente")
def api_docente_alumno_crear():
    d = cuerpo()
    nombres = d.get("nombres") if isinstance(d.get("nombres"), list) else [d.get("nombre")]
    if str(d.get("grado")) not in ("1", "2", "3"):
        return error("Elegí el grado (1.º, 2.º o 3.º).")
    grado = int(d.get("grado"))
    con = con_db()
    if grado not in mis_grados(con):
        con.close()
        return error(f"Solo podés cargar alumnos de tus grados ({nombre_grados(mis_grados(con))}). Podés cambiarlos en Ajustes.", 403)
    con.close()
    try:
        nombres = [nombre_alumno(n) for n in nombres if str(n or "").strip()]
    except ValueError as e:
        return error(str(e))
    if not nombres:
        return error("Escribí el nombre del alumno.")
    if len(nombres) > 60:
        return error("Podés cargar hasta 60 alumnos por vez.")
    vistos, dobles = set(), []
    for n in nombres:
        if n.lower() in vistos:
            dobles.append(n)
        vistos.add(n.lower())
    if dobles:
        return error("Escribiste dos veces: " + ", ".join(f"«{n}»" for n in dict.fromkeys(dobles)) + ". Agregá la inicial del apellido para distinguirlos.")
    con = con_db()
    existentes = {r[0].lower() for r in con.execute("SELECT nombre FROM alumnos")}
    repetidos = [n for n in nombres if n.lower() in existentes]
    if repetidos:
        con.close()
        return error("Ya existe un alumno con ese nombre (puede ser de otro grado): " + ", ".join(f"«{n}»" for n in repetidos) + ". Agregá la inicial del apellido.")
    for n in nombres:
        av = dict(C.AVATAR_INICIAL)
        av["piel"] = secrets.choice(["p1", "p2", "p3", "p4", "p5", "p6"])
        av["pelo"] = secrets.choice(["corto", "largo", "colitas"])
        av["colorPelo"] = secrets.choice(["negro", "castano", "rubio", "colorado"])
        av["colorRopa"] = secrets.choice(["azul", "rojo", "verde", "amarillo"])
        con.execute("INSERT INTO alumnos(nombre, grado, clave, avatar, creado) VALUES(?,?,?,?,?)",
                    (n, grado, json.dumps(clave_nueva(), ensure_ascii=False), json.dumps(av), db.ahora()))
    con.commit()
    con.close()
    return jsonify({"ok": True, "creados": len(nombres)})


@app.put("/api/docente/alumnos/<int:aid>")
@requiere("docente")
def api_docente_alumno_editar(aid):
    d = cuerpo()
    con = con_db()
    a = alumno_mio(con, aid)
    if not a:
        con.close()
        return error("No existe.", 404)
    try:
        nombre = nombre_alumno(d["nombre"]) if "nombre" in d else a["nombre"]
        activo = int(si_no(d, "activo", bool(a["activo"])))
    except ValueError as e:
        con.close()
        return error(str(e))
    if str(d.get("grado", a["grado"])) not in ("1", "2", "3"):
        con.close()
        return error("Elegí el grado (1.º, 2.º o 3.º).")
    grado = int(d.get("grado", a["grado"]))
    if grado not in mis_grados(con):
        con.close()
        return error(f"Solo podés pasarlo a uno de tus grados ({nombre_grados(mis_grados(con))}).", 403)
    if con.execute("SELECT 1 FROM alumnos WHERE lower(nombre)=lower(?) AND id<>?", (nombre, aid)).fetchone():
        con.close()
        return error("Ya existe otro alumno con ese nombre.")
    con.execute("UPDATE alumnos SET nombre=?, grado=?, activo=? WHERE id=?", (nombre, grado, activo, aid))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.post("/api/docente/alumnos/<int:aid>/clave")
@requiere("docente")
def api_docente_alumno_clave(aid):
    con = con_db()
    if not alumno_mio(con, aid):
        con.close()
        return error("Ese alumno no existe.", 404)
    c = clave_nueva()
    con.execute("UPDATE alumnos SET clave=? WHERE id=?", (json.dumps(c, ensure_ascii=False), aid))
    con.commit()
    con.close()
    return jsonify({"ok": True, "clave": c})


@app.post("/api/docente/alumnos/<int:aid>/reiniciar")
@requiere("docente")
def api_docente_alumno_reiniciar(aid):
    con = con_db()
    if not alumno_mio(con, aid):
        con.close()
        return error("Ese alumno no existe.", 404)
    for t in ("respuestas", "intentos", "medallas", "inventario", "tarea_entregas"):
        con.execute(f"DELETE FROM {t} WHERE alumno_id=?", (aid,))
    con.execute("UPDATE alumnos SET monedas=0, xp=0, avatar=? WHERE id=?", (json.dumps(C.AVATAR_INICIAL), aid))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.delete("/api/docente/alumnos/<int:aid>")
@requiere("docente")
def api_docente_alumno_borrar(aid):
    con = con_db()
    if not alumno_mio(con, aid):
        con.close()
        return error("Ese alumno no existe.", 404)
    con.execute("DELETE FROM alumnos WHERE id=?", (aid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.get("/api/docente/alumnos/<int:aid>")
@requiere("docente")
def api_docente_alumno_ficha(aid):
    con = con_db()
    a = alumno_mio(con, aid)
    if not a:
        con.close()
        return error("No existe.", 404)
    acts = {x["id"]: x for x in todas_actividades(con)}
    st = stats_temas(con, aid)
    temas = [{"id": t, "n_tema": C.TEMAS[t]["n"], "i": C.TEMAS[t]["i"], "obj": C.TEMAS[t]["obj"],
              **(st.get(t) or {"pct": None, "n": 0}), "tendencia": tendencia(con, aid, t)} for t in C.TEMAS]
    intentos = [{**nombre_act(acts, r["actividad_id"]), "fecha": r["fecha"], "aciertos": r["aciertos"], "total": r["total"],
                 "estrellas": r["estrellas"], "segundos": r["segundos"], "tarea": r["tarea_titulo"]}
                for r in con.execute("SELECT i.*, t.titulo tarea_titulo FROM intentos i LEFT JOIN tareas t ON t.id=i.tarea_id "
                                     "WHERE i.alumno_id=? ORDER BY i.fecha DESC, i.id DESC LIMIT 40", (aid,))]
    errores = [{"texto": texto_item(acts[r[0]], r[1]) if r[0] in acts else "(actividad borrada)",
                **nombre_act(acts, r[0]), "tema": r[2], "veces": r[3]}
               for r in con.execute("SELECT actividad_id, item_idx, tema, COUNT(*) c FROM respuestas "
                                    "WHERE alumno_id=? AND primera=0 GROUP BY actividad_id, item_idx ORDER BY c DESC LIMIT 8", (aid,))]
    hoy = date.today().isoformat()
    tareas = []
    for t in tareas_de_alumno(con, a):
        hechas = sum(1 for x in t["actividades"] if x["estrellas"])
        estado = "entregada" if t["entregada"] else ("vencida" if t["fecha_limite"] and t["fecha_limite"] < hoy else "pendiente")
        tareas.append({"titulo": t["titulo"], "fecha_limite": t["fecha_limite"], "estado": estado, "entregada": t["entregada"],
                       "tarde": entrega_tarde(t["entregada"], t["fecha_limite"]),
                       "hechas": hechas, "total": len(t["actividades"])})
    obs = [dict(r) for r in con.execute("SELECT id, fecha, texto FROM observaciones WHERE alumno_id=? ORDER BY fecha DESC", (aid,))]
    tot = con.execute("SELECT SUM(primera), COUNT(*) FROM respuestas WHERE alumno_id=?", (aid,)).fetchone()
    mejores = mejores_estrellas(con, aid)
    n_med = con.execute("SELECT COUNT(*) FROM medallas WHERE alumno_id=?", (aid,)).fetchone()[0]
    tiempo = con.execute("SELECT SUM(segundos) FROM intentos WHERE alumno_id=?", (aid,)).fetchone()[0] or 0
    out = {"id": aid, "nombre": a["nombre"], "grado": a["grado"], "activo": bool(a["activo"]), "clave": json.loads(a["clave"]),
           "avatar": avatar_de(a), "nivel": info_nivel(a["xp"]), "monedas": a["monedas"], "creado": a["creado"],
           "pct": pct(tot[0] or 0, tot[1]), "respuestas": tot[1], "actividades": len(mejores),
           "estrellas": sum(mejores.values()), "medallas": n_med, "minutos": round(tiempo / 60),
           "temas": temas, "semanas": semanas(con, aid), "intentos": intentos, "errores": errores,
           "tareas": tareas, "observaciones": obs}
    con.close()
    return jsonify(out)


@app.post("/api/docente/alumnos/<int:aid>/observaciones")
@requiere("docente")
def api_docente_obs_crear(aid):
    t = str(cuerpo().get("texto") or "").strip()
    if not t:
        return error("Escribí la observación.")
    if len(t) > 1000:
        return error(f"La observación es muy larga ({len(t)} letras; el máximo es 1000).")
    con = con_db()
    if not alumno_mio(con, aid):
        con.close()
        return error("No existe.", 404)
    con.execute("INSERT INTO observaciones(alumno_id, fecha, texto) VALUES(?,?,?)", (aid, db.ahora(), t))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.delete("/api/docente/observaciones/<int:oid>")
@requiere("docente")
def api_docente_obs_borrar(oid):
    con = con_db()
    f, p = sql_mios(con)
    if not con.execute(f"SELECT 1 FROM observaciones WHERE id=? AND {f}", (oid, *p)).fetchone():
        con.close()
        return error("Esa observación ya no existe.", 404)
    con.execute("DELETE FROM observaciones WHERE id=?", (oid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


# =================================================================
# API docente: tareas
# =================================================================
DESTINOS = {"todos": "Todos mis grados", "grado1": "1.º grado", "grado2": "2.º grado", "grado3": "3.º grado", "elegidos": "Alumnos elegidos"}


@app.get("/api/docente/tareas")
@requiere("docente")
def api_docente_tareas():
    con = con_db()
    acts = {a["id"]: a for a in todas_actividades(con)}
    hoy = date.today().isoformat()
    out = []
    for t in con.execute("SELECT * FROM tareas ORDER BY archivada, creada DESC"):
        t = dict(t)
        if not tarea_mia(con, t):
            continue
        asig = asignados(con, t)
        ent = {r[0] for r in con.execute("SELECT alumno_id FROM tarea_entregas WHERE tarea_id=?", (t["id"],))}
        out.append({**t, "destino_n": DESTINOS.get(t["destino"], t["destino"]), "asignados": len(asig),
                    "entregadas": len([x for x in asig if x in ent]),
                    "actividades": [resumen_actividad(a) for a in actividades_tarea(con, t["id"], acts)],
                    "vencida": bool(t["fecha_limite"] and t["fecha_limite"] < hoy)})
    con.close()
    return jsonify(out)


@app.post("/api/docente/tareas")
@requiere("docente")
def api_docente_tarea_crear():
    d = cuerpo()
    titulo = re.sub(r"\s+", " ", texto(d.get("titulo"), 80))
    consigna = texto(d.get("consigna"), 400)
    destino = d.get("destino", "todos")
    recompensa = entero(d.get("recompensa", 30), 0, 200)
    elegidas = d.get("actividades") or []
    if not titulo:
        return error("Poné un título a la tarea.")
    if len(str(d.get("titulo") or "").strip()) > 80 or len(str(d.get("consigna") or "").strip()) > 400:
        return error("El título puede tener hasta 80 letras y la consigna hasta 400.")
    if destino not in DESTINOS:
        return error("Elegí para quién es la tarea.")
    if recompensa is None:
        return error("El premio tiene que ser un número entero entre 0 y 200.")
    if not isinstance(elegidas, list) or not isinstance(d.get("alumnos") or [], list):
        return error("Datos inválidos.")
    try:
        limite = fecha_limite(d.get("fecha_limite"))
    except ValueError as e:
        return error(str(e))
    con = con_db()
    ids_validos = {a["id"] for a in todas_actividades(con) if a.get("estado", "publicado") == "publicado"}
    acts = list(dict.fromkeys(x for x in elegidas if x in ids_validos))
    if not acts:
        con.close()
        return error("Elegí al menos una actividad.")
    if len(acts) > 12:
        con.close()
        return error("Una tarea puede tener hasta 12 actividades.")
    alumnos = []
    gs = mis_grados(con)
    grados = ",".join(map(str, gs))
    if destino.startswith("grado"):
        if int(destino[-1]) not in gs:
            con.close()
            return error(f"Solo podés asignar actividades a tus grados ({nombre_grados(gs)}).", 403)
        grados = destino[-1]
    if destino == "elegidos":
        fg, pg = sql_grados(con)
        validos = {r[0] for r in con.execute(f"SELECT id FROM alumnos WHERE activo=1 AND {fg}", pg)}
        alumnos = [int(x) for x in (d.get("alumnos") or []) if str(x).isdigit() and int(x) in validos]
        if not alumnos:
            con.close()
            return error("Elegí al menos un alumno.")
    elif destino == "todos" and not con.execute(f"SELECT 1 FROM alumnos WHERE activo=1 AND {sql_grados(con)[0]}", gs).fetchone():
        con.close()
        return error("Todavía no hay alumnos activos en tus grados.")
    elif destino != "todos" and not con.execute(
            "SELECT 1 FROM alumnos WHERE activo=1 AND grado=?", (int(destino[-1]),)).fetchone():
        con.close()
        return error(f"No hay alumnos activos en {DESTINOS[destino]}.")
    cur = con.execute("INSERT INTO tareas(titulo, consigna, fecha_limite, destino, recompensa, creada, grados) VALUES(?,?,?,?,?,?,?)",
                      (titulo, consigna, limite, destino, recompensa, db.ahora(), grados))
    for i, a in enumerate(acts):
        con.execute("INSERT INTO tarea_actividades VALUES(?,?,?)", (cur.lastrowid, a, i))
    for a in alumnos:
        con.execute("INSERT OR IGNORE INTO tarea_alumnos VALUES(?,?)", (cur.lastrowid, a))
    con.commit()
    con.close()
    return jsonify({"ok": True, "id": cur.lastrowid})


def actividades_de_tema(con, alumno, tema, cfg):
    """Actividades publicadas de su grado que trabajan ese tema; primero las que menos estrellas tiene."""
    niveles = niveles_para(alumno["grado"], cfg)
    mejores = mejores_estrellas(con, alumno["id"])
    acts = [a for a in todas_actividades(con) if a.get("estado", "publicado") == "publicado" and int(a["nivel"]) in niveles
            and (any(q["tema"] == tema for q in a["preguntas"]) if a["tipo"] == "cuento"
                 else C.TIPOS[a["tipo"]]["tema"] == tema)]
    acts.sort(key=lambda a: (mejores.get(a["id"], 0), int(a["nivel"])))
    return acts


@app.post("/api/docente/alumnos/<int:aid>/refuerzo")
@requiere("docente")
def api_docente_refuerzo(aid):
    """Crea una tarea de repaso de un tema para un alumno (botón «Asignar refuerzo»)."""
    tema = texto(cuerpo().get("tema"), 30)
    if tema not in C.TEMAS:
        return error("Tema inválido.")
    con = con_db()
    al = alumno_mio(con, aid)
    if not al or not al["activo"]:
        con.close()
        return error("No existe.", 404)
    acts = actividades_de_tema(con, al, tema, db.leer_config(con))[:3]
    if not acts:
        con.close()
        return error("No hay actividades de ese tema para su grado. Podés crear una en «Actividades».")
    T = C.TEMAS[tema]
    titulo = f"Repaso: {T['n']}"
    consigna = f"¡Vamos a repasar «{T['kid']}»! Hacé estas actividades con calma. 💪"
    limite = (date.today() + timedelta(days=7)).isoformat()
    cur = con.execute("INSERT INTO tareas(titulo, consigna, fecha_limite, destino, recompensa, creada, grados) VALUES(?,?,?,?,?,?,?)",
                      (titulo, consigna, limite, "elegidos", 30, db.ahora(), str(al["grado"])))
    for i, a in enumerate(acts):
        con.execute("INSERT INTO tarea_actividades VALUES(?,?,?)", (cur.lastrowid, a["id"], i))
    con.execute("INSERT INTO tarea_alumnos VALUES(?,?)", (cur.lastrowid, aid))
    con.commit()
    con.close()
    return jsonify({"ok": True, "id": cur.lastrowid, "titulo": titulo, "actividades": [x["titulo"] for x in acts]})


@app.get("/api/docente/tareas/<int:tid>")
@requiere("docente")
def api_docente_tarea_ver(tid):
    con = con_db()
    t = con.execute("SELECT * FROM tareas WHERE id=?", (tid,)).fetchone()
    if not t or not tarea_mia(con, t):
        con.close()
        return error("No existe.", 404)
    t = dict(t)
    acts = actividades_tarea(con, tid, {a["id"]: a for a in todas_actividades(con)})
    filas = []
    for aid in asignados(con, t):
        al = con.execute("SELECT * FROM alumnos WHERE id=?", (aid,)).fetchone()
        mej = {r[0]: (r[1], r[2], r[3]) for r in con.execute(
            "SELECT actividad_id, MAX(estrellas), SUM(aciertos), SUM(total) FROM intentos WHERE alumno_id=? AND tarea_id=? "
            "GROUP BY actividad_id", (aid, tid))}
        ent = con.execute("SELECT fecha FROM tarea_entregas WHERE tarea_id=? AND alumno_id=?", (tid, aid)).fetchone()
        filas.append({"id": aid, "nombre": al["nombre"], "avatar": avatar_de(al), "entregada": ent[0] if ent else None,
                      "tarde": entrega_tarde(ent[0] if ent else None, t["fecha_limite"]),
                      "actividades": [{"estrellas": mej[a["id"]][0], "pct": pct(mej[a["id"]][1], mej[a["id"]][2])}
                                      if a["id"] in mej else None for a in acts]})
    con.close()
    return jsonify({**t, "destino_n": DESTINOS.get(t["destino"]), "actividades": [resumen_actividad(a) for a in acts],
                    "alumnos": filas})


@app.post("/api/docente/tareas/<int:tid>/archivar")
@requiere("docente")
def api_docente_tarea_archivar(tid):
    con = con_db()
    t = con.execute("SELECT * FROM tareas WHERE id=?", (tid,)).fetchone()
    if not t or not tarea_mia(con, t):
        con.close()
        return error("Esa tarea no existe.", 404)
    con.execute("UPDATE tareas SET archivada=1-archivada WHERE id=?", (tid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.delete("/api/docente/tareas/<int:tid>")
@requiere("docente")
def api_docente_tarea_borrar(tid):
    con = con_db()
    t = con.execute("SELECT * FROM tareas WHERE id=?", (tid,)).fetchone()
    if not t or not tarea_mia(con, t):
        con.close()
        return error("Esa tarea no existe.", 404)
    con.execute("UPDATE intentos SET tarea_id=NULL WHERE tarea_id=?", (tid,))
    con.execute("DELETE FROM tareas WHERE id=?", (tid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


# =================================================================
# API docente: actividades
# =================================================================
@app.get("/api/docente/actividades")
@requiere("docente")
def api_docente_actividades():
    con = con_db()
    cfg = db.leer_config(con)
    fm, pm = sql_mios(con)
    uso = {r[0]: (r[1], r[2]) for r in con.execute(
        f"SELECT actividad_id, COUNT(*), COUNT(DISTINCT alumno_id) FROM intentos WHERE {fm} GROUP BY actividad_id", pm)}
    res = {r[0]: pct(r[1], r[2]) for r in con.execute(
        f"SELECT actividad_id, SUM(primera), COUNT(*) FROM respuestas WHERE {fm} GROUP BY actividad_id", pm)}
    out = []
    for a in todas_actividades(con):
        r = resumen_actividad(a)
        out.append({**r, "visible": a["id"] not in cfg["ocultas"], "veces": uso.get(a["id"], (0, 0))[0],
                    "alumnos": uso.get(a["id"], (0, 0))[1], "pct": res.get(a["id"])})
    out.sort(key=lambda x: (ORDEN_TIPOS.index(x["tipo"]), x["nivel"]))
    con.close()
    return jsonify(out)


@app.get("/api/docente/actividades/<aid>")
@requiere("docente")
def api_docente_actividad(aid):
    con = con_db()
    a = actividad(con, aid)
    errores = {}
    if a:
        fm, pm = sql_mios(con)
        errores = {r[0]: {"pct": pct(r[1], r[2]), "n": r[2]} for r in con.execute(
            f"SELECT item_idx, SUM(primera), COUNT(*) FROM respuestas WHERE actividad_id=? AND {fm} GROUP BY item_idx", (aid, *pm))}
    con.close()
    if not a:
        return error("No existe.", 404)
    return jsonify({**a, "resultados": errores})


def _s(v, n=120):
    return texto(v, n)


def opciones(it, n, donde):
    """Opciones de un ítem de elegir: la primera es la correcta. Lanza ValueError si faltan o se repiten."""
    o = it.get("o") if isinstance(it.get("o"), list) else []
    o = [_s(x, n) for x in o]
    if not o or not o[0]:
        raise ValueError(f"{donde}: falta la respuesta correcta (va en el primer casillero).")
    limpias = [x for x in o if x]
    if len({x.lower() for x in limpias}) < len(limpias):
        raise ValueError(f"{donde}: hay opciones repetidas.")
    if len(limpias) < 2:
        raise ValueError(f"{donde}: agregá al menos una opción incorrecta.")
    return limpias[:3]


def textos(v, clave=None):
    """Todos los textos escritos en un ítem (sin contar dibujos ni listas desplegables)."""
    if isinstance(v, dict):
        return [t for k, x in v.items() for t in textos(x, k)]
    if isinstance(v, list):
        return [t for x in v for t in textos(x, clave)]
    return [] if clave in ("e", "r", "c") or not isinstance(v, str) else [v.strip()]


SOLO_LETRAS = "a-zñáéíóúü"


def dibujo(v, donde, que="el dibujo"):
    """Emoji de un dibujo o figurita ("" si viene vacío). No se corta: un emoji cortado se ve roto."""
    s = str(v or "").strip()
    if not s:
        return ""
    con_letras = re.search(rf"[\s{LETRAS}<>&\"']", s) or (re.search(r"\d", s) and "⃣" not in s)  # 1️⃣ lleva un número
    if len(s) > 12 or con_letras:
        raise ValueError(f"{donde}: {que} tiene que ser un solo emoji (en Windows: tecla Windows + punto).")
    return s


def validar_item(tipo, it, donde):
    """Valida una fila de un juego. Devuelve el ítem limpio o lanza ValueError con el motivo."""
    e = dibujo(it.get("e"), donde)
    if tipo == "oraciones":
        t = re.sub(r"\s+", " ", _s(it.get("t"), 140)).strip(" .")
        if not 3 <= len(t.split()) <= 10:
            raise ValueError(f"{donde}: la oración tiene que tener entre 3 y 10 palabras.")
        return {"e": e or "📝", "t": t}
    if tipo == "palabras":
        p = _s(it.get("p"), 20).lower()
        if not re.fullmatch(rf"[{SOLO_LETRAS}]{{2,10}}", p):
            raise ValueError(f"{donde}: escribí una sola palabra, solo con letras (de 2 a 10).")
        return {"e": e or "🔤", "p": p}
    if tipo == "rimas":
        c = it.get("c") if isinstance(it.get("c"), dict) else {}
        p, ct = _s(it.get("p"), 20).lower(), _s(c.get("t"), 20).lower()
        x = [{"t": _s(o.get("t"), 20).lower(), "e": dibujo(o.get("e"), donde)}
             for o in (it.get("x") if isinstance(it.get("x"), list) else []) if isinstance(o, dict) and _s(o.get("t"))]
        if not p or not ct:
            raise ValueError(f"{donde}: falta la palabra o la palabra que rima.")
        if not x:
            raise ValueError(f"{donde}: agregá al menos una palabra que no rime.")
        if ct == p or any(o["t"] in (p, ct) for o in x) or len({o["t"] for o in x}) < len(x):
            raise ValueError(f"{donde}: hay palabras repetidas.")
        return {"p": p, "e": e, "c": {"t": ct, "e": dibujo(c.get("e"), donde)}, "x": x[:2]}
    if tipo == "silabas":
        p = re.sub(r"\s*-\s*", "-", _s(it.get("p"), 40).lower())
        if not re.fullmatch(rf"[{SOLO_LETRAS}]{{1,5}}(-[{SOLO_LETRAS}]{{1,5}}){{1,4}}", p):
            raise ValueError(f"{donde}: separá la palabra en sílabas con guiones, de 2 a 5 sílabas (ej.: ma-ri-po-sa).")
        return {"e": e or "👏", "p": p}
    if tipo == "ortografia":
        p = _s(it.get("p"), 16).lower()
        if p.count("_") != 1 or not re.fullmatch(rf"[{SOLO_LETRAS}]*_[{SOLO_LETRAS}]*", p) or len(p) < 3:
            raise ValueError(f"{donde}: escribí la palabra con un solo _ donde va la letra (ej.: ca_a).")
        o = [x.lower() for x in opciones(it, 3, donde)]
        if not all(re.fullmatch(rf"[{SOLO_LETRAS}]{{1,3}}", x) for x in o):
            raise ValueError(f"{donde}: las opciones tienen que ser letras (hasta 3, como «ll» o «rr»).")
        return {"e": e or "🖍️", "p": p, "o": o}
    if tipo == "completar":
        t = re.sub(r"_+", "_", re.sub(r"\s+", " ", _s(it.get("t"), 140))).strip(" .")
        if t.count("_") != 1 or len(t) < 6:
            raise ValueError(f"{donde}: escribí la oración con un solo _ donde va la palabra que falta.")
        return {"e": e or "📌", "t": t, "o": opciones(it, 30, donde)}
    if tipo == "opuestos":
        p = _s(it.get("p"), 30).lower()
        if not p:
            raise ValueError(f"{donde}: falta la palabra.")
        o = opciones(it, 30, donde)
        if o[0].lower() == p:
            raise ValueError(f"{donde}: la respuesta no puede ser la misma palabra.")
        return {"e": e or "🔄", "p": p, "r": "parecido" if it.get("r") == "parecido" else "opuesto", "o": o}
    if tipo == "clases":
        p = _s(it.get("p"), 30)
        t = re.sub(r"\s+", " ", _s(it.get("t"), 140)).strip(" .")
        if not p or " " in p:
            raise ValueError(f"{donde}: escribí una sola palabra.")
        if it.get("c") not in C.CLASES:
            raise ValueError(f"{donde}: elegí la clase de palabra.")
        if t and not re.search(rf"(?<![{LETRAS}]){re.escape(p)}(?![{LETRAS}])", t, re.IGNORECASE):
            raise ValueError(f"{donde}: la oración de ejemplo tiene que incluir la palabra «{p}».")
        return {"e": e or "🏷️", "p": p, "c": it["c"], **({"t": t} if t else {})}
    raise ValueError("Tipo de actividad inválido.")


def validar_actividad(d):
    """Devuelve (tipo, datos) o lanza ValueError con un mensaje claro."""
    tipo = d.get("tipo")
    if tipo not in C.TIPOS:
        raise ValueError("Tipo de actividad inválido.")
    titulo = re.sub(r"\s+", " ", str(d.get("titulo") or "")).strip()
    if not titulo:
        raise ValueError("Falta el título.")
    if len(titulo) > 60:
        raise ValueError("El título puede tener hasta 60 letras.")
    if str(d.get("nivel", 1)) not in ("1", "2", "3"):
        raise ValueError("Elegí el nivel (1, 2 o 3).")
    datos = {"titulo": titulo, "e": dibujo(d.get("e"), "Datos generales") or C.TIPOS[tipo]["i"], "sticker": dibujo(d.get("sticker"), "Datos generales", "la figurita") or "⭐",
             "nivel": int(d.get("nivel", 1))}
    comprension = [k for k, v in C.TEMAS.items() if v["area"] == "Comprensión lectora"]
    if tipo == "cuento":
        txt = re.sub(r"\s+", " ", str(d.get("texto") or "")).strip()
        if len(txt) < 20:
            raise ValueError("El texto del cuento es muy corto.")
        if len(txt) > 2500:
            raise ValueError(f"El texto del cuento es muy largo ({len(txt)} letras; el máximo es 2500).")
        preguntas = []
        for i, q in enumerate(d.get("preguntas") if isinstance(d.get("preguntas"), list) else [], 1):
            if not isinstance(q, dict):
                continue
            t = q.get("t")
            if t == "o":
                items = [_s(x) for x in (q.get("items") if isinstance(q.get("items"), list) else []) if _s(x)]
                if not items:
                    continue
                if len(items) < 3:
                    raise ValueError("Orden de los hechos: completá al menos 3 partes (o dejalo vacío).")
                if len({x.lower() for x in items}) < len(items):
                    raise ValueError("Orden de los hechos: hay partes repetidas.")
                preguntas.append({"t": "o", "tema": "secuencia", "items": items[:5]})
                continue
            tema = q.get("tema") if q.get("tema") in comprension else "detalles"
            p = _s(q.get("p"), 200)
            if not p:
                if t != "vf" and any(textos(q.get("o"))):
                    raise ValueError(f"Pregunta {i}: falta escribir la pregunta.")
                continue
            if t == "vf":
                if not isinstance(q.get("v"), bool):
                    raise ValueError(f"Pregunta {i}: elegí si la oración es verdadera o falsa.")
                preguntas.append({"t": "vf", "tema": tema, "p": p, "v": q["v"]})
            else:
                preguntas.append({"t": "e", "tema": tema, "p": p, "o": opciones(q, 120, f"Pregunta {i}")})
        if len([q for q in preguntas if q["t"] != "o"]) < 2:
            raise ValueError("Agregá al menos 2 preguntas completas.")
        if len(preguntas) > 12:
            raise ValueError("Un cuento puede tener hasta 12 preguntas.")
        datos.update({"texto": txt, "preguntas": preguntas})
        return tipo, datos
    items = []
    for n, it in enumerate(d.get("items") if isinstance(d.get("items"), list) else [], 1):
        if not isinstance(it, dict) or not any(textos(it)):
            continue  # fila vacía: se ignora
        items.append(validar_item(tipo, it, f"Fila {n}"))
    if len(items) < 3:
        raise ValueError(f"Completá al menos 3 filas (hay {len(items)}).")
    if len(items) > 12:
        raise ValueError("Una actividad puede tener hasta 12 filas.")
    return tipo, {**datos, "items": items}


def titulo_repetido(con, tipo, titulo, excepto=None):
    return any(a["tipo"] == tipo and a["id"] != excepto and a["titulo"].strip().lower() == titulo.lower()
               for a in todas_actividades(con))


@app.post("/api/docente/actividades")
@requiere("docente")
def api_docente_actividad_crear():
    d = cuerpo()
    try:
        tipo, datos = validar_actividad(d)
    except ValueError as e:
        return error(str(e))
    con = con_db()
    if titulo_repetido(con, tipo, datos["titulo"]):
        con.close()
        return error(f"Ya hay una actividad de este juego llamada «{datos['titulo']}». Elegí otro título.")
    yo = con.execute("SELECT nombre FROM docentes WHERE id=?", (session["uid"],)).fetchone()
    datos.update(estado="publicado" if d.get("publicar") else "borrador", autor=yo[0] if yo else None, actualizado=db.ahora())
    aid = "c-" + secrets.token_hex(4)
    con.execute("INSERT INTO actividades_custom VALUES(?,?,?,?)", (aid, tipo, json.dumps(datos, ensure_ascii=False), db.ahora()))
    con.commit()
    con.close()
    return jsonify({"ok": True, "id": aid})


@app.put("/api/docente/actividades/<aid>")
@requiere("docente")
def api_docente_actividad_editar(aid):
    d = cuerpo()
    try:
        tipo, datos = validar_actividad(d)
    except ValueError as e:
        return error(str(e))
    con = con_db()
    r = con.execute("SELECT tipo, datos FROM actividades_custom WHERE id=?", (aid,)).fetchone()
    if not r:
        con.close()
        return error("Solo se pueden editar las actividades creadas por ustedes.", 403)
    if r["tipo"] != tipo:
        con.close()
        return error("No se puede cambiar el tipo de una actividad. Creá una nueva.")
    if titulo_repetido(con, tipo, datos["titulo"], aid):
        con.close()
        return error(f"Ya hay otra actividad de este juego llamada «{datos['titulo']}». Elegí otro título.")
    viejo = json.loads(r["datos"])
    yo = con.execute("SELECT nombre FROM docentes WHERE id=?", (session["uid"],)).fetchone()
    datos.update(estado="publicado" if d.get("publicar") else "borrador", autor=viejo.get("autor"),
                 editado_por=yo[0] if yo else None, actualizado=db.ahora())
    con.execute("UPDATE actividades_custom SET tipo=?, datos=? WHERE id=?", (tipo, json.dumps(datos, ensure_ascii=False), aid))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.delete("/api/docente/actividades/<aid>")
@requiere("docente")
def api_docente_actividad_borrar(aid):
    con = con_db()
    if not existe(con, "actividades_custom", aid):
        con.close()
        return error("Solo se pueden borrar las actividades creadas por ustedes.", 403)
    con.execute("DELETE FROM actividades_custom WHERE id=?", (aid,))
    con.execute("DELETE FROM tarea_actividades WHERE actividad_id=?", (aid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.post("/api/docente/actividades/<aid>/estado")
@requiere("docente")
def api_docente_actividad_estado(aid):
    estado = cuerpo().get("estado")
    if estado not in ("publicado", "borrador"):
        return error("Estado inválido.")
    con = con_db()
    r = con.execute("SELECT datos FROM actividades_custom WHERE id=?", (aid,)).fetchone()
    if not r:
        con.close()
        return error("Solo se pueden publicar las actividades creadas por ustedes.", 403)
    datos = json.loads(r["datos"])
    yo = con.execute("SELECT nombre FROM docentes WHERE id=?", (session["uid"],)).fetchone()
    datos.update(estado=estado, actualizado=db.ahora(), revisado_por=yo[0] if yo else None)
    con.execute("UPDATE actividades_custom SET datos=? WHERE id=?", (json.dumps(datos, ensure_ascii=False), aid))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.post("/api/docente/actividades/<aid>/visible")
@requiere("docente")
def api_docente_actividad_visible(aid):
    visible = cuerpo().get("visible")
    if not isinstance(visible, bool):
        return error("Valor inválido.")
    con = con_db()
    if not actividad(con, aid):
        con.close()
        return error("Esa actividad no existe.", 404)
    cfg = db.leer_config(con)
    ocultas = set(cfg["ocultas"])
    if visible:
        ocultas.discard(aid)
    else:
        ocultas.add(aid)
    db.guardar_config(con, {"ocultas": sorted(ocultas)})
    con.close()
    return jsonify({"ok": True})


# =================================================================
# API docente: configuración y datos
# =================================================================
@app.get("/api/docente/config")
@requiere("docente")
def api_docente_config():
    con = con_db()
    cfg = db.leer_config(con)
    temas = []
    acts = todas_actividades(con)
    grupo = stats_temas(con)
    for k, t in C.TEMAS.items():
        n = sum(1 for a in acts if a["tipo"] == "cuento" for q in a["preguntas"] if q["tema"] == k) + \
            sum(len(a["items"]) for a in acts if a["tipo"] != "cuento" and C.TIPOS[a["tipo"]]["tema"] == k)
        ej = next((q["p"] for a in acts if a["tipo"] == "cuento" for q in a["preguntas"] if q["tema"] == k and q["t"] != "o"), None)
        temas.append({"id": k, **t, "activo": k not in cfg["temas_off"], "items": n, "ejemplo": ej,
                      "pct": (grupo.get(k) or {}).get("pct"), "cant": (grupo.get(k) or {}).get("n", 0)})
    con.close()
    return jsonify({"cfg": cfg, "temas": temas})


@app.put("/api/docente/config")
@requiere("docente")
def api_docente_config_guardar():
    d = cuerpo()
    cambios = {}
    for k in ("mayus_1", "nivel2_para_1", "nivel3_para_2", "auto_leer", "voz_lenta", "voz_alegre", "sonido", "progresivo", "registro_abierto"):
        if k in d:
            if not isinstance(d[k], bool):
                return error("Valor inválido para un ajuste.")
            cambios[k] = d[k]
    if "voz" in d:
        voz = str(d.get("voz") or "").strip()
        if len(voz) > 120 or re.search(r"[\x00-\x1f<>]", voz):
            return error("El nombre de la voz no es válido.")
        cambios["voz"] = voz
    if "temas_off" in d:
        if not isinstance(d["temas_off"], list):
            return error("Datos inválidos.")
        off = [t for t in d["temas_off"] if t in C.TEMAS]
        if len(off) >= len(C.TEMAS):
            return error("Tiene que quedar al menos un tema activo.")
        cambios["temas_off"] = off
    con = con_db()
    db.guardar_config(con, cambios)
    con.close()
    return jsonify({"ok": True})


@app.get("/api/docente/docentes")
@requiere("docente")
def api_docente_docentes():
    con = con_db()
    ult = {r[0]: r[1] for r in con.execute(
        "SELECT usuario, MAX(fecha) FROM auditoria WHERE evento IN ('Ingreso correcto','Cuenta docente creada') GROUP BY usuario")}
    out = [{"id": r["id"], "nombre": r["nombre"], "usuario": r["usuario"], "creado": r["creado"],
            "ultimo": ult.get(r["usuario"]), "yo": r["id"] == session["uid"],
            "grados": [int(x) for x in (r["grados"] or "1,2,3").split(",")]}
           for r in con.execute("SELECT * FROM docentes ORDER BY creado")]
    con.close()
    return jsonify(out)


@app.put("/api/docente/mis-grados")
@requiere("docente")
def api_docente_mis_grados():
    """La docente cambia los grados que tiene a cargo."""
    try:
        grados = leer_grados(cuerpo().get("grados"))
    except ValueError as e:
        return error(str(e))
    con = con_db()
    con.execute("UPDATE docentes SET grados=? WHERE id=?", (grados, session["uid"]))
    con.commit()
    con.close()
    return jsonify({"ok": True, "grados": [int(x) for x in grados.split(",")]})


@app.delete("/api/docente/docentes/<int:did>")
@requiere("docente")
def api_docente_docente_borrar(did):
    if did == session["uid"]:
        return error("No podés eliminar tu propia cuenta.")
    con = con_db()
    r = con.execute("SELECT usuario FROM docentes WHERE id=?", (did,)).fetchone()
    if not r:
        con.close()
        return error("Esa cuenta docente no existe.", 404)
    con.execute("DELETE FROM docentes WHERE id=?", (did,))
    yo = con.execute("SELECT usuario FROM docentes WHERE id=?", (session["uid"],)).fetchone()[0]
    db.registrar(con, f"Cuenta docente eliminada: {r[0]}", yo, ip())
    con.close()
    return jsonify({"ok": True})


@app.get("/api/docente/auditoria")
@requiere("docente")
def api_docente_auditoria():
    con = con_db()
    out = [dict(r) for r in con.execute("SELECT fecha, usuario, evento, ip FROM auditoria ORDER BY id DESC LIMIT 40")]
    con.close()
    return jsonify(out)


def celda(v):
    """Texto para el CSV: si empieza con = + - @, Excel lo tomaría como fórmula; se le antepone un apóstrofo."""
    s = str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@", "\t", "\r") else s


@app.get("/api/docente/exportar.csv")
@requiere("docente")
def api_docente_exportar():
    con = con_db()
    acts = {a["id"]: a for a in todas_actividades(con)}
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Fecha", "Alumno", "Grado", "Actividad", "Tipo", "Correctas a la primera", "Total", "Porcentaje",
                "Estrellas", "Minutos", "Tarea"])
    fg, pg = sql_grados(con, "a.grado")
    for r in con.execute("SELECT i.*, a.nombre, a.grado, t.titulo tt FROM intentos i JOIN alumnos a ON a.id=i.alumno_id "
                         f"LEFT JOIN tareas t ON t.id=i.tarea_id WHERE {fg} ORDER BY i.fecha", pg):
        act = acts.get(r["actividad_id"])
        w.writerow([r["fecha"], celda(r["nombre"]), r["grado"], celda(act["titulo"] if act else r["actividad_id"]),
                    C.TIPOS.get(act["tipo"], {}).get("n", "") if act else "", r["aciertos"], r["total"],
                    pct(r["aciertos"], r["total"]), r["estrellas"], round(r["segundos"] / 60, 1), celda(r["tt"] or "")])
    con.close()
    datos = io.BytesIO(buf.getvalue().encode("utf-8-sig"))
    return send_file(datos, mimetype="text/csv", as_attachment=True,
                     download_name=f"resultados-isla-{date.today().isoformat()}.csv")


@app.get("/api/docente/copia")
@requiere("docente")
def api_docente_copia():
    con = con_db()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp.close()
    destino = sqlite3.connect(tmp.name)
    con.backup(destino)
    destino.close()
    db.registrar(con, "Descarga de copia de seguridad", None, ip())
    con.close()
    with open(tmp.name, "rb") as f:
        datos = io.BytesIO(f.read())
    os.unlink(tmp.name)
    return send_file(datos, mimetype="application/octet-stream", as_attachment=True,
                     download_name=f"copia-isla-{date.today().isoformat()}.db")


# =================================================================
# Arranque
# =================================================================
def ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        r = s.getsockname()[0]
        s.close()
        return r
    except OSError:
        return "127.0.0.1"


def main():
    p = argparse.ArgumentParser(description="La Isla de los Cuentos")
    p.add_argument("--red", action="store_true", help="permitir conexiones desde otras computadoras de la red")
    p.add_argument("--puerto", type=int, default=5000)
    p.add_argument("--sin-navegador", action="store_true")
    a = p.parse_args()
    db.inicializar()
    host = "0.0.0.0" if a.red else "127.0.0.1"
    url = f"http://localhost:{a.puerto}"
    print("\n  🏝️  La Isla de los Cuentos")
    print(f"  Chicos:   {url}/")
    print(f"  Docente:  {url}/docente")
    if a.red:
        print(f"  Desde otras computadoras del aula: http://{ip_local()}:{a.puerto}/")
    print("  Para cerrar el juego, cerrá esta ventana (o apretá Ctrl+C).\n")
    if not a.sin_navegador:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host=host, port=a.puerto, debug=False, threaded=True)


db.inicializar()

if __name__ == "__main__":
    main()
