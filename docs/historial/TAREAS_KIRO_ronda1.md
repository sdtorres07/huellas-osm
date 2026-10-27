# TAREAS_KIRO.md: Huellas de la gentrificación, versión 2

Este documento es la especificación completa del trabajo. Léelo entero antes de tocar código.
El proyecto es una charla de 20 minutos para **State of the Map LATAM 2026 (Ciudad de México)**.
La fecha límite es el **viernes 17 de octubre de 2026**. El público son mapeadores de OpenStreetMap
expertos, que van a revisar los datos con lupa. Por eso **la honestidad metodológica es más
importante que un resultado espectacular**. Nunca maquilles un número para que la historia
quede mejor: si un resultado es débil, se reporta como débil.

---

## 0. Por qué existe la versión 2 (diagnóstico de la v1)

La v1 (resultados en `salidas_v1/`) tiene fallas que un mapeador detecta en minutos:

1. **La "evidencia fuerte" era sobre todo limpieza de etiquetas.** De 296 mutaciones, 151
   no cambian la etiqueta principal:
   - `shop=Kiosk → shop=kiosk` (63): la taxonomía distingue mayúsculas, así que `Kiosk`
     contaba como neutral y corregir la errata parecía "el barrio se tradicionaliza".
   - `amenity=restaurant → amenity=restaurant` (52): solo se agregó `cuisine`.
   - `shop=yes → shop=convenience` (45): alguien especificó el tipo.
   Por eso el ITCO estricto contradice al base (Bolivariana +18 frente a −56).
2. **Solo hubo 7 sustituciones tradicional → transformación**, y 4 son
   `shop=bakery → amenity=cafe` (probablemente re-etiquetado del mismo negocio).
3. **El 79 % de los eventos son creaciones**, es decir, fechas de mapeo y no de apertura.
   El ITCO base mide sobre todo *qué mapea la gente*, no *qué cambió*.
4. **Los mapeadores reales no registran los cambios de local como mutaciones.** Normalmente
   borran el nodo viejo y crean uno nuevo, o cambian el `name` sin tocar la categoría. La v1
   no veía ninguno de los dos casos.
5. **Las "aperturas" turísticas eran fechas de mapeo** y no estaban normalizadas por la
   actividad total de mapeo.
6. **Barrios prometidos sin dato:** Barrio Colombia y Prado quedan insuficientes y Loreto
   sin datos. El nivel de barrio es demasiado fino para los sectores populares.
7. **La muestra de validación** incluía objetos que no son comercio (por ejemplo, una
   institución educativa) y nunca se llenó.

---

## 1. Lo que la charla prometió (todo debe quedar cumplido)

| # | Compromiso de la propuesta | Cómo se cumple en v2 | Tarea |
|---|---|---|---|
| C1 | Usar **ohsome API y ohsome-py** | API v2 por HTTP (ya existe) **y** un script con `ohsome-py` sobre la API v1 (vigente hasta el 30-nov-2026) para las series temporales | T8 |
| C2 | Series temporales de **amenity, shop y craft** por barrio | `series_claves.csv` + figura, por comuna y barrios de estudio | T8 |
| C3 | Comparar **El Poblado y Laureles con sectores populares y periféricos** | ITCO también **por comuna**, para que los sectores populares tengan valor | T6 |
| C4 | **Python + QGIS**, mapas temáticos comparativos | Estilos `.qml` + script PyQGIS que arma el proyecto y exporta los mapas | T10 |
| C5 | **ITCO**: qué tan rápido y en qué dirección cambia un barrio | ITCO v2 calculado sobre evidencia de cambio real | T5 |
| C6 | **Calibrar con casos reales y reconocibles** | Casos emblemáticos + muestra de validación lista para Street View o Mapillary | T9 |
| C7 | **Herramienta para comunidades** | Dashboard con ficha por barrio + `KIT_COMUNITARIO.md` | T11 |
| C8 | **100 % replicable**, sin presupuesto | Réplica en **CDMX** con la misma herramienta (solo cambia la configuración) | T12 |
| C9 | **Desigualdades sociodigitales** | Mapa de mapeadores + "puntos ciegos" + (opcional) contraste con estrato | T7 |
| C10 | Barrio Colombia, Loreto, centro histórico | Reportados explícitamente, con su nivel de dato. Si no hay, se dice y se muestra | T6, T9 |

