"""
Seguridad: contraseñas con hash, clave secreta de sesiones,
límite de intentos de ingreso y cabeceras de protección.
"""
import hashlib
import hmac
import os
import secrets
import threading
import time

ITERACIONES = 240_000


def hashear(password: str) -> str:
    sal = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(sal), ITERACIONES).hex()
    return f"pbkdf2_sha256${ITERACIONES}${sal}${h}"


def verificar(password: str, guardado: str) -> bool:
    try:
        _, it, sal, h = guardado.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(sal), int(it)).hex()
        return hmac.compare_digest(calc, h)
    except (ValueError, TypeError):
        return False


def clave_secreta(carpeta: str) -> str:
    """Genera una vez una clave aleatoria para firmar las sesiones y la guarda en disco."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "clave_secreta.txt")
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(secrets.token_hex(32))
    with open(ruta, encoding="utf-8") as f:
        return f.read().strip()


class LimiteIntentos:
    """Bloquea temporalmente después de varios intentos fallidos."""

    def __init__(self, maximo=5, ventana=600, bloqueo=600):
        self.maximo, self.ventana, self.bloqueo = maximo, ventana, bloqueo
        self.fallos = {}
        self.bloqueados = {}
        self.lock = threading.Lock()

    def bloqueado(self, clave) -> int:
        """Devuelve los segundos que faltan de bloqueo (0 si no está bloqueado)."""
        with self.lock:
            hasta = self.bloqueados.get(clave, 0)
            resto = int(hasta - time.time())
            return max(0, resto)

    def fallo(self, clave):
        with self.lock:
            t = time.time()
            lista = [x for x in self.fallos.get(clave, []) if t - x < self.ventana] + [t]
            self.fallos[clave] = lista
            if len(lista) >= self.maximo:
                self.bloqueados[clave] = t + self.bloqueo
                self.fallos[clave] = []

    def exito(self, clave):
        with self.lock:
            self.fallos.pop(clave, None)
            self.bloqueados.pop(clave, None)


CSP = ("default-src 'self'; "
       "script-src 'self'; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src 'self' https://fonts.gstatic.com; "
       "img-src 'self' data:; "
       "connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


def cabeceras(resp):
    resp.headers["Content-Security-Policy"] = CSP
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if resp.mimetype == "application/json":
        resp.headers["Cache-Control"] = "no-store"
    return resp
