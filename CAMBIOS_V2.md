# CAMBIOS_V2.md — Qué cambió de la versión 1 a la versión 2

Documento de trazabilidad metodológica. Explica, con honestidad, cada cambio de
fórmula o de criterio respecto a la v1 (resultados en `salidas_v1/`), por qué se
hizo y qué efecto tuvo. La v1 **no se borró**; queda como línea base.

---

## 1. Normalización de etiquetas (corrige el bug de `Kiosk`)

- **Antes (v1):** las etiquetas se clasificaban con su valor crudo. `shop=Kiosk`
  (con mayúscula) no coincidía con ninguna regla y caía en "neutral", así que
  corregir la errata a `shop=kiosk` parecía "el barrio se tradicionaliza". De 296
  mutaciones de la v1, 151 eran ruido de este tipo.
- **Ahora (v2):** `normalizar_tags()` pasa todos los valores a minúsculas, quita
  espacios y los vuelve `_` antes de clasificar. `shop=Kiosk` y `shop=kiosk` son
  lo mismo. Un cambio entre ambos ya no es mutación: es **corrección**.
- **Nuevo:** categoría `generico` para `shop=yes`, `amenity=yes`, `office=yes`,
  `craft=yes` (pero `shop=general` sigue siendo tradicional). Se trata como
  "no clasificable" (None) en todas las variantes.

## 2. Nueva tipología de eventos (el corazón de la v2)

- **Antes:** solo tres tipos útiles (`mutacion`, `eliminacion`, `desetiquetado`)
  y una bandera `evidencia_fuerte`. Mezclaba limpieza de datos con cambio real.
- **Ahora:** cada contribución recibe **un** tipo:
  `creacion`, `etiquetado`, `especificacion`, `correccion`, `mutacion`,
  `relevo`, `cierre`, `eliminacion`. La bandera se renombró a **`cambio_real`**
  y la constante es `CAMBIO_REAL = (mutacion, relevo, cierre, reemplazo)`.
- **Nuevos criterios:**
  - `especificacion`: `generico → X`, o solo se agregó/cambió `cuisine` sin
    cambiar el `name`. Es refinamiento del dato, **no** cambio del territorio.
  - `correccion`: la etiqueta cambió pero normaliza igual (errata).
  - `relevo`: el **mismo objeto** cambia de `name` de forma sustancial
    (`rapidfuzz.token_sort_ratio < 60` tras normalizar sin tildes ni palabras
    vacías). Captura "un negocio nuevo ocupó el lugar", que la v1 no veía.
  - `cierre`: el objeto pasa a `disused:`/`was:`/`abandoned:`/`vacant` o pierde
    la etiqueta comercial pero sigue existiendo.
- Columnas nuevas en los eventos: `nombre_antes`, `nombre_despues`,
  `fecha_declarada`.

## 3. Reemplazo espacial (lo que de verdad hacen los mapeadores)

- **Antes:** no existía. La v1 no veía el patrón más común: borrar el nodo viejo
  y crear uno nuevo cerca.
- **Ahora (`huellas/reemplazos.py`):** un comercio A sale (cierre/eliminación) y
  B aparece **≤ 25 m** y entre **−3 y +24 meses**. Emparejamiento voraz 1‑a‑1
  (por distancia, luego por tiempo). Se descartan **redibujos** (nombres
  parecidos, `ratio ≥ 80`, o misma etiqueta sin nombres) y se marcan las
  **ediciones masivas** (changeset con > 50 objetos comerciales), que no cuentan
  para el ITCO. Parámetros en `config.yaml → reemplazo`. Sensibilidad obligatoria
  (radios 15/25/40 m × ventanas 12/24/36 meses) en `sensibilidad_reemplazo.csv`.

## 4. ITCO v2 y separación mirada / cambio real

- **Fórmula del ITCO: igual que la v1** (dirección × percentil de velocidad),
  pero calculada **solo con eventos de cambio real** (mutación, relevo, cierre,
  reemplazo). Antes se calculaba sobre todo cambio de categoría, incluido el
  ruido de mapeo.
- **Nuevo `indice_mirada`:** la misma fórmula aplicada **solo a creaciones y
  etiquetados**. Mide *qué decide mapear la gente*; **no es gentrificación** y así
  se rotula. Sirve para el bloque de desigualdad sociodigital.
- **Se eliminó el "ITCO estricto"** de la v1 (quedó superado por la nueva
  tipología). Se conserva la columna **`itco_v1`** para comparar v1 ↔ v2.
- `fecha_declarada`: si el objeto trae `start_date`/`opening_date`/`check_date`
  se guarda y se reporta el porcentaje; no se cambia la fecha del evento.
- La confianza se calcula ahora sobre eventos de cambio real.

## 5. Agregación por comuna (C3, C10)

- **Nuevo:** el ITCO v2 se calcula **también por comuna** (`itco_por_comuna.csv`,
  `mapa_itco_comunas.png`), para que los sectores populares, donde el barrio es
  demasiado fino, tengan tamaño de muestra. Los corregimientos cuentan como
  unidades propias.
- Tabla **"Barrios prometidos"** en `resumen.md`. **Bug corregido:** un barrio sin
  contribuciones aparece con **0** e "insuficiente", nunca "sin datos".

## 6. Turismo, corregido (C-turismo)

- "aperturas" → **"apariciones en OSM"** (una aparición es la fecha de mapeo, no
  necesariamente la de apertura; se dice explícitamente).
- Nueva **`proporcion_turismo`** = apariciones turísticas / todas las creaciones
  de comercio del año, para separar el crecimiento del fenómeno del crecimiento
  del mapa (`turismo_normalizado.png`).
