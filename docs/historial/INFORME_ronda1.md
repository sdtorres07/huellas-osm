# INFORME_KIRO.md — Huellas de la gentrificación, versión 2

> Documento de entrega para validación y diapositivas. Se escribe de forma
> incremental mientras avanzan las tareas. La honestidad metodológica manda:
> si un número es débil, aquí se reporta como débil.

Fecha de ejecución: octubre de 2026
Entorno: Windows, Python 3.13, `.venv` local.

---

## 0. Estado de la API key

✅ **Resuelto.** El usuario entregó la `OHSOME_API_KEY`, que se guardó en `.env`
(ignorado por git). Todo se corrió **con datos reales**: Medellín (T14) y la
réplica de CDMX (T12). Las series (T8) usan la API v1 de ohsome, que no necesita
clave. El `.env` **no** se incluye en el zip de entrega (verificado).

---

## Estado por tarea

| Tarea | Estado | Nota |
|---|---|---|
| T1 Entorno y línea base | ✅ | `.venv` creado; instaladas dependencias + `ohsome`, `pytest`, `rapidfuzz`. `pytest` = **7/7 en verde**. `python -m huellas demo` corre de principio a fin (EXIT=0). `.env` **no existe** → T14 queda a la espera de la key. |
| T2 Normalización de etiquetas | ✅ | `normalizar_tags()` (strip, minúsculas, espacios→`_`, no muta el original). Nueva categoría `generico` para `shop/amenity/office/craft=yes` (y `shop=general` sigue siendo tradicional). `generico` se trata como None en todas las variantes. Pruebas nuevas: `test_bug_kiosk`, `test_valores_genericos`, `test_normalizar_tags_no_muta`. **10/10 en verde.** |
| T3 Tipología de eventos | ✅ | `historia.py` reescrito: `_tipo` asigna uno de `creacion/etiquetado/especificacion/correccion/mutacion/relevo/cierre/eliminacion`. `CAMBIO_REAL=(mutacion,relevo,cierre,reemplazo)`. Columna renombrada `evidencia_fuerte`→`cambio_real`. Nuevas columnas `nombre_antes`, `nombre_despues`, `fecha_declarada`. Relevo por `rapidfuzz.token_sort_ratio < 60` tras normalizar nombre (sin tildes/puntuación/palabras vacías). `eventos()` ahora clasifica **todas** las contribuciones comerciales, no solo cambios de categoría. Pruebas nuevas: especificación (cuisine), corrección (Kiosk), relevo T←R, cierre, mutación sin nombre, genérico→específico. **16/16 en verde.** Demo v2 EXIT=0. |
| T4 Reemplazo espacial | ✅ | Nuevo módulo `huellas/reemplazos.py`. Empareja A (sale: cierre/eliminación) con B (aparece: creación comercial) a ≤25 m (haversine) y entre −3 y +24 meses. Emparejamiento voraz 1-a-1 (distancia, luego tiempo). Descarta **redibujos** (nombres `token_sort_ratio ≥ 80`, o misma etiqueta y sin nombre) y marca **ediciones masivas** (changeset con > 50 objetos comerciales). Parámetros en `config.yaml → reemplazo`. Barrido de sensibilidad (radios 15/25/40 × ventanas 12/24/36) → `sensibilidad_reemplazo.csv`. Integrado al ITCO como `tipo="reemplazo"`. Pruebas: válido, redibujo descartado, fuera de radio, sensibilidad. **20/20 en verde.** |
| T5 ITCO v2 | ✅ | `huellas/itco.py` reescrito. **ITCO** se calcula solo con cambio real (mutación/relevo/cierre/reemplazo). **Índice de mirada** (`indice_mirada`) con la misma fórmula pero sobre creaciones+etiquetados (no es gentrificación). Se elimina el ITCO estricto; se conserva `itco_v1` para comparar. `fecha_declarada` por evento + % reportado en el resumen. `itco_por_periodo.csv` trae todas las columnas pedidas: `itco`, `indice_mirada`, `itco_v1`, `n_cambio_real`, `n_mutacion`, `n_relevo`, `n_cierre`, `n_reemplazo`, `sustituciones_R_a_T`. |
| T6 Agregación por comuna | ✅ | ITCO v2 también por comuna (`_itco_por_comuna` reusa `calcular_periodo` tratando la comuna como unidad; los 5 corregimientos son unidades propias). Salidas: `itco_por_comuna.csv` y `figuras/mapa_itco_comunas.png` (cada barrio pintado con el ITCO de su comuna). `config.yaml` → `barrios_estudio` ampliado (La Candelaria, Boston, Los Conquistadores en transformación; Versalles No. 1, Llanaditas en control). Tabla **"Barrios prometidos"** en `resumen.md` (Barrio Colombia, Loreto, Prado, La Candelaria) con comercios/mapeadores/cambios reales y frase simple. **Bug corregido:** un barrio sin contribuciones sale con 0 e "insuficiente", nunca "sin datos". **25/25 en verde.** (Los números reales dependen de T14.) |
| T7 Desigualdad sociodigital | ✅/⚠️ | `mapa_mapeadores.png` se mantiene. Nuevos: `puntos_ciegos.png` (barrios grandes con < 3 mapeadores; **sin dato de población, se usa el área del barrio como proxy y así se rotula**) y `mirada_vs_cambio.png` (dispersión índice de mirada vs ITCO, con los barrios de estudio etiquetados y diagonal "lo que se mapea = lo que cambia"). **Opcional (estrato): ⚠️ no se descargó automáticamente** — el dato existe en GeoMedellín/MEData pero no hay un GeoJSON barrio↔estrato de descarga directa en el tiempo acordado. Se dejó la función `grafico_mapeadores_vs_estrato` lista: si el usuario coloca `data/estrato_por_barrio.csv` (barrio, estrato), se genera `mapeadores_vs_estrato.png`. El estrato solo contrasta, nunca entra al ITCO (así se rotula). **25/25 en verde.** |
| T8 Series con ohsome-py | ✅ | Nuevo `huellas/series_ohsome.py` + comando `python -m huellas series`. Usa **ohsome-py sobre la API v1 (sin API key)** para `elements/count/groupBy/boundary` anual de amenity/shop/craft por comuna. Plan B: v2 por HTTP si la v1 falla. Salidas: `series_claves.csv` (unidad, nivel, clave, año, conteo, proporción) y `figuras/series_claves.png` (3 paneles, comunas de estudio en color, resto en gris). Normaliza por el total de las tres claves en la ciudad ese año. **CORRIDO CON DATOS REALES de Medellín** (la v1 no necesita key): p. ej. amenity en El Poblado 45→777 nodos (2012→2026), Laureles 57→831, La Candelaria 36→528. |
| T9 Casos emblemáticos y validación | ✅ | Nuevo módulo `huellas/validacion.py`. `casos_emblematicos.csv` (25 mejores sustituciones T→transf, ordenadas por: tiene ambos nombres > barrio de estudio > reciente; con enlaces a historial OSM de A y B, Street View y Mapillary). `muestra_validacion.csv` **nueva**, estratificada (15 T→transf, 10 inverso, 10 otros cambios reales, 5 controles negativos), **solo comercios** (sin oficinas institucionales), y **sin revelar el estrato** (va en `muestra_validacion_clave.csv`). Columnas para llenar: `verificado`, `fecha_aprox_cambio_real`, `notas`. `VALIDACION.md` con instrucciones. Comando `python -m huellas validar` calcula precisión por tipo con IC de **Wilson** → `resultado_validacion.md`. La validación la llena el usuario. Pruebas: muestra no filtra estrato, Wilson/precisión, casos priorizan nombres. **23/23 en verde.** |
| T10 QGIS | ✅ | Estilos en `qgis/`: `itco.qml` (graduado, cortes −100/−50/−20/−5/5/20/50/100, rampa divergente azul–gris–rojo, rayado gris para nulos), `mapeadores.qml` (secuencial azul) y `eventos.qml` (categorizado por `tipo`, solo cambio real visible por defecto). `qgis/armar_proyecto.py` carga `barrios_itco`/`comunas_itco`/`eventos`, aplica estilos, añade base OSM y exporta **dos composiciones comparativas a 300 dpi**: (a) ITCO v1 vs v2 y (b) mirada vs cambio real. `GUIA_QGIS.md` actualizada (parte 9). **QGIS SÍ está instalado (3.36.3): el script se corrió headless y generó `salidas/figuras/qgis_comparativo_*.png`.** La capa `comunas_itco.geojson` se añadió al pipeline. El mapa base OSM no aparece en el render headless (sin red en ese proceso); se ve limpio sobre blanco. |
| T11 Kit comunitario y dashboard | ✅ | `dashboard.py` actualizado: **ficha por barrio al hacer clic** (ITCO, índice de mirada, mapeadores, línea de tiempo de cambios reales con enlace al historial OSM y frase en lenguaje simple). Un solo HTML sin servidor; `salidas/dashboard.html` pesa **9,5 MB** (< 10 MB; geometrías simplificadas). Corregida la referencia al desaparecido `itco_estricto` → `indice_mirada`/`itco_v1`. `KIT_COMUNITARIO.md` (2 páginas, sin jerga): qué dice y qué no el ITCO, cómo leer la ficha, cómo mapear el barrio (`disused:*`, editar el mismo punto, `check_date`/`opening_date`, mapear comercio popular) y cómo replicar en otra ciudad. |
| T12 Réplica CDMX | ✅ | **Corrida con datos reales de la alcaldía Cuauhtémoc.** `config_cdmx.yaml` + `taxonomia_cdmx.yaml` (misma base + cocina mexicana: tacos, antojitos, fonda, tortas…; `shop=tortilleria`/`abarrotes`). Colonias descargadas de datos abiertos (opendatasoft, 64 colonias de Cuauhtémoc) → `data/colonias_cuauhtemoc.geojson`. `cargar()` parametriza `taxonomia:` y `datos_crudos:`. Corrido `descargar`+`procesar`+`turismo`+`series` con `--config config_cdmx.yaml`; salidas en `salidas_cdmx/` (incluye `resumen.md`, `mapa_itco.png`, `turismo_normalizado.png`, `mapa_mapeadores.png`). **Números reales:** 15.657 contribuciones, 11.572 comerciales en el periodo, cambio real 559 (5%), 11 sustituciones T→transf. Las colonias de la propuesta se reportan igual aunque el dato sea débil. |
| T13 Turismo corregido | ✅ | `turismo.py`: "aperturas" → **"apariciones en OSM"** (columnas, títulos, textos). Nueva columna `proporcion_turismo` = apariciones turísticas / todas las creaciones de comercio del año (separa el crecimiento del fenómeno del crecimiento del mapa). Nueva figura `turismo_normalizado.png` (barras absolutas + línea de proporción). `dominancia_por_anio()` reporta usuarios distintos y peso del principal usuario/changeset → `turismo_dominancia.csv`. `tourism=apartment` (proxy de renta corta tipo Airbnb) separado de hostales/hoteles en textos y gráficos. Pruebas: renombrado+proporción, dominancia. **25/25 en verde.** |
| T14 Correr con datos reales | ✅ | **Corrido con la API key real.** `descargar` movió `data/raw`→`data/raw_v1` y bajó 2008–2026 con el filtro nuevo (incluye ciclo de vida). `procesar` + `turismo` corrieron sobre **14.455 contribuciones reales** de Medellín (7.283 objetos, 13% fuera de polígonos). Nota de rendimiento: `reemplazos` se vectorizó (de 133 s a 1,4 s) para que el pipeline completo corra en ~30 s. Resultados reales en `salidas/`. |
| T15 Informe final | ✅ | Este documento (secciones 1–9 abajo), `CAMBIOS_V2.md` y el zip de entrega. Pruebas finales en verde. |


