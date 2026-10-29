"""
Contenido fijo del juego: temas, cuentos, juegos de palabras,
catálogo del avatar, niveles y medallas.

Para agregar contenido sin programar, la docente puede crear
actividades desde su panel (se guardan en la base de datos).
"""

# ---------------------------------------------------------------
# Temas que trabaja el juego (área de Lengua y Literatura)
# ---------------------------------------------------------------
TEMAS = {
    # --- Comprensión lectora ---
    "personajes": {"area": "Comprensión lectora", "n": "Personajes", "i": "👫", "kid": "¿Quién?",
                   "desc": "Reconocer quiénes participan en el cuento y quién es el protagonista.",
                   "obj": "Identificar personajes principales y secundarios del relato.",
                   "pista": "Pensá: ¿quién hace las cosas en el cuento? 🤔"},
    "lugar": {"area": "Comprensión lectora", "n": "Lugar y tiempo", "i": "🗺️", "kid": "¿Dónde? ¿Cuándo?",
              "desc": "Ubicar dónde y cuándo ocurre la historia.",
              "obj": "Reconocer el espacio y el tiempo en que transcurre la narración.",
              "pista": "Buscá en el cuento dónde o cuándo pasa. 🗺️"},
    "detalles": {"area": "Comprensión lectora", "n": "Datos del texto", "i": "🔍", "kid": "Lo que dice el cuento",
                 "desc": "Encontrar información escrita en el texto (colores, objetos, acciones).",
                 "obj": "Localizar información explícita (comprensión literal).",
                 "pista": "¡La respuesta está escrita en el cuento! Miralo otra vez. 🔍"},
    "secuencia": {"area": "Comprensión lectora", "n": "Orden de los hechos", "i": "🧩", "kid": "¿Qué pasó primero?",
                  "desc": "Ordenar lo que pasó: principio, desarrollo y final.",
                  "obj": "Reconstruir la secuencia narrativa (inicio, conflicto, desenlace).",
                  "pista": "¿Qué pasó primero? Pensá en el principio del cuento. 🧩"},
    "vocabulario": {"area": "Comprensión lectora", "n": "Palabras nuevas", "i": "📝", "kid": "¿Qué quiere decir?",
                    "desc": "Descubrir el significado de palabras nuevas usando el cuento.",
                    "obj": "Ampliar el vocabulario e inferir significados por contexto.",
                    "pista": "Leé otra vez la oración donde aparece esa palabra. 📝"},
    "emociones": {"area": "Comprensión lectora", "n": "Sentimientos", "i": "💖", "kid": "¿Cómo se siente?",
                  "desc": "Reconocer cómo se sienten los personajes y por qué.",
                  "obj": "Identificar estados de ánimo y emociones de los personajes.",
                  "pista": "¿Cómo te sentirías vos en su lugar? 💖"},
    "inferencia": {"area": "Comprensión lectora", "n": "Pensar más allá", "i": "💡", "kid": "¿Por qué?",
                   "desc": "Entender causas y consecuencias que no siempre están escritas.",
                   "obj": "Realizar inferencias simples y relaciones de causa-efecto.",
                   "pista": "Pensá por qué pasó eso. ¡Vos podés! 💡"},
    # --- Reflexión sobre el lenguaje / escritura ---
    "oraciones": {"area": "Lengua: oraciones y palabras", "n": "Armar oraciones", "i": "🧱", "kid": "Ordeno la oración",
                  "desc": "Ordenar palabras para formar oraciones con sentido.",
                  "obj": "Reconocer la oración como unidad con sentido y su orden habitual.",
                  "pista": "¿Con qué palabra empieza la oración? 🧱"},
    "rimas": {"area": "Lengua: oraciones y palabras", "n": "Rimas y sonidos", "i": "🎵", "kid": "Busco la rima",
              "desc": "Escuchar el final de las palabras y encontrar las que riman.",
              "obj": "Desarrollar la conciencia fonológica (sonidos finales de las palabras).",
              "pista": "Escuchá cómo termina la palabra. 🎵"},
    "escritura": {"area": "Lengua: oraciones y palabras", "n": "Escritura de palabras", "i": "🔤", "kid": "Armo la palabra",
                  "desc": "Formar palabras letra por letra.",
                  "obj": "Establecer correspondencias entre sonidos y letras (escritura alfabética).",
                  "pista": "Decí la palabra despacito: ¿qué sonido va ahora? 🔤"},
    "silabas": {"area": "Lengua: oraciones y palabras", "n": "Sílabas", "i": "👏", "kid": "Palmas y sílabas",
                "desc": "Separar palabras en sílabas y volver a armarlas.",
                "obj": "Segmentar palabras en sílabas y reconocer la sílaba como unidad (conciencia silábica).",
                "pista": "Decí la palabra aplaudiendo: cada palmada es una sílaba. 👏"},
    "completar": {"area": "Lengua: oraciones y palabras", "n": "Completar oraciones", "i": "📌", "kid": "La palabra que falta",
                  "desc": "Elegir la palabra que le da sentido a la oración.",
                  "obj": "Seleccionar la palabra adecuada según el sentido y la concordancia de la oración.",
                  "pista": "Leé la oración entera con cada palabra. ¿Con cuál tiene sentido? 🤔"},
    "familias": {"area": "Lengua: oraciones y palabras", "n": "Familias de palabras", "i": "🌳", "kid": "Palabras parientes",
                 "desc": "Reconocer palabras de la misma familia, diminutivos y aumentativos.",
                 "obj": "Formar familias de palabras y reconocer diminutivos (-ito, -ita) y aumentativos (-ote, -azo).",
                 "pista": "Buscá la palabra que tiene adentro a la palabra principal. 🌳"},
    # --- Ortografía y gramática ---
    "sinonimos": {"area": "Lengua: ortografía y gramática", "n": "Sinónimos y antónimos", "i": "🔄", "kid": "Parecidas y opuestas",
                  "desc": "Encontrar palabras que quieren decir lo mismo o lo contrario.",
                  "obj": "Reconocer relaciones de significado entre palabras: sinónimos y antónimos.",
                  "pista": "Pensá qué quiere decir esa palabra. ¿Cuál se parece? ¿Cuál es lo contrario? 🔄"},
    "ortografia": {"area": "Lengua: ortografía y gramática", "n": "Ortografía", "i": "🖍️", "kid": "¿Con qué letra va?",
                   "desc": "Completar palabras con la letra correcta (que/qui, gue/gui, mp/mb, r/rr, -aba, b/v, ll/y…) y usar mayúsculas.",
                   "obj": "Reconocer la escritura convencional de palabras de uso frecuente y el uso de mayúsculas.",
                   "pista": "Pensá cómo la viste escrita en los libros o en los carteles. 📚"},
    "acentuacion": {"area": "Lengua: ortografía y gramática", "n": "Sílaba tónica y tildes", "i": "📢", "kid": "¿Dónde suena más fuerte?",
                    "desc": "Reconocer la sílaba que suena más fuerte y las palabras que llevan tilde.",
                    "obj": "Identificar la sílaba tónica y escribir con tilde palabras de uso frecuente.",
                    "pista": "Decí la palabra como si llamaras a alguien de lejos: ¿qué parte suena más fuerte? 📢"},
    "clases": {"area": "Lengua: ortografía y gramática", "n": "Clases de palabras", "i": "🏷️", "kid": "¿Quién, cómo es o qué hace?",
               "desc": "Distinguir palabras que nombran, que dicen cómo es algo y que dicen una acción.",
               "obj": "Reconocer sustantivos, adjetivos y verbos por su función en la oración.",
               "pista": "¿Esa palabra nombra algo, dice cómo es o dice qué hace? 🏷️"},
}

TIPOS = {
    "cuento":    {"n": "Cuentos",          "i": "📚", "tema": None,        "desc": "Leer un cuento y responder preguntas."},
    "oraciones": {"n": "Ordeno oraciones", "i": "🧱", "tema": "oraciones", "desc": "Ordenar palabras para armar oraciones."},
    "rimas":     {"n": "Busco la rima",    "i": "🎵", "tema": "rimas",     "desc": "Encontrar palabras que riman."},
    "palabras":  {"n": "Armo palabras",    "i": "🔤", "tema": "escritura", "desc": "Formar palabras con letras."},
    "silabas":   {"n": "Juego de sílabas", "i": "👏", "tema": "silabas",   "desc": "Armar palabras con sílabas."},
    "completar": {"n": "La palabra que falta", "i": "📌", "tema": "completar", "desc": "Completar oraciones con la palabra que tiene sentido."},
    "opuestos":  {"n": "Parecidas y opuestas", "i": "🔄", "tema": "sinonimos", "desc": "Encontrar palabras parecidas (sinónimos) y contrarias (antónimos)."},
    "ortografia": {"n": "¿Con qué letra va?", "i": "🖍️", "tema": "ortografia", "desc": "Completar palabras con la letra correcta."},
    "clases":    {"n": "¿Quién, cómo es o qué hace?", "i": "🏷️", "tema": "clases", "desc": "Clasificar palabras: sustantivos, adjetivos y verbos."},
}

# Respuestas del juego «clases» (clases de palabras)
CLASES = {"s": "🧸 Nombra algo (sustantivo)", "a": "🎨 Dice cómo es (adjetivo)", "v": "🏃 Dice una acción (verbo)"}

# ---------------------------------------------------------------
# Cuentos
#   {t:"e", tema, p, o:[correcta, incorrecta1, incorrecta2]}
#   {t:"vf", tema, p, v:True/False}
#   {t:"o", tema:"secuencia", items:[en orden]}
# ---------------------------------------------------------------
def _c(id, titulo, e, sticker, nivel, texto, preguntas):
    return {"id": id, "tipo": "cuento", "titulo": titulo, "e": e, "sticker": sticker,
            "nivel": nivel, "texto": texto, "preguntas": preguntas, "base": True}

