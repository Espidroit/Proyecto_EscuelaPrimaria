"""
Recuperar una cuenta docente desde la computadora donde está instalado el juego.

Sirve cuando una docente se olvidó la contraseña y no hay otra cuenta que la pueda
restablecer desde el panel ni tiene su código de recuperación.
Muestra las cuentas y genera una contraseña temporal; al entrar con ella, el panel
pide elegir una nueva.

    Windows: doble clic en recuperar_cuenta.bat
    Otra forma (por ejemplo en PythonAnywhere): python3 recuperar_cuenta.py
"""
import database as db
import seguridad as seg
from app import contrasena_temporal


def main():
    db.inicializar()  # por si la base es de una versión anterior
    con = db.conectar()
    cuentas = con.execute("SELECT id, usuario, nombre FROM docentes ORDER BY id").fetchall()
    if not cuentas:
        print("\n  Todavía no hay cuentas docentes. Creala desde http://localhost:5000/docente\n")
        return
    print("\n  Cuentas docentes:\n")
    for c in cuentas:
        print(f"    {c['id']}. {c['nombre']}  (usuario: {c['usuario']})")
    elegido = input("\n  Escribí el NÚMERO de la cuenta a restablecer (Enter para salir): ").strip()
    cuenta = next((c for c in cuentas if str(c["id"]) == elegido), None)
    if not cuenta:
        print("\n  No se cambió nada.\n")
        return
    temporal = contrasena_temporal()
    con.execute("UPDATE docentes SET pass_hash=?, debe_cambiar=1 WHERE id=?", (seg.hashear(temporal), cuenta["id"]))
    db.registrar(con, f"Contraseña restablecida desde la computadora para {cuenta['usuario']}", "recuperar_cuenta", "local")
    con.close()
    print(f"\n  Listo. Entrá al panel con:\n\n    Usuario:    {cuenta['usuario']}\n    Contraseña: {temporal}\n")
    print("  Al entrar, el panel te va a pedir que elijas una contraseña nueva.\n")


if __name__ == "__main__":
    main()
