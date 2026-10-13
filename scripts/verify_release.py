"""Read-only integrity checks. Does not run GEE, fit models or rewrite results."""
from pathlib import Path
import argparse, ast, csv, hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', action='store_true', help='Check parquet schemas and materialized sample membership')
    args = parser.parse_args()
    report = {}
    for name in ('tables/manuscript_results_manifest.csv', 'docs/provenance/release_checksums.csv'):
        path = ROOT / name
        assert path.is_file(), f'Missing manifest: {name}'
        records = list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))
        for row in records:
            rel = row.get('relative_path') or row['path']
            target = (ROOT / rel).resolve()
            assert target.is_relative_to(ROOT), f'Unsafe manifest path: {rel}'
            assert target.is_file(), f'Missing: {rel}'
            assert sha(target) == row['sha256'], f'Hash mismatch: {rel}'
            assert target.stat().st_size == int(row['size_bytes']), f'Size mismatch: {rel}'
        report[name] = {'verified': len(records)}
    public_sources = [ROOT/'src/gee'/n for n in json.loads((ROOT/'config/release_sources.json').read_text())['gee']]
    public_sources += list((ROOT/'src/analysis').glob('*.py')) + list((ROOT/'scripts').glob('*.py'))
    for path in public_sources:
        ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
    report['python_syntax'] = len(public_sources)
    for path in (ROOT/'docs/provenance').glob('*.zip'):
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None, f'Corrupt archive: {path.name}'
            for name in archive.namelist():
                assert not Path(name).is_absolute() and '..' not in Path(name).parts
        report[path.name] = 'CRC OK'
    if args.data:
        import pandas as pd
        annual = pd.read_parquet(ROOT/'data/processed/samples_annual.parquet')
        monthly = pd.read_parquet(ROOT/'data/processed/dw_monthly.parquet')
        points = pd.read_csv(ROOT/'data/processed/master_sampling_points.csv', keep_default_na=False)
        assert len(annual) == len(points) == 40000 and len(monthly) == 480000
        assert annual.sample_id.is_unique and points.sample_id.is_unique
        assert not monthly.duplicated(['sample_id','month']).any()
        assert set(annual.sample_id) == set(points.sample_id) == set(monthly.sample_id)
        assert (annual.main_sample == 1).sum() == 20000
        assert (annual.n_valid_months >= 8).all()
        assert (pd.to_numeric(annual.design_weight_robust, errors='raise') > 0).all()
        assert (pd.to_numeric(annual.loc[annual.main_sample == 1, 'design_weight_main'], errors='raise') > 0).all()
        assert set(annual.regime) == {'AA','AN','NA','NN'}
        for col in ['main_sample','regime','lat','lon']:
            lhs=annual.set_index('sample_id')[col].sort_index()
            rhs=points.set_index('sample_id')[col].sort_index()
            if col in ('lat','lon'):
                assert (lhs-rhs).abs().max() < 1e-10
            else:
                assert (lhs==rhs).all(), f'Master membership mismatch: {col}'
        municipalities = pd.read_csv(ROOT/'data/reference/matopiba_municipalities.csv')
        assert len(municipalities) == 337 and municipalities.CD_MUN.is_unique
        report['data'] = {'annual_rows':len(annual),'monthly_rows':len(monthly),'main_rows':20000,'municipalities':337}
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
