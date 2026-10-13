from __future__ import annotations

import sys

import ee


import os
PROJECT_ID = os.environ.get("EE_PROJECT", "dynamicworld-x-mapbiomas")
DYNAMIC_WORLD_COLLECTION = "GOOGLE/DYNAMICWORLD/V1"


def initialize_earth_engine() -> None:
    try:
        ee.Initialize(project=PROJECT_ID)
    except Exception:
        print("Autenticação do Google Earth Engine necessária.")
        ee.Authenticate()
        ee.Initialize(project=PROJECT_ID)


def main() -> int:
    try:
        initialize_earth_engine()

        collection = (
            ee.ImageCollection(DYNAMIC_WORLD_COLLECTION)
            .filterDate("2025-01-01", "2026-01-01")
        )

        count = collection.size().getInfo()

        first_image = collection.first()
        if first_image is None:
            raise RuntimeError(
                "Nenhuma imagem Dynamic World encontrada para 2025."
            )

        bands = first_image.bandNames().getInfo()

        expected_bands = {
            "water",
            "trees",
            "grass",
            "flooded_vegetation",
            "crops",
            "shrub_and_scrub",
            "built",
            "bare",
            "snow_and_ice",
            "label",
        }

        missing_bands = expected_bands.difference(bands)

        print(f"Google Cloud Project: {PROJECT_ID}")
        print(f"Collection: {DYNAMIC_WORLD_COLLECTION}")
        print(f"Imagens em 2025: {count:,}")
        print(f"Bandas encontradas: {bands}")

        if missing_bands:
            print(
                "ERRO: bandas esperadas ausentes: "
                + ", ".join(sorted(missing_bands))
            )
            return 1

        # Check MapBiomas 10m Col 4
        mb_asset = "projects/mapbiomas-public/assets/brazil/lulc_10m/collection4/mapbiomas_10m_collection4_coverage_v1"
        mb_image = ee.Image(mb_asset)
        mb_bands = mb_image.bandNames().getInfo()
        if "classification_2025" not in mb_bands:
            print(f"ERRO: classification_2025 ausente no asset MapBiomas: {mb_asset}")
            return 1
        print(f"MapBiomas 10m Col 4 OK: banda classification_2025 presente. Total bandas: {len(mb_bands)}")

        print("OK: Earth Engine, Dynamic World (2025) e MapBiomas (2025) acessíveis.")
        return 0

    except Exception as exc:
        print(f"ERRO: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())