---

# T15 · Informe final (datos reales)

## 1. Resumen de qué se hizo

Las 15 tareas quedaron ✅, todas corridas con **datos reales** de OSM vía ohsome.
Dos matices honestos: el contraste con estrato socioeconómico (T7, opcional) ⚠️
no se automatizó (queda la función lista si el usuario aporta el CSV), y el ITCO
por comuna en CDMX ⚠️ colapsa a una sola unidad (la alcaldía) porque la unidad
natural allí es la colonia (ver sección 7).

## 2. Tabla comparativa v1 → v2 (Medellín, periodo 2014–2026)

| Métrica | v1 | v2 |
|---|---:|---:|
| Barrios con ITCO calculable | 33 | 19 |
| Eventos considerados | 6.557 (cambios de categoría) | 468 **cambio real** (de 10.265 contribuciones) |
| "Evidencia fuerte" / cambio real (% del total) | 17 % | 5 % |
| Sustituciones directas tradicional → transformación | 7 | **11** |
| Correlación de rangos ITCO v1 ↔ v2 (Spearman) | — | **0,60** (n=19) |

La v2 es **más estricta y más honesta**: menos barrios "calculables" (porque exige
cambio real, no mapeo), pero más sustituciones reales detectadas (7 → 11) gracias
a relevos y reemplazos espaciales que la v1 no veía. La correlación 0,60 indica
que la v2 **reordena** bastante el ranking de barrios respecto a la v1 (no es un
simple reescalado).

