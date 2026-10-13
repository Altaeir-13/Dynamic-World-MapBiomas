"""
monitor_and_process_batches.py — Monitora e processa os 10 batches de exportação W2W
=====================================================================================
Executa:
  1. Consulta de status no GEE para os 10 batches registrados em tables/canonical_w2w_batch_tasks.csv.
  2. Atualização dos campos de estado, tempos e erros em tables/canonical_w2w_batch_tasks.csv.
  3. Verificação e download automático de cada CSV concluído do Google Drive (pasta matopiba_exports).
  4. Quando TODOS os 10 batches forem concluídos e baixados:
     - Concatena todos os registros em data/processed/canonical_wall_to_wall_by_slice.csv.
     - Valida: 182 linhas, 182 slices únicos, 0 duplicatas, 0 missing vs manifesto.
     - Executa o fechamento de área e métricas de Pontius & Millones (2011).
     - Atualiza data/processed/wall_to_wall_summary.csv (MATOPIBA + 4 estados).
     - Atualiza tables/sampling_frame_10m.csv.
     - Recalcula cotas científicas (tables/sampling_quotas.csv) e compara com antigas.
     - Gera nova alocação operacional (tables/slice_sampling_allocation_final.csv) garantindo pi > 0.
"""

from __future__ import annotations

import io
import math
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PROC = BASE_DIR / "data" / "processed"
BATCHES_DIR = DATA_PROC / "batches"
BATCHES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR = BASE_DIR / "tables"

MANIFEST_CSV = TABLES_DIR / "canonical_w2w_batch_manifest.csv"
TASKS_CSV = TABLES_DIR / "canonical_w2w_batch_tasks.csv"
BY_SLICE_CSV = DATA_PROC / "canonical_wall_to_wall_by_slice.csv"
SUMMARY_CSV = DATA_PROC / "wall_to_wall_summary.csv"
FRAME_CSV = TABLES_DIR / "sampling_frame_10m.csv"
QUOTAS_CSV = TABLES_DIR / "sampling_quotas.csv"
FINAL_ALLOC_CSV = TABLES_DIR / "slice_sampling_allocation_final.csv"

# Preserved invalid artifacts for comparison
OLD_W2W_CSV = DATA_PROC / "wall_to_wall_summary_SLICE_DEPENDENT_INVALID.csv"
OLD_QUOTAS_CSV = TABLES_DIR / "sampling_quotas_SLICE_DEPENDENT_INVALID.csv"

import sys
sys.path.insert(0, str(BASE_DIR))