---

## 2. Reglas de trabajo

- **No borres la v1.** `salidas_v1/` se queda intacta para comparar. Los resultados nuevos van a `salidas/`.
- **No cambies la fórmula del ITCO sin documentarlo** en `CAMBIOS_V2.md`.
- **Cada tarea tiene criterios de aceptación.** No pases a la siguiente sin cumplirlos.
- **Pruebas:** cada regla nueva (normalización, relevo, reemplazo, ciclo de vida) lleva una prueba en `tests/`. `python tests/test_basico.py` y `pytest` deben pasar al final.
- **El modo demo** (`python -m huellas demo`) debe seguir funcionando.
- **No subas ni imprimas la API key.** Está en `.env` (el usuario lo copia desde su versión anterior).
- **Si algo falla o no hay datos** (por ejemplo, no hay polígonos de colonias en CDMX), anótalo en `INFORME_KIRO.md` y sigue con lo demás. No inventes datos.
- **Idioma:** código, comentarios, salidas y documentos en español, como el resto del proyecto.

---

## 3. Tareas

### T1. Entorno y línea base (15 min)

1. Crea `.venv`, instala `requirements.txt` y además `ohsome` (ohsome-py), `pytest` y `rapidfuzz`.
2. Verifica que exista `.env` con `OHSOME_API_KEY`. Si no está, **detente y pídelo al usuario**.
3. Corre `python tests/test_basico.py` y `python -m huellas demo`. Ambos deben funcionar antes de cambiar nada.

**Aceptación:** pruebas en verde, demo generado.

---

### T2. Normalización de etiquetas (corrige el bug de `Kiosk`)

En `huellas/taxonomia.py`:

1. Antes de clasificar, normaliza **los valores** de todas las claves relevantes: `strip()`, `lower()` y espacios convertidos en `_` (`"Fast Food"` → `fast_food`). Hazlo en una función `normalizar_tags(tags) -> dict` que reciba y devuelva un dict nuevo (sin mutar el original).
2. **Valores genéricos.** Si la etiqueta principal es genérica (`shop=yes`, `amenity=yes`, `office=yes`, `craft=yes`, `shop=general` NO es genérico porque es una tienda real), la categoría es `"generico"`. Agrégalo a `CATEGORIAS`.
3. En `aplicar_variante`, `"generico"` se trata **como None** (no es comercio clasificable) en todas las variantes.

**Aceptación (pruebas nuevas):**
- `clasificar({"shop": "Kiosk"})` == `clasificar({"shop": "kiosk"})` y es `tradicional`.
- `{"shop": "yes"}` → `generico`; un cambio `shop=yes → shop=convenience` **no** produce mutación (produce `especificacion`, ver T3).

---

### T3. Nueva tipología de eventos (el corazón de la v2)

En `huellas/historia.py`, reescribe `_tipo` y amplía `eventos()`. Cada contribución de un objeto que ya era comercio clasificable se compara con su estado anterior **del mismo objeto** y se le asigna **un** tipo:

| Tipo | Regla | ¿Cuenta como cambio real? |
|---|---|---|
| `creacion` | El objeto aparece (CREATION) | No: es mapeo |
| `etiquetado` | Objeto existente recibe etiqueta comercial | No: es mapeo |
| `especificacion` | `generico → X`, o solo se agregó o cambió `cuisine` **sin** cambio de `name` | **No**: es refinamiento |
| `correccion` | Cambia la etiqueta, pero ambas normalizadas son iguales (`Kiosk → kiosk`) | **No** |
| `mutacion` | Cambia la etiqueta principal normalizada (`clave=valor`) a una categoría distinta | **Sí** |
| `relevo` | **Mismo objeto, el `name` cambia** de forma sustancial (similitud `rapidfuzz.fuzz.token_sort_ratio` < 60 tras normalizar minúsculas y tildes), antes y después son comercio. La categoría puede cambiar o no | **Sí**: un negocio nuevo ocupa el lugar |
| `cierre` | El objeto pasa a `disused:*`, `was:*`, `abandoned:*` o `vacant`, o pierde la etiqueta comercial pero el objeto sigue existiendo | **Sí** |
| `eliminacion` | El objeto se borra (DELETION) | Ambiguo: ver T4 |

