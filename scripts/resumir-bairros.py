import csv
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

import openpyxl
import shapefile
from shapely import prepare
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.strtree import STRtree


def chave(nome):
    return ''.join(c for c in unicodedata.normalize('NFKD', nome.upper()) if c.isalnum())


pasta = Path(sys.argv[1])
with ZipFile(pasta / 'Bairros_LC12112_16.zip') as bairros, ZipFile(pasta / 'EixosLogradouros.zip') as eixos:
    assert bairros.read('Bairros_LC12112_16.prj') == eixos.read('EixosLogradouros.prj')

poligonos = defaultdict(list)
for registro in shapefile.Reader(str(pasta / 'Bairros_LC12112_16.zip')).iterShapeRecords():
    nome = registro.record["NOME"]
    if chave(nome) == "CELAPARICIOBORGES":
        nome = "Coronel Aparício Borges"
    poligonos[chave(nome)].append(shape(registro.shape.__geo_interface__))

pop = {}
with (pasta / 'pop.csv').open(encoding='cp1252') as arquivo:
    for nome, numero, *_ in list(csv.reader(arquivo, delimiter=';'))[2:]:
        if nome != 'Total' and numero.replace('.', '').isdigit():
            pop[chave(nome)] = (nome, int(numero.replace('.', '')))

dppo = list(openpyxl.load_workbook(pasta / 'dppo.xlsx', read_only=True, data_only=True).active.values)
ocupados = {chave(t.split(' - Porto Alegre (RS)')[0]): dppo[1][i] for i,t in enumerate(dppo[0]) if isinstance(t, str)}
idades = list(openpyxl.load_workbook(pasta / 'idades.xlsx', read_only=True, data_only=True).active.values)
grupos = {}
for i, nome in enumerate(idades[1]):
    if isinstance(nome, str) and idades[2][i] == 'População':
        grupos[chave(nome)] = tuple(sum(int(idades[j][i] or 0) + int(idades[j+12][i] or 0) for j in indices) if all(str(idades[k][i] or 0).isdigit() for j in indices for k in (j,j+12)) else None for indices in (range(3, 6), range(6, 9), range(12, 14)))

pracas = defaultdict(dict)
for registro in json.loads((pasta / 'pracas-poa.json').read_text())['features']:
    item = registro['attributes']
    k = chave(item['bairro_ofi'] or '')
    codigo = item['cod']
    if k in poligonos and codigo:
        anterior = pracas[k].setdefault(codigo, item['tipo'])
        if anterior != item['tipo']:
            pracas[k][codigo] = 'classificação divergente'

trechos = []
eixos = shapefile.Reader(str(pasta / 'EixosLogradouros.zip'))
for i in range(len(eixos)):
    try:
        geometria = eixos.shape(i)
    except shapefile.ShapefileException as erro:
        if 'requires non-empty points' not in str(erro):
            raise
        print(f'Eixo sem pontos, índice {i}', file=sys.stderr)
        continue
    registro = eixos.record(i)
    if registro['CDLOG'] and geometria.shapeType != shapefile.NULL:
        trechos.append((shape(geometria.__geo_interface__), registro['CDLOG'], registro['CDIDECAT']))
arvore = STRtree([t[0] for t in trechos])
assert set(poligonos) == set(pop), (set(poligonos) - set(pop), set(pop) - set(poligonos))

writer = csv.writer(sys.stdout, lineterminator='\n')
writer.writerow(['bairro','area_km2_tm_poa','populacao_censo_2022','dppo_2022','pop_0a14_2022','pop_15a29_2022','pop_60mais_2022','pracas_registros','pracas_urbanizadas','pracas_nao_urbanizadas','pracas_gravame','pracas_outro_tipo','logradouros_interior','ruas_interior','logradouros_apenas_divisa','ruas_apenas_divisa'])
for k, (nome, habitantes) in sorted(pop.items()):
    limite = unary_union(poligonos[k])
    interior = limite.buffer(-1)
    entorno = limite.buffer(1)
    faixa = entorno.difference(interior)
    prepare(interior)
    prepare(faixa)
    comprimentos = defaultdict(lambda: [0.0, 0.0, set()])
    for indice in arvore.query(entorno):
        eixo, codigo, tipo = trechos[indice]
        dentro = eixo.length if interior.covers(eixo) else eixo.intersection(interior).length if interior.intersects(eixo) else 0.0
        borda = eixo.intersection(faixa).length if faixa.intersects(eixo) else 0.0
        if dentro or borda:
            item = comprimentos[codigo]
            item[0] += dentro
            item[1] += borda
            item[2].add(tipo)
    total_interno = [tipos for dentro, borda, tipos in comprimentos.values() if dentro >= 1]
    total_divisa = [tipos for dentro, borda, tipos in comprimentos.values() if dentro < 1 <= borda]
    tipos_praca = Counter(pracas[k].values())
    totais_praca = [tipos_praca[t] for t in ('urbanizada', 'não urbanizada', 'gravame')]
    writer.writerow([nome, f'{limite.area/1e6:.4f}', habitantes, ocupados[k], *grupos[k], len(pracas[k]), *totais_praca, len(pracas[k])-sum(totais_praca), len(total_interno), sum(t=={'R'} for t in total_interno), len(total_divisa), sum(t=={'R'} for t in total_divisa)])