import ee
import ee.oauth
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from src.gee.dw_annual import PROJECT_ID


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def get_drive_service():
    creds_args = ee.oauth.get_credentials_arguments()
    creds = Credentials(
        None,
        refresh_token=creds_args["refresh_token"],
        token_uri=creds_args["token_uri"],
        client_id=creds_args["client_id"],
        client_secret=creds_args["client_secret"],
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    return build("drive", "v3", credentials=creds)


def download_drive_file(service, file_id: str, dest_path: Path):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()


def check_and_download_batches(drive_service) -> dict[str, bool]:
    """Verifica e baixa os CSVs dos batches disponíveis no Google Drive."""
    query = "trashed = false and name contains 'canonical_w2w_batch_'"
    results = drive_service.files().list(
        q=query,
        pageSize=50,
        fields="files(id, name, createdTime, size)",
    ).execute()
    files = results.get("files", [])
    drive_files = {f["name"]: f for f in files}

    df_manifest = pd.read_csv(MANIFEST_CSV)
    batch_ids = sorted(df_manifest["batch_id"].unique())
    status_map = {}
    for b_id in batch_ids:
        expected_name = f"{b_id}_10m.csv"
        local_path = BATCHES_DIR / expected_name

        if local_path.exists() and local_path.stat().st_size > 500:
            status_map[b_id] = True
        elif expected_name in drive_files and int(drive_files[expected_name].get("size", 0)) > 500:
            f_info = drive_files[expected_name]
            log(f"Baixando {expected_name} do Google Drive ({f_info.get('size')} bytes)...")
            download_drive_file(drive_service, f_info["id"], local_path)
            log(f"  {expected_name} baixado com sucesso.")
            status_map[b_id] = True
        else:
            status_map[b_id] = False

    return status_map


def check_status() -> tuple[pd.DataFrame, bool]:
    ee.Initialize(project=PROJECT_ID)
    drive_service = get_drive_service()

    df_tasks = pd.read_csv(TASKS_CSV)
    download_status = check_and_download_batches(drive_service)

    updated_records = []
    all_succeeded = True
    any_failed = False

    for _, row in df_tasks.iterrows():
        b_id = row["batch_id"]
        t_id = row["task_id"]

        try:
            op = ee.data.getOperation(f"projects/{PROJECT_ID}/operations/{t_id}")
            meta = op.get("metadata", {})
            st = meta.get("state", row["state"])
            err = op.get("error", {}).get("message") if op.get("error") else None
            c_time = meta.get("createTime")
            s_time = meta.get("startTime")
            u_time = meta.get("updateTime")
        except Exception as e:
            st = row["state"]
            err = None if row.get("downloaded") else str(e)
            c_time = row["create_time"]
            s_time = row["start_time"]
            u_time = row["update_time"]

        is_dl = download_status.get(b_id, False)
        if st != "SUCCEEDED" and not is_dl:
            all_succeeded = False
        if st == "FAILED":
            any_failed = True

        updated_records.append({
            "batch_id": b_id,
            "task_id": t_id,
            "description": row["description"],
            "state": st,
            "downloaded": is_dl,
            "create_time": c_time,
            "start_time": s_time,
            "update_time": u_time,
            "error_message": err,
        })

    df_updated = pd.DataFrame(updated_records)
    df_updated.to_csv(TASKS_CSV, index=False)

    print("\n" + "=" * 80)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] STATUS DOS 10 BATCHES CANÔNICOS")
    print("=" * 80)
    print(df_updated[["batch_id", "state", "downloaded", "error_message"]].to_string(index=False))

    return df_updated, all_succeeded