Detalles:
- Usa el `name` de `tags` y `tags_before` (o de la contribución previa si no hay `tags_before`). Normaliza el nombre: minúsculas, sin tildes, sin palabras vacías ("la", "el", "de", "restaurante", "cafe", "tienda", "panaderia", "s.a.s", "sas").
- Un cambio `relevo` con `antes=tradicional` y `despues=transformacion` es una **sustitución directa**, la evidencia más fuerte de la charla.
- Si en la **misma** contribución cambian la categoría y el nombre, el tipo es `relevo` (es más informativo que `mutacion`).
- Agrega las columnas `nombre_antes` y `nombre_despues` a los eventos y a `eventos.csv`.
- Constante nueva: `CAMBIO_REAL = ("mutacion", "relevo", "cierre", "reemplazo")`. Reemplaza el uso de `EVIDENCIA_FUERTE` por esta y renombra la columna a `cambio_real`.

**Aceptación (pruebas nuevas, con contribuciones sintéticas):**
- `restaurant` con `cuisine` vacío → `cuisine=sushi`, mismo nombre: `especificacion`.
- `shop=Bakery` → `shop=bakery`: `correccion`.
- `name="Taller Don José", craft=carpenter` → `name="Pergamino Café", amenity=cafe`: `relevo`, tradicional → transformación.
- `shop=hardware` → `disused:shop=hardware`: `cierre`.

---

### T4. Reemplazo espacial (lo que de verdad hacen los mapeadores)

Nuevo módulo `huellas/reemplazos.py`.

Un **reemplazo** es cuando un comercio A sale del mapa (eliminación, cierre o desetiquetado) y aparece un comercio B nuevo **cerca y poco después**:

- Distancia entre A y B ≤ **25 m** (usa haversine o proyección UTM 18N, EPSG:32618).
- B aparece entre **3 meses antes** y **24 meses después** de la salida de A.
- Emparejamiento **uno a uno**: ordena los candidatos por distancia y luego por diferencia de tiempo, y empareja de forma voraz (cada A y cada B se usa una sola vez).
- **Se descarta como "redibujo"** (no es un cambio real) si los nombres normalizados de A y B son similares (`token_sort_ratio` ≥ 80), o si A y B tienen la misma etiqueta y ninguno tiene nombre. En ese caso alguien solo volvió a dibujar el mismo local.
- **Se marca como "edición masiva"** si A o B pertenecen a un changeset con más de 50 objetos comerciales tocados. Se reporta aparte y no cuenta para el ITCO.
- Parámetros (`25`, `3`, `24`, `80`, `50`) en `config.yaml`, en una sección nueva `reemplazo:`.

Salida: los reemplazos se agregan a los eventos con `tipo="reemplazo"`, `antes` = categoría de A, `despues` = categoría de B, la fecha de B, la posición de B, y los nombres y etiquetas de ambos. Agrega también `distancia_m` y `meses_entre`.

**Sensibilidad obligatoria:** recalcula el número de reemplazos con radios de 15, 25 y 40 m y ventanas de 12, 24 y 36 meses. Guárdalo en `salidas/sensibilidad_reemplazo.csv`.

**Aceptación:** pruebas sintéticas para un reemplazo válido, un redibujo descartado y un caso fuera de radio.

---

### T5. ITCO v2

En `huellas/itco.py`:

1. **ITCO** (el principal): igual a la fórmula actual (dirección × percentil de velocidad), pero calculado **solo con eventos de cambio real** (`mutacion`, `relevo`, `cierre`, `reemplazo`).
   - Para `cierre` y `eliminacion` no emparejada: cuentan como salida de su categoría.
   - Mínimo de eventos de cambio real para calcular: `eventos_minimos` (sigue siendo 5).
2. **Índice de mirada** (`indice_mirada`): la fórmula vieja aplicada **solo** a `creacion` y `etiquetado`. Mide *qué decide mapear la gente* en cada barrio. **No es gentrificación** y así se dice en los textos. Sirve para el bloque de desigualdad sociodigital.
3. Elimina el ITCO estricto viejo (queda superado), pero conserva la columna `itco_v1` para comparar.
4. **Fecha real:** si el objeto tiene `start_date`, `opening_date` o `check_date`, guárdalo en una columna `fecha_declarada` y reporta en el informe qué porcentaje de eventos la tiene. No cambies la fecha del evento; solo infórmalo.
5. La confianza sigue igual, pero calculada sobre eventos de cambio real.

