# Huellas de la gentrificación

**Lo que el historial de OpenStreetMap ve, y lo que no ve, de la transformación urbana.**
Caso Medellín, con réplica en la alcaldía Cuauhtémoc (Ciudad de México).

Charla presentada en **State of the Map LATAM 2026** (Ciudad de México, 26 de octubre de 2026) por Sergio David Torres Llanes.

---

## La idea en tres líneas

1. Cada cambio de un comercio queda en el historial de OSM: si un taller se vuelve café, el mapa guarda la fecha, la etiqueta anterior y la nueva.
2. Pero el historial mezcla dos cosas: **lo que cambia en la calle** y **lo que cambia en el mapa** (alguien agrega un local que ya existía, corrige una errata, redibuja un punto).
3. Este proyecto separa las dos, mide un índice de transformación comercial (ITCO) con su incertidumbre, lo valida en fotos de calle y lo replica en otra ciudad cambiando un archivo de configuración.

## Resultados principales (2014–2026)

| | Medellín | CDMX (Cuauhtémoc) |
|---|---:|---:|
| Ediciones de comercios analizadas | 10.238 | 11.548 |
| Cambio real en la calle | 352 (3,4 %) | 417 (3,6 %) |
| Cambios que mueven el balance tradicional ↔ transformación | 138 | 174 |
| Sustituciones de comercio tradicional por comercio de transformación | 3 | 8 |

- En la versión 1 del método, **218 de 296 "cambios fuertes" eran limpieza del mapa** (erratas como `shop=Kiosk → shop=kiosk`, cocina agregada, `shop=yes` especificado).
- El mapa de Medellín **todavía se está dibujando**: en Laureles, los comercios mapeados se multiplicaron por 2,5 entre 2020 y 2026. Mientras eso pase, un comercio "nuevo" en OSM puede ser solo uno recién mapeado.
- Para leer con confianza la dirección de un barrio se necesitan unos **25 cambios con dirección**; el barrio que más tiene en Medellín llega a 10.
- Lo que el mapa sí ve: los **hostales pasaron de 9 a 116** (2016–2026). Lo que no puede ver: Medellín tiene casi 15.000 anuncios de renta corta (AirDNA, sep. 2026) y OSM tiene 62 apartamentos turísticos.
- Validación manual en Street View: 8 de 34 cambios detectados se confirmaron en la calle (24 %).

Todas las cifras salen de `charla/cifras.json`, generado por `generar_charla.py`.

## Cómo correrlo