def process_all_batches_into_canonical_w2w():
    log("\n" + "=" * 80)
    log("TODOS OS 10 BATCHES CONCLUÍDOS! PROCESSANDO CENSO CANÔNICO 10M...")
    log("=" * 80)

    # 1. Carregar manifesto oficial
    df_manifest = pd.read_csv(MANIFEST_CSV)
    manifest_slices = set(df_manifest["slice_id"])
    assert len(manifest_slices) == 182

    # 2. Carregar e concatenar os arquivos CSV dos batches
    dfs = []
    for b_id in sorted(df_manifest["batch_id"].unique()):
        p = BATCHES_DIR / f"{b_id}_10m.csv"
        assert p.exists(), f"Arquivo do batch ausente: {p}"
        df_b = pd.read_csv(p)
        dfs.append(df_b)

    df_all = pd.concat(dfs, ignore_index=True)
    log(f"Total bruto de registros carregados: {len(df_all)}")

    # 3. Validações estritas da Seção 8:
    # N linhas finais = 182
    # N slice_id únicos = 182
    # duplicatas = 0
    # missing slices = 0
    # unexpected slices = 0
    assert len(df_all) == 182, f"Erro: Esperado 182 linhas, obtido {len(df_all)}"
    assert df_all["slice_id"].nunique() == 182, f"Erro: Esperado 182 slices únicos, obtido {df_all['slice_id'].nunique()}"

    res_slices = set(df_all["slice_id"])
    missing = manifest_slices - res_slices
    unexpected = res_slices - manifest_slices
    assert len(missing) == 0, f"Slices ausentes vs manifesto: {missing}"
    assert len(unexpected) == 0, f"Slices inesperadas: {unexpected}"
    log("VALIDAÇÃO DE SLICES (Seção 8): PASS (182 slices canônicos, 0 duplicatas, 0 missing, 0 unexpected)")

    # 4. Ordenar deterministicamente por state, slice_id e salvar
    df_all = df_all.sort_values(by=["state", "slice_id"]).reset_index(drop=True)
    df_all.to_csv(BY_SLICE_CSV, index=False)
    log(f"Salvo arquivo canônico por slice: {BY_SLICE_CSV}")

    # 5. Agregações para MATOPIBA e 4 Estados
    sum_cols = [
        "total_covered_ha", "eligible_ha", "excluded_mb_ha", "insufficient_dw_temporal_ha",
        "AA_ha", "AN_ha", "NA_ha", "NN_ha",
        "total_covered_count", "eligible_count", "excluded_mb_count", "insufficient_dw_temporal_count",
        "AA_count", "AN_count", "NA_count", "NN_count",
    ]
    for m in range(13):
        sum_cols.extend([f"m_{m}_ha", f"m_{m}_count"])

    for col in sum_cols:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce").fillna(0.0)

    # Estado por estado + MATOPIBA total
    summary_rows = []
    regions = ["MATOPIBA", "MA", "TO", "PI", "BA"]

    for reg in regions:
        if reg == "MATOPIBA":
            sub = df_all
        else:
            sub = df_all[df_all["state"] == reg]

        tot_cov = sub["total_covered_ha"].sum()
        elig = sub["eligible_ha"].sum()
        excl = sub["excluded_mb_ha"].sum()
        insuf = sub["insufficient_dw_temporal_ha"].sum()

        aa = sub["AA_ha"].sum()
        an = sub["AN_ha"].sum()
        na = sub["NA_ha"].sum()
        nn = sub["NN_ha"].sum()

        # Pontius & Millones (2011) components
        # Confusion matrix on eligible domain:
        # Columns = MapBiomas (Crop=A, Noncrop=N)
        # Rows = Dynamic World (Crop=A, Noncrop=N)
        # [AA, NA]
        # [AN, NN]
        agree = ((aa + nn) / elig) * 100.0 if elig > 0 else 0.0
        disagree = ((an + na) / elig) * 100.0 if elig > 0 else 0.0
        mb_crop_tot = aa + an
        dw_crop_tot = aa + na
        q_disagree = (abs(mb_crop_tot - dw_crop_tot) / elig) * 100.0 if elig > 0 else 0.0
        alloc_disagree = 2.0 * min(an, na) / elig * 100.0 if elig > 0 else 0.0

        summary_rows.append({
            "region": reg,
            "total_area_ha": tot_cov,
            "raster_covered_area_ha": tot_cov,
            "eligible_area_ha": elig,
            "excluded_mb_area_ha": excl,
            "insufficient_dw_temporal_area_ha": insuf,
            "AA_area_ha": aa,
            "AN_area_ha": an,
            "NA_area_ha": na,
            "NN_area_ha": nn,
            "AA_pct_eligible": (aa / elig) * 100.0 if elig > 0 else 0.0,
            "AN_pct_eligible": (an / elig) * 100.0 if elig > 0 else 0.0,
            "NA_pct_eligible": (na / elig) * 100.0 if elig > 0 else 0.0,
            "NN_pct_eligible": (nn / elig) * 100.0 if elig > 0 else 0.0,
            "agreement_pct": agree,
            "disagreement_pct": disagree,
            "quantity_disagreement": q_disagree,
            "allocation_disagreement": alloc_disagree,
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(SUMMARY_CSV, index=False)
    log(f"Salvo resumo wall-to-wall: {SUMMARY_CSV}")
    print("\n--- RESUMO CANÔNICO WALL-TO-WALL 10M ---")
    print(df_summary[["region", "eligible_area_ha", "AA_pct_eligible", "AN_pct_eligible", "NA_pct_eligible", "NN_pct_eligible", "agreement_pct", "disagreement_pct"]])

    # Validação de fechamento de área (Seção 8 e 9):
    for _, r in df_summary.iterrows():
        reg = r["region"]
        cov = r["raster_covered_area_ha"]
        el = r["eligible_area_ha"]
        ex = r["excluded_mb_area_ha"]
        ins = r["insufficient_dw_temporal_area_ha"]
        part_sum = el + ex + ins
        diff_part = abs(cov - part_sum)
        assert diff_part < 25.0 or (diff_part / cov) < 1e-4, f"Fechamento falhou em {reg}: cov={cov}, soma={part_sum}, diff={diff_part}"

        reg_sum = r["AA_area_ha"] + r["AN_area_ha"] + r["NA_area_ha"] + r["NN_area_ha"]
        diff_reg = abs(el - reg_sum)
        assert diff_reg < 1.0, f"Fechamento de regimes falhou em {reg}: el={el}, soma={reg_sum}, diff={diff_reg}"
    log("FECHAMENTO DE ÁREA (Seção 8 e 9): PASS (100% de consistência contábil)")

    # 6. Reconstruir tables/sampling_frame_10m.csv (Seção 9)
    frame_rows = []
    regimes = ["AA", "AN", "NA", "NN"]
    for _, row in df_all.iterrows():
        st = row["state"]
        s_id = row["slice_id"]
        for reg in regimes:
            a_hs = float(row[f"{reg}_ha"])
            n_hs = int(round(row[f"{reg}_count"]))
            frame_rows.append({
                "state": st,
                "regime": reg,
                "slice_id": s_id,
                "A_hs": a_hs,
                "N_hs_exact": n_hs,
            })
    df_frame = pd.DataFrame(frame_rows)
    df_frame.to_csv(FRAME_CSV, index=False)
    log(f"Salvo sampling frame 10m: {FRAME_CSV} ({len(df_frame)} registros)")

    # 7. Recalcular cotas científicas Hamilton (Seção 9)
    N_MAIN = 20000
    N_ROBUST = 40000
    FLOOR_MAIN = 400

    strata = df_frame.groupby(["state", "regime"]).agg(
        A_h=("A_hs", "sum"),
        N_h=("N_hs_exact", "sum"),
    ).reset_index()

    tot_area = strata["A_h"].sum()
    rem_points = N_MAIN - (FLOOR_MAIN * len(strata))
    assert rem_points > 0

    strata["raw_share"] = (strata["A_h"] / tot_area) * rem_points
    strata["int_part"] = strata["raw_share"].apply(math.floor).astype(int)
    strata["remainder"] = strata["raw_share"] - strata["int_part"]

    allocated = strata["int_part"].sum()
    surplus = rem_points - allocated

    strata = strata.sort_values(by=["remainder", "A_h"], ascending=[False, False]).reset_index(drop=True)
    strata["extra"] = 0
    if surplus > 0:
        strata.loc[:surplus - 1, "extra"] = 1

    strata["n_main"] = FLOOR_MAIN + strata["int_part"] + strata["extra"]
    strata["n_robust"] = strata["n_main"] * 2
    assert strata["n_main"].sum() == N_MAIN
    assert strata["n_robust"].sum() == N_ROBUST

    st_order = {"MA": 1, "TO": 2, "PI": 3, "BA": 4}
    reg_order = {"AA": 1, "AN": 2, "NA": 3, "NN": 4}
    strata["st_ord"] = strata["state"].map(st_order)
    strata["reg_ord"] = strata["regime"].map(reg_order)
    strata = strata.sort_values(["st_ord", "reg_ord"]).drop(
        columns=["st_ord", "reg_ord", "raw_share", "int_part", "remainder", "extra"]
    ).reset_index(drop=True)

    strata.to_csv(QUOTAS_CSV, index=False)
    log(f"Salvas novas cotas científicas: {QUOTAS_CSV}")
    print("\n--- NOVAS COTAS CIENTÍFICAS (CANÔNICAS) ---")
    print(strata[["state", "regime", "A_h", "N_h", "n_main", "n_robust"]].to_string(index=False))

    # Comparação old vs new quotas
    if OLD_QUOTAS_CSV.exists():
        df_old_q = pd.read_csv(OLD_QUOTAS_CSV)
        merged_q = pd.merge(df_old_q, strata, on=["state", "regime"], suffixes=("_old", "_new"))
        print("\n--- COMPARAÇÃO DE COTAS (SLICE_DEPENDENT_INVALID vs CANÔNICA FIXA) ---")
        print(merged_q[["state", "regime", "n_main_old", "n_main_new", "n_robust_old", "n_robust_new"]].to_string(index=False))

    # 8. Reconstruir alocação operacional por slice (Seção 10)
    alloc_rows = []
    for _, st_row in strata.iterrows():
        st = st_row["state"]
        reg = st_row["regime"]
        n_rob_target = int(st_row["n_robust"])

        sub = df_frame[(df_frame["state"] == st) & (df_frame["regime"] == reg)].copy()
        sub = sub[sub["N_hs_exact"] > 0].reset_index(drop=True)

        k_active = len(sub)
        assert k_active > 0, f"Sem subestratos ativos para {st} x {reg}!"
        assert n_rob_target >= k_active, f"Cota robusta {n_rob_target} < k_active {k_active}!"

        sub["n_base"] = 1
        points_to_distribute = n_rob_target - k_active
        tot_N = sub["N_hs_exact"].sum()

        sub["raw_share"] = (sub["N_hs_exact"] / tot_N) * points_to_distribute
        sub["int_part"] = sub["raw_share"].apply(math.floor).astype(int)
        sub["remainder"] = sub["raw_share"] - sub["int_part"]

        allocated_int = sub["int_part"].sum()
        leftover = points_to_distribute - allocated_int

        sub = sub.sort_values(by=["remainder", "slice_id"], ascending=[False, True]).reset_index(drop=True)
        sub["extra"] = 0
        if leftover > 0:
            sub.loc[:leftover - 1, "extra"] = 1

        sub["n_robust_hs"] = sub["n_base"] + sub["int_part"] + sub["extra"]
        assert sub["n_robust_hs"].sum() == n_rob_target
        assert (sub["n_robust_hs"] >= 1).all()

        sub["pi_robust_hs"] = sub["n_robust_hs"] / sub["N_hs_exact"]
        sub["design_weight_robust_hs"] = 1.0 / sub["pi_robust_hs"]
        sub["area_weight_robust_hs"] = (sub["A_hs"] * 10000.0) / sub["n_robust_hs"]
        alloc_rows.append(sub)

    df_alloc = pd.concat(alloc_rows, ignore_index=True)
    df_alloc["st_ord"] = df_alloc["state"].map(st_order)
    df_alloc["reg_ord"] = df_alloc["regime"].map(reg_order)
    df_alloc = df_alloc.sort_values(["st_ord", "reg_ord", "slice_id"]).drop(
        columns=["st_ord", "reg_ord", "n_base", "raw_share", "int_part", "remainder", "extra"]
    ).reset_index(drop=True)

    alloc_out_cols = [
        "state", "regime", "slice_id", "A_hs", "N_hs_exact",
        "n_robust_hs", "pi_robust_hs", "design_weight_robust_hs", "area_weight_robust_hs"
    ]
    df_alloc[alloc_out_cols].to_csv(FINAL_ALLOC_CSV, index=False)
    log(f"Salva alocação operacional final: {FINAL_ALLOC_CSV} ({len(df_alloc)} subestratos ativos)")
    log(f"Total n_robust: {df_alloc['n_robust_hs'].sum():,} (Alvo: 40.000)")
    log(f"Min pi_robust_hs: {df_alloc['pi_robust_hs'].min():.8e}")
    assert (df_alloc["pi_robust_hs"] > 0).all()
    log("PROVA FORMAL DE pi > 0: PASS (100% dos subestratos com N_hs > 0 têm n_robust_hs >= 1 e pi > 0)")


if __name__ == "__main__":
    df_tasks, all_done = check_status()
    failed_tasks = df_tasks[df_tasks["state"] == "FAILED"]
    if not failed_tasks.empty:
        print("\n" + "!" * 80)
        print("ALERTA: BATCH FALHOU:")
        print(failed_tasks[["batch_id", "task_id", "error_message"]])
        print("!" * 80)
        sys.exit(2)
    elif all_done:
        process_all_batches_into_canonical_w2w()
    else:
        print("\nAguardando conclusão de todos os batches...")
