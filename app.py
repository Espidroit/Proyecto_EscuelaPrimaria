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

from flask import Flask, abort, jsonify, request, send_file, send_from_directory, session

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
ORDEN_TIPOS = list(C.TIPOS.keys())


# =================================================================
# Infraestructura
# =================================================================
def con_db():
    return db.conectar()


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


def cuerpo():
    d = request.get_json(silent=True)
    return d if isinstance(d, dict) else {}


def texto(v, maximo=200):
    return str(v or "").strip()[:maximo]


# =================================================================
# Actividades (base + creadas por la docente)
# =================================================================
def todas_actividades(con):
    acts = [dict(a) for a in C.ACTIVIDADES_BASE]
    for r in con.execute("SELECT id, tipo, datos FROM actividades_custom ORDER BY creado"):
        d = json.loads(r["datos"])
        d.update({"id": r["id"], "tipo": r["tipo"], "base": False})
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
    return act["tipo"] == "cuento" or C.TIPOS[act["tipo"]]["tema"] not in cfg["temas_off"]


def niveles_para(grado, cfg):
    return (1,) if grado == 1 and not cfg["nivel2_para_1"] else (1, 2)


def visibles_para(con, alumno, cfg):
    niveles = niveles_para(alumno["grado"], cfg)
    acts = [a for a in todas_actividades(con)
            if a["id"] not in cfg["ocultas"] and int(a["nivel"]) in niveles and tema_juego_activo(a, cfg)]
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
        return f"Escribir «{it['p']}»"
    except (IndexError, KeyError):
        return "(ítem modificado)"


def resumen_actividad(act):
    temas = sorted({q["tema"] for q in act["preguntas"]}) if act["tipo"] == "cuento" else [C.TIPOS[act["tipo"]]["tema"]]
    n = len(act["preguntas"] if act["tipo"] == "cuento" else act["items"])
    return {"id": act["id"], "tipo": act["tipo"], "titulo": act["titulo"], "e": act.get("e", "📖"),
            "sticker": act.get("sticker", "⭐"), "nivel": int(act["nivel"]), "temas": temas, "n": n,
            "base": act.get("base", False)}


# =================================================================
# Tareas
# =================================================================
def asignados(con, tarea):
    if tarea["destino"] == "todos":
        q = con.execute("SELECT id FROM alumnos WHERE activo=1")
    elif tarea["destino"] in ("grado1", "grado2"):
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
    acts_por_id = {a["id"]: a for a in todas_actividades(con)}
    res = []
    for t in con.execute("SELECT * FROM tareas WHERE archivada=0 ORDER BY creada DESC"):
        t = dict(t)
        if alumno["id"] not in asignados(con, t):
            continue
        acts = actividades_tarea(con, t["id"], acts_por_id)
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
                    "tipos": C.TIPOS, "medallas": C.MEDALLAS, "niveles": C.NIVELES})


