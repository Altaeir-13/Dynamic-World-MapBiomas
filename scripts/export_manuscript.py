"""Export the final editable DOCX with LibreOffice into a separate directory."""
from pathlib import Path
import argparse, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'paper/manuscript_space_week_nordeste_2026_final_title_references.docx'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--soffice', default=None, help='Path to soffice executable if absent from PATH')
    args=parser.parse_args()
    output=args.output_dir.resolve()
    assert output != SOURCE.parent.resolve(), 'Export into a separate directory to preserve the frozen PDF'
    exe=args.soffice or shutil.which('soffice') or shutil.which('soffice.exe')
    if not exe:
        parser.error('Install LibreOffice and put soffice on PATH, or use --soffice')
    output.mkdir(parents=True, exist_ok=True)
    target=output/(SOURCE.stem+'.pdf')
    assert not target.exists(), f'Output already exists: {target}'
    with tempfile.TemporaryDirectory(prefix='lo_profile_',dir=output) as profile:
        subprocess.run([exe,'-env:UserInstallation='+Path(profile).as_uri(),'--headless','--convert-to','pdf','--outdir',str(output),str(SOURCE)],check=True,timeout=180)
    assert target.is_file(), 'LibreOffice did not generate a PDF'
    print(target)

if __name__ == '__main__':
    main()
