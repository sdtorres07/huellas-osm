# Guía QGIS — paso a paso para los mapas temáticos

> Objetivo: abrir en QGIS las capas que ya generó el proyecto y producir un mapa
> temático del ITCO (y uno de mapeadores) con calidad de presentación, cumpliendo
> la promesa de tu propuesta ("visualización en QGIS").
>
> No necesitas saber QGIS. Son clics. Tiempo estimado: 20–30 min.
> Si no tienes QGIS: descárgalo gratis en https://qgis.org/es/site/forusers/download.html
> (versión LTR, "Long Term Release"). Instalación normal, siguiente-siguiente.

Las capas ya están en la carpeta `salidas/`:
- `barrios_itco.geojson` — polígonos de barrio con todas las columnas del ITCO
- `eventos.geojson` — cada cambio detectado, como puntos
- `comunas_itco.geojson` — polígonos de comuna (barrios disueltos) con su ITCO
- `huellas.gpkg` — las capas juntas en un GeoPackage (si prefieres)

---

## PARTE 1 — Abrir las capas

1. Abre **QGIS**.
2. Menú **Capa → Añadir capa → Añadir capa vectorial…**
3. En "Origen", el botón **…** y busca:
   `C:\Users\usuario\Desktop\Conferencia OSM\huellas-osm\salidas\barrios_itco.geojson`
4. Clic en **Añadir**. Cierra la ventana. Ya ves los barrios de Medellín en gris.
5. (Opcional) Repite para `eventos.geojson` — aparecerán puntos encima.

---

## PARTE 2 — Mapa base bonito (opcional pero recomendado)

Para que no se vea flotando en el vacío:

1. En el panel **Explorador** (izquierda), despliega **XYZ Tiles**.
2. Doble clic en **OpenStreetMap**. Se añade un fondo de mapa.
3. Arrastra la capa `barrios_itco` **por encima** del fondo OSM en el panel de Capas.

> Si vas a mostrarlo offline en la charla, mejor NO uses el fondo XYZ (necesita internet).
> Déjalo sobre fondo blanco; igual se ve limpio.

---

## PARTE 3 — Colorear los barrios por ITCO (el mapa principal)

1. Clic derecho sobre la capa `barrios_itco` → **Propiedades**.
2. Pestaña **Simbología** (icono de pincel, arriba izquierda).
3. Arriba, cambia el desplegable de **"Símbolo único"** a **"Graduado"**.
4. En **Valor**, elige la columna: **`itco`**.
5. En **Rampa de color**, elige una **divergente** (busca "RdBu" y luego **inviértela**
   con el botón "Invertir rampa de color", para que rojo = transformación, azul = tradicional).
