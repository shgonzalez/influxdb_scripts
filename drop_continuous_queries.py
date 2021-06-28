import requests, sys
import json
# SICD - Sergio Gonzalez
# > show retention policies on development
# name            duration   shardGroupDuration replicaN default
# ----            --------   ------------------ -------- -------
# autogen         0s         168h0m0s           1        false
# default         24h0m0s    1h0m0s             1        true
# rp_20m_for_720d 17280h0m0s 168h0m0s           1        false
# rp_2h_for_1800d 43200h0m0s 168h0m0s           1        false
# Examples: 
# [user1@wagyu-historico ~]$ curl -v -G 'http://localhost:8086/query?pretty=true' --data-urlencode "db=development" --data-urlencode "q=show field keys"
#> GET /query?pretty=true&db=development&q=show%20field%20keys HTTP/1.1
#
# CREATE CONTINUOUS QUERY "cq_20m_for_720d_bgwriter" ON "development" BEGIN   SELECT  mean(buffers_alloc) as "buffers_alloc"
# , mean(buffers_backend) as buffers_backend
# , mean(buffers_checkpoint) as buffers_checkpoint
# , mean(buffers_clean) as buffers_clean INTO "development"."rp_20m_for_720d".:MEASUREMENT FROM bgwriter GROUP BY time(20m),* END

influxHost= 'http://influxdb:8086/query'

def dropContinuousQueries(database):
    #Siguiendo los nombres de las retenciones, los queries empiezan con 'cq_' mas la parte del nombre de la retencion
    #continuousQueryName = "cq_" + retentionPolicy[3:]
    # el intervalo tambien está en nombre de la retencion por ejemplo: rp_2h_for_1800d, su intervalo es 2h (2 horas)
    #intervalo = retentionPolicy.split("_")[1]
    # query al influxdb
    payload = {'db': database, 'q':'show continuous queries'}
    #para ver la URL completa: print(response.url)
    
    try:
        response = requests.get(influxHost, params=payload)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print("Error: " + str(e))
        sys.exit(1)
    
    #si 'e' termina 
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        print("Error: " + str(e))
        sys.exit(1)
    # obtiene el json
    json_response = response.json()
    #print(response.url)
    #print(str(response.status_code))
    
    #print(json.dumps(json_response))
    #results = json_response['list']
    resultados = json_response['results'][0]['series'][1]['values']
    for item in resultados:
        print("DROP CONTINUOUS QUERY \"" + item[0] + "\" ON \""+ database + "\";")
        print()
    

dropContinuousQueries("development")
