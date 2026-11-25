# Bairros de Porto Alegre em Dados

Base pública do [Porto Alegre em Dados](https://portoalegreemdados.com.br/) para responder perguntas sobre os bairros com mapas, documentos e cálculos reproduzíveis.

## Cavalhada

Primeira coleta em **25/11/2026**. O recorte geográfico usa a camada municipal de bairros vinculada à LC 12.112/2016.

| Pergunta | Resultado da primeira coleta |
| --- | --- |
| Quantos registros de praça o cadastro atribui à Cavalhada? | **19 códigos de praça**. São **9 urbanizados**, **9 não urbanizados** e **1 gravame**. |
| Quantos logradouros têm eixo no interior do bairro? | **177 códigos de logradouro**, dos quais **100** têm categoria cadastral `R` (rua). |
| Quantos aparecem apenas na faixa da divisa, segundo o critério adotado? | **53 códigos adicionais**, dos quais **35** têm categoria `R`. |

### Praças

[Baixar a lista do cadastro municipal](bairros/cavalhada/pracas.csv).

A consulta selecionou o bairro oficial Cavalhada e a categoria cadastral `Pr` no serviço **Praças e Parques 160126**. Cada código aparece uma vez na lista. O cadastro tem dois códigos com o nome **Praça Professor Angelo Ricci**, um urbanizado e outro não urbanizado. A primeira contagem usa os códigos, preservando os dois registros para conferência. O gravame é uma previsão ou restrição urbanística registrada na camada. A lista segue a atribuição municipal de bairro e as classificações do cadastro. Estado de conservação, equipamentos e casos de divisa ainda dependem de conferência específica.

[Camada municipal](https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/Pra%C3%A7as_e_Parques_160126/FeatureServer/0) · [Consulta dos registros](https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/Hosted/Pra%C3%A7as_e_Parques_160126/FeatureServer/0/query?where=UPPER%28bairro_ofi%29%20LIKE%20%27%25CAVALHADA%25%27&outFields=fid%2Ccod%2Cdenomina%C3%A7%2Ccategoria%2Ctipo%2Cbairro_ofi%2Cestado&returnGeometry=false&f=json)

### Logradouros

[Baixar a lista dos logradouros](bairros/cavalhada/logradouros.csv) · [Código do cruzamento](scripts/contar-logradouros.py).

Foi cruzado o polígono da Cavalhada com os eixos municipais de logradouros no sistema cartográfico TM-POA, em metros. Os trechos são agrupados pelo código municipal `CDLOG`. A categoria da via vem de `CDIDECAT`. A lista inclui todas as categorias de logradouro presentes na camada, inclusive códigos de praças e parques que têm eixo cadastral. Para contar apenas ruas, use a categoria `R`.

A classe **interior** exige pelo menos 1 m acumulado de eixo mais de 1 m para dentro do limite. A classe **faixa da divisa** exige pelo menos 1 m acumulado na faixa de 1 m de cada lado da divisa, com menos de 1 m acumulado no interior. A tolerância reduz efeitos de desalinhamentos cartográficos. Os comprimentos são de eixos cadastrados, com duas casas decimais, e pontos de contato sem comprimento ficam fora da contagem.

[Mapas digitais da SMAMUS](https://prefeitura.poa.br/carta-de-servicos/mapas-digitais-da-smamus) · [Bairros em shapefile](https://licenciamento-api.procempa.com.br/api/urbanismodrive/geopmpa/SPM/PUBLICO/PDDUA_ATUAL/SHP/Bairros_LC12112_16.zip) · [Eixos em shapefile](https://licenciamento-api.procempa.com.br/api/urbanismodrive/geopmpa/SPM/PUBLICO/PDDUA_ATUAL/SHP/EixosLogradouros.zip)

Para reproduzir com os dois arquivos ZIP oficiais, instale `pyshp>=3,<4` e `shapely>=2,<3` e execute:

```sh
python scripts/contar-logradouros.py Bairros_LC12112_16.zip EixosLogradouros.zip
```

| Arquivo na coleta | SHA-256 |
| --- | --- |
| Bairros_LC12112_16.zip | `258772459588f7941ac6eeda7c6839df02d58741cf6bc3e48825aecd60418251` |
| EixosLogradouros.zip | `264a74c5f6cf8e4a57ad5a2520cd737102f289e54ef2c60ae626cfae1116020e` |

## Como citar

Porto Alegre em Dados, **Bairros de Porto Alegre em Dados — Cavalhada**, levantamento de 25/11/2026. Indique o arquivo e o critério de contagem utilizado.
