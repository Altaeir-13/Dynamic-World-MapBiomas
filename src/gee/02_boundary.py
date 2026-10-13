"""
02_boundary.py — Materialização da delimitação oficial do MATOPIBA
===================================================================
Obtém a lista oficial dos 337 municípios do MATOPIBA do IBGE e as
malhas municipais oficiais (IBGE 2024/2025), consolidando a geometria
congelada e a lista de municípios.

Conforme PROJECT_BRIEF.md (Seção 6):
  data/reference/matopiba_boundary.geojson
  data/reference/matopiba_municipalities.csv
"""

from __future__ import annotations

import hashlib
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_REF = BASE_DIR / "data" / "reference"

IBGE_MATOPIBA_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/"
    "MATOPIBA/2021/MATOPIBA_2021.xls"
)

IBGE_MALHAS_API_TEMPLATE = (
    "https://servicodados.ibge.gov.br/api/v3/malhas/estados/{state}"
    "?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=maxima&data=2025"
)

UF_MAP = {"21": "MA", "17": "TO", "22": "PI", "29": "BA"}


def build_matopiba() -> dict:
    DATA_REF.mkdir(parents=True, exist_ok=True)

    print("[1/4] Baixando lista oficial dos 337 municípios do IBGE...")
    req = urllib.request.Request(IBGE_MATOPIBA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()

    df_ibge = pd.read_excel(io.BytesIO(content))
    df_ibge["CD_MUN"] = df_ibge["CD_MUN"].astype(str)
    df_ibge["state"] = df_ibge["CD_MUN"].str[:2].map(UF_MAP)
    df_ibge = df_ibge.sort_values(["state", "CD_MUN"]).reset_index(drop=True)

    if len(df_ibge) != 337:
        raise ValueError(f"Esperado 337 municípios, encontrado {len(df_ibge)}")

    csv_path = DATA_REF / "matopiba_municipalities.csv"
    df_ibge[["CD_MUN", "NM_MUN", "state", "cod_Mun_MATOPIBA"]].to_csv(
        csv_path, index=False, encoding="utf-8"
    )
    print(f"  Salvo: {csv_path} ({len(df_ibge)} municípios)")

    target_codes = set(df_ibge["CD_MUN"])

    print("[2/4] Baixando malhas municipais oficiais do IBGE (qualidade máxima)...")
    dfs_states = []
    for st in ["TO", "MA", "PI", "BA"]:
        api_url = IBGE_MALHAS_API_TEMPLATE.format(state=st)
        r = requests.get(api_url, timeout=120)
        r.raise_for_status()
        gdf_st = gpd.read_file(io.StringIO(r.text))
        gdf_st["codarea"] = gdf_st["codarea"].astype(str)
        gdf_target = gdf_st[gdf_st["codarea"].isin(target_codes)].copy()
        gdf_target["state"] = st
        print(f"  {st}: {len(gdf_target)} municípios filtrados")
        dfs_states.append(gdf_target)

    gdf_all = pd.concat(dfs_states, ignore_index=True)
    if len(gdf_all) != 337:
        raise ValueError(f"Esperado 337 feições espaciais, encontrado {len(gdf_all)}")

    print("[3/4] Dissolvendo polígonos municipais em boundaries estaduais e único...")
    dissolved_states = gdf_all.dissolve(by="state").reset_index()
    states_geojson_path = DATA_REF / "matopiba_states.geojson"
    dissolved_states.to_file(states_geojson_path, driver="GeoJSON")
    print(f"  Salvo: {states_geojson_path} (4 estados)")

    dissolved = gdf_all.dissolve()

    dissolved_5880 = dissolved.to_crs("EPSG:5880")
    area_ha_5880 = float(dissolved_5880.geometry.area.iloc[0] / 10000.0)
    area_km2_5880 = float(dissolved_5880.geometry.area.iloc[0] / 1e6)

    geojson_str = dissolved.to_json()
    geojson_dict = json.loads(geojson_str)

    metadata = {
        "name": "MATOPIBA",
        "source": (
            "IBGE - Estrutura Territorial MATOPIBA 2021 (MATOPIBA_2021.xls) + "
            "IBGE Malhas Municipais 2025 via Servico de Dados (qualidade maxima, data=2025)"
        ),
        "definition": "delimitação operacional do MATOPIBA reconstruída a partir da lista oficial de 337 municípios e da malha municipal IBGE 2025",
        "retrieval_date": datetime.now(timezone.utc).isoformat(),
        "n_municipalities": 337,
        "crs_original": "EPSG:4674 (SIRGAS 2000)",
        "area_ha_epsg5880": round(area_ha_5880, 2),
        "area_km2_epsg5880": round(area_km2_5880, 2),
        "states": ["MA", "TO", "PI", "BA"],
        "state_counts": df_ibge["state"].value_counts().to_dict(),
    }

    geojson_dict["features"][0]["properties"] = metadata

    geojson_path = DATA_REF / "matopiba_boundary.geojson"
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_dict, f, ensure_ascii=False, indent=2)

    sha256_geojson = hashlib.sha256(geojson_path.read_bytes()).hexdigest()
    sha256_csv = hashlib.sha256(csv_path.read_bytes()).hexdigest()

    print(f"[4/4] Geometria congelada salva:")
    print(f"  GeoJSON: {geojson_path}")
    print(f"  SHA-256 GeoJSON: {sha256_geojson}")
    print(f"  SHA-256 CSV:     {sha256_csv}")
    print(f"  Área EPSG:5880:  {area_ha_5880:,.2f} ha ({area_km2_5880:,.2f} km²)")

    return {
        "boundary_file": str(geojson_path),
        "municipalities_file": str(csv_path),
        "sha256_geojson": sha256_geojson,
        "sha256_csv": sha256_csv,
        "area_ha_epsg5880": area_ha_5880,
        "area_km2_epsg5880": area_km2_5880,
        "n_municipalities": 337,
        "metadata": metadata,
    }


if __name__ == "__main__":
    build_matopiba()
