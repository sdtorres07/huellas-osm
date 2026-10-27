"""Genera TODAS las figuras y cifras de la charla con un solo comando.

    .venv\\Scripts\\python.exe generar_charla.py

Lee los resultados ya verificados del análisis (salidas/, salidas_cdmx/ y
salidas_v1/) y escribe en charla/:
  - figuras numeradas en el orden de la charla (PNG 16:9, 2000×1125 px);
  - cifras.json: cada número que aparece en las diapositivas, con su origen.

No descarga nada ni recalcula el ITCO: solo lee los CSV de resultados.
Datos © colaboradores de OpenStreetMap (ODbL), vía ohsome API (HeiGIT).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from math import comb
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# ----------------------------------------------------------------------
# Diseño (paleta validada; azul = serie principal, gris = contexto)
# ----------------------------------------------------------------------
SUPERFICIE = "#fcfcfb"
TINTA, TINTA_2, MUDO = "#0b0b0b", "#52514e", "#898781"
GRIS, GRIS_CLARO, REJILLA = "#b5b4ae", "#dcdbd5", "#ecebe6"
AZUL, NARANJA, AGUA, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
FUENTE_OSM = "Datos © colaboradores de OpenStreetMap (ODbL), vía ohsome API (HeiGIT). 2014–2025."

plt.rcParams.update({
    "font.size": 15, "axes.edgecolor": GRIS, "axes.labelcolor": TINTA_2,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE, "text.color": TINTA, "axes.titleweight": "bold",
})
ANCHO, ALTO, DPI = 10, 5.625, 200  # 16:9 → 2000×1125 px

# Dato externo, SOLO para dar escala (no entra en ningún cálculo del índice).
AIRDNA_MEDELLIN = {"anuncios_activos": 14957, "fecha": "septiembre de 2026",
                   "fuente": "https://www.airdna.co/vacation-rental-data/app/co/default/medellin/supply"}

T, R = "transformacion", "tradicional"


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def p_signo(k: int, n: int) -> float:
    """Prueba de signos bilateral (p = 0,5): ¿hay más movimientos hacia un lado
    de lo que daría el azar? Más conservadora que el bootstrap con pocos datos."""
    if n == 0:
        return 1.0
    cola = sum(comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * cola)


def movimientos(cr: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Por evento: movimientos hacia transformación (+) y hacia tradicional (−)."""
    a, d = cr["antes"], cr["despues"]
    mas = ((d == T) & (a != T)).astype(int) + ((a == R) & (d != R)).astype(int)
    menos = ((d == R) & (a != R)).astype(int) + ((a == T) & (d != T)).astype(int)
    return mas, menos


def n_minimo_signo(proporcion: float = 0.7, alfa: float = 0.05) -> int:
    """Menor n en el que una división `proporcion` / (1 − proporcion) ya es
    estadísticamente distinguible del azar con la prueba de signos."""
    for n in range(2, 500):
        k = round(n * proporcion)
        if p_signo(k, n) < alfa:
            return n
    return 500


def guardar(fig, ruta: Path, nota: str = FUENTE_OSM):
    fig.text(0.012, 0.018, nota, fontsize=9.5, color=MUDO)
    fig.savefig(ruta, dpi=DPI)
    plt.close(fig)
    print(f"  ✓ {ruta.name}")


def fmt(n) -> str:
    return f"{int(n):,}".replace(",", ".")


