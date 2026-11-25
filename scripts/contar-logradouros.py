import csv
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import shapefile
from shapely.geometry import box, shape

bairro_zip, eixos_zip = map(Path, sys.argv[1:3])
with ZipFile(bairro_zip) as bairros, ZipFile(eixos_zip) as eixos:
    assert bairros.read("Bairros_LC12112_16.prj") == eixos.read("EixosLogradouros.prj")

bairros = shapefile.Reader(str(bairro_zip))
[registro] = [r for r in bairros.iterShapeRecords() if r.record["NOME"] == "CAVALHADA"]
limite = shape(registro.shape.__geo_interface__)
assert limite.is_valid
interior = limite.buffer(-1)
entorno = limite.buffer(1)
faixa = entorno.difference(interior)
janela = box(*entorno.bounds).bounds

registros = defaultdict(lambda: {"nomes": set(), "tipos": set(), "interior": 0.0, "faixa": 0.0})
eixos = shapefile.Reader(str(eixos_zip))
for trecho in eixos.iterShapeRecords(bbox=janela):
    if trecho.shape.shapeType == shapefile.NULL:
        continue
    eixo = shape(trecho.shape.__geo_interface__)
    interno = eixo.intersection(interior).length
    divisa = eixo.intersection(faixa).length
    if interno == 0 and divisa == 0:
        continue
    campos = trecho.record
    codigo = campos["CDLOG"]
    if not codigo:
        print(f"Trecho sem código: {campos['CDSEG']}", file=sys.stderr)
        continue
    item = registros[codigo]
    item["nomes"].add(campos["NMIDELOG"])
    item["tipos"].add(campos["CDIDECAT"])
    item["interior"] += interno
    item["faixa"] += divisa

saida = csv.writer(sys.stdout, lineterminator="\n")
saida.writerow(["cdlog", "nome_cadastral", "categoria_cadastral", "metros_no_interior", "metros_na_faixa_da_divisa", "classe"])
for codigo, item in sorted(registros.items()):
    if max(item["interior"], item["faixa"]) < 1:
        continue
    classe = "interior" if item["interior"] >= 1 else "faixa_da_divisa"
    saida.writerow([codigo, " / ".join(sorted(item["nomes"])), " / ".join(sorted(item["tipos"])), f'{item["interior"]:.2f}', f'{item["faixa"]:.2f}', classe])
