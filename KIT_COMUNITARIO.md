# Kit comunitario · Huellas de la gentrificación

Guía corta para juntas de acción comunal, colectivos y vecinos que quieran usar
el mapa de OpenStreetMap (OSM) como evidencia de cómo cambia el comercio de su
barrio. Sin jerga, sin presupuesto.

---

## 1. Qué dice —y qué NO dice— el ITCO

El **ITCO** (Índice de Transformación Comercial en OSM) resume, para cada barrio,
**qué tan rápido y en qué dirección** cambia su comercio:

- **Positivo (rojo):** el barrio se mueve hacia comercio de *transformación*
  (cafés de especialidad, boutiques, coworking, hostales).
- **Negativo (azul):** se mueve hacia comercio *tradicional* (tiendas, talleres,
  panaderías, misceláneas).
- **Cerca de cero o sin dato:** no hubo suficientes cambios para medir.

**Lo que el ITCO NO dice:**
- No mide precios de arriendo ni desplazamiento de personas. Es una señal del
  comercio, no una prueba de gentrificación por sí sola.
- Solo ve **lo que alguien mapeó en OSM**. Si tu barrio está poco mapeado, el
  ITCO sale "sin datos" aunque esté cambiando mucho. Eso es desigualdad digital,
  no ausencia de cambio.
- El **índice de mirada** (que aparece aparte) mide *qué decide mapear la gente*,
  no lo que cambia. No lo confundas con gentrificación.

> Regla de oro: si un número es débil o el barrio tiene pocos mapeadores, se dice
> claramente. La honestidad vale más que un mapa bonito.

---

## 2. Cómo leer la ficha de tu barrio

En el **dashboard** (`salidas/dashboard.html`, se abre en cualquier navegador,
sin internet), haz clic en tu barrio. Verás:

- **ITCO**: dirección y velocidad del cambio real.
- **Índice de mirada**: cuánto se mapea el barrio (atención, no cambio).
- **Mapeadores**: cuántas personas distintas han editado comercio allí.
- **Cambios reales**: cuántos locales de verdad cambiaron (no erratas ni mapeo).
- **Línea de tiempo**: la lista de esos cambios, con enlace al historial de cada
  local en OSM para que lo verifiques tú mismo.

Si tu barrio dice "pocos mapeadores" o "sin datos": el primer paso es **mapearlo**.

---

## 3. Cómo mapear tu barrio para que el mapa vea lo que pasa

El método solo funciona si los cambios quedan bien registrados. Cuatro hábitos:

1. **Cuando un local cierra, no lo borres: márcalo.** Cambia `shop=bakery` por
   `disused:shop=bakery` (o `was:shop=*`). Así el mapa sabe que cerró, en vez de
   que "desapareció".
2. **Cuando cambia de dueño o de giro, edita el MISMO punto.** No borres y crees
   uno nuevo: abre el local existente y cambia el `name` y la etiqueta. Así se ve
   el relevo ("Taller Don José" → "Pergamino Café") en el mismo lugar.
3. **Agrega fechas cuando las sepas.** `opening_date=2023` (cuándo abrió),
   `check_date=2026-01` (cuándo lo verificaste). Eso vuelve el dato mucho más
   fuerte.
4. **Mapea también el comercio popular.** Tiendas de barrio, talleres, ventas,
   misceláneas, panaderías. Si solo se mapean los cafés nuevos, el mapa cuenta
   una historia incompleta.

Herramientas fáciles para mapear desde el celular o el navegador:
**StreetComplete** (celular), **Every Door** (celular, ideal para comercio) o el
editor **iD** en openstreetmap.org (navegador).

---

## 4. Cómo replicarlo en otra ciudad

Todo el método es abierto y se adapta cambiando **solo la configuración**:

1. Consigue los **polígonos de los barrios/colonias** de tu ciudad (datos
   abiertos de la alcaldía o límites de OSM) en formato GeoJSON.
2. Copia `config.yaml` a `config_miciudad.yaml` y ajusta: el área
   (`area_descarga`), el archivo de barrios, la carpeta de datos
   (`datos_crudos`), las unidades de estudio y la carpeta de `salidas`.
3. Si tu ciudad tiene comercio típico propio (p. ej. `shop=tortilleria` en
   México), agrégalo a una copia de la taxonomía (`taxonomia_miciudad.yaml`).
4. Corre:
   ```
   python -m huellas descargar --config config_miciudad.yaml
   python -m huellas procesar  --config config_miciudad.yaml
   python -m huellas turismo   --config config_miciudad.yaml
   python -m huellas series    --config config_miciudad.yaml
   ```
   (Las series usan la API v1 de ohsome y **no necesitan clave**; la descarga de
   contribuciones sí usa una clave gratuita de HeiGIT.)

El caso de **Ciudad de México (alcaldía Cuauhtémoc)** incluido en este proyecto
es exactamente eso: la misma herramienta, otra configuración.

---

Datos © colaboradores de OpenStreetMap (ODbL), vía la API ohsome de HeiGIT.
Código y método abiertos. Úsalo, critícalo y mejóralo.