**Top 10 ITCO v2:** Las Acacias (+42), La Candelaria (+34), La Florida (+32),
Patio Bonito (+23), Rosales (+16), Lorena (+10), Suburbano La Loma (+10),
Manila (+5), Versalles No. 1 (+5), Santa Teresita (0).

**Top 10 ITCO v1 (columna conservada):** La Aguacatala (+44), La Florida (+37),
Las Acacias (+33), Laureles (+26), Patio Bonito (+26), El Poblado (+23),
Bolivariana (+20), Manila (+18), Los Conquistadores (+18), Naranjal (+13).

## 3. Conteo de eventos por tipo (Medellín)

| Tipo | ¿Cambio real? | N |
|---|:--:|---:|
| creacion | | 5.203 |
| especificacion | | 3.517 |
| eliminacion | (ambiguo) | 664 |
| etiquetado | | 225 |
| correccion | | 188 |
| cierre | ✔ | 172 |
| relevo | ✔ | 128 |
| reemplazo | ✔ | 104 |
| mutacion | ✔ | 64 |

Reemplazos: **403 pares** detectados → **120 válidos**, 280 descartados como
redibujo, 30 marcados como edición masiva.

## 4. Las 10 transiciones más frecuentes DENTRO de cambio real

| N | etq_antes → etq_despues |
|---:|---|
| 27 | amenity=restaurant → amenity=restaurant |
| 23 | shop=supermarket → shop=supermarket |
| 13 | amenity=cafe → amenity=cafe |
| 9 | amenity=fast_food → amenity=fast_food |
| 9 | amenity=cafe → amenity=restaurant |
| 8 | tourism=hostel → tourism=hostel |
| 8 | tourism=hotel → tourism=hotel |
| 6 | shop=convenience → shop=mall |
| 6 | amenity=restaurant → amenity=fast_food |
| 6 | shop=mall → shop=mall |

