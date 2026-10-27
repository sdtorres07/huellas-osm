# TAREAS_KIRO_R2.md: segunda ronda (ajustes finos antes de la validación)

Claude revisó la entrega v2. El trabajo es muy bueno y el informe es honesto. Quedan **seis
ajustes** que hay que hacer **antes** de que el usuario llene la validación, porque cambian
la muestra. Las reglas de la ronda 1 siguen vigentes: honestidad antes que espectacularidad,
cada regla nueva con su prueba, no tocar `salidas_v1/`, no incluir `.env`.

Antes de empezar, copia `salidas/` a `salidas_v2_r1/` (y `salidas_cdmx/` a `salidas_cdmx_r1/`)
para poder comparar.

---

## R1. Mutación con el mismo nombre = re-etiquetado (no es cambio real)

Hoy 6 de las 11 "sustituciones" de Medellín son el mismo negocio re-etiquetado:
Tostao' (`bakery → cafe`, 3 veces), Café Revolución, Olala (`general → gift`) y "EDIFICIO"
(`pawnbroker → hotel`).

- En `historia._tipo`: si la categoría cambia y los nombres normalizados son similares
  (`rapidfuzz.fuzz.token_set_ratio ≥ 85`), el tipo es **`reetiquetado`** (no es cambio real).
- Si ambos nombres están vacíos, sigue siendo `mutacion`.
- Prueba: `Tostao'` → `Tostao’` con `bakery → cafe` da `reetiquetado`.

## R2. Relevo: quitar falsos positivos

En una muestra de 25 relevos, unos 10 no son un negocio nuevo:
- **El nombre solo se acortó o alargó:** "D1 pilarica" → "D1", "Makro San Juan" ↔ "Makro",
  "Homecenter - Constructor San Juan" → "Homecenter", "Pizza Express San Joaquin" → "PizzaExpress".
  Regla: si `token_set_ratio ≥ 90`, o si un nombre normalizado (sin espacios) está contenido
  en el otro, **no** es relevo (es `especificacion`).
- **Uno de los nombres es genérico** (el nombre es solo el tipo de negocio): "Carnes",
  "Papeleria", "Tienda", "Hostal", "Librería", "Edificio", "Cancha", "Miselanea".
  Regla: crea en `taxonomia.yaml` una lista `nombres_genericos:` (tienda, tiendas, carnes,
  carniceria, papeleria, miscelanea, miselanea, hostal, hotel, libreria, edificio, cancha,
  restaurante, cafeteria, cafe, panaderia, supermercado, minimercado, mini_mercado, barberia,
  peluqueria, droguería, drogueria, licorera, bar, discoteca, ferreteria, comidas, comida_rapida,
  local, bodega). Si el nombre normalizado completo de antes **o** de después está en esa lista,
  **no** es relevo (es `especificacion`).
- Pruebas para los dos casos.

## R3. Reemplazo: redibujos que se escapan

- En la normalización de nombres para comparar, quita también estas palabras: "centro comercial",
  "c.c.", "cc", "hotel", "hostal", "restaurante", "bar", "tienda", "supermercado", "drogueria".
  Así "Centro Comercial Unicentro" y "Unicentro" se reconocen como el mismo objeto.
- Para detectar redibujos usa `max(token_sort_ratio, token_set_ratio) ≥ 80`.
- Aplica la misma lista de `nombres_genericos`: si A o B tienen un nombre genérico y la misma
  etiqueta, es redibujo.
- Agrega la columna `mismo_changeset` (A y B en el mismo changeset). **No lo descartes**: un
  mapeador en terreno que borra el local viejo y crea el nuevo en la misma edición es evidencia
  legítima. Solo repórtalo en el informe (qué % de reemplazos válidos lo son).
- Repite la sensibilidad (radio × ventana).

## R4. Intervalos de confianza del ITCO (lo más importante de esta ronda)

Un cálculo rápido con *bootstrap* muestra que en **17 de los 19 barrios** con ITCO v2 la
dirección no se distingue de cero. Las Acacias (+42) se apoya en 5 eventos. Esto hay que
mostrarlo en las salidas, no esconderlo.

- En `itco.py`, calcula un **intervalo de confianza del 95 % por bootstrap** (2.000 remuestreos,
  semilla fija desde `config.yaml`) remuestreando los eventos de cambio real de cada unidad
  (barrio y comuna). Hazlo sobre la `direccion` y sobre el `itco` (el percentil de velocidad se
  deja fijo).
- Columnas nuevas: `itco_ic_bajo`, `itco_ic_alto` y `direccion_clara` (True si el IC de la
  dirección no incluye el 0).
- **Mapas:** los barrios con ITCO pero sin `direccion_clara` se pintan con su color **muy
  aclarado** (alfa 0,35) y con un borde punteado; en la leyenda: "dirección incierta (IC 95 %
  incluye 0)".
- `resumen.md`: cuántos barrios y comunas tienen dirección clara. En la tabla de los 10 mayores,
  agrega la columna "IC 95 %".
- Lo mismo para CDMX.

## R5. Taxonomía: pizza y hamburguesa no son gentrificación en Medellín

En la regla de restaurantes de transformación, saca `pizza` y `burger`. Ponlas en una regla
`ambiguo` para `restaurant` y `fast_food`. Documéntalo en `CAMBIOS_V2.md`. Lo mismo en
`taxonomia_cdmx.yaml`.

## R6. Regenerar, volver a correr y reportar

1. `python -m huellas procesar`, `turismo` y `dashboard` (Medellín) y lo mismo con
   `--config config_cdmx.yaml`. No hace falta volver a descargar.
2. Regenera `casos_emblematicos.csv` y `muestra_validacion.csv` (+ `_clave`). Si no hay
   15 sustituciones tradicional → transformación, incluye **todas** las que haya y completa con
   otros cambios reales; anota cuántas hubo.
3. **Figura nueva `figuras/embudo.png`** (Medellín y CDMX): barras horizontales de
   - contribuciones comerciales analizadas
   - cambio real (después de R1–R3)
   - con dirección (entre tradicional y transformación)
   - sustituciones tradicional → transformación
   - (deja una barra "verificadas en Street View" con valor vacío y la etiqueta "pendiente")
   Escala logarítmica, con el número escrito sobre cada barra.
4. **Arregla `qgis_comparativo_*.png`**: hoy solo se ven manchas sin contexto. Agrega el contorno
   de **todos** los barrios en gris claro, la leyenda de colores y un subtítulo por panel. Si no
   alcanzas, elimina esos dos PNG y anótalo.
5. Actualiza `INFORME_KIRO.md` con una sección **"Ronda 2"**: tabla antes → después de R1–R5
   (cambio real por tipo, sustituciones tradicional → transformación con su lista completa y
   nombres, reemplazos válidos, barrios con dirección clara, la nueva sensibilidad del reemplazo)
   y los 10 relevos y 10 reemplazos válidos que se vean **más sólidos**, con nombres.
6. Todas las pruebas en verde. Crea `huellas-osm-v2r2-resultados.zip` con las mismas exclusiones
   de antes (sin `.venv`, `.env`, `__pycache__`, `data/raw*`, `*.gpkg`) y verifica que `.env`
   no quedó adentro.