**Aceptación:** `itco_por_periodo.csv` con las columnas `itco`, `indice_mirada`, `itco_v1`, `n_cambio_real`, `n_mutacion`, `n_relevo`, `n_cierre`, `n_reemplazo` y `sustituciones_R_a_T` (que ahora suma mutaciones, relevos y reemplazos de tradicional a transformación).

---

### T6. Agregación por comuna (para cumplir C3 y C10)

- Calcula todo el ITCO v2 **también por comuna** (usa el campo `nombre_comuna` del GeoJSON de barrios). Los 5 corregimientos cuentan como unidades propias.
- Salida: `itco_por_comuna.csv` y `figuras/mapa_itco_comunas.png`.
- Agrega a `config.yaml` → `barrios_estudio`:
  - `transformacion_esperada`: agrega **La Candelaria** (centro histórico), **Boston** y **Los Conquistadores**.
  - `control`: agrega **Versalles No. 1** y **Llanaditas** (populares con datos).
- En `resumen.md`, una tabla **"Barrios prometidos en la propuesta"** con Barrio Colombia, Loreto, Prado y La Candelaria, mostrando, aunque no haya ITCO: número de comercios mapeados hoy, número de mapeadores, eventos de cambio real y una frase en lenguaje simple ("OSM casi no ve este barrio: 3 comercios mapeados y 2 mapeadores").
- **Bug:** si un barrio no tiene ninguna contribución, debe aparecer con 0 (no con "–" ni "sin datos"). Loreto debe salir con sus números, aunque sean cero.

---

### T7. Desigualdad sociodigital (C9)

1. `figuras/mapa_mapeadores.png`: se mantiene.
2. Nuevo `figuras/puntos_ciegos.png`: barrios con **población residente alta y menos de 3 mapeadores de comercio**. Si no hay población disponible, usa área urbana del barrio como aproximación y dilo en la leyenda.
3. Nuevo `figuras/mirada_vs_cambio.png`: un diagrama de dispersión por barrio con `indice_mirada` (x) contra `itco` (y). Etiqueta los barrios de estudio. La idea es mostrar si *lo que se mapea* y *lo que cambia* son lo mismo o no.
4. **Opcional:** si encuentras en datos abiertos de Medellín el **estrato socioeconómico predominante por barrio** (busca en `medata.gov.co` o en el portal GeoMedellín), haz `figuras/mapeadores_vs_estrato.png` (mapeadores por cada 1.000 comercios según estrato). Ese dato institucional **solo se usa para contrastar, nunca como insumo del ITCO**, y así se rotula. Si no lo encuentras en 30 minutos, sáltalo y anótalo.

---

### T8. Series temporales con ohsome-py (C1 y C2)

Nuevo script `huellas/series_ohsome.py` y comando `python -m huellas series`.

1. Con **ohsome-py** (`from ohsome import OhsomeClient`) y la **API v1** (sin API key), pide `elements/count/groupBy/boundary` anual de 2010 a 2026 para tres filtros: `amenity=* and type:node`, `shop=* and type:node`, `craft=* and type:node`. Los límites son los polígonos de las **comunas** (y los barrios de estudio, si el tiempo lo permite).
2. Si ohsome-py o la v1 fallan, haz lo mismo con la v2 por HTTP (ya existe `serie_estadistica` en `api.py`) y anota la razón.
3. Salidas: `series_claves.csv` (unidad, clave, año, conteo) y `figuras/series_claves.png` (tres paneles pequeños, uno por clave, con las comunas de estudio resaltadas y el resto en gris).
4. **Normaliza** también por el total de objetos con cualquiera de esas tres claves en la ciudad ese año (proporción), para separar crecimiento del mapa de crecimiento real.

---

### T9. Casos emblemáticos y validación (C6)