**Lectura crítica (importante):** ya **no** hay ruido de erratas (`Kiosk→kiosk`),
que era el problema de la v1. Pero la mayoría de los cambios reales son
**relevos de MISMO giro** (restaurante→restaurante, supermercado→supermercado):
un negocio nuevo con otro nombre, misma categoría. Eso es un cambio real legítimo
(cambió el local), pero **no** es sustitución tradicional→transformación. Las
sustituciones de dirección (lo más "gentrificador") son pocas: 11. Hay que
presentarlo así de claro.

## 5. Sensibilidad del reemplazo (radio × ventana, Medellín)

| | 12 meses | 24 meses | 36 meses |
|---|---:|---:|---:|
| **15 m** | 72 | 77 | 80 |
| **25 m** | 111 | **120** | 128 |
| **40 m** | 142 | 157 | 171 |

(válidos, tras descartar redibujos y ediciones masivas). El número crece de forma
suave y monótona con el radio y la ventana: no hay un salto que delate un umbral
frágil. La configuración base (25 m / 24 meses) da 120.

## 6. Los 5 casos emblemáticos más fuertes (Medellín)

De `salidas/casos_emblematicos.csv` (sustituciones tradicional → transformación):

1. **Laureles** — `shop=bakery` "Cafe Revolucion" → `amenity=cafe` "Café Revolución" (2025).
2. **La Candelaria** — `shop=general` "Olala" → `shop=gift` "Olala" (2023).
3. **San Cristóbal (reemplazo)** — "Tienda parroquial" (convenience) → "Cafetería Parroquia San Vicente Ferrer" (cafe), 2025.
4. **El Poblado (Astorga)** — `shop=bakery` "Tostao'" → `amenity=cafe` "Tostao'" (2023).
5. **Laureles (Bolivariana, reemplazo)** — "Mi Arroz" (restaurant) → "La Gran Esquina" (restaurant), 2022.

**Advertencia honesta sobre estos casos:** los números 1, 2 y 4 tienen el **mismo
nombre** antes y después (o casi): son el **mismo negocio re‑etiquetado**
(`bakery→cafe` de la cadena Tostao, por ejemplo), no una sustitución de un negocio
por otro. El método los cuenta como mutación porque la *categoría* cambió, pero un
mapeador experto dirá —con razón— que no es gentrificación. Los casos realmente
fuertes son los **reemplazos con nombres distintos** (3 y 5). Para la charla,
conviene mostrar reemplazos nombrados, no mutaciones de cadena.

