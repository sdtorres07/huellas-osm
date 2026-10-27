"""Genera el sitio web del mapa vivo (docs/mapa.html) a partir de las salidas del análisis.

Uso (después de `python -m huellas procesar` para cada ciudad):

    python generar_mapa.py --medellin salidas --cdmx salidas_cdmx

Cada carpeta debe tener `eventos.csv` y `barrios_itco.geojson` (las genera `procesar`).
Escribe docs/mapa.html y docs/idioma_<ciudad>.csv. Para otra ciudad, pásala en lugar
de una de las dos (los nombres de los botones se cambian en docs/plantilla_mapa.html).
La página de inicio (docs/index.html) es estática: edita sus cifras a mano.
"""
import argparse, json, os
from pathlib import Path
from huellas.idioma import build

T = {"creacion": "c", "etiquetado": "e", "especificacion": "s", "correccion": "o", "reetiquetado": "t",
     "mutacion": "m", "relevo": "r", "cierre": "x", "reemplazo": "p", "eliminacion": "d"}


def compactar(c):
    for o in c["objs"]:
        prev = None
        for h in o["h"]:
            h[4] = T.get(h[4], "?")
            if h[2] == prev:
                h[2] = 0
            else:
                prev = h[2]
    try:  # simplificar polígonos si shapely está instalado (opcional)
        from shapely.geometry import shape, mapping
        r = lambda x: [round(x[0], 5), round(x[1], 5)] if isinstance(x[0], (int, float)) else [r(y) for y in x]
        for f in c["barrios"]["features"]:
            m = mapping(shape(f["geometry"]).simplify(0.00008, preserve_topology=True))
            f["geometry"] = {"type": m["type"], "coordinates": r(json.loads(json.dumps(m["coordinates"])))}
    except ImportError:
        pass
    c["ciudad_en"] = {int(k): float(v) for k, v in c["ciudad_en"].items()}
    return c


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--medellin", required=True, help="carpeta de salidas de la primera ciudad")
    a.add_argument("--cdmx", required=True, help="carpeta de salidas de la segunda ciudad")
    a.add_argument("--destino", default="docs")
    x = a.parse_args()
    dest = Path(x.destino); dest.mkdir(exist_ok=True)
    here = os.getcwd(); os.chdir(dest)
    try:
        data = {"med": compactar(build(os.path.join(here, x.medellin), os.path.join(here, x.medellin), "medellin")),
                "cdmx": compactar(build(os.path.join(here, x.cdmx), os.path.join(here, x.cdmx), "cdmx"))}
    finally:
        os.chdir(here)
    t = (dest / "plantilla_mapa.html").read_text(encoding="utf-8")
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (dest / "mapa.html").write_text(t.replace("/*DATA*/", js), encoding="utf-8")
    print("Listo:", dest / "mapa.html")


if __name__ == "__main__":
    main()
