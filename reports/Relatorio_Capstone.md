# Relatório do Projeto Capstone em Ciência de Dados
## Previsão de pouso do primeiro estágio do Falcon 9

### Resumo executivo

Este projeto reúne a coleta e análise de registros de lançamentos da SpaceX e constrói classificadores para estimar o sucesso do pouso do primeiro estágio do Falcon 9. A matriz de atributos fornecida contém 90 lançamentos e 80 colunas; sua correspondência foi validada por número do voo e categorias contra a tabela rotulada oficial da IBM. A variável `Class` tem 60 sucessos e 30 falhas.

Foram comparados Regressão Logística, SVM, KNN e Árvore de Decisão com busca de hiperparâmetros em validação cruzada estratificada de cinco partes. O modelo selecionado por acurácia média de validação cruzada foi Árvore de Decisão. O teste contém apenas 18 lançamentos, então os resultados são didáticos e exploratórios.

### 1. Problema e objetivo

O objetivo é classificar o resultado do pouso do primeiro estágio do Falcon 9 a partir de atributos de voo, carga, órbita, local e hardware. `Class=1` indica pouso bem-sucedido; `Class=0` indica falha. As relações descritas são observacionais e não demonstram causalidade.

### 2. Coleta pela API SpaceX

O arquivo JSON arquivado do IBM Skills Network foi coletado e preservado em `data/raw/API_call_spacex_api.json`. Ele contém 107 registros. Os campos de voo, data, foguete, plataforma, carga, núcleo, tentativas de pouso e falhas foram normalizados em `data/processed/api_launches_normalized.csv` (107 linhas e 18 campos). O conjunto arquivado tem cobertura maior que a amostra didática rotulada, por isso não foi misturado com ela.

### 3. Web scraping

Para manter o período histórico, foi usada a revisão 987426997 da página da Wikipedia, de 6 de novembro de 2020. `pandas.read_html` extraiu as tabelas de lançamentos; datas e números de voo foram limpos, registros sem data e duplicados removidos, e o recorte terminou em 5 de novembro de 2020. O CSV final contém 97 linhas numeradas. O esquema e a numeração da página diferem da tabela didática IBM de 90 registros; as fontes permanecem separadas.

### 4. Limpeza e preparação

A matriz `dataset_part_3.csv` (90 × 80) foi conferida contra `data/raw/dataset_part_2.csv` (90 × 18). O código valida número do voo, valores das categorias decodificadas e alinhamento antes de usar a coluna oficial `Class`. A distribuição é 60 sucessos e 30 falhas. O conjunto `course_model_dataset.csv` preserva os atributos categóricos e o alvo para SQL, mapa e dashboard.

### 5. Análise exploratória

As figuras do relatório foram extraídas das saídas do notebook de EDA fornecido. Os gráficos de dispersão comparam resultado por número do voo, local, massa de carga e órbita. O gráfico de barras compara taxas observadas por órbita, e a série anual mostra a evolução da taxa de sucesso. As diferenças são descrições da amostra e podem refletir mudanças simultâneas de veículo, local, missão e período.

### 6. Análise exploratória com SQL

As consultas foram executadas em SQLite sobre o conjunto rotulado de 90 lançamentos. O arquivo SQL e os resultados CSV estão em `outputs/sql/`. Além dos agrupamentos por local, órbita e resultado, a consulta anual conta lançamentos, sucessos e taxa por ano em `outputs/sql/year_success.csv`.

| Local | Lançamentos | Taxa de sucesso |
|---|---:|---:|
| KSC LC 39A | 22 | 77,3% |
| VAFB SLC 4E | 13 | 76,9% |
| CCAFS SLC 40 | 55 | 60,0% |

A massa média da carga foi 4.784,6 kg nas falhas e 6.765,2 kg nos sucessos. A diferença não ajusta por órbita, local ou ano e não deve ser interpretada causalmente.

### 7. Mapa de locais de lançamento

`src/build_folium_map.py` gerou `outputs/launch_sites_folium.html` com Folium. O mapa mostra os três locais da amostra, contagem de lançamentos e popups com sucessos, taxa observada e distância até o local amostrado mais próximo. KSC LC 39A e CCAFS SLC 40 ficam a aproximadamente 5,6 km entre si.

### 8. Dashboard Plotly Dash

`src/dash_app.py` oferece filtros por local e órbita, gráfico de pizza com os resultados no recorte selecionado e gráfico de dispersão de massa de carga versus resultado de pouso. A rota principal e os dois gráficos do callback filtrado foram verificados pelo cliente de teste do Flask. Para abrir localmente: `python src/dash_app.py`, depois `http://127.0.0.1:8050`.

### 9. Modelagem preditiva

A matriz de 80 atributos foi dividida em treino e teste com estratificação (72/18, semente 2). Regressão Logística, SVM e KNN usam padronização dentro de um pipeline; a Árvore de Decisão usa os atributos sem escala. Os hiperparâmetros foram escolhidos por acurácia média em validação cruzada estratificada de cinco partes, executada apenas nos dados de treino. As métricas finais abaixo vêm do holdout.

| Modelo | Acurácia CV | Acurácia teste | Precisão teste | Recall teste | F1 teste |
|---|---:|---:|---:|---:|---:|
| Regressão Logística | 83,7% | 77,8% | 78,6% | 91,7% | 84,6% |
| SVM | 82,3% | 77,8% | 78,6% | 91,7% | 84,6% |
| KNN | 69,4% | 66,7% | 66,7% | 100,0% | 80,0% |
| Árvore de Decisão | 87,7% | 83,3% | 84,6% | 91,7% | 88,0% |

O modelo selecionado pela acurácia média de validação cruzada foi a Árvore de Decisão (`criterion=gini`, `max_depth=5`, `min_samples_leaf=1`). Sua matriz de confusão (linhas = classe real; colunas = prevista) foi:

|  | Previsto 0 | Previsto 1 |
|---|---:|---:|
| Real 0 | 4 | 2 |
| Real 1 | 1 | 11 |

O holdout tem apenas seis falhas; cada erro muda bastante as métricas dessa classe. A comparação serve como exercício de modelagem, não como garantia de desempenho em lançamentos futuros.

### 10. Conclusão

A amostra do curso permite comparar o comportamento de quatro classificadores após ajuste de hiperparâmetros. O modelo selecionado por validação cruzada obteve o maior desempenho médio nos folds de treino; o holdout fornece a checagem final independente usada no relatório. As análises por local, órbita e carga são descritivas, e o tamanho limitado da amostra impede conclusões operacionais.

### Arquivos para o envio

O PDF de apresentação é o arquivo a enviar no Mark. Os notebooks, dados, scripts e saídas de mapa/dashboard estão no repositório público: https://github.com/joaoltrevisan/spacex-falcon9-capstone.

### Fontes

- [IBM Skills Network - API arquivada](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json)
- [IBM Skills Network - tabela rotulada dataset_part_2.csv](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv)
- [IBM Skills Network - dataset_part_3.csv](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_3.csv)
- [Wikipedia - revisão 987426997 (6 nov. 2020)](https://en.wikipedia.org/w/index.php?oldid=987426997)