- `tourism=apartment` (proxy de renta corta tipo Airbnb) se separa de hostales y
  hoteles; ya no se dice "Airbnb" para hablar de hostales.
- Se reporta usuarios distintos y peso del principal usuario/changeset por año
  (`turismo_dominancia.csv`), para mostrar que no fue una importación.

## 7. Filtro de descarga (ciclo de vida)

- El filtro ohsome ahora incluye `disused:shop/amenity`, `was:shop/amenity` y
  `abandoned:shop/amenity`, necesarias para ver cierres. Al cambiar el filtro, la
  descarga vieja quedó incompleta: `data/raw` se mueve a `data/raw_v1` y se vuelve
  a descargar.

## 8. Validación honesta (C6)

- `muestra_validacion.csv` **nueva**: 40 filas estratificadas, **solo comercios**
  (sin oficinas institucionales), sin revelar el estrato esperado (va en
  `muestra_validacion_clave.csv`). Comando `python -m huellas validar` calcula la
  precisión por tipo con intervalo de **Wilson**.

---

## Nota de rendimiento (no cambia resultados)

El emparejamiento de reemplazos se vectorizó (filtro por caja en grados +
haversine vectorizado): de ~133 s a ~1,4 s sobre los datos reales de Medellín.
El resultado es idéntico; solo cambia la velocidad.

Cualquier otro cambio de criterio futuro debe anotarse aquí.

---

## Ronda 2: ajustes antes de la validación

Revisión independiente de los resultados v2, hecha caso por caso sobre `eventos.csv` y
`reemplazos.csv`. Quedaban cuatro fuentes de falsos positivos y una de falsa precisión.

### R1. Mutación con el mismo nombre = `reetiquetado` (no es cambio real)
- **Problema:** 6 de las 11 "sustituciones" de Medellín eran el mismo negocio con otra
  etiqueta: Tostao' (`bakery → cafe`, 3 veces), Café Revolución, Olala (`general → gift`) y
  "EDIFICIO" (`pawnbroker → hotel`).
- **Ahora:** si la categoría cambia pero el nombre es el mismo (mismo nombre base, o
  `token_set_ratio ≥ 85`), el tipo es `reetiquetado` y no cuenta como cambio real.

### R2. Relevo: menos falsos positivos
- **Problema:** en una muestra de 25 relevos, unos 10 no eran un negocio nuevo: el nombre
  solo se acortó ("D1 pilarica" → "D1", "Makro San Juan" ↔ "Makro") o era genérico
  ("Carnes" → "Carnicería Roja", "Papeleria" → "Miselanea").
- **Ahora:** solo es relevo si los nombres son claramente distintos: ninguno es genérico
  (lista `NOMBRES_GENERICOS` en `historia.py`), ninguno contiene al otro y
  `token_set_ratio < 90`, además del `token_sort_ratio < 60` de antes.

### R3. Reemplazo: redibujos que se escapaban
- **Problema:** "Centro Comercial Unicentro" → "Unicentro" o "Tienda" → "Mini Mercado"
  contaban como reemplazos válidos.
- **Ahora:** para decidir si es redibujo, los nombres se comparan sin palabras de tipo de local
  ("centro comercial", "hotel", "tienda"…), con el mayor de `token_sort_ratio` y
  `token_set_ratio` y aceptando que un nombre contenga al otro. Si a uno le falta el nombre o
  es genérico y la etiqueta es la misma, es redibujo.
- **Columna nueva `mismo_changeset`:** A y B en la misma edición. No se descarta, porque un
  mapeador en terreno que borra el local viejo y crea el nuevo es evidencia legítima. Se
  reporta en `sensibilidad_reemplazo.csv` (`n_validos_mismo_changeset`).

### R4. Intervalo de confianza del ITCO (bootstrap)
- **Problema:** un cálculo rápido mostró que en 17 de los 19 barrios con ITCO v2 la dirección
  no se distinguía de cero. Las Acacias (+42) se apoyaba en 5 eventos.
- **Ahora:** IC 95 % por bootstrap (2.000 remuestreos de los eventos de cambio real, semilla
  fija en `config.yaml → itco`). Columnas `itco_ic_bajo`, `itco_ic_alto`, `direccion_ic_*` y
  `direccion_clara` (el IC de la dirección no incluye 0), por barrio y por comuna.
- **Mapas:** los barrios y comunas sin dirección clara se pintan aclarados y con borde
  punteado. El resumen dice cuántos tienen dirección clara.

### R5. Taxonomía: pizza y burger pasan a `ambiguo`
- En Medellín y en CDMX hay pizzerías y hamburgueserías populares en todos los barrios; no
  son señal de gentrificación. Se quitaron de la cocina de transformación en las dos
  taxonomías. Un restaurante `pizza;italian` sigue siendo de transformación por `italian`.

### Otros
- **Validación:** la muestra ya no muestra la columna `tipo` (delataba los controles
  negativos; queda en la clave) y trae el enlace al historial del local **anterior** en los
  reemplazos. Los `reetiquetado` entran como controles negativos.
- **Figura nueva `embudo.png`:** de todas las ediciones a las sustituciones verificadas.
- **Resumen:** lista completa de sustituciones con nombres, IC 95 % en las tablas, y
  "Comercios mapeados hoy" ahora incluye los neutrales (antes solo contaba los de
  transformación y tradicionales, y por eso Barrio Colombia aparecía con 3).
- **`requirements.txt`:** se agregaron `rapidfuzz` y `ohsome`, que faltaban.
