"""Arma el zip de entrega (código, reportes y evidencias) SIN secretos ni estado de Terraform. Uso: python entrega/crear_zip.py"""
import pathlib, zipfile

raiz = pathlib.Path(__file__).resolve().parent.parent
excluir_dir = {".git", ".terraform", "__pycache__", ".pytest_cache", "node_modules", ".vscode"}
excluir_ext = {".tfstate", ".backup", ".tfplan", ".pyc", ".key", ".pem", ".crt", ".bak", ".zip"}
excluir_nombre = {"key.json", "config.json", ".env", "plan.txt", "crash.log",
                  "Unidad3_Infraestructura_y_despliegue_material_de_estudio.pdf"}
salida = raiz / "entrega" / "Ruta_del_Condor_entrega.zip"
n = 0
with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(raiz.rglob("*")):
        rel = f.relative_to(raiz)
        if f.is_dir() or set(rel.parts) & excluir_dir or f.suffix in excluir_ext or f.name in excluir_nombre:
            continue
        if "tfstate" in f.name or f == salida:
            continue
        z.write(f, rel); n += 1
print(f"{salida.name}: {n} archivos, {salida.stat().st_size/1e6:.1f} MB")