6. En **Modo**, elige **"Intervalos definidos por el usuario"** (o "Discontinuidades
   naturales"). Si usas intervalos manuales, pon estos cortes de clase:
   **-100, -50, -20, -5, 5, 20, 50, 100**
7. Clic en **Clasificar**. Verás los barrios tomar color.
8. **Importante:** los barrios sin ITCO (valor nulo) hay que distinguirlos. Abajo, en
   "Representar con valores nulos", actívalo y asígnale un gris claro o un patrón de rayas.
9. **Aplicar → Aceptar.**

Ya tienes el mapa del ITCO. El centro-sur (El Poblado, Laureles) debe verse en rojos.

---

## PARTE 4 — Resaltar los barrios de estudio (opcional)

Para que El Poblado, Laureles, etc. destaquen con un borde:

1. Propiedades de `barrios_itco` → Simbología → arriba cambia a **"Basado en reglas"**
   (si quieres combinar) — o más simple: duplica la capa (clic derecho → Duplicar capa),
   y en la copia pon relleno transparente y borde negro grueso, filtrada por los barrios
   de estudio (clic derecho → Filtrar → `"grupo_estudio" <> ''`).

*(Si te complica, sáltate esta parte: el mapa ya funciona sin ella.)*

---

## PARTE 5 — Etiquetar los barrios

1. Propiedades de `barrios_itco` → pestaña **Etiquetas**.
2. Cambia "Sin etiquetas" a **"Etiquetas individuales"**.
3. En **Valor**, elige **`barrio`**.
4. Para no saturar: en la sub-pestaña **Representación**, activa "mostrar solo las
   etiquetas que no se solapen". O filtra para etiquetar solo los barrios de estudio.
5. **Aplicar → Aceptar.**

---

## PARTE 6 — Exportar la imagen para la charla

1. Menú **Proyecto → Importar/Exportar → Exportar mapa a imagen…**
2. Ajusta la resolución a **200 dpi** (para que se vea nítido en proyector).
3. Guarda como `mapa_itco_qgis.png` en la carpeta `salidas/figuras/`.

Ese PNG es tu respaldo y tu "prueba de QGIS" para la charla.

---

## PARTE 7 (bonus) — Segundo mapa: mapeadores

Repite la PARTE 3 pero con la columna **`contribuyentes`** en vez de `itco`, y una
rampa de color **secuencial azul** (modo "Cuantiles", 6 clases). Exporta como
`mapa_mapeadores_qgis.png`. Es el mapa de la desigualdad digital.

---

## PARTE 8 (bonus) — Los eventos como puntos

1. Clic derecho en `eventos.geojson` → **Filtrar…**
2. Escribe:  `"tipo" = 'mutacion'`  → Aceptar. (Solo los locales que cambiaron de giro.)
3. Propiedades → Simbología → puntos pequeños en terracota.
4. Quedan encima del mapa de ITCO como "pruebas" puntuales del cambio.

---

## Consejos para que se vea profesional

- Fondo blanco, sin bordes azules de QGIS: usa el **Diseñador de impresión**
  (**Proyecto → Nuevo diseño de impresión**) si quieres un mapa con título, leyenda
  y norte. Para una diapositiva, con exportar a imagen basta.
- La leyenda: en el Diseñador de impresión, **Añadir leyenda**; renómbrala a algo
  claro como "ITCO (−100 tradicional … +100 transformación)".
- Mantén la misma paleta divergente que el dashboard (rojo/azul) para coherencia visual.

---

## Si algo sale mal

- **No veo los barrios:** revisa que la ruta del archivo sea correcta y que el CRS del
  proyecto sea EPSG:4326 (abajo a la derecha). El GeoJSON ya está en WGS84.
- **Todo sale de un solo color:** no clasificaste; vuelve a Simbología → "Graduado" →
  Clasificar.
- **Los números del ITCO no aparecen como columna:** confirma que abriste
  `barrios_itco.geojson` y no otro archivo. Abre la **Tabla de atributos** (clic derecho →
  Abrir tabla de atributos) y verifica que están las columnas `itco`, `contribuyentes`, etc.

---

## PARTE 9 — Atajo automático (estilos .qml + composiciones comparativas)

Si prefieres no hacer los clics a mano, el proyecto trae todo listo en la
carpeta `qgis/`:

- `itco.qml` — estilo graduado del ITCO (cortes −100…100, rampa divergente
  azul–gris–rojo, gris rayado para los barrios sin dato).
- `mapeadores.qml` — estilo secuencial azul para el número de mapeadores.
- `eventos.qml` — estilo categorizado por `tipo`; **por defecto solo se ven los
  eventos de cambio real** (mutación, relevo, cierre, reemplazo); los demás
  (creación, especificación, corrección, etiquetado, eliminación) van ocultos.

### Opción A — desde la consola de Python de QGIS
1. Abre QGIS → **Complementos → Consola de Python**.
2. Pega:
   ```python
   exec(open(r"C:\Users\usuario\Desktop\Conferencia OSM\huellas-osm\qgis\armar_proyecto.py", encoding="utf-8").read())
   ```
3. El script carga las capas de `salidas/`, aplica los estilos, agrega un mapa
   base OSM y exporta a `salidas/figuras/`:
   - `qgis_comparativo_v1_vs_v2.png` — ITCO v1 (con ruido) vs ITCO v2 (cambio real).
   - `qgis_comparativo_mirada_vs_cambio.png` — índice de mirada vs cambio real.

### Opción B — sin abrir QGIS (headless)
Desde una terminal, con QGIS instalado:
```
"C:\Program Files\QGIS 3.36.3\bin\python-qgis.bat" qgis\armar_proyecto.py
```
(ajusta la versión de QGIS a la que tengas). El script detecta que no hay una
app de QGIS viva y la inicializa solo.

> Nota: para aplicar un estilo a mano, clic derecho en la capa → **Propiedades →
> Simbología → ⚙ Estilo → Cargar estilo…** y elige el `.qml` correspondiente.
> El mapa base OSM necesita internet; para la charla offline, déjalo sobre fondo
> blanco (igual se ve limpio).