Necesitas Python 3.10 o superior y una clave gratuita de la API ohsome (https://account.heigit.org/signup).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env      # y pon tu clave en .env  (Mac/Linux: cp)
python -m huellas demo      # prueba sin internet con una ciudad sintética
```

Con datos reales:

```bash
python -m huellas descargar     # historial 2008–2026 (se puede reanudar)
python -m huellas procesar      # eventos, reemplazos, ITCO, mapas, muestra de validación
python -m huellas turismo       # alojamiento turístico
python -m huellas series        # series de amenity/shop/craft con ohsome-py
python -m huellas dashboard     # dashboard HTML que funciona sin internet
python -m huellas validar       # precisión, cuando la muestra de validación esté llena
python generar_charla.py        # figuras y cifras de la charla en charla/
```

Para otra ciudad: copia `config_cdmx.yaml` y `taxonomia_cdmx.yaml`, cambia el área, los polígonos y la cocina local, y agrega `--config tu_config.yaml` a cada comando.

## Mapa vivo y sitio web

**Explóralo:** https://sdtorres07.github.io/huellas-osm/

- `docs/index.html`: página de inicio con los hallazgos (a ella apunta el QR de la charla).
- `docs/mapa.html`: mapa interactivo de Medellín y Cuauhtémoc. Colorea los barrios por ITCO, por % de nombres en inglés o por número de mapeadores; tiene una barra de años (2008–2026) y el historial de cada local, con enlace a OSM. Leaflet y los datos van dentro del archivo; solo el fondo de calles requiere conexión. El fondo usa las teselas libres del estilo Humanitario (HOT, alojado por OSM France) y, si fallan, cambia solo a las teselas estándar de OpenStreetMap: no necesita ninguna clave.
- Se publica con GitHub Pages: *Settings → Pages → Deploy from a branch → main → /docs*.

Para regenerarlo con tus propios resultados (por ejemplo, otra ciudad):

```
python -m huellas procesar                         # Medellín (config.yaml)
python -m huellas procesar --config config_cdmx.yaml
python generar_mapa.py --medellin salidas --cdmx salidas_cdmx
```

## Indicador de idioma de los nombres comerciales

`huellas/idioma.py` clasifica el nombre vigente de cada negocio como español o inglés por palabras clave y calcula, por barrio, el porcentaje de nombres en inglés (cortes 2015 y 2026). Solo cuenta nombres con idioma identificable (empates y nombres propios quedan fuera, unos 3 de cada 5), y solo se reportan barrios con al menos 15 nombres. Es un indicador aproximado: úsalo como señal, no como medida.

```
python -m huellas.idioma --salidas salidas --capas salidas --nombre medellin
```

Resultados: `docs/idioma_medellin.csv` y `docs/idioma_cdmx.csv`. Medellín: 15 % de nombres en inglés en la ciudad, 59 % en La Florida, 0 % en Belén. Cuauhtémoc: 14 % en la alcaldía, 31 % en la Juárez, 0 % en la Guerrero.

## Validación en la calle

La muestra validada está en `validacion/muestra_validada.csv` (40 casos al azar de Medellín, revisados en Street View de varios años, a ciegas respecto a lo que esperaba el método) y el resumen en `validacion/resultado_validacion.md`:

- 8 de 34 cambios detectados se confirmaron en la calle: **24 %** (IC 95 % de Wilson: 12–40 %).
- Controles negativos: **5 de 5** correctos (el método no inventa cambios).
- Por tipo: relevo (mismo objeto) 4 de 8; reemplazo (borrar y crear cerca) 4 de 20; cierre 0 de 6.
- La mitad de los "no" eran negocios que ya existían desde 2013: el mapa se ponía al día.

Para repetirla en tu ciudad: `python -m huellas procesar` genera la muestra, la llenas siguiendo `VALIDACION.md` y corres `python -m huellas validar`.

## Verificar los datos con una herramienta independiente

El conteo de alojamientos turísticos se puede reproducir con Overpass (https://overpass-turbo.eu). Debe dar un número cercano a los 406 de nuestros datos al 1-ene-2026; un poco más si se ha mapeado desde entonces:

```
[out:json][timeout:60];
nw["tourism"~"^(hotel|hostel|guest_house|apartment)$"](6.155,-75.665,6.355,-75.515);
out count;
```

## Cómo funciona

| Paso | Qué hace | Dónde |
|---|---|---|
| Descarga | Historial completo de contribuciones vía ohsome API v2 | `huellas/api.py` |
| Clasificación | Tradicional, de transformación, ambiguo o neutro, con etiquetas normalizadas | `taxonomia.yaml`, `huellas/taxonomia.py` |
| Tipología | Creación, etiquetado, especificación, corrección, re-etiquetado (mapa) frente a mutación, relevo, cierre (calle) | `huellas/historia.py` |
| Reemplazo espacial | Un local sale y otro aparece a ≤ 25 m en ≤ 24 meses; se descartan redibujos | `huellas/reemplazos.py` |
| ITCO | Dirección × percentil de velocidad, solo con cambio real, con intervalo bootstrap | `huellas/itco.py` |
| Índice de mirada | La misma fórmula, solo con lo que la gente decide mapear | `huellas/itco.py` |
| Validación | Muestra estratificada con controles negativos, precisión con IC de Wilson | `huellas/validacion.py` |

Los detalles y cada decisión metodológica están en `CAMBIOS_V2.md`. Pruebas: `python tests/test_basico.py` (33 pruebas).

## Límites (dichos en voz alta)

- OSM registra lo que alguien mapeó, no todo lo que pasa. Donde hay menos mapeadores, el mapa ve menos.
- El ITCO mide transformación **comercial**, no desplazamiento de residentes.
- Con el volumen actual de cambios registrados, el ITCO no puede ordenar barrios con confianza: el método funciona, falta dato.
- Se descargan nodos y vías (no relaciones). El 13 % de los objetos de Medellín cae fuera de los polígonos de barrio.

## Para comunidades

`KIT_COMUNITARIO.md` explica, sin jerga, cómo leer los resultados y cómo mapear para que el mapa guarde la memoria del barrio:
marcar `disused:shop=*` cuando un local cierra, editar el mismo punto cuando llega otro negocio, agregar `check_date` y `opening_date`, y mapear el comercio popular.

## Licencias y atribución

- Código: MIT (ver `LICENSE`).
- Datos: © colaboradores de OpenStreetMap, licencia ODbL (https://www.openstreetmap.org/copyright), consultados vía ohsome API de HeiGIT.
- Límites de barrio: Alcaldía de Medellín, datos abiertos. Colonias: datos abiertos de la Ciudad de México.
- La cifra de AirDNA se usa solo como referencia de escala y no entra en ningún cálculo.