# =================================================================
# API de los chicos
# =================================================================
@app.post("/api/alumno/ingresar")
def api_alumno_ingresar():
    d = cuerpo()
    try:
        aid = int(d.get("id"))
    except (TypeError, ValueError):
        return error("Datos incompletos.")
    clave = d.get("clave")
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
    out = {
        "id": a["id"], "nombre": a["nombre"], "grado": a["grado"], "monedas": a["monedas"],
        "nivel": info_nivel(a["xp"]), "avatar": avatar_de(a), "items": estado_items(con, a),
        "estrellas": sum(mejores.values()), "hechas": len(mejores), "tareas_pendientes": pendientes,
        "medallas": [{**m, "fecha": meds.get(m["id"])} for m in C.MEDALLAS], "album": album,
        "cfg": {"mayus": a["grado"] == 1 and cfg["mayus_1"], "auto_leer": cfg["auto_leer"],
                "voz_lenta": cfg["voz_lenta"], "sonido": cfg["sonido"], "voz": cfg["voz"]},
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
    segundos = max(0, min(int(d.get("segundos") or 0), 3 * 3600))
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
def es_local():
    return ip() in ("127.0.0.1", "::1", "localhost")


@app.get("/api/docente/estado")
def api_docente_estado():
    con = con_db()
    n = con.execute("SELECT COUNT(*) FROM docentes").fetchone()[0]
    yo = None
    if session.get("rol") == "docente":
        r = con.execute("SELECT nombre, usuario FROM docentes WHERE id=?", (session["uid"],)).fetchone()
        yo = dict(r) if r else None
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
    nombre, usuario, pw = texto(d.get("nombre"), 60), texto(d.get("usuario"), 30).lower(), str(d.get("password") or "")
    if not nombre or not re.fullmatch(r"[a-z0-9._-]{3,30}", usuario):
        con.close()
        return error("El usuario debe tener entre 3 y 30 letras o números, sin espacios.")
    if len(pw) < 8 or pw.isdigit() or pw.isalpha():
        con.close()
        return error("La contraseña debe tener al menos 8 caracteres, con letras y números.")
    if con.execute("SELECT 1 FROM docentes WHERE usuario=?", (usuario,)).fetchone():
        con.close()
        return error("Ese usuario ya existe. Elegí otro.")
    cur = con.execute("INSERT INTO docentes(usuario, nombre, pass_hash, creado) VALUES(?,?,?,?)",
                      (usuario, nombre, seg.hashear(pw), db.ahora()))
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
    if not r or not seg.verificar(pw, r["pass_hash"]):
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
    if not seg.verificar(str(d.get("actual") or ""), r["pass_hash"]):
        con.close()
        return error("La contraseña actual no es correcta.", 403)
    nueva = str(d.get("nueva") or "")
    if len(nueva) < 8 or nueva.isdigit() or nueva.isalpha():
        con.close()
        return error("La nueva contraseña debe tener al menos 8 caracteres, con letras y números.")
    con.execute("UPDATE docentes SET pass_hash=? WHERE id=?", (seg.hashear(nueva), r["id"]))
    db.registrar(con, "Cambio de contraseña", r["usuario"], ip())
    con.close()
    return jsonify({"ok": True})


# =================================================================
# API docente: estadísticas
# =================================================================
def pct(ok, n):
    return round(ok * 100 / n) if n else None


def stats_temas(con, alumno_id=None):
    sql = "SELECT tema, SUM(primera), COUNT(*) FROM respuestas" + (" WHERE alumno_id=?" if alumno_id else "") + " GROUP BY tema"
    return {r[0]: {"pct": pct(r[1], r[2]), "n": r[2]} for r in con.execute(sql, (alumno_id,) if alumno_id else ())}


def semanas(con, alumno_id=None, tema=None, cuantas=10):
    filtros, params = [], []
    if alumno_id:
        filtros.append("alumno_id=?"); params.append(alumno_id)
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
    alumnos = [dict(r) for r in con.execute("SELECT * FROM alumnos WHERE activo=1 ORDER BY nombre COLLATE NOCASE")]
    hace7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    semana = con.execute("SELECT COUNT(*) FROM intentos WHERE fecha>=?", (hace7,)).fetchone()[0]
    tot = con.execute("SELECT SUM(primera), COUNT(*) FROM respuestas").fetchone()
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
        bajos = [C.TEMAS[t]["n"] for t in temas_on if st.get(t) and st[t]["n"] >= 3 and st[t]["pct"] < 50]
        if bajos:
            alertas.append({"id": a["id"], "nombre": a["nombre"], "motivo": "Le cuesta: " + ", ".join(bajos)})
        if not ultimo.get(a["id"]):
            alertas.append({"id": a["id"], "nombre": a["nombre"], "motivo": "Todavía no jugó ninguna actividad"})
        elif ultimo[a["id"]] < hace7:
            alertas.append({"id": a["id"], "nombre": a["nombre"], "motivo": "Hace más de una semana que no juega"})
    recientes = [{"alumno": r["nombre"], "alumno_id": r["alumno_id"], **nombre_act(acts, r["actividad_id"]),
                  "fecha": r["fecha"], "estrellas": r["estrellas"], "aciertos": r["aciertos"], "total": r["total"],
                  "tarea": r["tarea_id"] is not None}
                 for r in con.execute("SELECT i.*, a.nombre FROM intentos i JOIN alumnos a ON a.id=i.alumno_id "
                                      "ORDER BY i.fecha DESC, i.id DESC LIMIT 8")]
    hoy = date.today().isoformat()
    tareas = []
    for t in con.execute("SELECT * FROM tareas WHERE archivada=0 ORDER BY creada DESC LIMIT 6"):
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
           for r in con.execute("SELECT * FROM alumnos ORDER BY activo DESC, grado, nombre COLLATE NOCASE")]
    con.close()
    return jsonify(out)


