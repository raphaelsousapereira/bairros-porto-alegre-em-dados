"""Confere o CSV dos bairros contra o Censo e compara duas versões."""
import argparse
import csv
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

AREA = "area_km2_tm_poa"
POPULACAO = "populacao_censo_2022"
IDADES = ("pop_0a14_2022", "pop_15a29_2022", "pop_60mais_2022")
PRACAS = ("pracas_urbanizadas", "pracas_nao_urbanizadas", "pracas_gravame", "pracas_outro_tipo")
CAMPOS = (
    "bairro", AREA, POPULACAO, "dppo_2022", *IDADES, "pracas_registros", *PRACAS,
    "logradouros_interior", "ruas_interior",
    "logradouros_apenas_divisa", "ruas_apenas_divisa",
)


def ler_fonte(caminho):
    conteudo = caminho.read_bytes()
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = conteudo.decode("cp1252")

    bairros = {}
    total = None
    for nome, quantidade, *_ in list(csv.reader(texto.splitlines(), delimiter=";"))[2:]:
        digitos = quantidade.strip().replace(".", "")
        if not digitos.isascii() or not digitos.isdecimal():
            continue
        nome = nome.strip()
        if nome == "Total":
            if total is not None:
                raise ValueError("A fonte oficial contém mais de uma linha Total.")
            total = int(digitos)
            continue
        if not nome or nome in bairros:
            raise ValueError(f"Bairro vazio ou repetido na fonte oficial: {nome!r}.")
        bairros[nome] = int(digitos)
    if not bairros or total is None or sum(bairros.values()) != total:
        raise ValueError("A soma dos bairros na fonte oficial diverge do total informado.")
    return bairros, total


def ler_tabela(caminho):
    bairros = {}
    with caminho.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        if leitor.fieldnames != list(CAMPOS):
            raise ValueError(f"Cabeçalho inesperado em {caminho}.")
        for linha in leitor:
            if None in linha or None in linha.values():
                raise ValueError(f"Número incorreto de campos na linha {leitor.line_num}.")
            nome = linha.pop("bairro").strip()
            if not nome or nome in bairros:
                raise ValueError(f"Bairro vazio ou repetido na linha {leitor.line_num}: {nome!r}.")
            valores = {}
            for campo, valor in linha.items():
                if campo in IDADES and not valor:
                    valores[campo] = None
                elif campo == AREA:
                    area = Decimal(valor)
                    if not area.is_finite() or area <= 0:
                        raise ValueError(f"{nome}: área precisa ser positiva e finita.")
                    valores[campo] = area
                elif valor.isascii() and valor.isdecimal():
                    valores[campo] = int(valor)
                else:
                    raise ValueError(f"{nome}: valor inválido em {campo}: {valor!r}.")
            bairros[nome] = valores
    return bairros


def conferir(bairros, oficial):
    erros = []
    for nome in sorted(oficial.keys() - bairros.keys()):
        erros.append(f"Bairro ausente: {nome}.")
    for nome in sorted(bairros.keys() - oficial.keys()):
        erros.append(f"Bairro fora da lista oficial: {nome}.")

    for nome, dados in bairros.items():
        if nome in oficial and dados[POPULACAO] != oficial[nome]:
            erros.append(f"{nome}: população {dados[POPULACAO]} difere da fonte ({oficial[nome]}).")
        if sum(dados[campo] for campo in IDADES if dados[campo] is not None) > dados[POPULACAO]:
            erros.append(f"{nome}: soma das faixas etárias supera a população.")
        if sum(dados[campo] for campo in PRACAS) != dados["pracas_registros"]:
            erros.append(f"{nome}: total de praças diverge da soma das categorias.")
        for recorte in ("interior", "apenas_divisa"):
            if dados[f"ruas_{recorte}"] > dados[f"logradouros_{recorte}"]:
                erros.append(f"{nome}: ruas superam os logradouros no recorte {recorte}.")
    return erros


def comparar(anterior, atual):
    mudancas = []
    for nome in sorted(anterior.keys() | atual.keys()):
        if nome not in anterior or nome not in atual:
            mudancas.append({"bairro": nome, "mudanca": "incluído" if nome in atual else "removido"})
            continue
        for campo in CAMPOS[1:]:
            antes = anterior[nome][campo]
            depois = atual[nome][campo]
            if antes != depois:
                mudancas.append({"bairro": nome, "indicador": campo, "antes": antes, "depois": depois})
    return mudancas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tabela", type=Path)
    parser.add_argument("--fonte-populacao", required=True, type=Path)
    parser.add_argument("--anterior", type=Path, help="CSV publicado para comparação.")
    args = parser.parse_args()
    try:
        oficial, total_oficial = ler_fonte(args.fonte_populacao)
        bairros = ler_tabela(args.tabela)
        erros = conferir(bairros, oficial)
        soma_populacao = sum(dados[POPULACAO] for dados in bairros.values())
        if soma_populacao != total_oficial:
            erros.append(f"População somada ({soma_populacao}) diverge do total oficial ({total_oficial}).")
        if erros:
            print("\n".join(erros), file=sys.stderr)
            return 1

        relatorio = {
            "bairros": len(bairros),
            "populacao_censo_2022": soma_populacao,
            "total_oficial_censo_2022": total_oficial,
            "faixas_etarias_ausentes": [
                {"bairro": nome, "indicador": campo}
                for nome, dados in bairros.items()
                for campo in IDADES
                if dados[campo] is None
            ],
        }
        if args.anterior:
            relatorio["mudancas"] = comparar(ler_tabela(args.anterior), bairros)
        print(json.dumps(relatorio, ensure_ascii=False, indent=2, default=str))
        return 0
    except (OSError, csv.Error, InvalidOperation, ValueError) as erro:
        print(f"Falha na conferência: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