CUENTOS = [
    _c("bobi", "Bobi y la pelota", "🐶", "🐶", 1,
       "Bobi es un perro chiquito. Tiene el pelo marrón. Un día, Bobi encontró una pelota roja en el jardín. Corrió y corrió con la pelota. Después, se durmió muy contento.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién es el personaje principal?", "o": ["Bobi, el perro", "Un gato", "Una nena"]},
        {"t": "e", "tema": "detalles", "p": "¿De qué color era la pelota?", "o": ["Roja", "Azul", "Verde"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde encontró la pelota?", "o": ["En el jardín", "En la escuela", "En el mar"]},
        {"t": "vf", "tema": "detalles", "p": "Bobi es un perro muy grande.", "v": False},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sintió Bobi al final?", "o": ["Contento", "Triste", "Enojado"]},
        {"t": "o", "tema": "secuencia", "items": ["🔍 Bobi encontró una pelota.", "🏃 Corrió con la pelota.", "😴 Se durmió contento."]}]),
    _c("luli", "La luna Luli", "🌙", "🌙", 1,
       "Luli era una luna muy curiosa. Una noche quiso conocer el mar. Bajó despacito y tocó el agua con un rayito de luz. Los peces saltaron felices. —¡Gracias por visitarnos! —le dijeron.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién quería conocer el mar?", "o": ["Luli, la luna", "Un pez", "El sol"]},
        {"t": "e", "tema": "lugar", "p": "¿Cuándo pasó la historia?", "o": ["De noche", "De mañana", "Al mediodía"]},
        {"t": "e", "tema": "detalles", "p": "¿Con qué tocó el agua Luli?", "o": ["Con un rayito de luz", "Con una mano", "Con una piedra"]},
        {"t": "e", "tema": "vocabulario", "p": "Luli era «curiosa». ¿Qué quiere decir curiosa?", "o": ["Que quiere conocer cosas nuevas", "Que tiene mucho sueño", "Que es muy grande"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo estaban los peces?", "o": ["Felices", "Asustados", "Dormidos"]},
        {"t": "o", "tema": "secuencia", "items": ["🌙 Luli quiso conocer el mar.", "✨ Tocó el agua con un rayito de luz.", "🐟 Los peces saltaron felices."]}]),
    _c("tomi", "Tomi y la semilla", "🌱", "🌻", 1,
       "Tomi plantó una semilla en una maceta. Todos los días le puso agua y la dejó al sol. Pasaron muchos días. ¡Por fin nació una flor amarilla! Tomi saltó de alegría.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién plantó la semilla?", "o": ["Tomi", "La abuela", "Un pájaro"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde plantó la semilla?", "o": ["En una maceta", "En la plaza", "En la playa"]},
        {"t": "e", "tema": "detalles", "p": "¿De qué color era la flor?", "o": ["Amarilla", "Rosa", "Blanca"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué nació la flor?", "o": ["Porque Tomi la cuidó con agua y sol", "Porque llovieron caramelos", "Porque Tomi la pintó"]},
        {"t": "e", "tema": "emociones", "p": "Tomi saltó de alegría. ¿Cómo se sentía?", "o": ["Feliz", "Aburrido", "Con miedo"]},
        {"t": "o", "tema": "secuencia", "items": ["🌱 Tomi plantó una semilla.", "💧 Le puso agua todos los días.", "🌻 Nació una flor amarilla."]}]),
    _c("caco", "El caracol apurado", "🐌", "🐌", 1,
       "Caco era un caracol que siempre estaba apurado. Quería llegar rápido a la fiesta del bosque. Pero los caracoles caminan muy lento. Su amiga la mariposa lo llevó volando. ¡Llegaron justo a tiempo para bailar!",
       [{"t": "e", "tema": "personajes", "p": "¿Quién ayudó a Caco?", "o": ["La mariposa", "El perro", "La lluvia"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde era la fiesta?", "o": ["En el bosque", "En la escuela", "En el río"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué Caco necesitaba ayuda?", "o": ["Porque los caracoles caminan lento", "Porque no quería ir", "Porque estaba dormido"]},
        {"t": "e", "tema": "vocabulario", "p": "Caco estaba «apurado». ¿Qué quiere decir?", "o": ["Que quiere hacer todo rápido", "Que está mojado", "Que tiene hambre"]},
        {"t": "vf", "tema": "detalles", "p": "La mariposa llevó a Caco volando.", "v": True},
        {"t": "o", "tema": "secuencia", "items": ["🐌 Caco quería ir a la fiesta.", "🦋 La mariposa lo llevó volando.", "💃 Llegaron a tiempo para bailar."]}]),
    _c("lola", "Lola y el globo", "🎈", "🎈", 1,
       "Lola tenía un globo azul. Fue a la plaza con su papá. De pronto sopló un viento fuerte y el globo se escapó. Lola lloró un poquito. Su papá le compró otro globo y Lola sonrió.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién tenía un globo?", "o": ["Lola", "Un nene", "La abuela"]},
        {"t": "e", "tema": "lugar", "p": "¿A dónde fueron Lola y su papá?", "o": ["A la plaza", "A la escuela", "A la playa"]},
        {"t": "e", "tema": "detalles", "p": "¿De qué color era el globo?", "o": ["Azul", "Rojo", "Verde"]},
        {"t": "e", "tema": "vocabulario", "p": "El globo «se escapó». ¿Qué quiere decir?", "o": ["Que se fue volando lejos", "Que se rompió", "Que se hizo más grande"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sintió Lola cuando el globo se escapó?", "o": ["Triste", "Contenta", "Con sueño"]},
        {"t": "vf", "tema": "detalles", "p": "El papá le compró otro globo.", "v": True},
        {"t": "o", "tema": "secuencia", "items": ["🎈 Lola fue a la plaza con su globo.", "💨 El viento se llevó el globo.", "😊 Su papá le compró otro."]}]),
    _c("pipo", "El pato Pipo", "🦆", "🦆", 1,
       "Pipo era un pato que no sabía nadar. Sus hermanos nadaban en la laguna. Pipo los miraba desde la orilla. Un día, mamá pata le enseñó despacito. ¡Pipo movió las patas y nadó! Estaba muy orgulloso.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién no sabía nadar?", "o": ["Pipo", "Mamá pata", "Un pez"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde nadaban los hermanos de Pipo?", "o": ["En la laguna", "En una pileta", "En el mar"]},
        {"t": "e", "tema": "vocabulario", "p": "Pipo miraba desde la «orilla». ¿Qué es la orilla?", "o": ["El borde del agua", "El fondo de la laguna", "Un nido de pato"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué al final Pipo pudo nadar?", "o": ["Porque mamá pata le enseñó", "Porque se puso un salvavidas", "Porque llovió mucho"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sentía Pipo al final?", "o": ["Orgulloso y feliz", "Triste", "Enojado"]},
        {"t": "o", "tema": "secuencia", "items": ["👀 Pipo miraba desde la orilla.", "🦆 Mamá pata le enseñó.", "🏊 ¡Pipo nadó!"]}]),
    _c("tita", "Tita va a la escuela", "🐢", "🐢", 2,
       "Tita era una tortuga que iba a empezar primer grado. Esa mañana se puso su mochila verde y salió de su casa. En el camino se encontró con Ramón, un conejo que también iba a la escuela. Tita estaba nerviosa porque no conocía a nadie. Ramón le dijo: —No te preocupes, yo me siento con vos. Cuando llegaron, la seño les leyó un cuento muy lindo. Al final del día, Tita ya tenía un amigo nuevo.",
       [{"t": "e", "tema": "personajes", "p": "¿Quiénes son los personajes del cuento?", "o": ["Tita, Ramón y la seño", "Tita y un perro", "Solamente Ramón"]},
        {"t": "e", "tema": "lugar", "p": "¿A dónde iba Tita?", "o": ["A la escuela", "A la plaza", "Al médico"]},
        {"t": "e", "tema": "detalles", "p": "¿De qué color era la mochila de Tita?", "o": ["Verde", "Roja", "Azul"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sentía Tita al principio?", "o": ["Nerviosa", "Enojada", "Aburrida"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué Tita estaba nerviosa?", "o": ["Porque no conocía a nadie", "Porque perdió la mochila", "Porque llovía mucho"]},
        {"t": "e", "tema": "vocabulario", "p": "En el cuento aparece «la seño». ¿Quién es?", "o": ["La maestra", "La mamá", "Una compañera"]},
        {"t": "o", "tema": "secuencia", "items": ["🎒 Tita salió de su casa.", "🐰 Se encontró con Ramón.", "📖 La seño leyó un cuento.", "🤝 Tita tenía un amigo nuevo."]}]),
    _c("fuego", "El dragón que tenía frío", "🐉", "🐉", 2,
       "En una montaña con nieve vivía Fuego, un dragón muy simpático. Pero Fuego tenía un problema: ¡no podía echar fuego por la boca! Por eso siempre tenía frío. Un día, la abuela oveja le tejió una bufanda larga y colorida. Fuego se la puso y se sintió calentito. Desde ese día, Fuego y la abuela oveja toman chocolate juntos todas las tardes.",
       [{"t": "e", "tema": "personajes", "p": "¿Quiénes son los personajes del cuento?", "o": ["Fuego y la abuela oveja", "Un pirata y un loro", "Fuego y un león"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde vivía Fuego?", "o": ["En una montaña con nieve", "En el desierto", "En la ciudad"]},
        {"t": "vf", "tema": "detalles", "p": "Fuego echaba mucho fuego por la boca.", "v": False},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué Fuego tenía frío?", "o": ["Porque no podía echar fuego", "Porque estaba enojado", "Porque no tenía casa"]},
        {"t": "e", "tema": "vocabulario", "p": "La abuela «tejió» una bufanda. ¿Qué quiere decir tejió?", "o": ["La hizo con lana y agujas", "La compró en el kiosco", "La rompió"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sintió Fuego con la bufanda?", "o": ["Calentito y contento", "Triste", "Con miedo"]},
        {"t": "o", "tema": "secuencia", "items": ["🥶 Fuego siempre tenía frío.", "🧶 La abuela oveja le tejió una bufanda.", "🧣 Fuego se puso la bufanda.", "☕ Toman chocolate juntos."]}]),
    _c("pepa", "Pepa y el paraguas mágico", "☂️", "☂️", 2,
       "Pepa encontró un paraguas viejo en el altillo de su abuelo. Era amarillo con lunares azules. Cuando lo abrió, empezó a soplar un viento fuerte y Pepa salió volando por la ventana. Desde arriba vio su barrio, la plaza y la escuela. ¡Qué chiquito se veía todo! Después de un rato, el paraguas la bajó despacito en su jardín. Pepa decidió que mañana volvería a volar.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién es la protagonista del cuento?", "o": ["Pepa", "El abuelo", "La maestra"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde encontró Pepa el paraguas?", "o": ["En el altillo de su abuelo", "En la escuela", "En la plaza"]},
        {"t": "e", "tema": "detalles", "p": "¿Cómo era el paraguas?", "o": ["Amarillo con lunares azules", "Rojo con rayas", "Negro y grande"]},
        {"t": "e", "tema": "vocabulario", "p": "¿Qué es un «altillo»?", "o": ["Un lugar arriba de la casa para guardar cosas", "Una comida", "Un animal"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué decimos que el paraguas era mágico?", "o": ["Porque la hizo volar", "Porque era nuevo", "Porque era de su abuelo"]},
        {"t": "e", "tema": "emociones", "p": "¿Qué creés que sintió Pepa mientras volaba?", "o": ["Sorpresa y alegría", "Aburrimiento", "Mucho sueño"]},
        {"t": "o", "tema": "secuencia", "items": ["🔍 Pepa encontró un paraguas.", "🌬️ Salió volando por la ventana.", "🏘️ Vio su barrio desde arriba.", "🏡 Bajó despacito en su jardín."]}]),
    _c("jacinta", "El cumpleaños de Jacinta", "🦒", "🎂", 2,
       "Hoy es el cumpleaños de Jacinta, la jirafa. Sus amigos le prepararon una sorpresa. El mono trajo bananas, el elefante infló globos con su trompa y la cebra hizo una torta de frutillas. Pero había un problema: ¡la mesa era muy bajita para Jacinta! Entonces, todos subieron la torta a la rama de un árbol. Jacinta sopló las velas y pidió un deseo.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién cumplía años?", "o": ["Jacinta, la jirafa", "El mono", "La cebra"]},
        {"t": "e", "tema": "detalles", "p": "¿Qué hizo el elefante?", "o": ["Infló globos con su trompa", "Trajo bananas", "Hizo la torta"]},
        {"t": "vf", "tema": "detalles", "p": "La torta era de chocolate.", "v": False},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué la mesa era un problema?", "o": ["Porque Jacinta es muy alta", "Porque estaba rota", "Porque era de color azul"]},
        {"t": "e", "tema": "vocabulario", "p": "Le prepararon una «sorpresa». ¿Qué es una sorpresa?", "o": ["Algo lindo que no esperás", "Una fruta", "Un juego de pelota"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se habrá sentido Jacinta con la fiesta?", "o": ["Feliz y querida", "Enojada", "Aburrida"]},
        {"t": "o", "tema": "secuencia", "items": ["🎁 Le prepararon una sorpresa.", "😮 La mesa era muy bajita.", "🌳 Subieron la torta a un árbol.", "🎂 Jacinta sopló las velas."]}]),
    _c("nico", "Nico y el ruido de la noche", "🔦", "🔦", 2,
       "Una noche, Nico escuchó un ruido raro: ¡toc, toc, toc! Tenía mucho miedo y se tapó con la frazada. Pensó que era un monstruo. Juntó coraje, prendió la linterna y miró por la ventana. ¡Era una rama del árbol que golpeaba el vidrio con el viento! Nico se rió, apagó la linterna y se durmió tranquilo.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién es el personaje del cuento?", "o": ["Nico", "Un monstruo", "Su mamá"]},
        {"t": "e", "tema": "lugar", "p": "¿Cuándo pasa la historia?", "o": ["De noche", "En el recreo", "A la mañana"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sintió Nico al escuchar el ruido?", "o": ["Con miedo", "Feliz", "Con hambre"]},
        {"t": "e", "tema": "detalles", "p": "¿Qué usó Nico para mirar?", "o": ["Una linterna", "Una lupa", "Un celular"]},
        {"t": "e", "tema": "inferencia", "p": "¿Qué hacía el ruido en realidad?", "o": ["Una rama que golpeaba la ventana", "Un monstruo", "Un perro que ladraba"]},
        {"t": "e", "tema": "vocabulario", "p": "Nico «juntó coraje». ¿Qué quiere decir?", "o": ["Que se animó a pesar del miedo", "Que se fue a dormir", "Que juntó juguetes"]},
        {"t": "o", "tema": "secuencia", "items": ["👂 Nico escuchó un ruido raro.", "🛏️ Se tapó con la frazada.", "🔦 Prendió la linterna y miró.", "😴 Se durmió tranquilo."]}]),
    _c("faro", "El faro de Martina", "🌊", "💡", 3,
       "Martina vivía con su abuelo cerca del mar, en una casita junto al faro. Todas las noches, el abuelo subía la escalera caracol y encendía la gran luz para guiar a los barcos. Una tarde de invierno, el abuelo se torció un tobillo y no podía caminar. Esa noche se largó una tormenta muy fuerte. Martina escuchó a lo lejos la bocina de un barco pesquero. Aunque tenía un poco de miedo, tomó la linterna y subió los ciento veinte escalones. Con las manos temblorosas, giró la llave tal como le había enseñado su abuelo. ¡La luz del faro se encendió! El barco esquivó las rocas y llegó sano y salvo al puerto. A la mañana siguiente, los pescadores le trajeron a Martina una caja llena de caracoles de regalo.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién encendió el faro la noche de la tormenta?", "o": ["Martina", "El abuelo", "Un pescador"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde vivía Martina?", "o": ["Cerca del mar, junto al faro", "En una ciudad muy grande", "En el campo, lejos del mar"]},
        {"t": "e", "tema": "lugar", "p": "¿En qué época del año pasó la historia?", "o": ["En invierno", "En verano", "En primavera"]},
        {"t": "vf", "tema": "detalles", "p": "El abuelo no pudo subir porque se había torcido un tobillo.", "v": True},
        {"t": "e", "tema": "vocabulario", "p": "El barco llegó «sano y salvo». ¿Qué quiere decir?", "o": ["Que llegó sin que le pasara nada malo", "Que llegó muy rápido", "Que llegó lleno de peces"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sentía Martina cuando subió la escalera?", "o": ["Con un poco de miedo, pero se animó", "Aburrida", "Enojada con su abuelo"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué era importante encender el faro esa noche?", "o": ["Para que el barco no chocara contra las rocas", "Para que el abuelo pudiera leer", "Para secar la ropa"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué los pescadores le hicieron un regalo a Martina?", "o": ["Para agradecerle que los ayudó", "Porque era su cumpleaños", "Porque vendían caracoles"]},
        {"t": "o", "tema": "secuencia", "items": ["🦶 El abuelo se torció un tobillo.", "⛈️ Empezó una tormenta muy fuerte.", "🔦 Martina subió la escalera del faro.", "💡 La luz del faro se encendió.", "🎁 Los pescadores le trajeron un regalo."]}]),
    _c("cuaderno", "El cuaderno escondido", "📓", "📓", 3,
       "En la escuela de Joaquín había una biblioteca pequeña, con estantes de madera que crujían. Un martes, mientras buscaba un libro de dinosaurios, Joaquín encontró un cuaderno viejo escondido detrás de una enciclopedia. Tenía la tapa gastada y adentro había dibujos de plantas, mapas del barrio y una firma: «Elsa, 1975». Joaquín se lo mostró a la bibliotecaria, que se quedó sorprendida. —Elsa fue alumna de esta escuela y hoy es la abuela de tu compañera Sofía —le contó. Al día siguiente, Sofía llevó a su abuela al aula. Elsa reconoció su cuaderno enseguida y se emocionó tanto que se le llenaron los ojos de lágrimas. Les contó que de chica le encantaba observar la naturaleza y anotar todo lo que veía. Desde ese día, el grado tiene su propio cuaderno de observaciones, y cada semana un alumno distinto se lo lleva a su casa.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién encontró el cuaderno?", "o": ["Joaquín", "Sofía", "La bibliotecaria"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde estaba escondido el cuaderno?", "o": ["Detrás de una enciclopedia", "Debajo de un banco del patio", "En la mochila de Sofía"]},
        {"t": "e", "tema": "lugar", "p": "¿Qué día lo encontró?", "o": ["Un martes", "Un sábado", "Un domingo"]},
        {"t": "e", "tema": "detalles", "p": "¿Qué había adentro del cuaderno?", "o": ["Dibujos de plantas y mapas del barrio", "Fotos de dinosaurios", "Recetas de cocina"]},
        {"t": "vf", "tema": "detalles", "p": "Elsa era la maestra de Joaquín.", "v": False},
        {"t": "e", "tema": "vocabulario", "p": "Los estantes «crujían». ¿Qué quiere decir?", "o": ["Que hacían ruido al moverse", "Que estaban recién pintados", "Que eran muy altos"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sintió Elsa al ver su cuaderno?", "o": ["Muy emocionada", "Enojada", "Aburrida"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué el cuaderno era tan importante para Elsa?", "o": ["Porque lo había hecho cuando era chica", "Porque costaba mucha plata", "Porque era de su maestra"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué el grado empezó su propio cuaderno?", "o": ["Porque Elsa los entusiasmó a observar y anotar", "Porque la seño los retó", "Porque se perdió el cuaderno de Elsa"]},
        {"t": "o", "tema": "secuencia", "items": ["🔍 Joaquín buscaba un libro de dinosaurios.", "📓 Encontró un cuaderno viejo.", "👩‍🏫 Se lo mostró a la bibliotecaria.", "👵 Elsa reconoció su cuaderno.", "✏️ El grado empezó su propio cuaderno."]}]),
    _c("galleta", "Ramiro y el perro perdido", "🐕", "🐕", 3,
       "Un sábado a la tarde, Ramiro volvía de la panadería cuando vio un perro blanco con una mancha negra en el ojo. Estaba solo, mojado y temblaba de frío debajo de un árbol de la vereda. Tenía un collar rojo, pero sin chapita con el nombre. Ramiro lo envolvió con su campera y lo llevó a su casa. Su mamá le preparó una manta y un plato con agua. —Seguro que alguien lo está buscando —dijo Ramiro, preocupado. Entonces tuvo una idea: hizo carteles con un dibujo del perro y el teléfono de su mamá, y los pegó en los negocios del barrio. Esa misma noche sonó el teléfono. Era Clara, una nena de la otra cuadra, que lloraba de alegría. Cuando llegó a buscarlo, el perro movió la cola sin parar. Se llamaba Galleta. Desde entonces, Clara y Ramiro pasean juntos a Galleta todos los domingos.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién era la dueña del perro?", "o": ["Clara", "La mamá de Ramiro", "La panadera"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde encontró Ramiro al perro?", "o": ["Debajo de un árbol de la vereda", "Adentro de la panadería", "En la plaza"]},
        {"t": "e", "tema": "lugar", "p": "¿Cuándo lo encontró?", "o": ["Un sábado a la tarde", "Un lunes a la mañana", "Un domingo a la noche"]},
        {"t": "e", "tema": "detalles", "p": "¿Cómo era el perro?", "o": ["Blanco, con una mancha negra en el ojo", "Marrón, con manchas blancas", "Todo negro"]},
        {"t": "vf", "tema": "detalles", "p": "El perro tenía una chapita con su nombre.", "v": False},
        {"t": "e", "tema": "vocabulario", "p": "El perro «temblaba». ¿Qué quiere decir?", "o": ["Que se sacudía sin querer por el frío", "Que corría muy rápido", "Que ladraba fuerte"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo se sentía Ramiro cuando dijo «Seguro que alguien lo está buscando»?", "o": ["Preocupado", "Contento", "Enojado"]},
        {"t": "e", "tema": "inferencia", "p": "¿Para qué hizo carteles Ramiro?", "o": ["Para que los dueños del perro se enteraran", "Para vender el perro", "Para adornar el barrio"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué el perro movió la cola sin parar?", "o": ["Porque estaba feliz de ver a su dueña", "Porque tenía frío", "Porque quería comer"]},
        {"t": "o", "tema": "secuencia", "items": ["🐕 Ramiro vio un perro mojado.", "🧥 Lo llevó a su casa con su campera.", "📋 Pegó carteles en el barrio.", "📞 Llamó Clara por teléfono.", "🦮 Ahora pasean juntos a Galleta."]}]),
    _c("plumita", "El viaje de Plumita", "🌬️", "🌼", 3,
       "En un campo lleno de flores vivía Plumita, una semilla de diente de león. Era tan liviana que parecía un paraguas diminuto. Todas sus hermanas ya habían salido volando, pero Plumita tenía miedo de soltarse. —¿Y si me pierdo? —le preguntó a la abeja Rufina. —Las semillas no se pierden: viajan para encontrar su lugar —le respondió la abeja. Al otro día sopló un viento tibio de primavera. Plumita respiró hondo y se soltó. Pasó sobre un arroyo, esquivó un nido de horneros y saludó a unos chicos que jugaban a la pelota. Al atardecer, el viento se calmó y Plumita cayó suavemente en un rincón de tierra húmeda, cerca de una escuela. Con la lluvia y el sol, echó raíces. Meses después, una flor amarilla asomó junto a la puerta del aula, y los chicos la cuidaron todos los días.",
       [{"t": "e", "tema": "personajes", "p": "¿Quién le dio un consejo a Plumita?", "o": ["La abeja Rufina", "Un hornero", "Los chicos de la escuela"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde vivía Plumita al principio?", "o": ["En un campo lleno de flores", "En el patio de una escuela", "Al lado de un arroyo"]},
        {"t": "e", "tema": "lugar", "p": "¿En qué estación del año se soltó?", "o": ["En primavera", "En invierno", "En otoño"]},
        {"t": "e", "tema": "detalles", "p": "¿A qué se parecía Plumita?", "o": ["A un paraguas diminuto", "A una piedra", "A una mariposa"]},
        {"t": "vf", "tema": "detalles", "p": "Plumita cayó cerca de una escuela.", "v": True},
        {"t": "e", "tema": "vocabulario", "p": "Plumita parecía un paraguas «diminuto». ¿Qué quiere decir?", "o": ["Muy, muy chiquito", "Muy pesado", "De muchos colores"]},
        {"t": "e", "tema": "emociones", "p": "¿Qué sentía Plumita antes de soltarse?", "o": ["Miedo de perderse", "Mucho sueño", "Enojo con sus hermanas"]},
        {"t": "e", "tema": "inferencia", "p": "¿Qué quiso decir la abeja con «viajan para encontrar su lugar»?", "o": ["Que las semillas vuelan para crecer en otro lugar", "Que las semillas se van de vacaciones", "Que las semillas buscan a su mamá"]},
        {"t": "o", "tema": "secuencia", "items": ["😟 Plumita tenía miedo de soltarse.", "🐝 La abeja le dio un consejo.", "🌬️ Se soltó con el viento.", "🌱 Cayó en la tierra y echó raíces.", "🌼 Nació una flor junto al aula."]}]),
]

# ---------------------------------------------------------------
# Juegos de palabras
# ---------------------------------------------------------------
def _j(id, tipo, titulo, e, sticker, nivel, items):
    return {"id": id, "tipo": tipo, "titulo": titulo, "e": e, "sticker": sticker,
            "nivel": nivel, "items": items, "base": True}

JUEGOS = [
    _j("or-dia", "oraciones", "Oraciones de todos los días", "🏠", "🏠", 1, [
        {"e": "🐱", "t": "El gato duerme en la cama"}, {"e": "☀️", "t": "El sol brilla en el cielo"},
        {"e": "👧", "t": "Ana lee un libro"}, {"e": "🍞", "t": "Mamá compra pan"},
        {"e": "🐶", "t": "El perro corre rápido"}, {"e": "🚲", "t": "Tomi anda en bici"}]),
    _j("or-ani", "oraciones", "Animales en acción", "🐸", "🐸", 1, [
        {"e": "🐟", "t": "Los peces nadan en el agua"}, {"e": "🐄", "t": "La vaca come pasto"},
        {"e": "🐦", "t": "El pájaro canta en el árbol"}, {"e": "🐸", "t": "La rana salta alto"},
        {"e": "🐻", "t": "El oso come miel"}, {"e": "🦆", "t": "El pato nada en la laguna"}]),
    _j("or-esc", "oraciones", "Un día en la escuela", "🎒", "🎒", 2, [
        {"e": "👩‍🏫", "t": "La seño escribe en el pizarrón"}, {"e": "⚽", "t": "Los chicos juegan en el recreo"},
        {"e": "🎒", "t": "Mi mochila tiene muchos útiles"}, {"e": "📖", "t": "Leo un cuento con mi amiga"},
        {"e": "🎨", "t": "Pinto un dibujo de muchos colores"}, {"e": "🥪", "t": "Comemos la merienda todos juntos"}]),
    _j("ri-1", "rimas", "Rimas fáciles", "🐱", "🦆", 1, [
        {"p": "gato", "e": "🐱", "c": {"t": "pato", "e": "🦆"}, "x": [{"t": "mesa", "e": "🍽️"}, {"t": "sol", "e": "☀️"}]},
        {"p": "luna", "e": "🌙", "c": {"t": "cuna", "e": "🛏️"}, "x": [{"t": "flor", "e": "🌸"}, {"t": "pan", "e": "🍞"}]},
        {"p": "pelota", "e": "⚽", "c": {"t": "bota", "e": "👢"}, "x": [{"t": "casa", "e": "🏠"}, {"t": "pez", "e": "🐟"}]},
        {"p": "ratón", "e": "🐭", "c": {"t": "camión", "e": "🚚"}, "x": [{"t": "árbol", "e": "🌳"}, {"t": "mano", "e": "✋"}]},
        {"p": "cama", "e": "🛏️", "c": {"t": "rama", "e": "🌿"}, "x": [{"t": "perro", "e": "🐶"}, {"t": "libro", "e": "📚"}]},
        {"p": "mano", "e": "✋", "c": {"t": "gusano", "e": "🐛"}, "x": [{"t": "pie", "e": "🦶"}, {"t": "ojo", "e": "👁️"}]}]),
    _j("ri-2", "rimas", "Rimas divertidas", "🎵", "🎵", 2, [
        {"p": "sol", "e": "☀️", "c": {"t": "farol", "e": "🏮"}, "x": [{"t": "gato", "e": "🐱"}, {"t": "luna", "e": "🌙"}]},
        {"p": "avión", "e": "✈️", "c": {"t": "botón", "e": "🔘"}, "x": [{"t": "barco", "e": "⛵"}, {"t": "nube", "e": "☁️"}]},
        {"p": "casa", "e": "🏠", "c": {"t": "taza", "e": "☕"}, "x": [{"t": "perro", "e": "🐶"}, {"t": "flor", "e": "🌸"}]},
        {"p": "ballena", "e": "🐋", "c": {"t": "sirena", "e": "🧜"}, "x": [{"t": "sapo", "e": "🐸"}, {"t": "tren", "e": "🚂"}]},
        {"p": "estrella", "e": "⭐", "c": {"t": "botella", "e": "🍾"}, "x": [{"t": "lápiz", "e": "✏️"}, {"t": "uva", "e": "🍇"}]},
        {"p": "queso", "e": "🧀", "c": {"t": "beso", "e": "💋"}, "x": [{"t": "pan", "e": "🍞"}, {"t": "silla", "e": "🪑"}]}]),
    _j("pa-1", "palabras", "Palabras cortas", "☀️", "☀️", 1, [
        {"e": "☀️", "p": "sol"}, {"e": "🍞", "p": "pan"}, {"e": "🐟", "p": "pez"},
        {"e": "🐻", "p": "oso"}, {"e": "🌙", "p": "luna"}, {"e": "🐱", "p": "gato"}]),
    _j("pa-2", "palabras", "Palabras más largas", "🦋", "🦋", 2, [
        {"e": "🐶", "p": "perro"}, {"e": "📚", "p": "libro"}, {"e": "🎈", "p": "globo"},
        {"e": "🍎", "p": "manzana"}, {"e": "🦋", "p": "mariposa"}, {"e": "🐢", "p": "tortuga"}]),
    _j("or-3", "oraciones", "Oraciones más largas", "🚂", "🚂", 3, [
        {"e": "🚂", "t": "El tren de carga cruza el puente de madera"}, {"e": "🌧️", "t": "Ayer llovió toda la tarde en el pueblo"},
        {"e": "🐝", "t": "Las abejas juntan el polen de las flores"}, {"e": "🎪", "t": "El sábado fuimos al circo con mis primos"},
        {"e": "📮", "t": "Mi abuela me mandó una carta muy larga"}, {"e": "🏔️", "t": "En la montaña hace mucho frío en invierno"}]),
    # Sílabas: la palabra va separada con guiones
    _j("si-1", "silabas", "Palmas con sílabas", "👏", "👏", 1, [
        {"e": "🦆", "p": "pa-to"}, {"e": "🌙", "p": "lu-na"}, {"e": "🐱", "p": "ga-to"},
        {"e": "🍲", "p": "so-pa"}, {"e": "✋", "p": "ma-no"}, {"e": "⚽", "p": "pe-lo-ta"}]),
    _j("si-2", "silabas", "Palabras con muchas sílabas", "🐌", "🐌", 2, [
        {"e": "🦋", "p": "ma-ri-po-sa"}, {"e": "🍅", "p": "to-ma-te"}, {"e": "🐌", "p": "ca-ra-col"},
        {"e": "🦒", "p": "ji-ra-fa"}, {"e": "🍦", "p": "he-la-do"}, {"e": "🚲", "p": "bi-ci-cle-ta"}]),
    # La palabra que falta: «_» marca el hueco y la primera opción es la correcta
    _j("co-1", "completar", "¿Qué palabra falta?", "📌", "🐦", 1, [
        {"e": "🐱", "t": "El gato toma _", "o": ["leche", "zapato", "silla"]},
        {"e": "🐦", "t": "El pájaro _ en el árbol", "o": ["canta", "mesa", "azul"]},
        {"e": "🌙", "t": "De noche sale la _", "o": ["luna", "pelota", "sopa"]},
        {"e": "🍎", "t": "La manzana es _", "o": ["roja", "corre", "mesa"]},
        {"e": "🐟", "t": "Los peces viven en el _", "o": ["agua", "cielo", "horno"]},
        {"e": "🎂", "t": "Hoy es mi _ y soplo las velitas", "o": ["cumpleaños", "zapato", "lápiz"]}]),
    _j("co-2", "completar", "Oraciones con sentido", "🧠", "🌻", 2, [
        {"e": "🐶", "t": "Los perros _ en el patio", "o": ["juegan", "juega", "jugamos"]},
        {"e": "🧥", "t": "Ana se puso una campera _", "o": ["roja", "rojos", "rojas"]},
        {"e": "☔", "t": "Llevé el paraguas porque _", "o": ["llovía", "tenía hambre", "me gusta el pan"]},
        {"e": "🧊", "t": "El hielo es muy _", "o": ["frío", "caliente", "alto"]},
        {"e": "🌻", "t": "Las plantas necesitan agua y _", "o": ["sol", "zapatos", "tijeras"]},
        {"e": "📚", "t": "Mañana _ a la biblioteca", "o": ["vamos", "fuimos", "íbamos"]}]),
    # Parecidas y opuestas: r = "opuesto" o "parecido"; la primera opción es la correcta
    _j("op-1", "opuestos", "Palabras opuestas", "🔄", "☯️", 2, [
        {"e": "🐘", "p": "grande", "r": "opuesto", "o": ["chico", "pesado", "gris"]},
        {"e": "☀️", "p": "día", "r": "opuesto", "o": ["noche", "sol", "mañana"]},
        {"e": "🧊", "p": "frío", "r": "opuesto", "o": ["caliente", "hielo", "blanco"]},
        {"e": "🦒", "p": "alto", "r": "opuesto", "o": ["bajo", "largo", "flaco"]},
        {"e": "🚪", "p": "abierto", "r": "opuesto", "o": ["cerrado", "puerta", "grande"]},
        {"e": "😀", "p": "feliz", "r": "opuesto", "o": ["triste", "contento", "bueno"]}]),
    _j("op-2", "opuestos", "Parecidas y opuestas", "🪞", "🪞", 3, [
        {"e": "😊", "p": "contento", "r": "parecido", "o": ["alegre", "triste", "cansado"]},
        {"e": "🐇", "p": "rápido", "r": "opuesto", "o": ["lento", "veloz", "corto"]},
        {"e": "🌸", "p": "lindo", "r": "parecido", "o": ["bonito", "feo", "chico"]},
        {"e": "🏁", "p": "empezar", "r": "opuesto", "o": ["terminar", "comenzar", "correr"]},
        {"e": "🗣️", "p": "hablar", "r": "parecido", "o": ["conversar", "callar", "mirar"]},
        {"e": "🍯", "p": "lleno", "r": "opuesto", "o": ["vacío", "completo", "pesado"]}]),
    # Ortografía: «_» marca la letra que falta y la primera opción es la correcta
    _j("ot-1", "ortografia", "Letras que suenan igual", "🖍️", "🖍️", 2, [
        {"e": "🐄", "p": "_aca", "o": ["v", "b"]}, {"e": "⛵", "p": "_arco", "o": ["b", "v"]},
        {"e": "🏠", "p": "ca_a", "o": ["s", "z"]}, {"e": "👞", "p": "_apato", "o": ["z", "s"]},
        {"e": "🐶", "p": "pe_o", "o": ["rr", "r"]}, {"e": "🔑", "p": "_ave", "o": ["ll", "y"]},
        {"e": "🦒", "p": "_irafa", "o": ["j", "g"]}, {"e": "🧊", "p": "_ielo", "o": ["h", "y"]}]),
    _j("ot-2", "ortografia", "Palabras difíciles", "📝", "🦉", 3, [
        {"e": "🐴", "p": "ca_allo", "o": ["b", "v"]}, {"e": "☁️", "p": "nu_e", "o": ["b", "v"]},
        {"e": "🥛", "p": "_aso", "o": ["v", "b"]}, {"e": "☕", "p": "ta_a", "o": ["z", "s"]},
        {"e": "⭐", "p": "estre_a", "o": ["ll", "y"]}, {"e": "🤡", "p": "pa_aso", "o": ["y", "ll"]},
        {"e": "🌻", "p": "_irasol", "o": ["g", "j"]}, {"e": "✏️", "p": "lápi_", "o": ["z", "s"]}]),
    # Clases de palabras: c = "s" (sustantivo), "a" (adjetivo) o "v" (verbo); t = oración de ejemplo (opcional)
    _j("cl-1", "clases", "Palabras en oraciones", "🏷️", "🏷️", 3, [
        {"e": "🐶", "p": "perro", "c": "s", "t": "El perro ladra fuerte"},
        {"e": "🐸", "p": "salta", "c": "v", "t": "La rana salta muy alto"},
        {"e": "🌹", "p": "roja", "c": "a", "t": "Tengo una rosa roja"},
        {"e": "🏫", "p": "escuela", "c": "s", "t": "Voy a la escuela todos los días"},
        {"e": "😴", "p": "duerme", "c": "v", "t": "El bebé duerme en la cuna"},
        {"e": "🐘", "p": "enorme", "c": "a", "t": "El elefante es enorme"},
        {"e": "🍰", "p": "torta", "c": "s", "t": "Mamá hizo una torta de chocolate"},
        {"e": "✍️", "p": "escribe", "c": "v", "t": "Sofía escribe una carta"},
        {"e": "🧸", "p": "suave", "c": "a", "t": "Mi oso de peluche es suave"}]),
    _j("cl-2", "clases", "Clasifico palabras", "🗂️", "🗂️", 3, [
        {"e": "🍎", "p": "manzana", "c": "s"}, {"e": "🏃", "p": "correr", "c": "v"},
        {"e": "😊", "p": "alegre", "c": "a"}, {"e": "⚽", "p": "pelota", "c": "s"},
        {"e": "🎨", "p": "pintar", "c": "v"}, {"e": "🐢", "p": "lenta", "c": "a"},
        {"e": "🍽️", "p": "comer", "c": "v"}, {"e": "🌈", "p": "colorido", "c": "a"}]),
]

# ---------------------------------------------------------------
# Actividades agregadas (octubre 2026): al menos 10 por tipo de juego.
# Elegidas según los NAP de Lengua del primer ciclo y el Plan de Alfabetización de Jujuy:
# letra inicial y vocales (1.º), que/qui, gue/gui, mp/mb, sílabas trabadas (2.º),
# r/rr y nr, -aba, puntuación, conectores, sinónimos/antónimos, sustantivos propios (3.º).
# ---------------------------------------------------------------
def _r(p, e, ct, ce, x1, e1, x2, e2):
    """Ítem de rimas: palabra, palabra que rima y dos que no riman (con sus dibujos)."""
    return {"p": p, "e": e, "c": {"t": ct, "e": ce}, "x": [{"t": x1, "e": e1}, {"t": x2, "e": e2}]}


JUEGOS += [
    # ---------------- Ordeno oraciones ----------------
    _j("or-casa", "oraciones", "En casa", "🏡", "🧸", 1, [
        {"e": "🍽️", "t": "Papá lava los platos"}, {"e": "🧸", "t": "Mi oso está en la cama"},
        {"e": "🌱", "t": "Riego la planta del patio"}, {"e": "📺", "t": "Vemos dibujos en la tele"},
        {"e": "🐈", "t": "El gato toma su leche"}, {"e": "🧹", "t": "Barro el piso de la cocina"}]),
    _j("or-plaza", "oraciones", "En la plaza", "🌳", "🎈", 1, [
        {"e": "🌳", "t": "Juego en la plaza con Leo"}, {"e": "🎈", "t": "Mi globo es de color azul"},
        {"e": "🐦", "t": "Las palomas comen migas"}, {"e": "⚽", "t": "Pateo la pelota muy fuerte"},
        {"e": "🍦", "t": "Mamá me compra un helado"}, {"e": "🌼", "t": "Hay flores en el pasto"}]),
    _j("or-masc", "oraciones", "Mis mascotas", "🐾", "🐹", 2, [
        {"e": "🐹", "t": "Mi hámster corre en su rueda"}, {"e": "🐕", "t": "Saco a pasear al perro cada tarde"},
        {"e": "🐠", "t": "El pez dorado nada en la pecera"}, {"e": "🐢", "t": "La tortuga come hojas de lechuga"},
        {"e": "🐇", "t": "Mi conejo tiene orejas largas"}, {"e": "🦜", "t": "El loro repite todo lo que digo"}]),
    _j("or-comida", "oraciones", "Comidas ricas", "🍲", "🥟", 2, [
        {"e": "🥟", "t": "La abuela prepara empanadas"}, {"e": "🍲", "t": "En invierno tomamos sopa caliente"},
        {"e": "🍌", "t": "Me gusta la banana con leche"}, {"e": "🥪", "t": "Llevo un sándwich para la merienda"},
        {"e": "🍊", "t": "Exprimimos naranjas para el jugo"}, {"e": "🍪", "t": "Horneamos galletitas de vainilla"}]),
    _j("or-queb", "oraciones", "Paseo por la Quebrada", "🏜️", "🦙", 3, [
        {"e": "🦙", "t": "Las llamas caminan despacio por el cerro"},
        {"e": "🌵", "t": "El cardón crece entre las piedras del camino"},
        {"e": "🏔️", "t": "Desde el cerro se ven los colores de la quebrada"},
        {"e": "🧣", "t": "La tejedora hace un poncho de lana"},
        {"e": "🌽", "t": "En la feria venden choclos y papas andinas"},
        {"e": "☀️", "t": "Al mediodía el sol calienta mucho"}]),
    _j("or-notic", "oraciones", "Noticias de la escuela", "📰", "📰", 3, [
        {"e": "🏆", "t": "Nuestro grado ganó el concurso de lectura"},
        {"e": "🌱", "t": "El lunes plantamos árboles en el patio"},
        {"e": "🎭", "t": "Los alumnos de tercero prepararon una obra de teatro"},
        {"e": "📚", "t": "La biblioteca recibió cajas llenas de libros nuevos"},
        {"e": "🚌", "t": "El viernes viajamos en micro al museo"},
        {"e": "🎶", "t": "El coro cantará en el acto de fin de año"}]),

    # ---------------- Busco la rima ----------------
    _j("ri-ani", "rimas", "Rimas de animales", "🐻", "🐑", 1, [
        _r("ratón", "🐭", "jabón", "🧼", "sol", "☀️", "mesa", "🍽️"),
        _r("abeja", "🐝", "oveja", "🐑", "gato", "🐱", "pan", "🍞"),
        _r("perro", "🐶", "cerro", "⛰️", "flor", "🌸", "luna", "🌙"),
        _r("rana", "🐸", "manzana", "🍎", "auto", "🚗", "pie", "🦶"),
        _r("león", "🦁", "corazón", "❤️", "pato", "🦆", "casa", "🏠"),
        _r("conejo", "🐰", "viejo", "👴", "nube", "☁️", "uva", "🍇")]),
    _j("ri-casa", "rimas", "Rimas de la casa", "🏠", "🕯️", 1, [
        _r("mesa", "🍽️", "fresa", "🍓", "perro", "🐶", "sol", "☀️"),
        _r("silla", "🪑", "ardilla", "🐿️", "tren", "🚂", "pez", "🐟"),
        _r("vela", "🕯️", "muela", "🦷", "luna", "🌙", "gato", "🐱"),
        _r("taza", "☕", "calabaza", "🎃", "libro", "📚", "mono", "🐒"),
        _r("olla", "🍲", "cebolla", "🧅", "flor", "🌸", "pie", "🦶"),
        _r("puerta", "🚪", "huerta", "🥕", "nube", "☁️", "auto", "🚗")]),
    _j("ri-cielo", "rimas", "Rimas del cielo", "☁️", "☄️", 1, [
        _r("nube", "☁️", "sube", "⬆️", "pato", "🦆", "mesa", "🍽️"),
        _r("cometa", "☄️", "bicicleta", "🚲", "perro", "🐶", "uva", "🍇"),
        _r("rayo", "⚡", "gallo", "🐓", "flor", "🌸", "casa", "🏠"),
        _r("viento", "🌬️", "cuento", "📖", "gato", "🐱", "pan", "🍞"),
        _r("sol", "☀️", "caracol", "🐌", "silla", "🪑", "mano", "✋"),
        _r("noche", "🌃", "coche", "🚗", "oso", "🐻", "pie", "🦶")]),
    _j("ri-fruta", "rimas", "Rimas de frutas", "🍓", "🍐", 2, [
        _r("pera", "🍐", "tijera", "✂️", "perro", "🐶", "sol", "☀️"),
        _r("banana", "🍌", "campana", "🔔", "libro", "📚", "pez", "🐟"),
        _r("frutilla", "🍓", "semilla", "🌱", "gato", "🐱", "tren", "🚂"),
        _r("melón", "🍈", "balón", "⚽", "nube", "☁️", "casa", "🏠"),
        _r("naranja", "🍊", "granja", "🚜", "luna", "🌙", "pie", "🦶"),
        _r("cereza", "🍒", "princesa", "👸", "barco", "⛵", "oso", "🐻")]),
    _j("ri-cantar", "rimas", "Rimas para cantar", "🎶", "🎸", 2, [
        _r("cuaderno", "📓", "invierno", "❄️", "pato", "🦆", "flor", "🌸"),
        _r("guitarra", "🎸", "cigarra", "🦗", "mesa", "🍽️", "sol", "☀️"),
        _r("papel", "📄", "pincel", "🖌️", "gato", "🐱", "luna", "🌙"),
        _r("lectura", "📖", "basura", "🗑️", "perro", "🐶", "pan", "🍞"),
        _r("dibujo", "🎨", "brujo", "🧙", "silla", "🪑", "tren", "🚂"),
        _r("escuela", "🏫", "abuela", "👵", "barco", "⛵", "uva", "🍇")]),
    _j("ri-jug", "rimas", "Rimas de juguetes", "🧸", "🥁", 2, [
        _r("tambor", "🥁", "flor", "🌸", "mesa", "🍽️", "pato", "🦆"),
        _r("barco", "⛵", "arco", "🏹", "luna", "🌙", "pie", "🦶"),
        _r("tren", "🚂", "sartén", "🍳", "gato", "🐱", "casa", "🏠"),
        _r("globo", "🎈", "lobo", "🐺", "sol", "☀️", "silla", "🪑"),
        _r("dado", "🎲", "helado", "🍦", "perro", "🐶", "nube", "☁️"),
        _r("osito", "🧸", "pollito", "🐤", "libro", "📚", "pan", "🍞")]),
    _j("ri-larg", "rimas", "Rimas con palabras largas", "✨", "🦋", 3, [
        _r("mariposa", "🦋", "rosa", "🌹", "camión", "🚚", "estrella", "⭐"),
        _r("chocolate", "🍫", "tomate", "🍅", "tortuga", "🐢", "camisa", "👔"),
        _r("elefante", "🐘", "diamante", "💎", "caracol", "🐌", "pelota", "⚽"),
        _r("tortuga", "🐢", "oruga", "🐛", "elefante", "🐘", "manzana", "🍎"),
        _r("cocodrilo", "🐊", "hilo", "🧵", "zapato", "👞", "galleta", "🍪"),
        _r("zanahoria", "🥕", "noria", "🎡", "paloma", "🕊️", "conejo", "🐰")]),
    _j("ri-poema", "rimas", "Rimas para poemas", "📜", "🐧", 3, [
        _r("caramelo", "🍬", "hielo", "🧊", "tortuga", "🐢", "camión", "🚚"),
        _r("mariquita", "🐞", "campanita", "🔔", "elefante", "🐘", "zapato", "👞"),
        _r("colibrí", "🐦", "maní", "🥜", "caracol", "🐌", "bufanda", "🧣"),
        _r("pingüino", "🐧", "camino", "🛤️", "galleta", "🍪", "estrella", "⭐"),
        _r("hormiga", "🐜", "espiga", "🌾", "pelota", "⚽", "paraguas", "☂️"),
        _r("panadero", "👨‍🍳", "sombrero", "👒", "tomate", "🍅", "conejo", "🐰")]),

    # ---------------- Armo palabras ----------------
    _j("pa-tres", "palabras", "Palabras de tres letras", "🔤", "👑", 1, [
        {"e": "🍇", "p": "uva"}, {"e": "🦶", "p": "pie"}, {"e": "🌊", "p": "mar"},
        {"e": "👑", "p": "rey"}, {"e": "🧂", "p": "sal"}, {"e": "👁️", "p": "ojo"}]),
    _j("pa-ani", "palabras", "Animales cortos", "🐾", "🐸", 1, [
        {"e": "🐸", "p": "rana"}, {"e": "🦆", "p": "pato"}, {"e": "🐄", "p": "vaca"},
        {"e": "🐒", "p": "mono"}, {"e": "🦜", "p": "loro"}, {"e": "🐂", "p": "toro"}]),
    _j("pa-mesa", "palabras", "En la mesa", "🍽️", "🍯", 1, [
        {"e": "☕", "p": "taza"}, {"e": "🥤", "p": "vaso"}, {"e": "🍲", "p": "sopa"},
        {"e": "🥔", "p": "papa"}, {"e": "🍯", "p": "miel"}, {"e": "🍐", "p": "pera"}]),
    _j("pa-nat", "palabras", "La naturaleza", "🌳", "🌋", 2, [
        {"e": "🌳", "p": "árbol"}, {"e": "🍃", "p": "hoja"}, {"e": "🌧️", "p": "lluvia"},
        {"e": "⛰️", "p": "montaña"}, {"e": "🌱", "p": "planta"}, {"e": "🌋", "p": "volcán"}]),
    _j("pa-ropa", "palabras", "La ropa", "👕", "🧣", 2, [
        {"e": "👕", "p": "remera"}, {"e": "🧢", "p": "gorra"}, {"e": "🧣", "p": "bufanda"},
        {"e": "👞", "p": "zapato"}, {"e": "🧦", "p": "medias"}, {"e": "🧤", "p": "guantes"}]),
    _j("pa-trans", "palabras", "Medios de transporte", "🚗", "🚀", 2, [
        {"e": "⛵", "p": "barco"}, {"e": "✈️", "p": "avión"}, {"e": "🚚", "p": "camión"},
        {"e": "🚀", "p": "cohete"}, {"e": "🏍️", "p": "moto"}, {"e": "🚂", "p": "tren"}]),
    _j("pa-larg", "palabras", "Animales con nombres largos", "🦒", "🦛", 3, [
        {"e": "🐘", "p": "elefante"}, {"e": "🐊", "p": "cocodrilo"}, {"e": "🦇", "p": "murciélago"},
        {"e": "🦖", "p": "dinosaurio"}, {"e": "🦛", "p": "hipopótamo"}, {"e": "🦘", "p": "canguro"}]),
    _j("pa-trab", "palabras", "Dos consonantes juntas", "🧩", "🐉", 3, [
        {"e": "🎺", "p": "trompeta"}, {"e": "🪐", "p": "planeta"}, {"e": "🐉", "p": "dragón"},
        {"e": "🦓", "p": "cebra"}, {"e": "🐯", "p": "tigre"}, {"e": "🧙", "p": "bruja"}]),

    # ---------------- Juego de sílabas ----------------
    _j("si-dos", "silabas", "Dos palmadas", "👏", "🍍", 1, [
        {"e": "🏠", "p": "ca-sa"}, {"e": "🍽️", "p": "me-sa"}, {"e": "🐄", "p": "va-ca"},
        {"e": "🌹", "p": "ro-sa"}, {"e": "🐂", "p": "to-ro"}, {"e": "🍍", "p": "pi-ña"}]),
    _j("si-fac", "silabas", "Sílabas fáciles", "🐒", "🐸", 1, [
        {"e": "🐒", "p": "mo-no"}, {"e": "🍐", "p": "pe-ra"}, {"e": "🦜", "p": "lo-ro"},
        {"e": "🐸", "p": "sa-po"}, {"e": "🛏️", "p": "ca-ma"}, {"e": "👄", "p": "bo-ca"}]),
    _j("si-ani", "silabas", "Animales en sílabas", "🐾", "🦁", 1, [
        {"e": "🐻", "p": "o-so"}, {"e": "🐸", "p": "ra-na"}, {"e": "🐓", "p": "ga-llo"},
        {"e": "🐶", "p": "pe-rro"}, {"e": "🦁", "p": "le-ón"}, {"e": "🐐", "p": "ca-bra"}]),
    _j("si-tres", "silabas", "Tres sílabas", "🍎", "🐴", 2, [
        {"e": "🍎", "p": "man-za-na"}, {"e": "👞", "p": "za-pa-to"}, {"e": "🕊️", "p": "pa-lo-ma"},
        {"e": "🍪", "p": "ga-lle-ta"}, {"e": "🐰", "p": "co-ne-jo"}, {"e": "🐴", "p": "ca-ba-llo"}]),
    _j("si-coc", "silabas", "En la cocina", "🍳", "🥄", 2, [
        {"e": "🥄", "p": "cu-cha-ra"}, {"e": "🔪", "p": "cu-chi-llo"}, {"e": "🍳", "p": "sar-tén"},
        {"e": "🧅", "p": "ce-bo-lla"}, {"e": "🥕", "p": "za-na-ho-ria"}, {"e": "🧀", "p": "que-so"}]),
    _j("si-trab", "silabas", "Sílabas trabadas", "🧱", "🐉", 2, [
        {"e": "🎈", "p": "glo-bo"}, {"e": "🍽️", "p": "pla-to"}, {"e": "📚", "p": "li-bro"},
        {"e": "🐉", "p": "dra-gón"}, {"e": "🧙", "p": "bru-ja"}, {"e": "🌾", "p": "tri-go"}]),
    _j("si-larg", "silabas", "Palabras muy largas", "🐊", "🦛", 3, [
        {"e": "🐊", "p": "co-co-dri-lo"}, {"e": "🦇", "p": "mur-cié-la-go"}, {"e": "🦛", "p": "hi-po-pó-ta-mo"},
        {"e": "🐞", "p": "ma-ri-qui-ta"}, {"e": "🥑", "p": "a-gua-ca-te"}, {"e": "☎️", "p": "te-lé-fo-no"}]),
    _j("si-dif", "silabas", "Sílabas difíciles", "🎼", "🦖", 3, [
        {"e": "💻", "p": "com-pu-ta-do-ra"}, {"e": "🦖", "p": "di-no-sau-rio"}, {"e": "☂️", "p": "pa-ra-guas"},
        {"e": "⭐", "p": "es-tre-lla"}, {"e": "❄️", "p": "in-vier-no"}, {"e": "📚", "p": "bi-blio-te-ca"}]),

    # ---------------- La palabra que falta ----------------
    _j("co-cosas", "completar", "Completo con dibujos", "🐸", "☔", 1, [
        {"e": "🐸", "t": "La rana vive en la _", "o": ["laguna", "heladera", "mochila"]},
        {"e": "🍌", "t": "El mono come una _", "o": ["banana", "silla", "nube"]},
        {"e": "☔", "t": "Cuando llueve uso el _", "o": ["paraguas", "helado", "libro"]},
        {"e": "🛏️", "t": "De noche duermo en mi _", "o": ["cama", "plato", "auto"]},
        {"e": "🦷", "t": "Me lavo los _ con el cepillo", "o": ["dientes", "zapatos", "árboles"]},
        {"e": "🔥", "t": "El fuego está muy _", "o": ["caliente", "frío", "dulce"]}]),
    _j("co-acc", "completar", "¿Qué hace?", "🏃", "📖", 1, [
        {"e": "🏊", "t": "Los chicos _ en la pileta", "o": ["nadan", "duermen", "escriben"]},
        {"e": "🎂", "t": "Juan _ las velitas de la torta", "o": ["sopla", "lava", "pinta"]},
        {"e": "📖", "t": "La seño _ un cuento", "o": ["lee", "barre", "cocina"]},
        {"e": "🐕", "t": "El perro _ cuando ve un gato", "o": ["ladra", "vuela", "maúlla"]},
        {"e": "🎵", "t": "Los pájaros _ en la mañana", "o": ["cantan", "nadan", "leen"]},
        {"e": "🍎", "t": "Sofía _ una manzana roja", "o": ["come", "lee", "escribe"]}]),
    _j("co-como", "completar", "¿Cómo es?", "🎨", "❄️", 1, [
        {"e": "🐘", "t": "El elefante es muy _", "o": ["grande", "chiquito", "verde"]},
        {"e": "🍋", "t": "El limón es _", "o": ["ácido", "dulce", "peludo"]},
        {"e": "❄️", "t": "La nieve es _", "o": ["blanca", "negra", "caliente"]},
        {"e": "🐌", "t": "El caracol camina _", "o": ["despacio", "rápido", "volando"]},
        {"e": "✨", "t": "Las estrellas se ven de _", "o": ["noche", "día", "siesta"]},
        {"e": "🍬", "t": "El caramelo es _", "o": ["dulce", "salado", "amargo"]}]),
    _j("co-conc", "completar", "Palabras que concuerdan", "🧩", "🌸", 2, [
        {"e": "🐱", "t": "Los gatitos son muy _", "o": ["juguetones", "juguetón", "juguetona"]},
        {"e": "🌸", "t": "Las flores del jardín están _", "o": ["lindas", "lindo", "linda"]},
        {"e": "👧", "t": "Mi hermana _ en tercer grado", "o": ["está", "están", "estamos"]},
        {"e": "🚗", "t": "Los autos _ por la calle", "o": ["pasan", "pasa", "pasás"]},
        {"e": "🍞", "t": "El pan está _", "o": ["fresco", "fresca", "frescas"]},
        {"e": "🐦", "t": "Ayer los pájaros _ en el nido", "o": ["cantaron", "canta", "cantará"]}]),
    _j("co-tiempo", "completar", "¿Cuándo pasó?", "⏰", "📅", 2, [
        {"e": "📅", "t": "Ayer _ al parque con mi tío", "o": ["fui", "voy", "iré"]},
        {"e": "🔮", "t": "Mañana _ una torta de chocolate", "o": ["haremos", "hicimos", "hacíamos"]},
        {"e": "👶", "t": "Cuando era chico, mi papá _ a la pelota", "o": ["jugaba", "jugará", "juega"]},
        {"e": "✏️", "t": "Ahora mismo _ un dibujo", "o": ["estoy haciendo", "hice", "haré"]},
        {"e": "🎄", "t": "El año que viene _ a visitar a mi abuela", "o": ["iremos", "fuimos", "íbamos"]},
        {"e": "📜", "t": "Hace mucho tiempo, los incas _ grandes caminos", "o": ["construían", "construirán", "construyen"]}]),
    _j("co-conect", "completar", "Palabras que unen ideas", "🔗", "🔗", 2, [
        {"e": "🌧️", "t": "Me mojé _ estaba lloviendo", "o": ["porque", "pero", "y"]},
        {"e": "🍦", "t": "Quería un helado _ no tenía plata", "o": ["pero", "porque", "entonces"]},
        {"e": "🥪", "t": "Comí un sándwich _ una fruta", "o": ["y", "pero", "porque"]},
        {"e": "😴", "t": "Tenía sueño, _ me fui a dormir", "o": ["entonces", "pero", "aunque"]},
        {"e": "🧥", "t": "Hacía frío, _ me puse la campera", "o": ["así que", "pero", "aunque"]},
        {"e": "📚", "t": "Primero leí el cuento y _ hice el dibujo", "o": ["después", "antes", "nunca"]}]),
    _j("co-signos", "completar", "Signos de puntuación", "❓", "❗", 3, [
        {"e": "❓", "t": "¿Cómo te llamás_", "o": ["?", ".", "!"]},
        {"e": "❗", "t": "¡Qué lindo día_", "o": ["!", "?", ","]},
        {"e": "🛒", "t": "Compré pan, leche_ queso y frutas", "o": [",", "?", "!"]},
        {"e": "🎒", "t": "_Dónde está mi mochila?", "o": ["¿", "¡", "."]},
        {"e": "🎉", "t": "_Feliz cumpleaños!", "o": ["¡", "¿", ","]},
        {"e": "🌙", "t": "Ya es de noche_ Vamos a dormir", "o": [".", "?", ","]}]),
    _j("co-texto", "completar", "Completo textos informativos", "📰", "🦙", 3, [
        {"e": "🦙", "t": "La llama es un animal que vive en la _", "o": ["Puna", "playa", "selva"]},
        {"e": "🌵", "t": "El cardón es una planta con muchas _", "o": ["espinas", "plumas", "ruedas"]},
        {"e": "🌋", "t": "Un volcán puede largar lava muy _", "o": ["caliente", "fría", "dulce"]},
        {"e": "🐝", "t": "Las abejas fabrican _ en la colmena", "o": ["miel", "leche", "pan"]},
        {"e": "🌱", "t": "Para crecer, las semillas necesitan agua, tierra y _", "o": ["sol", "plástico", "sal"]},
        {"e": "🦉", "t": "El búho caza de noche porque ve bien en la _", "o": ["oscuridad", "escuela", "lluvia"]}]),

    # ---------------- Parecidas y opuestas ----------------
    _j("op-fac", "opuestos", "Contrarios fáciles", "↔️", "🧼", 1, [
        {"e": "⬆️", "p": "arriba", "r": "opuesto", "o": ["abajo", "alto", "encima"]},
        {"e": "🐢", "p": "lento", "r": "opuesto", "o": ["rápido", "tortuga", "verde"]},
        {"e": "🍬", "p": "dulce", "r": "opuesto", "o": ["salado", "rico", "azúcar"]},
        {"e": "💧", "p": "mojado", "r": "opuesto", "o": ["seco", "agua", "limpio"]},
        {"e": "🧼", "p": "limpio", "r": "opuesto", "o": ["sucio", "jabón", "nuevo"]},
        {"e": "✨", "p": "nuevo", "r": "opuesto", "o": ["viejo", "lindo", "grande"]}]),
    _j("op-mas", "opuestos", "Más contrarios", "🌗", "🌗", 1, [
        {"e": "🔊", "p": "ruidoso", "r": "opuesto", "o": ["silencioso", "fuerte", "música"]},
        {"e": "📏", "p": "largo", "r": "opuesto", "o": ["corto", "alto", "flaco"]},
        {"e": "🌑", "p": "oscuro", "r": "opuesto", "o": ["claro", "negro", "noche"]},
        {"e": "🏠", "p": "adentro", "r": "opuesto", "o": ["afuera", "casa", "arriba"]},
        {"e": "🥶", "p": "invierno", "r": "opuesto", "o": ["verano", "frío", "nieve"]},
        {"e": "😄", "p": "reír", "r": "opuesto", "o": ["llorar", "cantar", "sonreír"]}]),
    _j("op-par1", "opuestos", "Palabras que se parecen", "🤝", "🤝", 1, [
        {"e": "🚗", "p": "auto", "r": "parecido", "o": ["coche", "camión", "rueda"]},
        {"e": "🧒", "p": "chico", "r": "parecido", "o": ["niño", "grande", "viejo"]},
        {"e": "🏠", "p": "casa", "r": "parecido", "o": ["hogar", "calle", "puerta"]},
        {"e": "😋", "p": "rico", "r": "parecido", "o": ["sabroso", "feo", "salado"]},
        {"e": "👀", "p": "mirar", "r": "parecido", "o": ["ver", "oír", "dormir"]},
        {"e": "😀", "p": "alegre", "r": "parecido", "o": ["feliz", "triste", "enojado"]}]),
    _j("op-mix", "opuestos", "Opuestas y parecidas", "🔁", "🎁", 2, [
        {"e": "🌅", "p": "comenzar", "r": "parecido", "o": ["empezar", "terminar", "dormir"]},
        {"e": "😠", "p": "enojado", "r": "parecido", "o": ["furioso", "tranquilo", "feliz"]},
        {"e": "🧺", "p": "poco", "r": "opuesto", "o": ["mucho", "nada", "chico"]},
        {"e": "🐜", "p": "pequeño", "r": "parecido", "o": ["chiquito", "enorme", "rápido"]},
        {"e": "🎁", "p": "dar", "r": "opuesto", "o": ["recibir", "regalar", "entregar"]},
        {"e": "🏔️", "p": "subir", "r": "opuesto", "o": ["bajar", "trepar", "escalar"]}]),
    _j("op-verb", "opuestos", "Acciones contrarias", "🔀", "💡", 2, [
        {"e": "🚪", "p": "abrir", "r": "opuesto", "o": ["cerrar", "empujar", "entrar"]},
        {"e": "💡", "p": "prender", "r": "opuesto", "o": ["apagar", "encender", "mirar"]},
        {"e": "🛬", "p": "llegar", "r": "opuesto", "o": ["irse", "venir", "volver"]},
        {"e": "🛏️", "p": "acostarse", "r": "opuesto", "o": ["levantarse", "dormir", "sentarse"]},
        {"e": "🏆", "p": "ganar", "r": "opuesto", "o": ["perder", "jugar", "festejar"]},
        {"e": "➕", "p": "sumar", "r": "opuesto", "o": ["restar", "contar", "agregar"]}]),
    _j("op-sin", "opuestos", "Sinónimos", "🪞", "🧠", 2, [
        {"e": "👩‍🏫", "p": "maestra", "r": "parecido", "o": ["docente", "alumna", "directora"]},
        {"e": "😢", "p": "triste", "r": "parecido", "o": ["apenado", "alegre", "cansado"]},
        {"e": "🐆", "p": "veloz", "r": "parecido", "o": ["rápido", "lento", "fuerte"]},
        {"e": "🎁", "p": "regalar", "r": "parecido", "o": ["obsequiar", "comprar", "pedir"]},
        {"e": "🧠", "p": "inteligente", "r": "parecido", "o": ["listo", "dormido", "alto"]},
        {"e": "🏁", "p": "terminar", "r": "parecido", "o": ["finalizar", "empezar", "correr"]}]),
    _j("op-dif", "opuestos", "Sinónimos y antónimos difíciles", "📚", "🌟", 3, [
        {"e": "🏡", "p": "vivienda", "r": "parecido", "o": ["casa", "calle", "jardín"]},
        {"e": "😱", "p": "temor", "r": "parecido", "o": ["miedo", "valor", "alegría"]},
        {"e": "💰", "p": "caro", "r": "opuesto", "o": ["barato", "rico", "precio"]},
        {"e": "🗺️", "p": "viajar", "r": "parecido", "o": ["recorrer", "quedarse", "dormir"]},
        {"e": "🧹", "p": "ordenado", "r": "opuesto", "o": ["desordenado", "limpio", "prolijo"]},
        {"e": "🌟", "p": "brillante", "r": "parecido", "o": ["luminoso", "oscuro", "apagado"]}]),
    _j("op-pref", "opuestos", "Contrarios con in- y des-", "🔣", "🧩", 3, [
        {"e": "😊", "p": "feliz", "r": "opuesto", "o": ["infeliz", "felicidad", "alegre"]},
        {"e": "🧩", "p": "posible", "r": "opuesto", "o": ["imposible", "fácil", "probable"]},
        {"e": "🎀", "p": "atar", "r": "opuesto", "o": ["desatar", "atrapar", "nudo"]},
        {"e": "🛋️", "p": "cómodo", "r": "opuesto", "o": ["incómodo", "sillón", "blando"]},
        {"e": "👕", "p": "vestir", "r": "opuesto", "o": ["desvestir", "ropa", "poner"]},
        {"e": "✅", "p": "correcto", "r": "opuesto", "o": ["incorrecto", "bien", "perfecto"]}]),

    # ---------------- ¿Con qué letra va? ----------------
    _j("ot-ini", "ortografia", "¿Con qué letra empieza?", "🔠", "🐸", 1, [
        {"e": "🐸", "p": "_ana", "o": ["r", "l", "m"]}, {"e": "🍎", "p": "_anzana", "o": ["m", "n", "p"]},
        {"e": "🦆", "p": "_ato", "o": ["p", "t", "l"]}, {"e": "🐻", "p": "_so", "o": ["o", "a", "u"]},
        {"e": "🌙", "p": "_una", "o": ["l", "t", "s"]}, {"e": "🍞", "p": "_an", "o": ["p", "d", "t"]}]),
    _j("ot-voc", "ortografia", "La vocal que falta", "🅰️", "☀️", 1, [
        {"e": "☀️", "p": "s_l", "o": ["o", "a", "u"]}, {"e": "🐱", "p": "g_to", "o": ["a", "o", "e"]},
        {"e": "🌸", "p": "fl_r", "o": ["o", "a", "e"]}, {"e": "🐟", "p": "p_z", "o": ["e", "a", "i"]},
        {"e": "🧀", "p": "qu_so", "o": ["e", "i", "a"]}, {"e": "🦶", "p": "p_e", "o": ["i", "a", "o"]}]),
    _j("ot-fin", "ortografia", "¿Con qué letra termina?", "🔚", "🍯", 1, [
        {"e": "🍞", "p": "pa_", "o": ["n", "l", "s"]}, {"e": "☀️", "p": "so_", "o": ["l", "n", "r"]},
        {"e": "🌸", "p": "flo_", "o": ["r", "n", "s"]}, {"e": "🐟", "p": "pe_", "o": ["z", "s", "n"]},
        {"e": "🍯", "p": "mie_", "o": ["l", "n", "r"]}, {"e": "🚂", "p": "tre_", "o": ["n", "s", "l"]}]),
    _j("ot-que", "ortografia", "Ca, que, qui, co, cu", "🧀", "🦟", 2, [
        {"e": "🧀", "p": "_eso", "o": ["qu", "c", "k"]}, {"e": "🏠", "p": "_asa", "o": ["c", "qu", "k"]},
        {"e": "🌳", "p": "bos_e", "o": ["qu", "c", "k"]}, {"e": "🐄", "p": "va_a", "o": ["c", "qu", "k"]},
        {"e": "🦟", "p": "mos_ito", "o": ["qu", "c", "k"]}, {"e": "🥥", "p": "_oco", "o": ["c", "qu", "k"]},
        {"e": "🥄", "p": "_uchara", "o": ["c", "qu", "k"]}, {"e": "🏸", "p": "ra_eta", "o": ["qu", "c", "k"]}]),
    _j("ot-gue", "ortografia", "Ga, gue, gui, go, gu", "🎸", "🎸", 2, [
        {"e": "🎸", "p": "_itarra", "o": ["gu", "g", "j"]}, {"e": "🐱", "p": "_ato", "o": ["g", "gu", "j"]},
        {"e": "💧", "p": "a_a", "o": ["gu", "g", "j"]}, {"e": "🔥", "p": "fue_o", "o": ["g", "gu", "j"]},
        {"e": "🐛", "p": "_usano", "o": ["g", "gu", "j"]}, {"e": "🎁", "p": "re_alo", "o": ["g", "gu", "j"]},
        {"e": "🍲", "p": "_iso", "o": ["gu", "g", "j"]}]),
    _j("ot-mb", "ortografia", "Antes de p y b va m", "🏕️", "🥁", 2, [
        {"e": "🏕️", "p": "ca_amento", "o": ["mp", "np"]}, {"e": "🎺", "p": "tro_eta", "o": ["mp", "np"]},
        {"e": "🥁", "p": "ta_or", "o": ["mb", "nb"]}, {"e": "👒", "p": "so_rero", "o": ["mb", "nb"]},
        {"e": "💡", "p": "lá_ara", "o": ["mp", "np"]}, {"e": "🔄", "p": "ca_iar", "o": ["mb", "nb"]},
        {"e": "➕", "p": "ta_ién", "o": ["mb", "nb"]}, {"e": "🌾", "p": "ca_o", "o": ["mp", "np"]}]),
    _j("ot-rr", "ortografia", "R o rr", "🐶", "🎸", 3, [
        {"e": "🐭", "p": "_atón", "o": ["r", "rr"]}, {"e": "🍚", "p": "a_oz", "o": ["rr", "r"]},
        {"e": "🌹", "p": "_osa", "o": ["r", "rr"]}, {"e": "⛰️", "p": "ce_o", "o": ["rr", "r"]},
        {"e": "🍐", "p": "pe_a", "o": ["r", "rr"]}, {"e": "🏅", "p": "hon_a", "o": ["r", "rr"]},
        {"e": "🚗", "p": "ca_o", "o": ["rr", "r"]}, {"e": "🎸", "p": "guita_a", "o": ["rr", "r"]}]),
    _j("ot-aba", "ortografia", "Verbos con -aba", "📜", "💃", 3, [
        {"e": "🎤", "p": "cant_", "o": ["aba", "ava"]}, {"e": "⚽", "p": "jug_", "o": ["aba", "ava"]},
        {"e": "🏊", "p": "nad_", "o": ["aba", "ava"]}, {"e": "🎨", "p": "pint_", "o": ["aba", "ava"]},
        {"e": "🚶", "p": "camin_", "o": ["aba", "ava"]}, {"e": "💃", "p": "bail_", "o": ["aba", "ava"]}]),

    # ---------------- ¿Quién, cómo es o qué hace? ----------------
    _j("cl-nombra", "clases", "¿Nombra algo o es una acción?", "🏷️", "🎤", 2, [
        {"e": "🐱", "p": "gato", "c": "s", "t": "El gato duerme en el sillón"},
        {"e": "🏃", "p": "corre", "c": "v", "t": "Juan corre en el recreo"},
        {"e": "🌳", "p": "árbol", "c": "s", "t": "El árbol tiene muchas hojas"},
        {"e": "🍽️", "p": "come", "c": "v", "t": "Ana come fideos con queso"},
        {"e": "⚽", "p": "pelota", "c": "s", "t": "La pelota quedó en el patio"},
        {"e": "🎨", "p": "pinta", "c": "v", "t": "Lucas pinta un sol amarillo"},
        {"e": "🏠", "p": "casa", "c": "s", "t": "Mi casa tiene un jardín"},
        {"e": "🎤", "p": "canta", "c": "v", "t": "Mi tía canta muy lindo"}]),
    _j("cl-desc", "clases", "Palabras que describen", "🎨", "🌈", 2, [
        {"e": "🌹", "p": "roja", "c": "a", "t": "La rosa es roja"},
        {"e": "🐘", "p": "elefante", "c": "s", "t": "El elefante toma agua"},
        {"e": "🍦", "p": "frío", "c": "a", "t": "El helado está frío"},
        {"e": "🐶", "p": "cachorro", "c": "s", "t": "El cachorro mueve la cola"},
        {"e": "😴", "p": "cansado", "c": "a", "t": "Papá llegó cansado del trabajo"},
        {"e": "🍫", "p": "rico", "c": "a", "t": "El chocolate es muy rico"},
        {"e": "🌈", "p": "arcoíris", "c": "s", "t": "Después de la lluvia salió un arcoíris"},
        {"e": "🐸", "p": "verde", "c": "a", "t": "La rana es verde"}]),
    _j("cl-ani", "clases", "Animales: quién, cómo es, qué hace", "🐾", "🦁", 2, [
        {"e": "🐦", "p": "vuela", "c": "v", "t": "El pájaro vuela alto"},
        {"e": "🐟", "p": "pez", "c": "s", "t": "El pez nada en la pecera"},
        {"e": "🐰", "p": "blanco", "c": "a", "t": "Tengo un conejo blanco"},
        {"e": "🐄", "p": "muge", "c": "v", "t": "La vaca muge en el campo"},
        {"e": "🐌", "p": "caracol", "c": "s", "t": "El caracol lleva su casa"},
        {"e": "🦁", "p": "valiente", "c": "a", "t": "El león es valiente"},
        {"e": "🐝", "p": "zumba", "c": "v", "t": "La abeja zumba entre las flores"},
        {"e": "🦒", "p": "alta", "c": "a", "t": "La jirafa es muy alta"}]),
    _j("cl-esc", "clases", "Palabras de la escuela", "🏫", "🔔", 2, [
        {"e": "📚", "p": "libro", "c": "s", "t": "Saqué un libro de la biblioteca"},
        {"e": "✏️", "p": "escribe", "c": "v", "t": "Martina escribe su nombre"},
        {"e": "🎒", "p": "pesada", "c": "a", "t": "Mi mochila está pesada"},
        {"e": "👩‍🏫", "p": "maestra", "c": "s", "t": "La maestra explica la tarea"},
        {"e": "📖", "p": "lee", "c": "v", "t": "El grupo lee un cuento"},
        {"e": "🖍️", "p": "colorido", "c": "a", "t": "Hicimos un mural colorido"},
        {"e": "🔔", "p": "suena", "c": "v", "t": "El timbre suena fuerte"},
        {"e": "🪑", "p": "silla", "c": "s", "t": "Cada chico tiene su silla"}]),
    _j("cl-orac", "clases", "Clasifico palabras de una oración", "🔍", "🏔️", 3, [
        {"e": "🌧️", "p": "lluvia", "c": "s", "t": "La lluvia mojó todo el patio"},
        {"e": "🌧️", "p": "mojó", "c": "v", "t": "La lluvia mojó todo el patio"},
        {"e": "🏔️", "p": "nevado", "c": "a", "t": "El cerro nevado brilla al sol"},
        {"e": "🏔️", "p": "brilla", "c": "v", "t": "El cerro nevado brilla al sol"},
        {"e": "🎻", "p": "música", "c": "s", "t": "La música suave me da sueño"},
        {"e": "🎻", "p": "suave", "c": "a", "t": "La música suave me da sueño"},
        {"e": "🧑‍🍳", "p": "cocina", "c": "v", "t": "El abuelo cocina locro los domingos"},
        {"e": "🍲", "p": "locro", "c": "s", "t": "El abuelo cocina locro los domingos"}]),
    _j("cl-prop", "clases", "Nombres de lugares y personas", "🏙️", "🗺️", 3, [
        {"e": "🗺️", "p": "Jujuy", "c": "s", "t": "Vivo en la provincia de Jujuy"},
        {"e": "⛰️", "p": "Humahuaca", "c": "s", "t": "Humahuaca está en la quebrada"},
        {"e": "👧", "p": "Martina", "c": "s", "t": "Martina es mi prima"},
        {"e": "🏙️", "p": "ciudad", "c": "s", "t": "La ciudad tiene muchas calles"},
        {"e": "🌄", "p": "hermosa", "c": "a", "t": "Purmamarca es hermosa"},
        {"e": "🚌", "p": "visitamos", "c": "v", "t": "Visitamos Tilcara en las vacaciones"},
        {"e": "🏞️", "p": "río", "c": "s", "t": "El río Grande baja del cerro"},
        {"e": "🎒", "p": "viajó", "c": "v", "t": "Tomás viajó a Salta"}]),
    _j("cl-tiempo", "clases", "Acciones de ayer, hoy y mañana", "⏳", "🎶", 3, [
        {"e": "🎶", "p": "cantaba", "c": "v", "t": "Mi abuela cantaba coplas"},
        {"e": "🎶", "p": "coplas", "c": "s", "t": "Mi abuela cantaba coplas"},
        {"e": "⚽", "p": "jugaremos", "c": "v", "t": "Mañana jugaremos al fútbol"},
        {"e": "🏚️", "p": "antigua", "c": "a", "t": "Es una casa muy antigua"},
        {"e": "🥾", "p": "caminamos", "c": "v", "t": "Ayer caminamos por el cerro"},
        {"e": "⛰️", "p": "cerro", "c": "s", "t": "Ayer caminamos por el cerro"},
        {"e": "🏞️", "p": "tranquilo", "c": "a", "t": "El río está tranquilo"},
        {"e": "🌅", "p": "amanece", "c": "v", "t": "En verano amanece temprano"}]),
    _j("cl-faro", "clases", "Palabras de «El faro de Martina»", "📖", "💡", 3, [
        {"e": "💡", "p": "faro", "c": "s", "t": "El abuelo encendía el faro"},
        {"e": "💡", "p": "encendía", "c": "v", "t": "El abuelo encendía el faro"},
        {"e": "⛈️", "p": "fuerte", "c": "a", "t": "Esa noche hubo una tormenta fuerte"},
        {"e": "⛈️", "p": "tormenta", "c": "s", "t": "Esa noche hubo una tormenta fuerte"},
        {"e": "🤲", "p": "temblorosas", "c": "a", "t": "Con las manos temblorosas giró la llave"},
        {"e": "🔑", "p": "giró", "c": "v", "t": "Con las manos temblorosas giró la llave"},
        {"e": "🚢", "p": "barco", "c": "s", "t": "El barco llegó al puerto"},
        {"e": "🚢", "p": "llegó", "c": "v", "t": "El barco llegó al puerto"}]),
]

# Textos que no son cuentos (NAP: adivinanzas, instructivos, notas de enciclopedia y poesía)
CUENTOS += [
    _c("adivina", "Adivinanzas", "❓", "🐰", 1,
       "Adivinanza uno. Tengo orejas largas, salto sin parar y como zanahorias. ¿Quién soy? "
       "Adivinanza dos. Brillo en el cielo durante el día y doy calor. ¿Quién soy? "
       "Adivinanza tres. Tengo hojas, pero no soy árbol. Tengo letras y dibujos adentro. ¿Qué soy?",
       [{"t": "e", "tema": "inferencia", "p": "¿Quién es el de la adivinanza uno?", "o": ["El conejo", "El perro", "El pez"]},
        {"t": "e", "tema": "detalles", "p": "¿Qué come el animal de la adivinanza uno?", "o": ["Zanahorias", "Carne", "Semillas"]},
        {"t": "e", "tema": "inferencia", "p": "¿Qué es la adivinanza dos?", "o": ["El sol", "La luna", "Una lámpara"]},
        {"t": "vf", "tema": "detalles", "p": "La adivinanza dos habla de algo que brilla de noche.", "v": False},
        {"t": "e", "tema": "inferencia", "p": "¿Qué es la adivinanza tres?", "o": ["Un libro", "Un árbol", "Una flor"]},
        {"t": "e", "tema": "vocabulario", "p": "En la adivinanza tres, ¿qué son las «hojas»?", "o": ["Las páginas del libro", "Las hojas de una planta", "Hojas secas del otoño"]}]),
    _c("limonada", "Cómo hacer limonada", "🍋", "🥤", 2,
       "Para hacer limonada necesitás: tres limones, un litro de agua fría, cuatro cucharadas de azúcar y una jarra. "
       "Primero, pedile a un adulto que corte los limones por la mitad. Después, exprimí los limones y echá el jugo en la jarra. "
       "Luego, agregá el agua y el azúcar. Revolvé con una cuchara larga hasta que el azúcar se disuelva. "
       "Por último, serví la limonada en vasos. ¡Lista para tomar!",
       [{"t": "e", "tema": "detalles", "p": "¿Cuántos limones se necesitan?", "o": ["Tres", "Diez", "Uno"]},
        {"t": "e", "tema": "personajes", "p": "¿Quién tiene que cortar los limones?", "o": ["Un adulto", "Los chicos solos", "Nadie"]},
        {"t": "e", "tema": "vocabulario", "p": "El azúcar se «disuelve». ¿Qué quiere decir?", "o": ["Que se mezcla con el agua y deja de verse", "Que se quema", "Que se vuelve sal"]},
        {"t": "vf", "tema": "detalles", "p": "La limonada se hace con agua caliente.", "v": False},
        {"t": "e", "tema": "inferencia", "p": "¿Para qué sirve este texto?", "o": ["Para explicar cómo hacer algo", "Para contar una historia de miedo", "Para vender limones"]},
        {"t": "o", "tema": "secuencia", "items": ["🔪 Un adulto corta los limones.", "🍋 Se exprimen los limones en la jarra.", "🥄 Se agregan el agua y el azúcar y se revuelve.", "🥤 Se sirve la limonada en vasos."]}]),
    _c("llama", "La llama de la Puna", "🦙", "🦙", 2,
       "La llama es un animal de la Puna y de la Quebrada de Humahuaca. Vive en lugares altos y fríos, donde hay poca agua. "
       "Tiene el cuello largo, las orejas puntiagudas y un pelaje grueso y suave. Con su lana, las familias tejen ponchos, medias y frazadas. "
       "La llama come pasto y hierbas. Es un animal tranquilo, pero si se enoja, ¡puede escupir! "
       "Desde hace muchísimos años, las llamas ayudan a las personas a llevar cargas por los caminos de montaña.",
       [{"t": "e", "tema": "personajes", "p": "¿De qué animal habla el texto?", "o": ["De la llama", "Del cóndor", "Del caballo"]},
        {"t": "e", "tema": "lugar", "p": "¿Dónde vive la llama?", "o": ["En lugares altos y fríos", "En el mar", "En la selva"]},
        {"t": "e", "tema": "detalles", "p": "¿Qué se hace con su lana?", "o": ["Ponchos, medias y frazadas", "Zapatos y gorras", "Pan y queso"]},
        {"t": "e", "tema": "vocabulario", "p": "Las orejas son «puntiagudas». ¿Qué quiere decir?", "o": ["Que terminan en punta", "Que son muy chiquitas", "Que son redondas"]},
        {"t": "vf", "tema": "detalles", "p": "La llama come carne.", "v": False},
        {"t": "e", "tema": "emociones", "p": "¿Cómo es la llama casi siempre?", "o": ["Tranquila", "Enojada", "Asustada"]},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué la llama tiene un pelaje grueso?", "o": ["Porque vive en lugares fríos", "Porque le gusta nadar", "Porque es muy rápida"]}]),
    _c("coplas", "Coplas de la Quebrada", "🎶", "🪕", 3,
       "Desde el cerro de colores baja el viento a saludar, trae el canto de los pájaros y el aroma del maizal. "
       "La llamita de la Puna camina sin apurar, lleva lana sobre el lomo para el poncho de mamá. "
       "Con la caja y con el erque se alegra todo el lugar: en febrero, el carnaval nos invita a bailar.",
       [{"t": "e", "tema": "personajes", "p": "¿Qué animal aparece en la segunda copla?", "o": ["La llamita", "El cóndor", "El caballo"]},
        {"t": "e", "tema": "lugar", "p": "¿Desde dónde baja el viento?", "o": ["Desde el cerro de colores", "Desde el mar", "Desde la ciudad"]},
        {"t": "e", "tema": "detalles", "p": "¿Para qué es la lana que lleva la llamita?", "o": ["Para el poncho de mamá", "Para una almohada", "Para vender en la feria"]},
        {"t": "e", "tema": "vocabulario", "p": "Según la copla, ¿qué es el «erque»?", "o": ["Un instrumento musical", "Una comida", "Un animal"]},
        {"t": "e", "tema": "emociones", "p": "¿Cómo está el lugar en la tercera copla?", "o": ["Alegre", "Triste", "Silencioso"]},
        {"t": "vf", "tema": "lugar", "p": "El carnaval de la copla es en febrero.", "v": True},
        {"t": "e", "tema": "inferencia", "p": "¿Por qué el viento trae «el aroma del maizal»?", "o": ["Porque pasa por donde crece el maíz", "Porque cocina choclos", "Porque viene del mar"]}]),
]


# Actividades que usan el juego de completar pero trabajan otro tema (campo «tema»).
# «pregunta»: reemplaza a «¿Qué palabra falta?» en la pantalla y en la voz.
# «minusculas»: se muestran tal cual aunque 1.º grado use IMPRENTA MAYÚSCULA (si no, no se verían las mayúsculas).
JUEGOS += [
    {**_j("co-mayus", "completar", "¿Mayúscula o minúscula?", "🔠", "🗺️", 2, [
        {"e": "🐕", "t": "Mi perra se llama _", "o": ["Luna", "luna"]},
        {"e": "🗺️", "t": "Vivo en la provincia de _", "o": ["Jujuy", "jujuy"]},
        {"e": "📅", "t": "_ fuimos al río con mi familia", "o": ["Ayer", "ayer"]},
        {"e": "👧", "t": "Mi amiga _ vive en Tilcara", "o": ["Sofía", "sofía"]},
        {"e": "❄️", "t": "En invierno hace mucho _", "o": ["frío", "Frío"]},
        {"e": "🐱", "t": "Me gusta jugar con mi _", "o": ["gato", "Gato"]},
        {"e": "🏙️", "t": "La capital de la Argentina es _", "o": ["Buenos Aires", "buenos aires"]},
        {"e": "🍞", "t": "Compramos pan. _ volvimos a casa", "o": ["Después", "después"]}]),
     "tema": "ortografia", "minusculas": True, "pregunta": "¿Con mayúscula o con minúscula?"},
    {**_j("co-tonica", "completar", "¿Qué sílaba suena más fuerte?", "📢", "📢", 3, [
        {"e": "⚽", "t": "En pe-lo-ta suena más fuerte _", "o": ["lo", "pe", "ta"]},
        {"e": "🍎", "t": "En man-za-na suena más fuerte _", "o": ["za", "man", "na"]},
        {"e": "☕", "t": "En ca-fé suena más fuerte _", "o": ["fé", "ca"]},
        {"e": "🌳", "t": "En ár-bol suena más fuerte _", "o": ["ár", "bol"]},
        {"e": "🐭", "t": "En ra-tón suena más fuerte _", "o": ["tón", "ra"]},
        {"e": "🦋", "t": "En ma-ri-po-sa suena más fuerte _", "o": ["po", "ri", "sa"]},
        {"e": "🦇", "t": "En mur-cié-la-go suena más fuerte _", "o": ["cié", "mur", "go"]},
        {"e": "🏠", "t": "En ca-sa suena más fuerte _", "o": ["ca", "sa"]}]),
     "tema": "acentuacion", "pregunta": "¿Qué sílaba suena más fuerte?"},
    {**_j("co-tilde", "completar", "¿Con tilde o sin tilde?", "✍️", "✈️", 3, [
        {"e": "✈️", "t": "El _ vuela sobre las nubes", "o": ["avión", "avion"]},
        {"e": "🐭", "t": "El _ se comió el queso", "o": ["ratón", "raton"]},
        {"e": "🌳", "t": "Me subí a un _ muy alto", "o": ["árbol", "arbol"]},
        {"e": "🍋", "t": "Le puse jugo de _ al agua", "o": ["limón", "limon"]},
        {"e": "🏠", "t": "Mi _ tiene un patio grande", "o": ["casa", "cása"]},
        {"e": "🎵", "t": "Escuchamos _ en el recreo", "o": ["música", "musica"]},
        {"e": "👩‍🏫", "t": "La maestra escribe en el _", "o": ["pizarrón", "pizarron"]},
        {"e": "📚", "t": "Leímos un _ de dinosaurios", "o": ["libro", "líbro"]}]),
     "tema": "acentuacion", "pregunta": "¿Cómo se escribe: con tilde o sin tilde?"},
    {**_j("co-familia", "completar", "Familias de palabras", "🌳", "🍞", 2, [
        {"e": "🍞", "t": "Pan, panadero, panadería y _", "o": ["panera", "pantalón", "manzana"]},
        {"e": "🌸", "t": "Flor, florero, florería y _", "o": ["florcita", "foto", "fiesta"]},
        {"e": "🐟", "t": "Pez, pecera, pescado y _", "o": ["pescador", "pelota", "perro"]},
        {"e": "🌊", "t": "Mar, marinero, marino y _", "o": ["marea", "mariposa", "martes"]},
        {"e": "📚", "t": "Libro, librería, librero y _", "o": ["librito", "liebre", "lima"]},
        {"e": "🌳", "t": "Árbol, arbolito y _", "o": ["arboleda", "árbitro", "arroz"]}]),
     "tema": "familias"},
    {**_j("co-dimin", "completar", "Chiquitos y grandotes", "🐘", "🐭", 2, [
        {"e": "🐶", "t": "Un perro muy chiquito es un _", "o": ["perrito", "perrazo", "perrera"]},
        {"e": "🏠", "t": "Una casa muy grande es un _", "o": ["casón", "casita", "casero"]},
        {"e": "🐱", "t": "Un gato bebé es un _", "o": ["gatito", "gatote", "gatear"]},
        {"e": "🎈", "t": "Un globo enorme es un _", "o": ["globote", "globito", "globero"]},
        {"e": "🌸", "t": "Una flor chiquita es una _", "o": ["florcita", "florota", "florero"]},
        {"e": "👟", "t": "Una patada muy fuerte es un _", "o": ["patadón", "patita", "patito"]}]),
     "tema": "familias"},
]


# ---------------------------------------------------------------
# «Escribo»: consignas de escritura (producción escrita, NAP)
#   min = cantidad mínima de palabras para poder enviar
#   Los textos los lee y los devuelve la docente desde el panel (sección «Escritos»).
# ---------------------------------------------------------------
def _w(id, titulo, e, nivel, consigna, minimo):
    return {"id": id, "titulo": titulo, "e": e, "nivel": nivel, "consigna": consigna, "min": minimo, "base": True}

CONSIGNAS = [
    _w("esc-nombre", "Me presento", "👋", 1, "Escribí tu nombre y algo que te guste hacer.", 3),
    _w("esc-mascota", "Mi animal favorito", "🐶", 1, "Escribí cuál es tu animal favorito y cómo es.", 3),
    _w("esc-cartel", "Un cartel para el aula", "📋", 1, "Escribí un cartel para la puerta del aula. Por ejemplo: «Bienvenidos a primer grado».", 2),
    _w("esc-bobi", "¿Qué encontró Bobi?", "⚽", 1, "Leíste «Bobi y la pelota». Escribí qué encontró Bobi en el jardín y qué hizo después.", 4),
    _w("esc-final", "Otro final para Tita", "🐢", 2, "Inventá otro final para el cuento «Tita va a la escuela». Empezá con mayúscula y terminá con punto.", 10),
    _w("esc-invitacion", "Una invitación", "🎉", 2, "Escribí una invitación para tu cumpleaños: a quién invitás, qué día, a qué hora y dónde es la fiesta.", 10),
    _w("esc-receta", "Mi receta favorita", "🍳", 2, "Escribí los pasos para preparar algo rico. Usá palabras como «primero», «después» y «por último».", 12),
    _w("esc-describo", "Describo un animal", "🦙", 2, "Elegí un animal y describilo: cómo es, dónde vive y qué come.", 12),
    _w("esc-carta", "Una carta para alguien especial", "✉️", 3, "Escribí una carta a alguien que quieras. Acordate del saludo, de lo que le querés contar y de la despedida.", 25),
    _w("esc-cuento", "Mi propio cuento", "📖", 3, "Inventá un cuento corto con un personaje, un problema y un final. Usá mayúsculas y puntos.", 30),
    _w("esc-faro", "Renarro «El faro de Martina»", "💡", 3, "Contá con tus palabras qué pasó en «El faro de Martina», en orden: el principio, el problema y el final.", 25),
    _w("esc-noticia", "Una noticia de la escuela", "📰", 3, "Escribí una noticia sobre algo que pasó en tu escuela: qué pasó, cuándo, dónde y quiénes participaron.", 25),
]
CONSIGNAS_POR_ID = {c["id"]: c for c in CONSIGNAS}

# Frases rápidas para la devolución de la docente
DEVOLUCIONES_RAPIDAS = ["¡Muy bien escrito! 👏", "Me encantó tu idea. 💡", "Revisá las mayúsculas al empezar.",
                        "Acordate del punto al terminar cada oración.", "Separá bien las palabras.",
                        "Contá un poquito más: ¿qué pasó después?", "Usá palabras como «primero», «después» y «al final»."]


ACTIVIDADES_BASE = CUENTOS + JUEGOS

# ---------------------------------------------------------------
# Acceso de los chicos: contraseña de 3 dibujos
# ---------------------------------------------------------------
DIBUJOS_CLAVE = ["🍎", "🐶", "⭐", "🚗", "🌸", "🐱", "⚽", "🌙", "🍦"]

# ---------------------------------------------------------------
# Niveles y recompensas
# ---------------------------------------------------------------
XP_NIVEL = 120
NIVELES = [
    {"n": "Semilla", "i": "🌱"}, {"n": "Brote", "i": "🌿"}, {"n": "Árbol", "i": "🌳"},
    {"n": "Brújula", "i": "🧭"}, {"n": "Barco pirata", "i": "🏴‍☠️"}, {"n": "Varita mágica", "i": "🪄"},
    {"n": "Estrella", "i": "🌟"}, {"n": "Leyenda de la Isla", "i": "🏆"},
]

def nivel_de(xp):
    return min(len(NIVELES) - 1, xp // XP_NIVEL)

MEDALLAS = [
    {"id": "m1", "n": "Primer cuento", "i": "📘", "d": "Terminaste tu primer cuento."},
    {"id": "m3", "n": "Lectura constante", "i": "📗", "d": "Terminaste 3 cuentos."},
    {"id": "m6", "n": "Ratón de biblioteca", "i": "📚", "d": "Terminaste 6 cuentos."},
    {"id": "j3", "n": "Juegos de palabras", "i": "🧱", "d": "Completaste 3 juegos de palabras."},
    {"id": "perf", "n": "Actividad perfecta", "i": "🌟", "d": "Ganaste 3 estrellas en una actividad."},
    {"id": "perf3", "n": "Superestrella", "i": "💫", "d": "Ganaste 3 estrellas en 5 actividades."},
    {"id": "rep", "n": "Repaso campeón", "i": "🔁", "d": "Volviste a jugar algo para mejorar."},
    {"id": "t1", "n": "Primera misión", "i": "🎯", "d": "Cumpliste tu primera misión de la seño."},
    {"id": "t5", "n": "Súper responsable", "i": "🎖️", "d": "Cumpliste 5 misiones de la seño."},
] + [
    {"id": "tema-" + k, "n": n, "i": i, "d": f"Respondé bien a la primera 5 veces en «{TEMAS[k]['n']}»."}
    for k, n, i in [
        ("personajes", "Detective de personajes", "🕵️"), ("lugar", "Brújula de lugares", "🧭"),
        ("detalles", "Ojo de águila", "🦅"), ("secuencia", "Orden perfecto", "🧩"),
        ("vocabulario", "Colección de palabras", "📖"), ("emociones", "Leer con el corazón", "💖"),
        ("inferencia", "Mente brillante", "💡"), ("oraciones", "Oraciones bien armadas", "🧱"),
        ("rimas", "Poesía de la isla", "🎵"), ("escritura", "Letra estrella", "✏️"),
        ("silabas", "Palmas de oro", "👏"), ("completar", "Detective de oraciones", "📌"),
        ("sinonimos", "Magia de las palabras", "🔄"), ("ortografia", "Escudo de la ortografía", "🖍️"),
        ("familias", "Árbol de palabras", "🌳"), ("acentuacion", "Oído de oro", "📢"),
        ("clases", "Etiquetas expertas", "🏷️"),
    ]
]
MEDALLAS_POR_ID = {m["id"]: m for m in MEDALLAS}

# ---------------------------------------------------------------
# Catálogo del avatar
#   precio: monedas · nivel: nivel mínimo · medalla: medalla necesaria
#   Lo que tiene precio 0 y no pide nada es gratis desde el inicio.
#   Criterio: todo lo que sirve para que el avatar «se parezca a mí» (piel, peinado, color de pelo natural,
#   ojos, boca, ropa básica y sus colores, anteojos comunes) es GRATIS. Lo que cuesta monedas o se gana
#   con niveles y medallas son los EXTRAS de fantasía: colores de pelo fantasía, remeras con dibujo, capa,
#   gorros, anteojos de sol, mascotas, fondos y marcos.
# ---------------------------------------------------------------
def _it(cat, v, n, precio=0, nivel=0, medalla=None, **extra):
    d = {"id": f"{cat}:{v}", "cat": cat, "v": v, "n": n, "precio": precio, "nivel": nivel, "medalla": medalla}
    d.update(extra)
    return d

CATEGORIAS_AVATAR = [
    {"id": "piel", "n": "Piel", "i": "🖐️"}, {"id": "pelo", "n": "Peinado", "i": "💇"},
    {"id": "colorPelo", "n": "Color de pelo", "i": "🎨"}, {"id": "ojos", "n": "Ojos", "i": "👀"},
    {"id": "boca", "n": "Boca", "i": "👄"}, {"id": "ropa", "n": "Ropa", "i": "👕"},
    {"id": "colorRopa", "n": "Color de ropa", "i": "🖍️"}, {"id": "gorro", "n": "Gorros", "i": "🎩"},
    {"id": "anteojos", "n": "Anteojos", "i": "👓"}, {"id": "mascota", "n": "Mascotas", "i": "🐾"},
    {"id": "fondo", "n": "Fondos", "i": "🌄"}, {"id": "marco", "n": "Marcos", "i": "🖼️"},
]

CATALOGO = [
    _it("piel", "p1", "Piel 1", color="#ffe0c7"), _it("piel", "p2", "Piel 2", color="#f6c9a0"),
    _it("piel", "p3", "Piel 3", color="#e0a878"), _it("piel", "p4", "Piel 4", color="#c68852"),
    _it("piel", "p5", "Piel 5", color="#9a6338"), _it("piel", "p6", "Piel 6", color="#6e4426"),

    _it("pelo", "corto", "Corto"), _it("pelo", "largo", "Largo"), _it("pelo", "colitas", "Colitas"),
    _it("pelo", "rulos", "Rulos"), _it("pelo", "rodete", "Rodete"),
    _it("pelo", "pelado", "Rapado"), _it("pelo", "punk", "Cresta", 80),

    _it("colorPelo", "negro", "Negro", color="#2b2320"), _it("colorPelo", "castano", "Castaño", color="#6b4226"),
    _it("colorPelo", "rubio", "Rubio", color="#e5b84f"), _it("colorPelo", "colorado", "Colorado", color="#c4532b"),
    _it("colorPelo", "azul", "Azul", 60, color="#3d7be0"), _it("colorPelo", "rosa", "Rosa", 60, color="#f07cb6"),
    _it("colorPelo", "violeta", "Violeta", 60, color="#8d5be0"), _it("colorPelo", "verde", "Verde", 60, color="#36b37e"),

    _it("ojos", "normal", "Normales"), _it("ojos", "felices", "Felices"),
    _it("ojos", "grandes", "Brillantes"), _it("ojos", "guino", "Guiño"),

    _it("boca", "sonrisa", "Sonrisa"), _it("boca", "contenta", "Contenta"),
    _it("boca", "lengua", "Lengua afuera"), _it("boca", "sorpresa", "Sorpresa"),

    _it("ropa", "remera", "Remera"), _it("ropa", "rayas", "Rayada"), _it("ropa", "guardapolvo", "Guardapolvo"),
    _it("ropa", "estrella", "Con estrella", 50), _it("ropa", "corazon", "Con corazón", 50),
    _it("ropa", "rayo", "Con rayo", 60), _it("ropa", "capa", "Capa de héroe", 120),

    _it("colorRopa", "azul", "Azul", color="#3d8bfd"), _it("colorRopa", "rojo", "Rojo", color="#e8505b"),
    _it("colorRopa", "verde", "Verde", color="#3bb273"), _it("colorRopa", "amarillo", "Amarillo", color="#ffc928"),
    _it("colorRopa", "violeta", "Violeta", color="#8f6bd8"), _it("colorRopa", "naranja", "Naranja", color="#ff8a3d"),
    _it("colorRopa", "rosa", "Rosa", color="#ff7eb6"), _it("colorRopa", "negro", "Negro", color="#34384a"),

    _it("gorro", "ninguno", "Sin gorro"), _it("gorro", "gorra", "Gorra", 30), _it("gorro", "mono", "Moño", 30),
    _it("gorro", "flores", "Vincha de flores", 50), _it("gorro", "auriculares", "Auriculares", 70),
    _it("gorro", "mago", "Gorro de mago", 100), _it("gorro", "corona", "Corona", 150),
    _it("gorro", "astronauta", "Casco espacial", 0, medalla="m6"),

    _it("anteojos", "ninguno", "Sin anteojos"), _it("anteojos", "redondos", "Redondos"),
    _it("anteojos", "sol", "De sol", 50), _it("anteojos", "corazon", "Corazones", 80),

    _it("mascota", "ninguna", "Sin mascota"), _it("mascota", "pollito", "Pollito", 40, e="🐣"),
    _it("mascota", "gato", "Gatito", 60, e="🐱"), _it("mascota", "perro", "Perrito", 60, e="🐶"),
    _it("mascota", "tortuga", "Tortuguita", 80, e="🐢"), _it("mascota", "unicornio", "Unicornio", 150, e="🦄"),
    _it("mascota", "dragon", "Dragoncito", 0, medalla="t5", e="🐲"), _it("mascota", "buho", "Búho sabio", 0, nivel=5, e="🦉"),

    _it("fondo", "cielo", "Cielo", c1="#bfe6ff", c2="#8fd0ff"), _it("fondo", "menta", "Menta", c1="#d4f7e4", c2="#9be3bf"),
    _it("fondo", "atardecer", "Atardecer", 40, c1="#ffd36e", c2="#ff8a8a"), _it("fondo", "bosque", "Bosque", 40, c1="#b9f3c2", c2="#3bb273"),
    _it("fondo", "mar", "Mar", 60, c1="#9fe7ff", c2="#2f7fd8"), _it("fondo", "espacio", "Espacio", 100, c1="#7b5bd6", c2="#1d1846"),
    _it("fondo", "arcoiris", "Arcoíris", 150, c1="#ff9a9e", c2="#a1c4fd"),

    _it("marco", "ninguno", "Sin marco"), _it("marco", "plata", "Plata", 0, nivel=2),
    _it("marco", "oro", "Oro", 0, nivel=4), _it("marco", "estrellas", "Estrellas", 0, medalla="perf3"),
    _it("marco", "arcoiris", "Arcoíris", 0, medalla="t1"),
]
CATALOGO_POR_ID = {i["id"]: i for i in CATALOGO}

AVATAR_INICIAL = {"piel": "p2", "pelo": "corto", "colorPelo": "castano", "ojos": "normal", "boca": "sonrisa",
                  "ropa": "remera", "colorRopa": "azul", "gorro": "ninguno", "anteojos": "ninguno",
                  "mascota": "ninguna", "fondo": "cielo", "marco": "ninguno"}