@app.post("/api/docente/alumnos")
@requiere("docente")
def api_docente_alumno_crear():
    d = cuerpo()
    nombres = d.get("nombres") if isinstance(d.get("nombres"), list) else [d.get("nombre")]
    nombres = [texto(n, 40) for n in nombres if texto(n, 40)]
    grado = 2 if str(d.get("grado")) == "2" else 1
    if not nombres:
        return error("Escribí el nombre del alumno.")
    if len(nombres) > 60:
        return error("Podés cargar hasta 60 alumnos por vez.")
    con = con_db()
    existentes = {r[0].lower() for r in con.execute("SELECT nombre FROM alumnos")}
    repetidos = [n for n in nombres if n.lower() in existentes]
    if repetidos:
        con.close()
        return error("Ya existe un alumno llamado: " + ", ".join(repetidos) + ". Agregá la inicial del apellido.")
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
    a = con.execute("SELECT * FROM alumnos WHERE id=?", (aid,)).fetchone()
    if not a:
        con.close()
        return error("No existe.", 404)
    nombre = texto(d.get("nombre"), 40) or a["nombre"]
    if con.execute("SELECT 1 FROM alumnos WHERE lower(nombre)=lower(?) AND id<>?", (nombre, aid)).fetchone():
        con.close()
        return error("Ya existe otro alumno con ese nombre.")
    grado = 2 if str(d.get("grado", a["grado"])) == "2" else 1
    activo = 1 if d.get("activo", bool(a["activo"])) else 0
    con.execute("UPDATE alumnos SET nombre=?, grado=?, activo=? WHERE id=?", (nombre, grado, activo, aid))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.post("/api/docente/alumnos/<int:aid>/clave")
@requiere("docente")
def api_docente_alumno_clave(aid):
    con = con_db()
    c = clave_nueva()
    con.execute("UPDATE alumnos SET clave=? WHERE id=?", (json.dumps(c, ensure_ascii=False), aid))
    con.commit()
    con.close()
    return jsonify({"ok": True, "clave": c})


