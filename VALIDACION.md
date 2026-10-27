# Cómo validar la muestra (una página)

El método detecta "cambios reales" en el comercio a partir del historial de
OpenStreetMap. Antes de confiar en los números, vale la pena comprobar a mano
una muestra: ir al punto, mirar las fotos de calle de distintos años y decidir
si de verdad cambió el negocio.

Esto lo hace **una persona** (tú o alguien de la comunidad). el programa ya dejó listo
el archivo; aquí no se inventa nada.

## Qué archivo llenar

Abre `salidas/muestra_validacion.csv` (con LibreOffice, Excel o Google Sheets).
Cada fila es un caso con enlaces listos. **No** mira el archivo
`muestra_validacion_clave.csv`: ese tiene la respuesta que esperaba el método y
lo guardamos aparte para no sesgarte.

## Qué hacer en cada fila

1. Abre el enlace **street_view** (Google Street View) o **mapillary**.
2. Usa la línea de tiempo (en Street View, el reloj "ver imágenes anteriores")
   para comparar **antes y después** de la fecha de edición.
3. Mira también el enlace **historial_osm** para ver qué etiquetas cambiaron.
4. Llena tres columnas:
   - `verificado (si/no/no_se)`:
     - **si** = sí hubo un cambio real de negocio (otro local, otro giro, cerró);
     - **no** = no hubo cambio real (el negocio es el mismo, solo se corrigió el dato);
     - **no_se** = las fotos no alcanzan para decidir.
   - `fecha_aprox_cambio_real`: si puedes estimar cuándo cambió (año o mes/año).
   - `notas`: lo que viste ("era ferretería, hoy es café de especialidad").

### Qué cuenta como "sí"

- Un local que pasó de taller/tienda a café/boutique/coworking/hostal.
- Un negocio nuevo con otro nombre en el mismo lugar.
- Un local que cerró (quedó vacío o con `disused:`).

### Qué cuenta como "no"

- El mismo negocio de siempre, solo que alguien **corrigió la etiqueta** o
  **agregó el tipo de cocina**. (Estos son los "controles negativos": deberían
  salir "no".)

## Al terminar

Guarda el CSV y corre:

```
python -m huellas validar
```

El programa cruza tus respuestas con la clave y calcula la **precisión por tipo
de evento**, con un intervalo de confianza del 95 % (método de Wilson). El
resultado queda en `salidas/resultado_validacion.md`.

Una precisión alta en `mutacion`, `relevo` y `reemplazo` respalda el método.
Si los **controles negativos** salen mal (el validador vio cambios donde el
método decía que no), hay que revisar las reglas: eso se reporta tal cual, sin
maquillar.