# ----------------------------------------------------------------------
# Cifras
# ----------------------------------------------------------------------
def cifras_ciudad(carpeta: Path) -> dict:
    ev = pd.read_csv(carpeta / "eventos.csv")
    cr = ev[ev["cambio_real"] == True]  # noqa: E712
    mas, menos = movimientos(cr)
    sust = cr[(cr["antes"] == R) & (cr["despues"] == T)]
    it = pd.read_csv(carpeta / "itco_por_periodo.csv")
    it = it[it["periodo"] == it["periodo"].iloc[-1]]
    g = cr.assign(mas=mas, menos=menos).groupby("barrio")[["mas", "menos"]].sum()
    g["n"] = g["mas"] + g["menos"]
    g["p_signo"] = [p_signo(int(m), int(m + k)) for m, k in zip(g["mas"], g["menos"])]
    rp = pd.read_csv(carpeta / "reemplazos.csv") if (carpeta / "reemplazos.csv").exists() else None
    c = {
        "ediciones_analizadas": int(len(ev)),
        "cambio_real": int(len(cr)),
        "pct_cambio_real": round(100 * len(cr) / len(ev), 1),
        "cambios_con_direccion": int(((mas + menos) > 0).sum()),
        "sustituciones_tradicional_a_transformacion": int(len(sust)),
        "eventos_por_tipo": {k: int(v) for k, v in ev["tipo"].value_counts().items()},
        "barrios_con_itco": int(it["itco"].notna().sum()),
        "barrios_total": int(len(it)),
        "barrios_direccion_significativa_signo": g[g["p_signo"] < 0.05].index.tolist(),
        "pct_eventos_con_fecha_declarada": round(100 * ev["fecha_declarada"].notna().mean(), 1),
        "fecha_primera_edicion": str(ev["edit_timestamp"].min())[:10],
        "fecha_ultima_edicion": str(ev["edit_timestamp"].max())[:10],
        "sustituciones": [
            {"barrio": r.barrio, "tipo": r.tipo, "fecha": str(r.edit_timestamp)[:10],
             "antes": r.etq_antes, "nombre_antes": r.nombre_antes if isinstance(r.nombre_antes, str) else None,
             "despues": r.etq_despues,
             "nombre_despues": r.nombre_despues if isinstance(r.nombre_despues, str) else None}
            for r in sust.sort_values("edit_timestamp").itertuples()],
    }
    if rp is not None and len(rp):
        c["reemplazos_todos_los_anios"] = {
            "candidatos": int(len(rp)), "validos": int(rp["cambio_real"].sum()),
            "redibujos_descartados": int(rp["redibujo"].sum()),
            "edicion_masiva": int(rp["edicion_masiva"].sum())}
    return c, ev, cr, g


def cifras_v1(carpeta_v1: Path) -> dict | None:
    ruta = carpeta_v1 / "eventos.csv"
    if not ruta.exists():
        return None
    v1 = pd.read_csv(ruta)
    m = v1[v1["tipo"] == "mutacion"]
    la, ld = m["etq_antes"].str.lower(), m["etq_despues"].str.lower()
    caso = np.where(m["etq_antes"] != m["etq_despues"],
                    np.where(la == ld, "errata",
                             np.where(m["etq_antes"].str.endswith("=yes"), "especifico", "otro")),
                    "cocina")
    vc = pd.Series(caso).value_counts()
    sust = int(((v1["antes"] == R) & (v1["despues"] == T) & (v1["tipo"] == "mutacion")).sum())
    return {"mutaciones": int(len(m)),
            "errata_mayusculas": int(vc.get("errata", 0)),
            "solo_se_agrego_cocina": int(vc.get("cocina", 0)),
            "se_especifico_un_generico": int(vc.get("especifico", 0)),
            "otros_cambios_de_etiqueta": int(vc.get("otro", 0)),
            "sustituciones_v1": sust}


# ----------------------------------------------------------------------
# Figuras
# ----------------------------------------------------------------------
def fig_v1(v1: dict, ruta: Path):
    filas = [("Errata de mayúsculas\n(shop=Kiosk → shop=kiosk)", v1["errata_mayusculas"], True),
             ("Solo se agregó el tipo de cocina", v1["solo_se_agrego_cocina"], True),
             ("Se especificó un genérico\n(shop=yes → shop=convenience)", v1["se_especifico_un_generico"], True),
             ("Otros cambios de etiqueta", v1["otros_cambios_de_etiqueta"], False)]
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    fig.subplots_adjust(left=0.36, right=0.92, top=0.95, bottom=0.12)
    y = np.arange(len(filas))[::-1]
    for yi, (etq, v, ruido) in zip(y, filas):
        ax.barh(yi, v, color=NARANJA if ruido else GRIS, height=0.58)
        ax.text(v + 1.5, yi, fmt(v), va="center", fontsize=16, fontweight="bold", color=TINTA)
    ax.set_yticks(y, [f[0] for f in filas], fontsize=13.5, color=TINTA)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([])
    ax.spines[["left", "bottom"]].set_visible(False)
    ruido = sum(f[1] for f in filas if f[2])
    guardar(fig, ruta, "En naranja: ediciones que no reflejan ningún cambio en la calle. " + FUENTE_OSM)