@app.post("/api/docente/alumnos/<int:aid>/reiniciar")
@requiere("docente")
def api_docente_alumno_reiniciar(aid):
    con = con_db()
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
    con.execute("DELETE FROM alumnos WHERE id=?", (aid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.get("/api/docente/alumnos/<int:aid>")
@requiere("docente")
def api_docente_alumno_ficha(aid):
    con = con_db()
    a = con.execute("SELECT * FROM alumnos WHERE id=?", (aid,)).fetchone()
    if not a:
        con.close()
        return error("No existe.", 404)
    a = dict(a)
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
    t = texto(cuerpo().get("texto"), 1000)
    if not t:
        return error("Escribí la observación.")
    con = con_db()
    if not con.execute("SELECT 1 FROM alumnos WHERE id=?", (aid,)).fetchone():
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
    con.execute("DELETE FROM observaciones WHERE id=?", (oid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


# =================================================================
# API docente: tareas
# =================================================================
DESTINOS = {"todos": "Todo el grupo", "grado1": "1.º grado", "grado2": "2.º grado", "elegidos": "Alumnos elegidos"}


@app.get("/api/docente/tareas")
@requiere("docente")
def api_docente_tareas():
    con = con_db()
    acts = {a["id"]: a for a in todas_actividades(con)}
    hoy = date.today().isoformat()
    out = []
    for t in con.execute("SELECT * FROM tareas ORDER BY archivada, creada DESC"):
        t = dict(t)
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
    titulo = texto(d.get("titulo"), 80)
    consigna = texto(d.get("consigna"), 400)
    limite = texto(d.get("fecha_limite"), 10) or None
    destino = d.get("destino") if d.get("destino") in DESTINOS else "todos"
    try:
        recompensa = max(0, min(int(d.get("recompensa", 30)), 200))
    except (TypeError, ValueError):
        recompensa = 30
    if not titulo:
        return error("Poné un título a la tarea.")
    if limite and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", limite):
        return error("La fecha límite no es válida.")
    con = con_db()
    ids_validos = {a["id"] for a in todas_actividades(con)}
    acts = [x for x in (d.get("actividades") or []) if x in ids_validos][:12]
    if not acts:
        con.close()
        return error("Elegí al menos una actividad.")
    alumnos = []
    if destino == "elegidos":
        validos = {r[0] for r in con.execute("SELECT id FROM alumnos WHERE activo=1")}
        alumnos = [int(x) for x in (d.get("alumnos") or []) if str(x).isdigit() and int(x) in validos]
        if not alumnos:
            con.close()
            return error("Elegí al menos un alumno.")
    cur = con.execute("INSERT INTO tareas(titulo, consigna, fecha_limite, destino, recompensa, creada) VALUES(?,?,?,?,?,?)",
                      (titulo, consigna, limite, destino, recompensa, db.ahora()))
    for i, a in enumerate(dict.fromkeys(acts)):
        con.execute("INSERT INTO tarea_actividades VALUES(?,?,?)", (cur.lastrowid, a, i))
    for a in alumnos:
        con.execute("INSERT OR IGNORE INTO tarea_alumnos VALUES(?,?)", (cur.lastrowid, a))
    con.commit()
    con.close()
    return jsonify({"ok": True, "id": cur.lastrowid})


@app.get("/api/docente/tareas/<int:tid>")
@requiere("docente")
def api_docente_tarea_ver(tid):
    con = con_db()
    t = con.execute("SELECT * FROM tareas WHERE id=?", (tid,)).fetchone()
    if not t:
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
                      "actividades": [{"estrellas": mej[a["id"]][0], "pct": pct(mej[a["id"]][1], mej[a["id"]][2])}
                                      if a["id"] in mej else None for a in acts]})
    con.close()
    return jsonify({**t, "destino_n": DESTINOS.get(t["destino"]), "actividades": [resumen_actividad(a) for a in acts],
                    "alumnos": filas})


@app.post("/api/docente/tareas/<int:tid>/archivar")
@requiere("docente")
def api_docente_tarea_archivar(tid):
    con = con_db()
    con.execute("UPDATE tareas SET archivada=1-archivada WHERE id=?", (tid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.delete("/api/docente/tareas/<int:tid>")
@requiere("docente")
def api_docente_tarea_borrar(tid):
    con = con_db()
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
    uso = {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT actividad_id, COUNT(*), COUNT(DISTINCT alumno_id) FROM intentos GROUP BY actividad_id")}
    res = {r[0]: pct(r[1], r[2]) for r in con.execute(
        "SELECT actividad_id, SUM(primera), COUNT(*) FROM respuestas GROUP BY actividad_id")}
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
        errores = {r[0]: {"pct": pct(r[1], r[2]), "n": r[2]} for r in con.execute(
            "SELECT item_idx, SUM(primera), COUNT(*) FROM respuestas WHERE actividad_id=? GROUP BY item_idx", (aid,))}
    con.close()
    if not a:
        return error("No existe.", 404)
    return jsonify({**a, "resultados": errores})


def _s(v, n=120):
    return texto(v, n)


def validar_actividad(d):
    """Devuelve (tipo, datos) o lanza ValueError con un mensaje claro."""
    tipo = d.get("tipo")
    if tipo not in C.TIPOS:
        raise ValueError("Tipo de actividad inválido.")
    titulo = _s(d.get("titulo"), 60)
    if not titulo:
        raise ValueError("Falta el título.")
    datos = {"titulo": titulo, "e": _s(d.get("e"), 8) or C.TIPOS[tipo]["i"], "sticker": _s(d.get("sticker"), 8) or "⭐",
             "nivel": 2 if str(d.get("nivel")) == "2" else 1}
    comprension = [k for k, v in C.TEMAS.items() if v["area"] == "Comprensión lectora"]
    if tipo == "cuento":
        txt = re.sub(r"\s+", " ", _s(d.get("texto"), 2500))
        if len(txt) < 20:
            raise ValueError("El texto del cuento es muy corto.")
        preguntas = []
        for i, q in enumerate(d.get("preguntas") or [], 1):
            if not isinstance(q, dict):
                continue
            t = q.get("t")
            if t == "o":
                items = [_s(x) for x in q.get("items") or [] if _s(x)]
                if len(items) >= 3:
                    preguntas.append({"t": "o", "tema": "secuencia", "items": items[:5]})
                continue
            tema = q.get("tema") if q.get("tema") in comprension else "detalles"
            p = _s(q.get("p"), 200)
            if not p:
                continue
            if t == "vf":
                preguntas.append({"t": "vf", "tema": tema, "p": p, "v": bool(q.get("v"))})
            else:
                o = [_s(x) for x in q.get("o") or []]
                if not o or not o[0] or len([x for x in o if x]) < 2:
                    raise ValueError(f"La pregunta {i} necesita la respuesta correcta y al menos una incorrecta.")
                preguntas.append({"t": "e", "tema": tema, "p": p, "o": [x for x in o if x][:3]})
        if len(preguntas) < 2:
            raise ValueError("Agregá al menos 2 preguntas completas.")
        datos.update({"texto": txt, "preguntas": preguntas[:12]})
        return tipo, datos
    items = []
    for it in d.get("items") or []:
        if not isinstance(it, dict):
            continue
        if tipo == "oraciones":
            t = re.sub(r"\s+", " ", _s(it.get("t"), 120)).strip(" .")
            if 3 <= len(t.split()) <= 10:
                items.append({"e": _s(it.get("e"), 8) or "📝", "t": t})
        elif tipo == "palabras":
            p = _s(it.get("p"), 12).lower()
            if re.fullmatch(r"[a-zñáéíóúü]{2,10}", p):
                items.append({"e": _s(it.get("e"), 8) or "🔤", "p": p})
        elif tipo == "rimas":
            p, c = _s(it.get("p"), 20).lower(), _s((it.get("c") or {}).get("t"), 20).lower()
            x = [{"t": _s(o.get("t"), 20).lower(), "e": _s(o.get("e"), 8)} for o in it.get("x") or [] if isinstance(o, dict) and _s(o.get("t"))]
            if p and c and x:
                items.append({"p": p, "e": _s(it.get("e"), 8), "c": {"t": c, "e": _s((it.get("c") or {}).get("e"), 8)}, "x": x[:2]})
    if len(items) < 3:
        raise ValueError({"oraciones": "Escribí al menos 3 oraciones (de 3 a 10 palabras cada una).",
                          "palabras": "Escribí al menos 3 palabras (solo letras, de 2 a 10 letras).",
                          "rimas": "Completá al menos 3 rimas con la palabra, la que rima y una que no rima."}[tipo])
    datos["items"] = items[:12]
    return tipo, datos


@app.post("/api/docente/actividades")
@requiere("docente")
def api_docente_actividad_crear():
    try:
        tipo, datos = validar_actividad(cuerpo())
    except ValueError as e:
        return error(str(e))
    con = con_db()
    aid = "c-" + secrets.token_hex(4)
    con.execute("INSERT INTO actividades_custom VALUES(?,?,?,?)", (aid, tipo, json.dumps(datos, ensure_ascii=False), db.ahora()))
    con.commit()
    con.close()
    return jsonify({"ok": True, "id": aid})


@app.put("/api/docente/actividades/<aid>")
@requiere("docente")
def api_docente_actividad_editar(aid):
    try:
        tipo, datos = validar_actividad(cuerpo())
    except ValueError as e:
        return error(str(e))
    con = con_db()
    r = con.execute("SELECT tipo FROM actividades_custom WHERE id=?", (aid,)).fetchone()
    if not r:
        con.close()
        return error("Solo se pueden editar las actividades creadas por vos.", 403)
    con.execute("UPDATE actividades_custom SET tipo=?, datos=? WHERE id=?", (tipo, json.dumps(datos, ensure_ascii=False), aid))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.delete("/api/docente/actividades/<aid>")
@requiere("docente")
def api_docente_actividad_borrar(aid):
    con = con_db()
    con.execute("DELETE FROM actividades_custom WHERE id=?", (aid,))
    con.execute("DELETE FROM tarea_actividades WHERE actividad_id=?", (aid,))
    con.commit()
    con.close()
    return jsonify({"ok": True})


@app.post("/api/docente/actividades/<aid>/visible")
@requiere("docente")
def api_docente_actividad_visible(aid):
    con = con_db()
    cfg = db.leer_config(con)
    ocultas = set(cfg["ocultas"])
    if cuerpo().get("visible"):
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
    for k in ("mayus_1", "nivel2_para_1", "auto_leer", "voz_lenta", "sonido", "progresivo", "registro_abierto"):
        if k in d:
            cambios[k] = bool(d[k])
    if "voz" in d:
        cambios["voz"] = texto(d.get("voz"), 120)
    if "temas_off" in d and isinstance(d["temas_off"], list):
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
            "ultimo": ult.get(r["usuario"]), "yo": r["id"] == session["uid"]}
           for r in con.execute("SELECT * FROM docentes ORDER BY creado")]
    con.close()
    return jsonify(out)


@app.delete("/api/docente/docentes/<int:did>")
@requiere("docente")
def api_docente_docente_borrar(did):
    if did == session["uid"]:
        return error("No podés eliminar tu propia cuenta.")
    con = con_db()
    r = con.execute("SELECT usuario FROM docentes WHERE id=?", (did,)).fetchone()
    if r:
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


@app.get("/api/docente/exportar.csv")
@requiere("docente")
def api_docente_exportar():
    con = con_db()
    acts = {a["id"]: a for a in todas_actividades(con)}
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Fecha", "Alumno", "Grado", "Actividad", "Tipo", "Correctas a la primera", "Total", "Porcentaje",
                "Estrellas", "Minutos", "Tarea"])
    for r in con.execute("SELECT i.*, a.nombre, a.grado, t.titulo tt FROM intentos i JOIN alumnos a ON a.id=i.alumno_id "
                         "LEFT JOIN tareas t ON t.id=i.tarea_id ORDER BY i.fecha"):
        act = acts.get(r["actividad_id"])
        w.writerow([r["fecha"], r["nombre"], r["grado"], act["titulo"] if act else r["actividad_id"],
                    C.TIPOS.get(act["tipo"], {}).get("n", "") if act else "", r["aciertos"], r["total"],
                    pct(r["aciertos"], r["total"]), r["estrellas"], round(r["segundos"] / 60, 1), r["tt"] or ""])
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
    datos = io.BytesIO(open(tmp.name, "rb").read())
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
