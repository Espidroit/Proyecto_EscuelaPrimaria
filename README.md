# 🏝️ La Isla de los Cuentos

Juego educativo de **Lengua y Literatura para 1.º, 2.º y 3.º grado**, hecho con **Python (Flask) + SQLite**.
Los chicos leen cuentos, arman oraciones, buscan rimas y escriben palabras. Ganan estrellas, monedas, medallas y figuritas, y personalizan su avatar.
La docente tiene un **panel aparte, protegido con usuario y contraseña**, donde deja tareas y sigue la evolución de cada alumno.

---

## Cómo se abre

1. Instalar **Python 3.10 o más nuevo** desde <https://www.python.org/downloads/> (al instalar, marcar **"Add Python to PATH"**).
2. Doble clic en **`iniciar.bat`**.
   - La primera vez prepara todo solo (necesita internet ese minuto).
   - Se abre el navegador con el juego.
3. Para cerrar, cerrar la ventana negra.

| Quién | Dirección |
|---|---|
| Chicos | <http://localhost:5000/> |
| Docente | <http://localhost:5000/docente> |

**Varias computadoras en el aula:** abrir `iniciar_en_red.bat` en la computadora principal. La ventana muestra la dirección (por ejemplo `http://192.168.0.15:5000/`) que hay que escribir en las otras computadoras de la misma red Wi-Fi.

> En Linux o Mac: `python3 -m pip install -r requirements.txt` y después `python3 app.py`.

## Primer uso (docente)

1. Entrar a `/docente` **desde la computadora donde está instalado** y crear la cuenta (usuario y contraseña).
2. En **Alumnos → Agregar alumnos**, escribir un nombre por línea y elegir el grado.
3. Imprimir las **tarjetas de acceso**: cada chico entra tocando su nombre y sus **3 dibujos secretos**.

**Otro docente o compañero de proyecto:** en la pantalla de ingreso de `/docente` tocar **«Crear mi cuenta»** (solo funciona desde la computadora donde corre el juego). Todas las cuentas ven el mismo grupo. En **Ajustes → Docentes** se ven las cuentas, se pueden eliminar y se puede desactivar el registro cuando ya estén todos.

## Qué hay en el juego (chicos)

- **📚 Cuentos** (10 incluidos): lectura con voz, preguntas de personajes, lugar y tiempo, datos del texto, vocabulario, sentimientos, inferencias y orden de los hechos.
- **🧱 Ordeno oraciones**, **🎵 Busco la rima** y **🔤 Armo palabras**.
- **👏 Juego de sílabas**: armar la palabra tocando sus sílabas en orden (conciencia silábica).
- **📌 La palabra que falta**: completar oraciones con la palabra que tiene sentido y concuerda.
- **🔄 Parecidas y opuestas**: sinónimos y antónimos.
- **🖍️ ¿Con qué letra va?**: ortografía (b/v, c/s/z, ll/y, r/rr, g/j, h).
- **🏷️ ¿Quién, cómo es o qué hace?**: clases de palabras (sustantivo, adjetivo, verbo), pensado para 3.º grado.
- **📝 Mis tareas**: las tareas que deja la seño, con su consigna (se puede escuchar).
- **👤 Mi perfil**: avatar con 12 categorías para personalizar (peinado, ropa, gorros, anteojos, mascotas, fondos, marcos…). Algunas cosas se compran con monedas; otras se desbloquean subiendo de nivel o ganando medallas.
- Adaptación por grado: en 1.º grado hay menos opciones por pregunta, secuencias más cortas y, si se quiere, texto en IMPRENTA MAYÚSCULA.
- Niveles de actividades: 1.º grado ve el nivel 1, 2.º grado los niveles 1 y 2, y 3.º grado los tres niveles. En **Ajustes** se puede abrir un nivel más a 1.º o a 2.º grado.

## Panel docente

- **Panel general**: indicadores, evolución semanal del grupo, alumnos para acompañar, resultados por tema, mapa del grupo y actividad reciente.
- **Alumnos**: ficha de cada chico con evolución, resultados por tema, preguntas donde se equivoca, historial, tareas, **observaciones** (registro con fecha) y su clave de acceso.
- **Tareas**: crear tareas eligiendo actividades, destinatarios (todos, un grado o algunos chicos), fecha límite y premio. Ver quién terminó y con qué resultado.
- **Actividades**: ocultar o mostrar actividades y **crear propias** de cualquiera de los 9 tipos de juego).
- **Temas y contenidos**: qué aprendizaje trabaja cada tema; se pueden desactivar temas no enseñados todavía.
- **Ajustes**: preferencias del juego, cambio de contraseña, exportar resultados a Excel (CSV), copia de seguridad y registro de accesos.

## Seguridad

- Contraseña de la docente guardada con **hash PBKDF2-SHA256** (nunca en texto plano).
- Sesiones firmadas con una clave secreta aleatoria (`datos/clave_secreta.txt`), cookies `HttpOnly` y `SameSite=Strict`.
- La sesión docente **se cierra sola a los 30 minutos sin uso**, y también si un chico entra al juego en esa misma computadora.
- **Bloqueo temporal** después de varios intentos fallidos (docente y chicos).
- La API de la docente rechaza cualquier pedido sin sesión docente; los chicos no pueden ver datos de otros ni ponerse objetos que no tienen (lo valida el servidor).
- Protección contra pedidos de otros sitios (cabecera propia + `SameSite`), y cabeceras de seguridad (CSP, `X-Frame-Options`, etc.).
- La cuenta docente solo se puede crear desde la computadora donde corre el programa.
- **Registro de accesos** visible en Ajustes.

## Archivos

```
app.py           servidor y API (rutas de chicos y de docente)
database.py      base de datos SQLite (se crea sola en datos/isla.db)
seguridad.py     contraseñas, sesiones, límite de intentos, cabeceras
contenido.py     cuentos, juegos, temas, avatar, niveles y medallas
static/alumno/   interfaz de los chicos
static/docente/  panel docente
static/comun/    utilidades y dibujo del avatar (SVG)
datos/           base de datos y clave secreta (¡hacer copias de seguridad!)
```

Para agregar contenido fijo se puede editar `contenido.py`; para contenido propio de cada docente, usar **Actividades → Crear** desde el panel.
