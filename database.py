"""
Base de datos SQLite de La Isla de los Cuentos.
El archivo se crea solo la primera vez (datos/isla.db).
"""
import json
import os
import sqlite3
from datetime import datetime

# ISLA_DATOS permite usar otra carpeta (las pruebas automáticas usan una temporal para no tocar los datos reales)
CARPETA_DATOS = os.environ.get("ISLA_DATOS") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
RUTA_DB = os.path.join(CARPETA_DATOS, "isla.db")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS docentes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    pass_hash TEXT NOT NULL,
    creado TEXT NOT NULL,
    grados TEXT NOT NULL DEFAULT '1,2,3',  -- grados a cargo de la docente (ve solo esos alumnos)
    recuperacion TEXT,                     -- código de recuperación (cifrado, como la contraseña)
    debe_cambiar INTEGER NOT NULL DEFAULT 0, -- 1 = entró con una contraseña temporal y tiene que elegir otra
    email TEXT
);
CREATE TABLE IF NOT EXISTS alumnos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    grado INTEGER NOT NULL DEFAULT 1,
    clave TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1,
    monedas INTEGER NOT NULL DEFAULT 0,
    xp INTEGER NOT NULL DEFAULT 0,
    avatar TEXT NOT NULL,
    creado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS inventario(
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL,
    fecha TEXT NOT NULL,
    PRIMARY KEY(alumno_id, item_id)
);
CREATE TABLE IF NOT EXISTS medallas(
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    medalla_id TEXT NOT NULL,
    fecha TEXT NOT NULL,
    PRIMARY KEY(alumno_id, medalla_id)
);
CREATE TABLE IF NOT EXISTS actividades_custom(
    id TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    datos TEXT NOT NULL,
    creado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS intentos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    actividad_id TEXT NOT NULL,
    tarea_id INTEGER,
    fecha TEXT NOT NULL,
    aciertos INTEGER NOT NULL,
    total INTEGER NOT NULL,
    estrellas INTEGER NOT NULL,
    monedas INTEGER NOT NULL,
    segundos INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS respuestas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intento_id INTEGER NOT NULL REFERENCES intentos(id) ON DELETE CASCADE,
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    actividad_id TEXT NOT NULL,
    item_idx INTEGER NOT NULL,
    tema TEXT NOT NULL,
    primera INTEGER NOT NULL,
    intentos INTEGER NOT NULL,
    fecha TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_resp_alumno ON respuestas(alumno_id, fecha);
CREATE INDEX IF NOT EXISTS idx_int_alumno ON intentos(alumno_id, fecha);
CREATE TABLE IF NOT EXISTS tareas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    consigna TEXT NOT NULL DEFAULT '',
    fecha_limite TEXT,
    destino TEXT NOT NULL DEFAULT 'todos',
    recompensa INTEGER NOT NULL DEFAULT 30,
    creada TEXT NOT NULL,
    archivada INTEGER NOT NULL DEFAULT 0,
    grados TEXT                             -- grados de la docente que la creó (NULL = todos)
);
CREATE TABLE IF NOT EXISTS tarea_actividades(
    tarea_id INTEGER NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    actividad_id TEXT NOT NULL,
    orden INTEGER NOT NULL,
    PRIMARY KEY(tarea_id, actividad_id)
);
CREATE TABLE IF NOT EXISTS tarea_alumnos(
    tarea_id INTEGER NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    PRIMARY KEY(tarea_id, alumno_id)
);
CREATE TABLE IF NOT EXISTS tarea_entregas(
    tarea_id INTEGER NOT NULL REFERENCES tareas(id) ON DELETE CASCADE,
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    fecha TEXT NOT NULL,
    PRIMARY KEY(tarea_id, alumno_id)
);
CREATE TABLE IF NOT EXISTS observaciones(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    fecha TEXT NOT NULL,
    texto TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS escritos(          -- «Escribo»: textos que escriben los chicos
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL REFERENCES alumnos(id) ON DELETE CASCADE,
    consigna_id TEXT NOT NULL,
    texto TEXT NOT NULL,
    fecha TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'pendiente',  -- pendiente / revisado
    devolucion TEXT,                           -- lo que le escribe la docente
    estrellas INTEGER,                         -- 1 a 3, las pone la docente
    revisado_por INTEGER,
    fecha_revision TEXT,
    visto INTEGER NOT NULL DEFAULT 0           -- 1 = el chico ya vio la devolución
);
CREATE INDEX IF NOT EXISTS idx_escritos_alumno ON escritos(alumno_id, fecha);
CREATE TABLE IF NOT EXISTS consignas_custom(  -- consignas de escritura que agregan las docentes
    id TEXT PRIMARY KEY,
    datos TEXT NOT NULL,
    creado TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS config(
    clave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS auditoria(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    usuario TEXT,
    evento TEXT NOT NULL,
    ip TEXT
);
"""

CONFIG_INICIAL = {
    "temas_off": [],          # temas desactivados por la docente
    "ocultas": [],            # actividades ocultas
    "mayus_1": True,          # imprenta mayúscula para 1.º grado
    "nivel2_para_1": False,   # mostrar actividades de nivel 2 a 1.º grado
    "nivel3_para_2": False,   # mostrar actividades de nivel 3 a 2.º grado
    "auto_leer": True,        # leer en voz alta automáticamente
    "auto_leer_grados": [1, 2],  # en qué grados se lee sola (en 3.º leen solos; tocan 🔊 si necesitan)
    "voz_lenta": False,
    "voz_alegre": True,       # tono alegre: un poco más aguda y con más ritmo
    "sonido": True,
    "progresivo": True,       # desbloquear actividades de a una
    "voz": "",                # nombre de la voz elegida ("" = automática)
    "registro_abierto": True, # otros docentes pueden crearse su cuenta (solo desde esta computadora)
}


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def conectar():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    con = sqlite3.connect(RUTA_DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# Columnas agregadas después de la primera versión: si la base es vieja, se agregan solas
COLUMNAS_NUEVAS = [
    ("docentes", "grados", "TEXT NOT NULL DEFAULT '1,2,3'"),
    ("tareas", "grados", "TEXT"),
    ("docentes", "recuperacion", "TEXT"),
    ("docentes", "debe_cambiar", "INTEGER NOT NULL DEFAULT 0"),
    ("docentes", "email", "TEXT"),
]


def inicializar():
    con = conectar()
    con.executescript(ESQUEMA)
    for tabla, col, tipo in COLUMNAS_NUEVAS:
        if col not in {r[1] for r in con.execute(f"PRAGMA table_info({tabla})")}:
            con.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}")
    for k, v in CONFIG_INICIAL.items():
        con.execute("INSERT OR IGNORE INTO config(clave, valor) VALUES(?, ?)", (k, json.dumps(v)))
    con.commit()
    con.close()


def leer_config(con):
    cfg = dict(CONFIG_INICIAL)
    for r in con.execute("SELECT clave, valor FROM config"):
        try:
            cfg[r["clave"]] = json.loads(r["valor"])
        except ValueError:
            pass
    return cfg


def guardar_config(con, cambios):
    for k, v in cambios.items():
        if k in CONFIG_INICIAL:
            con.execute("INSERT OR REPLACE INTO config(clave, valor) VALUES(?, ?)", (k, json.dumps(v)))
    con.commit()


def registrar(con, evento, usuario=None, ip=None):
    con.execute("INSERT INTO auditoria(fecha, usuario, evento, ip) VALUES(?,?,?,?)", (ahora(), usuario, evento, ip))
    con.commit()