1. `salidas/casos_emblematicos.csv`: los **25 mejores casos** de sustitución tradicional → transformación (relevos, reemplazos y mutaciones), ordenados por calidad de la evidencia (tienen nombre antes y después > están en un barrio de estudio > son recientes). Columnas: barrio, comuna, tipo, fecha, antes (etiqueta y nombre), después (etiqueta y nombre), distancia_m, link al historial OSM de **ambos** objetos, link a Street View, link a Mapillary (`https://www.mapillary.com/app/?lat=..&lng=..&z=19`).
2. `salidas/muestra_validacion.csv` **nueva**:
   - 40 filas, **solo eventos de cambio real** y **solo comercios** (categorías transformación, tradicional o neutral con `shop`/`amenity`/`craft`). Nada de oficinas institucionales.
   - Estratificación: 15 sustituciones tradicional → transformación, 10 en sentido contrario, 10 de otros cambios reales y 5 **controles negativos** (`correccion` o `especificacion`, que deberían salir "no hubo cambio real").
   - Las columnas del CSV no revelan el estrato al validador (pon el estrato en una hoja aparte, `muestra_validacion_clave.csv`).
   - Columnas para llenar: `verificado (si/no/no_se)`, `fecha_aprox_cambio_real`, `notas`.
3. `VALIDACION.md`: instrucciones de una página para el usuario (cómo usar las fechas anteriores de Street View, qué cuenta como "sí"), y el script `python -m huellas validar` que, cuando el CSV esté lleno, calcula la **precisión** por tipo de evento con un intervalo de confianza (Wilson) y escribe `salidas/resultado_validacion.md`.

**Esta tarea no incluye llenar la validación.** La hace el usuario. Tú dejas todo listo.

---

### T10. QGIS (C4)

1. Estilos en `qgis/`: `itco.qml` (graduado, cortes −100, −50, −20, −5, 5, 20, 50, 100, rampa divergente azul–gris–rojo, gris rayado para nulos), `mapeadores.qml` y `eventos.qml` (categorizado por `tipo`, solo cambio real visible por defecto).
2. `qgis/armar_proyecto.py`: script para la consola Python de QGIS que carga `barrios_itco.geojson`, `comunas_itco.geojson` y `eventos.geojson`, aplica los estilos, agrega un mapa base OSM (XYZ) y exporta **dos composiciones comparativas** lado a lado a PNG de 300 dpi: (a) ITCO v1 frente a ITCO v2, y (b) mirada frente a cambio real.
3. Actualiza `GUIA_QGIS.md` con los pasos.
4. Si QGIS no está instalado en la máquina, **no lo instales**. Deja el script y anota en el informe que falta correrlo.

---

### T11. Kit comunitario y dashboard (C7)

1. Actualiza `huellas/dashboard.py`: al hacer clic en un barrio se abre una **ficha** con su ITCO, índice de mirada, número de mapeadores, línea de tiempo de eventos de cambio real (con links al historial OSM) y una frase en lenguaje simple. Debe funcionar como un solo HTML sin servidor. Que el archivo pese **menos de 10 MB**: simplifica las geometrías (tolerancia ~0,00005) si hace falta.
2. `KIT_COMUNITARIO.md`, máximo 2 páginas, para una junta de acción comunal o un colectivo, sin jerga:
   - qué dice y qué **no** dice el ITCO;
   - cómo leer la ficha de su barrio;
   - cómo **mapear su barrio** para que el mapa vea lo que pasa: usar `disused:shop=*` cuando un local cierra, no borrar y crear de nuevo sino cambiar `name` y etiquetas sobre el mismo punto, agregar `check_date` y `opening_date`, mapear el comercio popular (tiendas, talleres, ventas);
   - cómo replicarlo en otra ciudad.

---

### T12. Réplica en Ciudad de México (C8, el momento "wow" para el público de CDMX)