def fig_embudo(cm: dict, cc: dict, ruta: Path):
    pasos = ["Ediciones de comercios", "Cambio real en la calle",
             "…con dirección\n(tradicional ↔ transformación)", "…tradicional → transformación"]
    claves = ["ediciones_analizadas", "cambio_real", "cambios_con_direccion",
              "sustituciones_tradicional_a_transformacion"]
    fig, axes = plt.subplots(1, 2, figsize=(ANCHO, ALTO), sharey=True)
    fig.subplots_adjust(left=0.33, right=0.97, top=0.88, bottom=0.1, wspace=0.12)
    y = np.arange(len(pasos))[::-1]
    for ax, c, nombre in ((axes[0], cm, "Medellín"), (axes[1], cc, "CDMX")):
        vals = [c[k] for k in claves]
        for yi, v, i in zip(y, vals, range(4)):
            ax.barh(yi, v, color=NARANJA if i == 3 else (GRIS if i == 0 else AZUL), height=0.6)
            ax.text(v * 1.25, yi, fmt(v), va="center", fontsize=16, fontweight="bold", color=TINTA)
        ax.set_xscale("log")
        ax.set_xlim(1, 2e5)
        ax.set_xticks([])
        ax.minorticks_off()
        ax.spines[["left", "bottom"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_title(f"{nombre}: {str(c['pct_cambio_real']).replace('.', ',')} %",
                     fontsize=15, loc="left", color=TINTA)
    axes[0].set_yticks(y, pasos, fontsize=13, color=TINTA)
    guardar(fig, ruta, "Barras en escala logarítmica. Cambio real = mutación, relevo, cierre o reemplazo. "
            + FUENTE_OSM)


def fig_dibujandose(series: Path, ruta: Path) -> dict:
    s = pd.read_csv(series)
    s = s[s["nivel"] == "comuna"]
    p = s.pivot_table(index="anio", columns="unidad", values="conteo", aggfunc="sum")
    destacadas = [("EL POBLADO", AZUL), ("LAURELES", NARANJA), ("LA CANDELARIA", AGUA)]
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    fig.subplots_adjust(left=0.09, right=0.8, top=0.96, bottom=0.1)
    for col in p.columns:
        if col not in dict(destacadas):
            ax.plot(p.index, p[col], color=GRIS_CLARO, lw=1.5, zorder=1)
    out = {}
    for col, color in destacadas:
        ax.plot(p.index, p[col], color=color, lw=3, zorder=3)
        ax.text(p.index[-1] + 0.25, p[col].iloc[-1], col.title(), color=TINTA, fontsize=14,
                va="center", fontweight="bold")
        out[col] = {int(a): int(v) for a, v in p[col].items()}
    ax.text(p.index[-1] + 0.25, 60, "Otras comunas", color=MUDO, fontsize=12, va="center")
    ax.grid(axis="y", color=REJILLA, lw=1)
    ax.set_ylabel("comercios mapeados", fontsize=13)
    ax.set_xlim(p.index[0], p.index[-1])
    ax.set_ylim(0)
    guardar(fig, ruta, "Conteo al 1 de enero de cada año, por comuna. "
            "Datos © colaboradores de OpenStreetMap (ODbL), vía ohsome API v1 (HeiGIT).")
    return out


def fig_turismo(turismo: Path, ruta: Path) -> dict:
    t = pd.read_csv(turismo).set_index("anio")
    series = [("hostel", "Hostales", NARANJA), ("hotel", "Hoteles", AZUL),
              ("guest_house", "Casas de huéspedes", AGUA), ("apartment", "Apartamentos turísticos", AMARILLO)]
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    fig.subplots_adjust(left=0.08, right=0.7, top=0.96, bottom=0.1)
    for col, nombre, color in series:
        ax.plot(t.index, t[col], color=color, lw=3 if col == "hostel" else 2.2)
        ax.text(t.index[-1] + 0.25, t[col].iloc[-1], f"{nombre} ({t[col].iloc[-1]})", color=TINTA,
                fontsize=13.5, va="center", fontweight="bold" if col == "hostel" else "normal")
    ax.grid(axis="y", color=REJILLA, lw=1)
    ax.set_ylabel("alojamientos en OSM", fontsize=13)
    ax.set_xlim(t.index[0], t.index[-1])
    ax.set_ylim(0)
    h0 = int(t.loc[2016, "hostel"]) if 2016 in t.index else None
    h1 = int(t["hostel"].iloc[-1])
    guardar(fig, ruta, "Alojamientos vivos al 1 de enero de cada año. " + FUENTE_OSM)
    return {"hostales_2016": h0, "hostales_2026": h1,
            "hoteles_2026": int(t["hotel"].iloc[-1]),
            "apartamentos_turisticos_2026": int(t["apartment"].iloc[-1]),
            "total_alojamientos_2026": int(t["total"].iloc[-1])}


def apartamentos_dudosos(ev: pd.DataFrame) -> dict:
    ids = ev[(ev["etq_despues"] == "tourism=apartment") | (ev["etq_antes"] == "tourism=apartment")][
        ["osm_type", "osm_id"]].drop_duplicates()
    x = ev.merge(ids, on=["osm_type", "osm_id"]).sort_values("edit_timestamp")
    ult = x.groupby(["osm_type", "osm_id"]).tail(1)
    vivos = ult[ult["etq_despues"] == "tourism=apartment"]
    nombres = vivos["nombre_despues"].fillna("")
    residencial = nombres.str.contains(
        r"(?i)\b(?:conjunto|unidad|urbanizaci|torres?|parques? de|edificio|residencial|reserva|"
        r"condominio|ciudadela|colegio|hogar)\b")
    return {"objetos_que_fueron_apartamento": int(len(ids)), "siguen_como_apartamento": int(len(vivos)),
            "con_nombre_residencial_u_otro_uso": int(residencial.sum()),
            "sin_nombre": int((nombres == "").sum())}


def fig_airbnb(osm_apartamentos: int, ruta: Path):
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    fig.subplots_adjust(left=0.3, right=0.9, top=0.92, bottom=0.12)
    filas = [("Anuncios activos de renta corta\n(AirDNA, " + AIRDNA_MEDELLIN["fecha"] + ")",
              AIRDNA_MEDELLIN["anuncios_activos"], GRIS),
             ("Apartamentos turísticos\nen OpenStreetMap", osm_apartamentos, NARANJA)]
    for yi, (etq, v, color) in zip([1, 0], filas):
        ax.barh(yi, v, color=color, height=0.55)
        ax.text(v + 250, yi, fmt(v), va="center", fontsize=22, fontweight="bold", color=TINTA)
    ax.set_yticks([1, 0], [f[0] for f in filas], fontsize=14, color=TINTA)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([])
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.set_xlim(0, AIRDNA_MEDELLIN["anuncios_activos"] * 1.18)
    guardar(fig, ruta, "AirDNA solo da la escala; no entra en ningún cálculo. "
            "OSM: elementos tourism=apartment al 1-ene-2026. Medellín.")


def fig_mirada(itco_csv: Path, estudio: list[str], ruta: Path):
    it = pd.read_csv(itco_csv)
    it = it[it["periodo"] == it["periodo"].iloc[-1]].dropna(subset=["itco", "indice_mirada"])
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    fig.subplots_adjust(left=0.1, right=0.97, top=0.97, bottom=0.17)
    ax.axhline(0, color=GRIS, lw=1)
    ax.axvline(0, color=GRIS, lw=1)
    ax.plot([-100, 100], [-100, 100], color=GRIS, lw=1, ls=(0, (3, 3)))
    ax.text(62, 72, "lo que se mapea\n= lo que cambia", fontsize=11, color=MUDO, ha="center")
    es = it["barrio"].isin(estudio)
    ax.scatter(it.loc[~es, "indice_mirada"], it.loc[~es, "itco"], s=70, color=GRIS, zorder=2,
               edgecolor=SUPERFICIE, lw=2)
    ax.scatter(it.loc[es, "indice_mirada"], it.loc[es, "itco"], s=110, color=AZUL, zorder=3,
               edgecolor=SUPERFICIE, lw=2)
    desplaz = {"Laureles": (8, -16), "El Poblado": (-10, -18)}
    for _, r in it[es].iterrows():
        dx, dy = desplaz.get(r["barrio"], (8, 6))
        ax.annotate(r["barrio"], (r["indice_mirada"], r["itco"]), xytext=(dx, dy),
                    textcoords="offset points", fontsize=12.5, color=TINTA,
                    ha="right" if dx < 0 else "left")
    ax.set_xlim(-105, 105)
    ax.set_ylim(-108, 108)
    ax.set_xlabel("Índice de mirada → qué decide MAPEAR la gente", fontsize=13)
    ax.set_ylabel("ITCO → qué CAMBIA en la calle", fontsize=13)
    guardar(fig, ruta, "Barrios de Medellín con ITCO calculable; en azul, los de estudio. "
            "Datos © colaboradores de OpenStreetMap (ODbL), vía ohsome API.")


def fig_necesarios(g: pd.DataFrame, n_min: int, ruta: Path, excluir: list[str]) -> list[dict]:
    top = g[~g.index.isin(excluir)].sort_values("n", ascending=False).head(10)[::-1]
    fig, ax = plt.subplots(figsize=(ANCHO, ALTO))
    fig.subplots_adjust(left=0.24, right=0.95, top=0.96, bottom=0.17)
    y = np.arange(len(top))
    ax.barh(y, top["n"], color=AZUL, height=0.6)
    for yi, v in zip(y, top["n"]):
        ax.text(v + 0.4, yi, str(int(v)), va="center", fontsize=13, color=TINTA)
    ax.axvline(n_min, color=NARANJA, lw=2.5)
    ax.text(n_min + 0.4, len(top) - 0.6, f"mínimo para que la\ndirección sea clara: ~{n_min}",
            color=TINTA, fontsize=12.5, va="top")
    ax.set_yticks(y, top.index, fontsize=13, color=TINTA)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, max(n_min * 1.45, top["n"].max() * 1.2))
    ax.grid(axis="x", color=REJILLA, lw=1)
    ax.set_xlabel("cambios reales con dirección, 2014–2025", fontsize=13)
    guardar(fig, ruta, "Mínimo: prueba de signos, si el 70 % de los cambios apuntara al mismo lado (p < 0,05). "
            "Datos © colaboradores de OpenStreetMap (ODbL), vía ohsome API.")
    return [{"barrio": b, "cambios_con_direccion": int(r["n"]), "hacia_transformacion": int(r["mas"]),
             "hacia_tradicional": int(r["menos"]), "p_signo": round(float(r["p_signo"]), 3)}
            for b, r in top[::-1].iterrows()]


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--salidas", default="salidas")
    ap.add_argument("--salidas-cdmx", default="salidas_cdmx")
    ap.add_argument("--salidas-v1", default="salidas_v1")
    ap.add_argument("--destino", default="charla")
    a = ap.parse_args()
    med, cdmx, v1dir, dest = Path(a.salidas), Path(a.salidas_cdmx), Path(a.salidas_v1), Path(a.destino)
    dest.mkdir(parents=True, exist_ok=True)
    print("Generando figuras y cifras de la charla…")

    cm, ev_m, _, g_m = cifras_ciudad(med)
    cc, _, _, g_c = cifras_ciudad(cdmx)
    v1 = cifras_v1(v1dir)
    n_min = n_minimo_signo(0.7)
    estudio = ["Manila", "El Poblado", "Laureles", "La Candelaria", "Belén", "Versalles No. 1"]

    cifras = {"medellin": cm, "cdmx": cc, "v1": v1,
              "minimo_cambios_para_direccion_clara": n_min,
              "airdna_medellin": AIRDNA_MEDELLIN}
    if v1:
        fig_v1(v1, dest / "01_v1_era_limpieza_del_mapa.png")
    fig_embudo(cm, cc, dest / "02_embudo_cambio_real.png")
    cifras["mapa_dibujandose"] = fig_dibujandose(med / "series_claves.csv",
                                                 dest / "03_el_mapa_se_sigue_dibujando.png")
    cifras["turismo"] = fig_turismo(med / "turismo_ciudad.csv", dest / "04_hostales.png")
    cifras["apartamentos_turisticos_revision"] = apartamentos_dudosos(ev_m)
    fig_airbnb(cifras["turismo"]["apartamentos_turisticos_2026"], dest / "05_airbnb_vs_osm.png")
    fig_mirada(med / "itco_por_periodo.csv", estudio, dest / "06_mirada_vs_cambio.png")
    # Fátima se excluye: su "dirección" es una corrección de etiquetas de un solo mapeador.
    cifras["barrios_cambios_con_direccion"] = fig_necesarios(
        g_m, n_min, dest / "07_cambios_necesarios.png", excluir=["Fátima"])
    for nombre in ("mapa_mapeadores.png", "puntos_ciegos.png"):
        origen = med / "figuras" / nombre
        if origen.exists():
            shutil.copy(origen, dest / f"08_{nombre}")
            print(f"  ✓ 08_{nombre} (copiada de salidas/figuras)")
    for nombre, f in (("medellin", med), ("cdmx", cdmx)):
        rv = f / "resultado_validacion.md"
        if rv.exists():
            shutil.copy(rv, dest / f"validacion_{nombre}.md")
            print(f"  ✓ validacion_{nombre}.md")

    (dest / "cifras.json").write_text(json.dumps(cifras, ensure_ascii=False, indent=1, default=str),
                                      encoding="utf-8")
    print(f"  ✓ cifras.json\n\nListo: {dest.resolve()}")


if __name__ == "__main__":
    main()
