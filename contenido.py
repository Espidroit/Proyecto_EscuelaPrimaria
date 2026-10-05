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
}

TIPOS = {
    "cuento":    {"n": "Cuentos",          "i": "📚", "tema": None,        "desc": "Leer un cuento y responder preguntas."},
    "oraciones": {"n": "Ordeno oraciones", "i": "🧱", "tema": "oraciones", "desc": "Ordenar palabras para armar oraciones."},
    "rimas":     {"n": "Busco la rima",    "i": "🎵", "tema": "rimas",     "desc": "Encontrar palabras que riman."},
    "palabras":  {"n": "Armo palabras",    "i": "🔤", "tema": "escritura", "desc": "Formar palabras con letras."},
}

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
]

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
    {"n": "Lector Semilla", "i": "🌱"}, {"n": "Lector Brote", "i": "🌿"}, {"n": "Lector Árbol", "i": "🌳"},
    {"n": "Lector Explorador", "i": "🧭"}, {"n": "Lector Pirata", "i": "🏴‍☠️"}, {"n": "Lector Mago", "i": "🪄"},
    {"n": "Lector Estrella", "i": "🌟"}, {"n": "Leyenda de la Isla", "i": "🏆"},
]

def nivel_de(xp):
    return min(len(NIVELES) - 1, xp // XP_NIVEL)

MEDALLAS = [
    {"id": "m1", "n": "Primer cuento", "i": "📘", "d": "Terminaste tu primer cuento."},
    {"id": "m3", "n": "Lector constante", "i": "📗", "d": "Terminaste 3 cuentos."},
    {"id": "m6", "n": "Ratón de biblioteca", "i": "📚", "d": "Terminaste 6 cuentos."},
    {"id": "j3", "n": "Jugador de palabras", "i": "🧱", "d": "Completaste 3 juegos de palabras."},
    {"id": "perf", "n": "Actividad perfecta", "i": "🌟", "d": "Ganaste 3 estrellas en una actividad."},
    {"id": "perf3", "n": "Superestrella", "i": "💫", "d": "Ganaste 3 estrellas en 5 actividades."},
    {"id": "rep", "n": "Repaso campeón", "i": "🔁", "d": "Volviste a jugar algo para mejorar."},
    {"id": "t1", "n": "Primera tarea", "i": "📝", "d": "Terminaste tu primera tarea de la seño."},
    {"id": "t5", "n": "Súper responsable", "i": "🎖️", "d": "Terminaste 5 tareas de la seño."},
] + [
    {"id": "tema-" + k, "n": n, "i": i, "d": f"Respondé bien a la primera 5 veces en «{TEMAS[k]['n']}»."}
    for k, n, i in [
        ("personajes", "Detective de personajes", "🕵️"), ("lugar", "Exploradora de lugares", "🧭"),
        ("detalles", "Ojo de águila", "🦅"), ("secuencia", "Maestro del orden", "🧩"),
        ("vocabulario", "Coleccionista de palabras", "📖"), ("emociones", "Lector de corazones", "💖"),
        ("inferencia", "Gran pensador", "💡"), ("oraciones", "Constructor de oraciones", "🧱"),
        ("rimas", "Poeta de la isla", "🎵"), ("escritura", "Escritor estrella", "✏️"),
    ]
]
MEDALLAS_POR_ID = {m["id"]: m for m in MEDALLAS}

# ---------------------------------------------------------------
# Catálogo del avatar
#   precio: monedas · nivel: nivel mínimo · medalla: medalla necesaria
#   Lo que tiene precio 0 y no pide nada es gratis desde el inicio.
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
    _it("pelo", "rulos", "Rulos", 40), _it("pelo", "rodete", "Rodete", 40),
    _it("pelo", "punk", "Cresta", 80), _it("pelo", "pelado", "Rapado", 20),

    _it("colorPelo", "negro", "Negro", color="#2b2320"), _it("colorPelo", "castano", "Castaño", color="#6b4226"),
    _it("colorPelo", "rubio", "Rubio", color="#e5b84f"), _it("colorPelo", "colorado", "Colorado", color="#c4532b"),
    _it("colorPelo", "azul", "Azul", 60, color="#3d7be0"), _it("colorPelo", "rosa", "Rosa", 60, color="#f07cb6"),
    _it("colorPelo", "violeta", "Violeta", 60, color="#8d5be0"), _it("colorPelo", "verde", "Verde", 60, color="#36b37e"),

    _it("ojos", "normal", "Normales"), _it("ojos", "felices", "Felices"),
    _it("ojos", "grandes", "Brillantes", 30), _it("ojos", "guino", "Guiño", 30),

    _it("boca", "sonrisa", "Sonrisa"), _it("boca", "contenta", "Contenta"),
    _it("boca", "lengua", "Lengua afuera", 30), _it("boca", "sorpresa", "Sorpresa", 30),

    _it("ropa", "remera", "Remera"), _it("ropa", "rayas", "Rayada", 40),
    _it("ropa", "estrella", "Con estrella", 50), _it("ropa", "corazon", "Con corazón", 50),
    _it("ropa", "rayo", "Con rayo", 60), _it("ropa", "capa", "Capa de héroe", 120),
    _it("ropa", "guardapolvo", "Guardapolvo", 0, nivel=2),

    _it("colorRopa", "azul", "Azul", color="#3d8bfd"), _it("colorRopa", "rojo", "Rojo", color="#e8505b"),
    _it("colorRopa", "verde", "Verde", color="#3bb273"), _it("colorRopa", "amarillo", "Amarillo", color="#ffc928"),
    _it("colorRopa", "violeta", "Violeta", 20, color="#8f6bd8"), _it("colorRopa", "naranja", "Naranja", 20, color="#ff8a3d"),
    _it("colorRopa", "rosa", "Rosa", 20, color="#ff7eb6"), _it("colorRopa", "negro", "Negro", 20, color="#34384a"),

    _it("gorro", "ninguno", "Sin gorro"), _it("gorro", "gorra", "Gorra", 30), _it("gorro", "mono", "Moño", 30),
    _it("gorro", "flores", "Vincha de flores", 50), _it("gorro", "auriculares", "Auriculares", 70),
    _it("gorro", "mago", "Gorro de mago", 100), _it("gorro", "corona", "Corona", 150),
    _it("gorro", "astronauta", "Casco espacial", 0, medalla="m6"),

    _it("anteojos", "ninguno", "Sin anteojos"), _it("anteojos", "redondos", "Redondos", 30),
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
