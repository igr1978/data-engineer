# 1. Разверните и подготовьте окружение

Запустите скрипт `./scripts/start.sh` 

******************************************************************
DONE! Connect to Confluent Control Center at http://localhost:9021
******************************************************************

igor@MBP-Igor cp-demo-5.4.0 %


# 2. Создайте KSQL Stream WIKILANG

CREATE STREAM WIKILANG WITH (PARTITIONS=2,REPLICAS=2) AS 
SELECT createdat, channel, username, wikipage, diffurl
FROM wikipedia
WHERE channel != '#en.wikipedia' AND channel != '#commons.wikimedia' AND isbot <> true;


# 3. Мониторинг WIKILANG

# - В KSQL CLI получите текущую статистику вашего стрима: describe extended wikilang;  

ksql> describe extended wikilang;

Name                 : WIKILANG
Type                 : STREAM
Key field            : 
Key format           : STRING
Timestamp field      : Not set - using <ROWTIME>
Value format         : AVRO
Kafka topic          : WIKILANG (partitions: 2, replication: 2)

 Field     | Type                      
---------------------------------------
 ROWTIME   | BIGINT           (system) 
 ROWKEY    | VARCHAR(STRING)  (system) 
 CREATEDAT | BIGINT                    
 CHANNEL   | VARCHAR(STRING)           
 USERNAME  | VARCHAR(STRING)           
 WIKIPAGE  | VARCHAR(STRING)           
 DIFFURL   | VARCHAR(STRING)           
---------------------------------------

Queries that write from this STREAM
-----------------------------------
CSAS_WIKILANG_11 : CREATE STREAM WIKILANG WITH (KAFKA_TOPIC='WIKILANG', PARTITIONS=2, REPLICAS=2) AS SELECT
  WIKIPEDIA.CREATEDAT "CREATEDAT",
  WIKIPEDIA.CHANNEL "CHANNEL",
  WIKIPEDIA.USERNAME "USERNAME",
  WIKIPEDIA.WIKIPAGE "WIKIPAGE",
  WIKIPEDIA.DIFFURL "DIFFURL"
FROM WIKIPEDIA WIKIPEDIA
WHERE (((WIKIPEDIA.CHANNEL <> '#en.wikipedia') AND (WIKIPEDIA.CHANNEL <> '#commons.wikimedia')) AND (WIKIPEDIA.ISBOT <> true))
EMIT CHANGES;

For query topology and execution plan please run: EXPLAIN <QueryId>

Local runtime statistics
------------------------
messages-per-sec:      1.70   total-messages:      1563     last-message: 2020-02-27T11:12:03.88Z

(Statistics of the local KSQL server interaction with the Kafka topic WIKILANG)
ksql> 


# - В KSQL CLI получите текущую статистику WIKIPEDIANOBOT: describe extended wikipedianobot;  

Local runtime statistics
------------------------
messages-per-sec:      4.04   total-messages:      6270     last-message: 2020-02-27T11:12:52.295Z

(Statistics of the local KSQL server interaction with the Kafka topic WIKIPEDIANOBOT)
ksql> 

# Почему для wikipedianobot интерфейс показывает также consumer-* метрики?
	Не нашел где это находится.


# 4. Добавьте данные из стрима WIKILANG в ElasticSearch
- Добавьте mapping - запустите скрипт set_elasticsearch_mapping_lang.sh
- Добавьте Kafka Connect - запустите submit_elastic_sink_lang_config.sh
- Добавьте index-pattern - Kibana UI -> Management -> Index patterns -> Create Index Pattern -> Index name or pattern: wikilang -> кнопка Create

Используя полученные знания и документацию ответьте на вопросы:  
# a) Опишите что делает каждая из этих операций?
	- set_elasticsearch_mapping_lang.sh - mapping для Wikilang в Elasticsearch
	- submit_elastic_sink_lang_config.sh - kafka connect к Wikilang для Elasticsearch
	- index-pattern - шаблон индекса Wikilang для подключения к Elasticsearch

# б) Зачем Elasticsearch нужен mapping чтобы принять данные?
	Маппинг (отображение) — это процесс определения того, как документ и содержащиеся в нем поля хранятся и индексируются.

# в) Что дает index-pattern?
	Шаблон индекса сообщает Kibana, какие индексы Elasticsearch содержат данные, которые хотите исследовать и визуализировать.


# 5. Создайте отчет "Топ10 национальных разделов" на базе индекса wikilang
- Kibana UI -> Visualize -> + -> Data Table -> выберите индекс wikilang
- Select bucket type -> Split Rows, Aggregation -> Terms, Field -> CHANNEL.keyword, Size -> 10, нажмите кнопку Apply changes (выглядит как кнопка Play)
- Сохраните визуализацию под удобным для вас именем

# - Что вы увидели в отчете?
Топ10 национальных разделов Wikipedia по количеству ключевых слов в термах.

CHANNEL.keyword: Descending Count 
#de.wikipedia				294
#fr.wikipedia				276
#it.wikipedia				215
#ru.wikipedia				166
#zh.wikipedia				139
#es.wikipedia				96
#uk.wikipedia				31
#en.wiktionary				20
#mediawiki.wikipedia		10
#eu.wikipedia				8


# - Нажав маленьку круглую кнопку со стрелкой вверх под отчетом, вы сможете запросить не только таблицу, но и запрос на Query DSL которым он получен.
Приложите тело запроса к заданию.

{
  "query": {
    "bool": {
      "must": [
        {
          "match_all": {}
        },
        {
          "range": {
            "CREATEDAT": {
              "gte": 1582801116571,
              "lte": 1582802016571,
              "format": "epoch_millis"
            }
          }
        }
      ],
      "must_not": []
    }
  },
  "size": 0,
  "_source": {
    "excludes": []
  },
  "aggs": {
    "2": {
      "terms": {
        "field": "CHANNEL.keyword",
        "size": 10,
        "order": {
          "_count": "desc"
        }
      }
    }
  }
}
