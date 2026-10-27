"""
Pruebas automáticas de La Isla de los Cuentos.

Usan una base de datos temporal: nunca tocan datos/isla.db.

    Windows:  probar.bat
    Otra forma: .venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""
import csv
import io
import os
import shutil
import sys
import tempfile
import unittest
from datetime import date, timedelta

CARPETA = tempfile.mkdtemp(prefix="isla-pruebas-")
os.environ["ISLA_DATOS"] = CARPETA
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as A  # noqa: E402
import contenido as C  # noqa: E402

A.ESPERA_INTENTO = 0  # en las pruebas se juega muy rápido
CLAVE_DOCENTE = "clave1234"
HOY = date.today()


def tearDownModule():
    shutil.rmtree(CARPETA, ignore_errors=True)


class Base(unittest.TestCase):
    """Cliente con la cuenta docente creada (una sola vez para todas las pruebas)."""

    @classmethod
    def setUpClass(cls):
        cls.c = A.app.test_client()
        A.LIMITE_DOCENTE.bloqueados.clear()
        A.LIMITE_ALUMNO.bloqueados.clear()
        s, _ = cls.pedir("post", "/api/docente/configurar", {"nombre": "Seño Prueba", "usuario": "seno", "password": CLAVE_DOCENTE,
                                                                  "grados": [1, 2, 3]})
        if s != 200:  # ya existía: entrar
            cls.docente()

    @classmethod
    def pedir(cls, metodo, url, body=None):
        r = getattr(cls.c, metodo)(url, json=body if body is not None else {}, headers={"X-Isla": "1"},
                                   environ_base={"REMOTE_ADDR": "127.0.0.1"})
        return r.status_code, (r.get_json(silent=True) or {})

    @classmethod
    def docente(cls):
        s, j = cls.pedir("post", "/api/docente/ingresar", {"usuario": "seno", "password": CLAVE_DOCENTE})
        assert s == 200, j

    def acepta(self, metodo, url, body=None):
        s, j = self.pedir(metodo, url, body)
        self.assertEqual(s, 200, j.get("error"))
        return j

    def rechaza(self, metodo, url, body, codigo, texto):
        s, j = self.pedir(metodo, url, body)
        self.assertEqual(s, codigo, f"esperaba {codigo} y vino {s}: {j}")
        self.assertIn(texto.lower(), (j.get("error") or "").lower())

    @classmethod
    def alumno(cls, nombre, grado):
        """Crea el alumno si hace falta y devuelve sus datos (id y clave)."""
        cls.pedir("post", "/api/docente/alumnos", {"nombres": [nombre], "grado": grado})
        return next(a for a in cls.pedir("get", "/api/docente/alumnos")[1] if a["nombre"] == nombre)


# =================================================================
class TestContenido(unittest.TestCase):
    def test_actividades_incluidas_pasan_la_validacion(self):
        for a in C.ACTIVIDADES_BASE:
            with self.subTest(a["id"]):
                tipo, d = A.validar_actividad({**a, "nivel": str(a["nivel"])})
                self.assertEqual(d.get("items", d.get("preguntas")), a.get("items", a.get("preguntas")))

    def test_ids_unicos_y_titulos_sin_repetir_por_juego(self):
        ids = [a["id"] for a in C.ACTIVIDADES_BASE]
        self.assertEqual(len(ids), len(set(ids)))
        titulos = [(a["tipo"], a["titulo"].lower()) for a in C.ACTIVIDADES_BASE]
        self.assertEqual(len(titulos), len(set(titulos)))

    def test_cada_tema_tiene_medalla_y_cada_juego_un_tema(self):
        for k in C.TEMAS:
            self.assertIn("tema-" + k, C.MEDALLAS_POR_ID)
        for k, t in C.TIPOS.items():
            self.assertTrue(t["tema"] is None or t["tema"] in C.TEMAS, k)

    def test_hay_actividades_para_cada_grado(self):
        for nivel in (1, 2, 3):
            self.assertTrue(any(a["nivel"] == nivel for a in C.ACTIVIDADES_BASE), nivel)


# =================================================================
class TestCuentaDocente(Base):
    def test_requiere_sesion(self):
        c = A.app.test_client()
        r = c.get("/api/docente/alumnos")
        self.assertEqual(r.status_code, 401)

    def test_pedidos_sin_cabecera_se_rechazan(self):
        r = self.c.post("/api/docente/alumnos", json={"nombres": ["Pepe"], "grado": 1})
        self.assertEqual(r.status_code, 403)

    def test_reglas_de_la_contrasena(self):
        url = "/api/docente/configurar"
        self.rechaza("post", url, {"nombre": "Otra", "usuario": "otra", "password": "abcdefghij"}, 400, "letras y números")
        self.rechaza("post", url, {"nombre": "Otra", "usuario": "otra", "password": "a1" * 100}, 400, "128")
        self.rechaza("post", url, {"nombre": "Otra", "usuario": "la otra", "password": "clave1234"}, 400, "usuario")
        self.rechaza("post", url, {"nombre": " ", "usuario": "otra", "password": "clave1234"}, 400, "nombre")
        self.rechaza("post", url, {"nombre": "<b>Otra</b>", "usuario": "otra", "password": "clave1234"}, 400, "signos")
        self.rechaza("post", url, {"nombre": "Otra", "usuario": "otra", "password": "clave1234"}, 400, "grado")
        self.rechaza("post", url, {"nombre": "Otra", "usuario": "otra", "password": "clave1234", "grados": [4]}, 400, "grado")
        self.rechaza("post", url, {"nombre": "Otra", "usuario": "seno", "password": "clave1234", "grados": [1]}, 400, "ya existe")
        self.docente()

    def test_cambio_de_contrasena(self):
        url = "/api/docente/password"
        self.rechaza("post", url, {"actual": "mal", "nueva": "nueva1234"}, 403, "actual")
        self.rechaza("post", url, {"actual": CLAVE_DOCENTE, "nueva": CLAVE_DOCENTE}, 400, "distinta")
        self.rechaza("post", url, {"actual": CLAVE_DOCENTE, "nueva": "12345678"}, 400, "letras y números")
        self.acepta("post", url, {"actual": CLAVE_DOCENTE, "nueva": "otra5678"})
        self.acepta("post", url, {"actual": "otra5678", "nueva": CLAVE_DOCENTE})

    def test_borrar_docente(self):
        self.rechaza("delete", "/api/docente/docentes/9999", None, 404, "no existe")


# =================================================================
class TestAlumnos(Base):
    URL = "/api/docente/alumnos"

    def test_grado_obligatorio(self):
        self.rechaza("post", self.URL, {"nombres": ["Ana"]}, 400, "grado")
        self.rechaza("post", self.URL, {"nombres": ["Ana"], "grado": 4}, 400, "grado")

    def test_nombres_invalidos(self):
        for nombre in ("Ana 2", "<b>Ana</b>", "123", "A" * 41, "-Ana"):
            with self.subTest(nombre):
                self.rechaza("post", self.URL, {"nombres": [nombre], "grado": 1}, 400, "nombre")

    def test_repetidos(self):
        self.rechaza("post", self.URL, {"nombres": ["Lola", "lola "], "grado": 1}, 400, "dos veces")
        self.acepta("post", self.URL, {"nombres": ["Lola P."], "grado": 1})
        self.rechaza("post", self.URL, {"nombres": ["lola p."], "grado": 2}, 400, "ya existe")

    def test_nombres_validos_se_limpian(self):
        self.acepta("post", self.URL, {"nombres": ["  Thiago   R. ", "María José", "O'Neill", "Ana-Laura"], "grado": "2"})
        nombres = {a["nombre"] for a in self.pedir("get", self.URL)[1]}
        self.assertTrue({"Thiago R.", "María José", "O'Neill", "Ana-Laura"} <= nombres)

    def test_editar(self):
        al = self.alumno("Editable", 1)
        url = f"{self.URL}/{al['id']}"
        self.rechaza("put", url, {"activo": "no"}, 400, "inválido")
        self.rechaza("put", url, {"grado": 9}, 400, "grado")
        self.rechaza("put", url, {"nombre": "123"}, 400, "letras")
        self.acepta("put", url, {"nombre": "Editado", "grado": "3", "activo": True})

    def test_inexistentes(self):
        self.rechaza("post", f"{self.URL}/9999/clave", None, 404, "no existe")
        self.rechaza("post", f"{self.URL}/9999/reiniciar", None, 404, "no existe")
        self.rechaza("delete", f"{self.URL}/9999", None, 404, "no existe")
        self.rechaza("delete", "/api/docente/observaciones/9999", None, 404, "no existe")

    def test_observaciones(self):
        al = self.alumno("Observado", 1)
        url = f"{self.URL}/{al['id']}/observaciones"
        self.rechaza("post", url, {"texto": "   "}, 400, "escribí")
        self.rechaza("post", url, {"texto": "x" * 1001}, 400, "muy larga")
        self.acepta("post", url, {"texto": "Leyó muy bien hoy."})


# =================================================================
class TestTareas(Base):
    URL = "/api/docente/tareas"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alumno("Tarea Dos", 2)

    def base(self, **extra):
        return {"titulo": "Repaso", "actividades": ["bobi"], "destino": "todos", "recompensa": 30, **extra}

    def test_fechas(self):
        self.rechaza("post", self.URL, self.base(fecha_limite="2026-02-31"), 400, "no es válida")
        self.rechaza("post", self.URL, self.base(fecha_limite="31/12/2026"), 400, "no es válida")
        self.rechaza("post", self.URL, self.base(fecha_limite=(HOY - timedelta(days=1)).isoformat()), 400, "anterior a hoy")
        self.rechaza("post", self.URL, self.base(fecha_limite=(HOY + timedelta(days=400)).isoformat()), 400, "más de un año")
        self.acepta("post", self.URL, self.base(fecha_limite=HOY.isoformat()))
        self.acepta("post", self.URL, self.base(fecha_limite=""))

    def test_premio_destino_y_actividades(self):
        self.rechaza("post", self.URL, self.base(recompensa=500), 400, "premio")
        self.rechaza("post", self.URL, self.base(recompensa="mucho"), 400, "premio")
        self.rechaza("post", self.URL, self.base(destino="grado7"), 400, "para quién")
        self.rechaza("post", self.URL, self.base(actividades=[]), 400, "al menos una")
        self.rechaza("post", self.URL, self.base(actividades="bobi"), 400, "inválidos")
        self.rechaza("post", self.URL, self.base(actividades=[a["id"] for a in C.ACTIVIDADES_BASE[:13]]), 400, "hasta 12")
        self.rechaza("post", self.URL, self.base(titulo="x" * 81), 400, "80")
        self.rechaza("post", self.URL, self.base(destino="elegidos", alumnos=[9999]), 400, "al menos un alumno")

    def test_grado_sin_alumnos(self):
        sin = next((g for g in (1, 2, 3) if not any(a["grado"] == g and a["activo"] for a in self.pedir("get", "/api/docente/alumnos")[1])), None)
        if sin:
            self.rechaza("post", self.URL, self.base(destino=f"grado{sin}"), 400, "no hay alumnos")

    def test_inexistentes(self):
        self.rechaza("post", f"{self.URL}/9999/archivar", None, 404, "no existe")
        self.rechaza("delete", f"{self.URL}/9999", None, 404, "no existe")


# =================================================================
class TestActividades(Base):
    URL = "/api/docente/actividades"

    def act(self, tipo, items, **extra):
        return {"tipo": tipo, "titulo": extra.pop("titulo", f"Prueba {tipo}"), "nivel": "1", "items": items, **extra}

    def test_datos_generales(self):
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 3, nivel="5"), 400, "nivel")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 3, titulo="x" * 61), 400, "60")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 3, titulo=" "), 400, "título")
        self.rechaza("post", self.URL, {**self.act("palabras", [{"p": "sol"}] * 3), "tipo": "inventado"}, 400, "tipo")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 3, e="abc"), 400, "emoji")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 3, sticker="⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"), 400, "emoji")

    def test_filas(self):
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}, {"p": "s0l"}, {"p": "pan"}]), 400, "fila 2")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}, {"e": "🐱", "p": ""}, {"p": "pan"}]), 400, "hay 2")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 13), 400, "hasta 12")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol", "e": "gato"}] * 3), 400, "fila 1: el dibujo")

    def test_cada_juego_rechaza_errores(self):
        casos = [
            ("oraciones", [{"t": "Hola chicos"}], "entre 3 y 10"),
            ("rimas", [{"p": "gato", "c": {"t": "pato"}, "x": [{"t": "pato"}]}], "repetidas"),
            ("rimas", [{"p": "gato", "c": {"t": "pato"}, "x": []}], "no rime"),
            ("silabas", [{"p": "mariposa"}], "guiones"),
            ("ortografia", [{"p": "_a_a", "o": ["c", "s"]}], "un solo _"),
            ("ortografia", [{"p": "ca_a", "o": ["s", "2"]}], "letras"),
            ("ortografia", [{"p": "ca_a", "o": ["s", "S"]}], "repetidas"),
            ("completar", [{"t": "El gato _ leche", "o": ["", "silla"]}], "correcta"),
            ("completar", [{"t": "El gato _ leche", "o": ["toma", "", ""]}], "incorrecta"),
            ("completar", [{"t": "El gato toma leche", "o": ["toma", "silla"]}], "un solo _"),
            ("opuestos", [{"p": "alto", "o": ["Alto", "bajo"]}], "misma palabra"),
            ("clases", [{"p": "gato", "c": "z"}], "clase"),
            ("clases", [{"p": "gato", "c": "s", "t": "El perro ladra"}], "incluir la palabra"),
            ("clases", [{"p": "gato", "c": "s", "t": "Los gatitos duermen"}], "incluir la palabra"),
            ("clases", [{"p": "el gato", "c": "s"}], "una sola palabra"),
        ]
        for tipo, items, texto in casos:
            with self.subTest(tipo=tipo, texto=texto):
                self.rechaza("post", self.URL, self.act(tipo, items * 3), 400, texto)

    def test_cuentos(self):
        cu = {"tipo": "cuento", "titulo": "Cuento de prueba", "nivel": "1", "texto": "Había una vez un gato que tomaba leche."}
        q = {"t": "e", "tema": "personajes", "p": "¿Quién?", "o": ["El gato", "Un perro", ""]}
        self.rechaza("post", self.URL, {**cu, "texto": "corto"}, 400, "muy corto")
        self.rechaza("post", self.URL, {**cu, "texto": "palabra " * 400, "preguntas": [q, q]}, 400, "muy largo")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q]}, 400, "al menos 2")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q, {**q, "o": ["Sí", "sí"]}]}, 400, "pregunta 2")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q, {**q, "p": ""}]}, 400, "falta escribir la pregunta")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q, {"t": "vf", "tema": "detalles", "p": "Es azul", "v": "x"}]}, 400, "verdadera o falsa")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q, q, {"t": "o", "items": ["a", "b", "A"]}]}, 400, "repetidas")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q, q, {"t": "o", "items": ["a", "b"]}]}, 400, "al menos 3")
        self.rechaza("post", self.URL, {**cu, "preguntas": [q] * 13}, 400, "hasta 12")
        self.acepta("post", self.URL, {**cu, "preguntas": [q, {"t": "vf", "tema": "detalles", "p": "Es azul", "v": False},
                                                         {"t": "o", "items": ["a", "b", "c"]}]})

    def test_cada_juego_acepta_datos_correctos(self):
        correctos = {
            "palabras": [{"p": "sol"}, {"p": "Pan"}, {"p": "luna", "e": "🌙"}],
            "oraciones": [{"t": "El sol sale temprano."}] * 3,
            "rimas": [{"p": "gato", "c": {"t": "pato", "e": "🦆"}, "x": [{"t": "mesa"}, {"t": ""}]}] * 3,
            "silabas": [{"p": "ma - ri - po - sa"}] * 3,
            "ortografia": [{"p": "ca_a", "o": ["s", "z", ""]}] * 3,
            "completar": [{"t": "El gato ___ leche.", "o": ["toma", "silla", ""]}] * 3,
            "opuestos": [{"p": "alto", "r": "opuesto", "o": ["bajo", "rojo", ""]}] * 3,
            "clases": [{"p": "Gato", "c": "s", "t": "El gato duerme"}, {"p": "salta", "c": "v"}, {"p": "azul", "c": "a", "e": "👩‍🏫"}],
        }
        for tipo, items in correctos.items():
            with self.subTest(tipo):
                self.acepta("post", self.URL, self.act(tipo, items, titulo=f"Correcta {tipo}"))

    def test_titulo_repetido_y_cambio_de_tipo(self):
        datos = self.act("palabras", [{"p": "sol"}] * 3, titulo="Única")
        aid = self.acepta("post", self.URL, datos)["id"]
        self.rechaza("post", self.URL, {**datos, "titulo": "única"}, 400, "ya hay")
        self.rechaza("post", self.URL, self.act("palabras", [{"p": "sol"}] * 3, titulo="palabras cortas"), 400, "ya hay")
        self.rechaza("put", f"{self.URL}/{aid}", self.act("silabas", [{"p": "pa-to"}] * 3, titulo="Única"), 400, "cambiar el tipo")
        self.acepta("put", f"{self.URL}/{aid}", {**datos, "items": [{"p": "pan"}] * 3})

    def test_actividades_incluidas_no_se_borran_ni_editan(self):
        self.rechaza("delete", f"{self.URL}/bobi", None, 403, "creadas por ustedes")
        self.rechaza("put", f"{self.URL}/bobi", self.act("palabras", [{"p": "sol"}] * 3, titulo="Otra"), 403, "creadas por ustedes")

    def test_visible(self):
        self.rechaza("post", f"{self.URL}/bobi/visible", {"visible": "sí"}, 400, "inválido")
        self.rechaza("post", f"{self.URL}/nada/visible", {"visible": False}, 404, "no existe")
        self.acepta("post", f"{self.URL}/bobi/visible", {"visible": True})


# =================================================================
class TestAjustes(Base):
    URL = "/api/docente/config"

    def test_valores(self):
        self.rechaza("put", self.URL, {"sonido": "false"}, 400, "inválido")
        self.rechaza("put", self.URL, {"temas_off": "rimas"}, 400, "inválidos")
        self.rechaza("put", self.URL, {"temas_off": list(C.TEMAS)}, 400, "al menos un tema")
        self.rechaza("put", self.URL, {"voz": "<script>"}, 400, "voz")
        self.rechaza("put", self.URL, {"voz_alegre": "sí"}, 400, "inválido")
        self.assertTrue(self.pedir("get", self.URL)[1]["cfg"]["voz_alegre"])  # alegre por defecto
        self.acepta("put", self.URL, {"voz_alegre": False})
        self.assertFalse(self.pedir("get", self.URL)[1]["cfg"]["voz_alegre"])
        self.acepta("put", self.URL, {"voz_alegre": True})
        self.acepta("put", self.URL, {"sonido": False, "voz": "Microsoft Elena Online (Natural)"})
        self.acepta("put", self.URL, {"sonido": True, "voz": ""})


# =================================================================
class TestChicos(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uno, cls.dos, cls.tres = (cls.alumno(n, g) for n, g in (("Chico Uno", 1), ("Chico Dos", 2), ("Chico Tres", 3)))

    def entrar(self, al):
        self.acepta("post", "/api/alumno/ingresar", {"id": al["id"], "clave": al["clave"]})

    def jugar(self, aid, intentos=1):
        act = self.pedir("get", f"/api/alumno/actividad/{aid}")[1]
        lista = act.get("preguntas") or act["items"]
        return self.pedir("post", "/api/alumno/intento", {"actividad_id": aid, "segundos": 30,
                                                          "respuestas": [{"idx": x["idx"], "intentos": intentos} for x in lista]})

    def test_ingreso(self):
        self.rechaza("post", "/api/alumno/ingresar", {"id": "x", "clave": self.uno["clave"]}, 400, "incompletos")
        self.rechaza("post", "/api/alumno/ingresar", {"id": self.uno["id"], "clave": ["🍎"]}, 400, "3 dibujos")
        self.rechaza("post", "/api/alumno/ingresar", {"id": self.uno["id"], "clave": ["a", "b", "c"]}, 400, "3 dibujos")
        mala = [d for d in C.DIBUJOS_CLAVE if d != self.uno["clave"][0]][:1] + self.uno["clave"][1:]
        self.rechaza("post", "/api/alumno/ingresar", {"id": self.uno["id"], "clave": mala}, 403, "no son")
        A.LIMITE_ALUMNO.bloqueados.clear()
        self.entrar(self.uno)
        self.assertIn("voz_alegre", self.pedir("get", "/api/alumno/perfil")[1]["cfg"])
        self.docente()

    def test_cada_grado_ve_sus_niveles_y_puede_jugar_todo(self):
        esperado = {1: {1}, 2: {1, 2}, 3: {1, 2, 3}}
        for al in (self.uno, self.dos, self.tres):
            with self.subTest(grado=al["grado"]):
                self.entrar(al)
                acts = self.pedir("get", "/api/alumno/actividades")[1]
                self.assertEqual({a["nivel"] for a in acts}, esperado[al["grado"]])
                for a in acts:
                    s, j = self.jugar(a["id"])
                    self.assertEqual(s, 200, (a["id"], j))
                    self.assertEqual(j["estrellas"], 3)
        self.docente()

    def test_resultados_invalidos(self):
        self.entrar(self.dos)
        act = self.pedir("get", "/api/alumno/actividad/bobi")[1]
        resp = [{"idx": x["idx"], "intentos": 1} for x in act["preguntas"]]
        url = "/api/alumno/intento"
        self.acepta("post", url, {"actividad_id": "bobi", "respuestas": resp, "segundos": "abc"})
        self.acepta("post", url, {"actividad_id": "bobi", "respuestas": resp, "segundos": -50})
        self.rechaza("post", url, {"actividad_id": "bobi", "respuestas": resp[:2]}, 400, "no está completa")
        self.rechaza("post", url, {"actividad_id": "bobi", "respuestas": resp + resp[:1]}, 400, "inválidas")
        self.rechaza("post", url, {"actividad_id": "bobi", "respuestas": "todo bien"}, 400, "inválidas")
        self.rechaza("post", url, {"actividad_id": "no-existe", "respuestas": resp}, 404, "inexistente")
        self.docente()

    def test_no_se_guarda_dos_veces_seguidas(self):
        self.entrar(self.dos)
        con = A.con_db()  # que el último resultado guardado sea viejo
        con.execute("UPDATE intentos SET fecha='2000-01-01 00:00:00' WHERE alumno_id=?", (self.dos["id"],))
        con.commit()
        con.close()
        A.ESPERA_INTENTO = 3
        try:
            self.assertEqual(self.jugar("bobi")[0], 200)
            s, j = self.jugar("bobi")
            self.assertEqual(s, 429, j)
        finally:
            A.ESPERA_INTENTO = 0
        self.docente()

    def test_no_ve_actividades_de_otro_grado(self):
        self.entrar(self.uno)
        nivel3 = next(a["id"] for a in C.ACTIVIDADES_BASE if a["nivel"] == 3)
        self.rechaza("get", f"/api/alumno/actividad/{nivel3}", None, 404, "no está disponible")
        self.docente()

    def test_borrador_no_aparece_ni_en_tareas(self):
        aid = self.acepta("post", "/api/docente/actividades", {"tipo": "palabras", "titulo": "En borrador", "nivel": "1",
                                                               "items": [{"p": "sol"}] * 3, "publicar": True})["id"]
        tid = self.acepta("post", "/api/docente/tareas", {"titulo": "Con borrador", "actividades": [aid], "destino": "todos"})["id"]
        self.acepta("post", f"/api/docente/actividades/{aid}/estado", {"estado": "borrador"})
        self.entrar(self.uno)
        self.assertFalse(any(t["id"] == tid for t in self.pedir("get", "/api/alumno/tareas")[1]))
        self.rechaza("get", f"/api/alumno/actividad/{aid}", None, 404, "no está disponible")
        self.docente()

    def test_avatar_y_tienda(self):
        self.entrar(self.uno)
        self.rechaza("post", "/api/alumno/avatar", {"avatar": "rojo"}, 400, "inválidos")
        bloqueado = next(i for i in C.CATALOGO if i["medalla"])
        self.rechaza("post", "/api/alumno/avatar", {"avatar": {bloqueado["cat"]: bloqueado["v"]}}, 403, "todavía no")
        self.rechaza("post", "/api/alumno/comprar", {"item": "nada"}, 400, "no se puede comprar")
        self.docente()


# =================================================================
class TestPanelYExportar(Base):
    def test_pantallas_del_panel_responden(self):
        al = self.alumno("Panel", 1)
        for url in ("/api/docente/resumen", "/api/docente/alumnos", "/api/docente/tareas", "/api/docente/actividades",
                    "/api/docente/config", "/api/docente/docentes", "/api/docente/auditoria", f"/api/docente/alumnos/{al['id']}"):
            with self.subTest(url):
                self.assertEqual(self.pedir("get", url)[0], 200)

    def test_csv_no_ejecuta_formulas(self):
        self.assertEqual(A.celda("=1+1"), "'=1+1")
        self.assertEqual(A.celda("-2"), "'-2")
        self.assertEqual(A.celda("Repaso"), "Repaso")
        r = self.c.get("/api/docente/exportar.csv", environ_base={"REMOTE_ADDR": "127.0.0.1"})
        self.assertEqual(r.status_code, 200)
        filas = list(csv.reader(io.StringIO(r.data.decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(filas[0][0], "Fecha")

    def test_copia_de_seguridad(self):
        r = self.c.get("/api/docente/copia", environ_base={"REMOTE_ADDR": "127.0.0.1"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data.startswith(b"SQLite format 3"))


# =================================================================
class TestMejoras(Base):
    """Cambios de la revisión: medallas posibles, refuerzo, entregas tarde, túnel y temas apagados."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p1 = cls.alumno("Primero Medallas", 1)
        cls.p3 = cls.alumno("Tercero Medallas", 3)

    def entrar(self, al):
        A.LIMITE_ALUMNO.bloqueados.clear()
        self.acepta("post", "/api/alumno/ingresar", {"id": al["id"], "clave": al["clave"]})

    def test_nombres_de_medallas_y_niveles_neutros(self):
        for m in C.MEDALLAS + C.NIVELES:
            self.assertNotRegex(m["n"], r"(?i)\b(lector|jugador|maestro|rey|mago|pensador|exploradora|guardián)\b")

    def test_hay_cuentos_suficientes_para_cada_grado(self):
        por_nivel = {n: sum(1 for a in C.ACTIVIDADES_BASE if a["tipo"] == "cuento" and a["nivel"] == n) for n in (1, 2, 3)}
        self.assertGreaterEqual(por_nivel[1], 6)   # 1.º puede ganar «Ratón de biblioteca» (6 cuentos)
        self.assertGreaterEqual(por_nivel[3], 4)

    def test_primer_grado_solo_ve_medallas_que_puede_ganar(self):
        self.entrar(self.p1)
        ids = {m["id"] for m in self.pedir("get", "/api/alumno/perfil")[1]["medallas"]}
        self.assertIn("m6", ids)
        for imposible in ("tema-clases", "tema-ortografia", "tema-sinonimos"):
            self.assertNotIn(imposible, ids)
        self.entrar(self.p3)
        self.assertIn("tema-clases", {m["id"] for m in self.pedir("get", "/api/alumno/perfil")[1]["medallas"]})
        self.docente()

    def test_refuerzo_crea_tarea_para_el_alumno(self):
        self.rechaza("post", f"/api/docente/alumnos/{self.p1['id']}/refuerzo", {"tema": "nada"}, 400, "inválido")
        self.rechaza("post", f"/api/docente/alumnos/{self.p1['id']}/refuerzo", {"tema": "clases"}, 400, "no hay actividades")
        j = self.acepta("post", f"/api/docente/alumnos/{self.p1['id']}/refuerzo", {"tema": "secuencia"})
        self.assertTrue(1 <= len(j["actividades"]) <= 3)
        t = self.acepta("get", f"/api/docente/tareas/{j['id']}")
        self.assertEqual([a["id"] for a in t["alumnos"]], [self.p1["id"]])
        self.assertTrue(all(a["nivel"] == 1 for a in t["actividades"]))
        self.entrar(self.p1)
        self.assertTrue(any(x["id"] == j["id"] for x in self.pedir("get", "/api/alumno/tareas")[1]))
        self.docente()

    def test_entrega_fuera_de_termino(self):
        self.assertTrue(A.entrega_tarde("2026-05-03 10:00:00", "2026-05-02"))
        self.assertFalse(A.entrega_tarde("2026-05-02 23:00:00", "2026-05-02"))
        self.assertFalse(A.entrega_tarde(None, "2026-05-02"))
        self.assertFalse(A.entrega_tarde("2026-05-03 10:00:00", None))

    def test_tunel_no_cuenta_como_esta_computadora(self):
        r = self.c.get("/api/docente/estado", headers={"X-Forwarded-For": "200.1.2.3"}, environ_base={"REMOTE_ADDR": "127.0.0.1"})
        self.assertFalse(r.get_json()["local"])
        r = self.c.get("/api/docente/estado", headers={"CF-Connecting-IP": "200.1.2.3"}, environ_base={"REMOTE_ADDR": "127.0.0.1"})
        self.assertFalse(r.get_json()["local"])
        self.assertTrue(self.pedir("get", "/api/docente/estado")[1]["local"])

    def test_cuento_con_todos_sus_temas_apagados_no_aparece(self):
        temas_bobi = sorted({q["tema"] for q in C.ACTIVIDADES_BASE[0]["preguntas"]})
        self.acepta("put", "/api/docente/config", {"temas_off": temas_bobi})
        try:
            self.entrar(self.p1)
            ids = {a["id"] for a in self.pedir("get", "/api/alumno/actividades")[1]}
            self.assertNotIn("bobi", ids)
        finally:
            self.docente()
            self.acepta("put", "/api/docente/config", {"temas_off": []})