1. Crea `config_cdmx.yaml` y `taxonomia_cdmx.yaml`. La taxonomía es la misma, con estos agregados: en cocina tradicional, `mexican`, `tacos`, `taco`, `regional`, `antojitos`, `fonda`, `tortas`, `seafood`; en tienda tradicional, `shop=tortilleria` y `shop=abarrotes`, si aparecen.
2. Área: la **alcaldía Cuauhtémoc** completa. Unidades: **colonias** del portal de datos abiertos de la CDMX (`datos.cdmx.gob.mx`, conjunto "Colonias de la Ciudad de México"). Si no está disponible, usa los límites `boundary=administrative` / `place=neighbourhood` de OSM y anótalo.
3. Barrios de estudio: `transformacion_esperada`: Roma Norte, Roma Sur, Condesa, Hipódromo, Hipódromo Condesa, Juárez; `control`: Morelos, Guerrero, Centro (y las que tengan dato suficiente).
4. El CLI ya acepta `--config`, pero `cargar()` tiene fija la ruta `taxonomia.yaml` y la carpeta de datos crudos probablemente también es fija. Agrega a la configuración las claves `taxonomia:` y `datos_crudos:` (con los valores actuales por defecto para Medellín), y usa `data/raw_cdmx/` para CDMX. Después corre `descargar`, `procesar` y `turismo` con `--config config_cdmx.yaml`. Salidas en `salidas_cdmx/`.
5. **Aceptación:** `salidas_cdmx/resumen.md`, `mapa_itco.png`, `turismo_aperturas_normalizado.png` y `mapa_mapeadores.png`. Si el dato es débil, se reporta igual.

---

### T13. Turismo, corregido

En `huellas/turismo.py`:
1. Renombra todo lo que diga "aperturas" a **"apariciones en OSM"** (en columnas, títulos y textos).
2. Agrega `proporcion_turismo` = apariciones turísticas / todas las creaciones de comercio de ese año, en `turismo_ciudad.csv`, y una figura nueva `turismo_normalizado.png` con las dos series (absoluta y proporción).
3. Reporta cuántos usuarios distintos y qué peso tiene el principal usuario y changeset por año (para mostrar que no fue una importación).
4. Separa **`tourism=apartment`** (proxy de renta corta tipo Airbnb) de hostales y hoteles en el texto y los gráficos. No digas "Airbnb" para referirte a hostales.

---

### T14. Correr todo con datos reales

1. El filtro de descarga debe incluir ahora las claves de ciclo de vida: `disused:shop`, `disused:amenity`, `was:shop`, `was:amenity`, `abandoned:shop` y `abandoned:amenity`. Al cambiar el filtro **hay que volver a descargar**: mueve `data/raw/` a `data/raw_v1/` y corre `python -m huellas descargar`.
2. `python -m huellas procesar`, `turismo`, `series`, `dashboard`.
3. Medellín y CDMX.

---

### T15. Informe final: `INFORME_KIRO.md`

Es el documento que yo (Claude) voy a leer para validar y hacer las diapositivas. Debe tener:

1. Qué se hizo, tarea por tarea, con ✅ / ⚠️ / ❌ y la razón de cada ⚠️ o ❌.
2. **Tabla comparativa v1 → v2:** sustituciones T←R, eventos de cambio real por tipo, barrios con ITCO, correlación de rangos ITCO v1 frente a v2, y los 10 primeros barrios en cada versión.
3. Conteos de eventos por tipo (`creacion`, `especificacion`, `correccion`, `mutacion`, `relevo`, `cierre`, `reemplazo`, redibujos descartados, ediciones masivas).
4. Las 10 transiciones `etq_antes → etq_despues` más frecuentes **dentro de cambio real** (para verificar que ya no hay ruido de erratas).
5. Resultados de la sensibilidad del reemplazo (radio y ventana).
6. Los 5 casos emblemáticos más fuertes, con nombre antes y después.
7. CDMX: los números principales.
8. Lo que no se pudo hacer y lo que queda pendiente para el usuario.
9. **Cualquier cosa sospechosa que veas en los datos.** Sé crítico.

---

## 4. Qué entregar (el zip de regreso)

El usuario me va a devolver un zip. Debe contener **todo el proyecto excepto** `.venv/`, `.env`, `__pycache__/`, `data/raw*/` y `*.gpkg`. Antes de comprimir, verifica que `.env` **no** esté incluido.

Incluye obligatoriamente: `INFORME_KIRO.md`, `CAMBIOS_V2.md`, `salidas/` (sin el `.gpkg`), `salidas_cdmx/`, `salidas_v1/`, el código y las pruebas.

## 5. Orden sugerido y prioridades

Si el tiempo no alcanza, este es el orden de importancia:

1. **Imprescindible:** T1, T2, T3, T4, T5, T9, T13, T14 (Medellín), T15.
2. **Muy importante:** T6, T7, T8, T12.
3. **Deseable:** T10, T11.
