# Dados comparáveis dos bairros

[Baixar a tabela dos 94 bairros](resumo-bairros.csv). Coleta em 25/11/2026. As linhas usam os nomes do ObservaPOA e a malha municipal vinculada à LC 12.112/2016.

- **Área.** Soma geográfica das partes de cada bairro no sistema TM-POA, em km².
- **População, moradia e idade.** Censo 2022, conforme as tabelas publicadas pelo ObservaPOA. DPPO corresponde aos domicílios particulares permanentes ocupados. As faixas somam urbano e rural e agregam os intervalos para 0–14, 15–29 e 60 ou mais.
- **Praças.** Contagem por código de praça, categoria `Pr`, agrupado pelo bairro informado no cadastro. As colunas distinguem urbanização, gravame e demais classificações. Um zero significa ausência de código correspondente no recorte cadastral usado.
- **Logradouros.** Contagem por código, com categorias de rua separadas. A mesma faixa de tolerância de 1 m da [metodologia da Cavalhada](../README.md#logradouros) foi aplicada à cidade inteira. Eixos sem pontos não entram na contagem. Um código pode aparecer em vários bairros. Somar as linhas conta essas ocorrências em cada bairro.

## Reprodução

O [script](../scripts/resumir-bairros.py) recebe a pasta com as seis entradas abaixo. Requer Python com `openpyxl`, `pyshp>=3,<4` e `shapely>=2,<3`.

| Nome local | Fonte |
| --- | --- |
| Bairros_LC12112_16.zip | [Malha municipal](https://licenciamento-api.procempa.com.br/api/urbanismodrive/geopmpa/SPM/PUBLICO/PDDUA_ATUAL/SHP/Bairros_LC12112_16.zip) |
| EixosLogradouros.zip | [Eixos municipais](https://licenciamento-api.procempa.com.br/api/urbanismodrive/geopmpa/SPM/PUBLICO/PDDUA_ATUAL/SHP/EixosLogradouros.zip) |
| pop.csv | [População por bairro](https://prefeitura.poa.br/sites/default/files/usu_doc/hotsites/smpae/observapoa/Pop_Bairro_Censo_2022.csv) |
| dppo.xlsx | [Domicílios ocupados](https://prefeitura.poa.br/sites/default/files/usu_doc/hotsites/smpae/observapoa/Pop.MoradorDPPO_bairro_POA_49.xlsx) |
| idades.xlsx | [Faixas etárias](https://prefeitura.poa.br/sites/default/files/usu_doc/hotsites/smpae/observapoa/Pop_SitDom_FaxEta_Bairro_2022_59.xlsx) |
| pracas-poa.json | [Consulta municipal de praças](https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/Pra%C3%A7as_e_Parques_160126/FeatureServer/0/query?where=categoria%3D%27Pr%27&outFields=fid%2Ccod%2Ccategoria%2Ctipo%2Cbairro_ofi&returnGeometry=false&f=json) |

```sh
python scripts/resumir-bairros.py pasta-das-fontes > dados/resumo-bairros.csv
```

A consulta de praças retornou 1.024 registros, o mesmo número do endpoint de contagem. Um teste com deslocamento de 1.024 registros retornou uma página vazia.