# =================================================================
class TestGradosDocente(Base):
    """Cada docente ve y maneja solo a los alumnos de sus grados."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.de1 = cls.alumno("Grado Uno Aislado", 1)
        cls.de3 = cls.alumno("Grado Tres Aislado", 3)

    def setUp(self):
        self.acepta("put", "/api/docente/mis-grados", {"grados": [1]})

    def tearDown(self):
        self.acepta("put", "/api/docente/mis-grados", {"grados": [1, 2, 3]})

    def test_validacion(self):
        self.rechaza("put", "/api/docente/mis-grados", {"grados": []}, 400, "grado")
        self.rechaza("put", "/api/docente/mis-grados", {"grados": ["x"]}, 400, "grado")
        self.assertEqual(self.acepta("get", "/api/docente/estado")["sesion"]["grados"], [1])

    def test_solo_ve_sus_alumnos(self):
        nombres = {a["nombre"] for a in self.pedir("get", "/api/docente/alumnos")[1]}
        self.assertIn("Grado Uno Aislado", nombres)
        self.assertNotIn("Grado Tres Aislado", nombres)
        self.assertTrue(all(a["grado"] == 1 for a in self.acepta("get", "/api/docente/resumen")["alumnos"]))
        r = self.c.get("/api/docente/exportar.csv", environ_base={"REMOTE_ADDR": "127.0.0.1"})
        self.assertNotIn("Grado Tres Aislado", r.data.decode("utf-8-sig"))

    def test_no_puede_tocar_alumnos_de_otro_grado(self):
        otro = self.de3["id"]
        self.rechaza("get", f"/api/docente/alumnos/{otro}", None, 404, "no existe")
        self.rechaza("put", f"/api/docente/alumnos/{otro}", {"nombre": "Hackeado"}, 404, "no existe")
        self.rechaza("post", f"/api/docente/alumnos/{otro}/clave", {}, 404, "no existe")
        self.rechaza("post", f"/api/docente/alumnos/{otro}/observaciones", {"texto": "hola"}, 404, "no existe")
        self.rechaza("post", f"/api/docente/alumnos/{otro}/refuerzo", {"tema": "lugar"}, 404, "no existe")
        self.rechaza("delete", f"/api/docente/alumnos/{otro}", None, 404, "no existe")
        self.rechaza("post", "/api/docente/alumnos", {"nombres": ["Nuevo De Tres"], "grado": 3}, 403, "tus grados")
        self.rechaza("put", f"/api/docente/alumnos/{self.de1['id']}", {"grado": 3}, 403, "tus grados")

    def test_misiones_por_grado(self):
        self.rechaza("post", "/api/docente/tareas", {"titulo": "De tercero", "actividades": ["bobi"], "destino": "grado3"}, 403, "tus grados")
        tid = self.acepta("post", "/api/docente/tareas", {"titulo": "Para mis grados", "actividades": ["bobi"], "destino": "todos"})["id"]
        asignados = {a["id"] for a in self.acepta("get", f"/api/docente/tareas/{tid}")["alumnos"]}
        self.assertIn(self.de1["id"], asignados)
        self.assertNotIn(self.de3["id"], asignados)
        # otra docente, de 3.º, no la ve
        self.acepta("put", "/api/docente/mis-grados", {"grados": [3]})
        self.assertFalse(any(t["id"] == tid for t in self.pedir("get", "/api/docente/tareas")[1]))
        self.rechaza("get", f"/api/docente/tareas/{tid}", None, 404, "no existe")


class TestAvatarGratis(unittest.TestCase):
    def test_lo_fisico_es_gratis_y_los_extras_cuestan(self):
        fisico = ("piel", "ojos", "boca", "colorRopa")
        for it in C.CATALOGO:
            if it["cat"] in fisico:
                self.assertFalse(it["precio"] or it["nivel"] or it["medalla"], it["id"])
        for iid in ("pelo:rulos", "colorPelo:negro", "ropa:remera", "ropa:guardapolvo", "anteojos:redondos"):
            it = C.CATALOGO_POR_ID[iid]
            self.assertFalse(it["precio"] or it["nivel"] or it["medalla"], iid)
        for cat in ("gorro", "mascota", "fondo", "marco"):
            self.assertTrue(any(i["precio"] or i["nivel"] or i["medalla"] for i in C.CATALOGO if i["cat"] == cat), cat)


if __name__ == "__main__":
    unittest.main(verbosity=2)
