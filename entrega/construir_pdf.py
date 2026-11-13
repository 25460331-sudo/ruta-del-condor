"""Convierte REPORTE_TECNICO.md en un PDF (usa Chrome sin pantalla). Uso: python entrega/construir_pdf.py"""
import pathlib, re, subprocess, markdown

raiz = pathlib.Path(__file__).resolve().parent.parent
md = (raiz / "REPORTE_TECNICO.md").read_text(encoding="utf-8")
def arreglar(texto):
    """Pone una línea en blanco antes de tablas y listas (lo exige este conversor)."""
    out, dentro_codigo = [], False
    for linea in texto.split(chr(10)):
        if linea.startswith("```"):
            dentro_codigo = not dentro_codigo
        if not dentro_codigo and out and out[-1].strip():
            ant = out[-1]
            if linea.startswith("|") and not ant.startswith("|"):
                out.append("")
            elif (linea.startswith("- ") or linea[:3] in ("1. ", "2. ", "3. ", "4. ")) and not (ant.startswith("-") or ant[:1].isdigit()):
                out.append("")
        out.append(linea)
    return chr(10).join(out)


md = arreglar(md)
cuerpo = markdown.markdown(md, extensions=["tables", "fenced_code"])
css = """
@page { size: A4; margin: 13mm 14mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.2pt; line-height: 1.38; color: #111; }
h1 { font-size: 18pt; margin: 0 0 2px; color: #0b3d66; } h2 { font-size: 12.5pt; margin: 12px 0 4px; color: #0b3d66; border-bottom: 1px solid #c9d6e2; padding-bottom: 1px; }
p { margin: 3px 0; } table { border-collapse: collapse; margin: 4px 0; width: 100%; } th, td { border: 1px solid #c9d6e2; padding: 2px 6px; text-align: left; } th { background: #eaf1f8; }
pre { background: #f3f6f9; padding: 4px 6px; font-size: 8.4pt; line-height: 1.25; margin: 4px 0; } code { font-family: Consolas, monospace; font-size: 9pt; background: #f3f6f9; }
pre code { background: none; } ol, ul { margin: 3px 0 3px 16px; padding: 0; } li { margin: 1px 0; } img { max-width: 100%; }
"""
html = f"<!doctype html><html lang='es'><head><meta charset='utf-8'><style>{css}</style></head><body>{cuerpo}</body></html>"
(raiz / "entrega" / "_reporte.html").write_text(html, encoding="utf-8")
# las rutas de las imágenes son relativas a la raíz del proyecto
(raiz / "_reporte.html").write_text(html, encoding="utf-8")
chrome = next(p for p in ["C:/Program Files/Google/Chrome/Application/chrome.exe",
                          "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"] if pathlib.Path(p).exists())
salida = raiz / "entrega" / "Reporte_Tecnico_Ruta_del_Condor.pdf"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={salida}",
                (raiz / "_reporte.html").as_uri()], check=True, capture_output=True, timeout=120)
(raiz / "_reporte.html").unlink(); (raiz / "entrega" / "_reporte.html").unlink()
paginas = len(re.findall(rb"/Type\s*/Page[^s]", salida.read_bytes()))
print(f"PDF listo: {salida.name}  |  páginas: {paginas}")