## 7. CDMX (alcaldía Cuauhtémoc) — números principales

- 15.657 contribuciones; 11.572 comerciales en el periodo; **cambio real 559 (5 %)**.
- Tipos: mutación 83, relevo 131, cierre 228, reemplazo 117. Reemplazos: 148
  válidos, 375 redibujos, 94 ediciones masivas.
- ITCO v2 calculable en **21 de 62 colonias**. Sustituciones T→transf: 11.
- **Juárez**: ITCO v2 **−24** pero índice de mirada **+31** y 3 sustituciones
  (el máximo). Contraintuitivo: la mirada dice "zona muy mapeada y en transición",
  pero el cambio real neto apunta a tradicional. Probable causa: cierres y
  relevos hacia categorías tradicionales/ambiguas que pesan más que las pocas
  sustituciones. **Se reporta como señal débil/ambigua, no como conclusión.**
- Turismo: 267 alojamientos mapeados, 65 renta corta, **18 apartamentos**
  (Airbnb‑like), despegue ~2016.

**Debilidades de CDMX (hay que decirlas):**
- **Sensibilidad alta a la taxonomía:** si lo ambiguo (bares, restaurantes,
  antros) cuenta como tradicional, la correlación de rangos con la base cae a
  **0,27** y 10 de 19 colonias cambian de signo. En Roma/Condesa el peso de la
  vida nocturna hace que la clasificación de lo ambiguo mueva mucho el resultado.
  El ITCO de CDMX es, por tanto, **menos robusto** que el de Medellín.
- **ITCO por comuna no aplica:** el GeoJSON de colonias trae la alcaldía como
  única "comuna", así que el agregado colapsa a una sola unidad (−25). La unidad
  informativa en CDMX es la **colonia**, no la comuna.
- En 2023, **un solo usuario** concentró el 68 % de las apariciones turísticas
  del año: ojo con leer ese pico como fenómeno real; puede ser una jornada de
  mapeo.

## 8. Lo que no se pudo hacer / pendiente del usuario

- **Validación de campo (T9):** el CSV `muestra_validacion.csv` está listo pero
  **vacío**; lo llena una persona en Street View/Mapillary y luego corre
  `python -m huellas validar`. Sin eso no hay cifra de precisión.
- **Contraste con estrato (T7, opcional):** no se descargó el estrato por barrio
  automáticamente (no hay un GeoJSON barrio↔estrato de descarga directa en el
  tiempo acordado). Si el usuario deja `data/estrato_por_barrio.csv`
  (columnas `barrio,estrato`), el pipeline genera `mapeadores_vs_estrato.png`.
- **QGIS:** las composiciones comparativas se generaron headless con QGIS 3.36;
  el mapa base OSM no aparece en ese render (sin red en el proceso). Si se quiere
  con fondo de calles, abrir el script desde la consola de QGIS con internet.

## 9. Cosas sospechosas en los datos (sé crítico)

1. **Relevos de mismo giro dominan el "cambio real"** (sección 4). Son cambios
   reales, pero no sustituciones de dirección; no inflar el relato con ellos.
2. **Mutaciones de cadena** (Tostao `bakery→cafe`) aparecen como sustituciones
   T→transf aunque sean el mismo negocio re‑etiquetado. Candidato a una regla
   futura: si el nombre normalizado es casi idéntico, degradar la mutación a
   "re‑etiquetado" (hoy el relevo exige nombre distinto, pero la mutación no mira
   el nombre). Documentado para no esconderlo.
3. **13 % (Medellín) y 14 % (CDMX) de los objetos caen fuera de los polígonos de
   barrio.** Son comercios en bordes o con geometría imprecisa; no entran al ITCO
   por barrio pero sí a los conteos globales.
4. **Solo el 5 % de los eventos tiene fecha declarada** (`opening_date` etc.). El
   ITCO usa la fecha de edición como proxy; es la limitación de fondo del método
   y por eso el bloque de turismo (que sí deja ver el "cuándo") lo complementa.
5. **CDMX es frágil a la taxonomía** (sección 7). El resultado de Medellín es más
   confiable que el de CDMX; la réplica demuestra que el método corre, no que
   CDMX esté midiendo lo mismo con la misma solidez.
