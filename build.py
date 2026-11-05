"""
Checks flow.json (questions + videos) and optionally makes a QR code for the site.

Usage:
    python build.py                                   # check flow.json and the video files
    python build.py --url https://your-site.netlify.app/   # also write qr.png + qr.svg
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLOW_FILE = ROOT / "flow.json"
BIG_FILE = 100 * 1024 * 1024  # 100 MB, the GitHub Pages per-file limit


def check_flow() -> bool:
    ok = True
    try:
        flow = json.loads(FLOW_FILE.read_text("utf-8"))
    except FileNotFoundError:
        print("flow.json is missing")
        return False
    except ValueError as e:
        print(f"flow.json is not valid JSON: {e}")
        return False

    steps = flow.get("steps")
    if not isinstance(steps, list) or not steps:
        print("flow.json has no steps")
        return False

    questions = videos = 0
    for n, step in enumerate(steps, 1):
        kind = step.get("type")
        if kind == "question":
            questions += 1
            opts = step.get("options") or []
            correct = [o for o in opts if o.get("correct")]
            label = (step.get("text") or "")[:50]
            if not step.get("text"):
                print(f"  step {n}: question has no text"); ok = False
            if len(opts) < 1:
                print(f"  step {n}: question '{label}' needs at least 1 option"); ok = False
            if not correct:
                print(f"  step {n}: question '{label}' has no option marked \"correct\": true"); ok = False
            if any(not o.get("label") for o in opts):
                print(f"  step {n}: question '{label}' has an option without a label"); ok = False
        elif kind == "text":
            if not step.get("text"):
                print(f"  step {n}: text step has no text"); ok = False
        elif kind == "shots":
            if not step.get("button"):
                print(f"  step {n}: shots step has no button text"); ok = False
        elif kind == "video":
            videos += 1
            src = step.get("src") or ""
            if not src:
                print(f"  step {n}: video has no src"); ok = False
            elif src.startswith(("http://", "https://")):
                print(f"  step {n}: {src} (external, not checked)")
            else:
                path = ROOT / src
                if not path.is_file():
                    print(f"  step {n}: {src} NOT FOUND (put the file there or fix the name)"); ok = False
                else:
                    size = path.stat().st_size
                    note = ""
                    if size > BIG_FILE:
                        note = "  <- over 100 MB; fine on Netlify, too big for GitHub Pages"
                    if path.suffix.lower() == ".mov":
                        note += "  <- .mov may not play on Android; convert to .mp4"
                    print(f"  step {n}: {src} ({size / 1024 / 1024:.1f} MB){note}")
        else:
            print(f"  step {n}: unknown type {kind!r} (use \"question\", \"text\", \"shots\" or \"video\")"); ok = False

    print(f"{len(steps)} steps: {questions} questions, {videos} videos")
    print("flow.json OK" if ok else "flow.json has problems (see above)")
    return ok


def _rounded_svg(matrix, box=10, radius=4.2, border=2):
    """SVG of the QR with rounded outer corners on each run of modules."""
    n = len(matrix)
    size = (n + 2 * border) * box
    def dark(r, c):
        return 0 <= r < n and 0 <= c < n and matrix[r][c]
    parts = []
    for r in range(n):
        for c in range(n):
            if not matrix[r][c]:
                continue
            x, y, b, k = (c + border) * box, (r + border) * box, box, radius
            tl = not dark(r - 1, c) and not dark(r, c - 1)
            tr = not dark(r - 1, c) and not dark(r, c + 1)
            br = not dark(r + 1, c) and not dark(r, c + 1)
            bl = not dark(r + 1, c) and not dark(r, c - 1)
            d = [f"M{x + (k if tl else 0)},{y}"]
            d.append(f"H{x + b - (k if tr else 0)}")
            if tr: d.append(f"a{k},{k} 0 0 1 {k},{k}")
            d.append(f"V{y + b - (k if br else 0)}")
            if br: d.append(f"a{k},{k} 0 0 1 -{k},{k}")
            d.append(f"H{x + (k if bl else 0)}")
            if bl: d.append(f"a{k},{k} 0 0 1 -{k},-{k}")
            d.append(f"V{y + (k if tl else 0)}")
            if tl: d.append(f"a{k},{k} 0 0 1 {k},-{k}")
            d.append("Z")
            parts.append("".join(d))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}" shape-rendering="geometricPrecision">'
            f'<rect width="100%" height="100%" fill="#fff"/>'
            f'<path fill="#000" d="{" ".join(parts)}"/></svg>')


def make_qr(url: str):
    try:
        import qrcode
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
    except ImportError:
        sys.exit('QR library missing. Run:  python -m pip install "qrcode[pil]"')

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=2, box_size=24)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer()).save(ROOT / "qr.png")
    (ROOT / "qr.svg").write_text(_rounded_svg(qr.get_matrix()), encoding="utf-8")

    print("QR code for " + url)
    print("  -> qr.png (print-ready, rounded)")
    print("  -> qr.svg (scales to any size, rounded)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="public address of the site; writes qr.png and qr.svg")
    args = ap.parse_args()
    good = check_flow()
    if args.url:
        make_qr(args.url)
    sys.exit(0 if good else 1)
