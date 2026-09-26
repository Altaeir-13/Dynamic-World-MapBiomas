from __future__ import annotations

import sys

import ee


PROJECT_ID = "dynamicworld-x-mapbiomas"
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
            .filterDate("2024-01-01", "2025-01-01")
        )

        count = collection.size().getInfo()

        first_image = collection.first()
        if first_image is None:
            raise RuntimeError(
                "Nenhuma imagem Dynamic World encontrada para 2024."
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
        print(f"Imagens em 2024: {count:,}")
        print(f"Bandas encontradas: {bands}")

        if missing_bands:
            print(
                "ERRO: bandas esperadas ausentes: "
                + ", ".join(sorted(missing_bands))
            )
            return 1

        print("OK: Earth Engine e Dynamic World acessíveis.")
        return 0

    except Exception as exc:
        print(f"ERRO: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())