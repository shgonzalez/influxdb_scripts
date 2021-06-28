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
# [gonzalse@wagyu-historico ~]$ curl -v -G 'http://localhost:8086/query?pretty=true' --data-urlencode "db=development" --data-urlencode "q=show field keys"
#> GET /query?pretty=true&db=development&q=show%20field%20keys HTTP/1.1
#
# CREATE CONTINUOUS QUERY "cq_20m_for_720d_bgwriter" ON "development" BEGIN   SELECT  mean(buffers_alloc) as "buffers_alloc"
# , mean(buffers_backend) as buffers_backend
# , mean(buffers_checkpoint) as buffers_checkpoint
# , mean(buffers_clean) as buffers_clean INTO "development"."rp_20m_for_720d".:MEASUREMENT FROM bgwriter GROUP BY time(20m),* END

influxHost= 'http://influxdb:8086/query'

def printContinuousQueries(database, retentionPolicy):
    #Siguiendo los nombres de las retenciones, los queries empiezan con 'cq_' mas la parte del nombre de la retencion
    continuousQueryName = "cq_" + retentionPolicy[3:]
    # el intervalo tambien está en nombre de la retencion por ejemplo: rp_2h_for_1800d, su intervalo es 2h (2 horas)
    intervalo = retentionPolicy.split("_")[1]
    # query al influxdb
    payload = {'db': database, 'q':'show field keys'}
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
    #print(json_response['results'][0]['series'])
    for item in json_response['results'][0]['series']:
        influxQL = ""
        #print(item['name'] )
        for value in (item['values']):
            if value[1] != "string":
                influxQL += "mean(\"" + value[0] + "\") as \""+ value[0] +"\", "
        
        influxQL = "CREATE CONTINUOUS QUERY \"" + continuousQueryName + "_" + item['name'] + "\" ON \""+database+"\" BEGIN   SELECT " + influxQL[:-2] + \
            " INTO \""+ database+"_"+retentionPolicy+"\".\""+retentionPolicy+"\".:MEASUREMENT FROM \"" + item['name'] + "\"  GROUP BY time("+intervalo+"),* END;"
        print(influxQL)
        print()
    

printContinuousQueries("operation","rp_20m_for_720d")
printContinuousQueries("operation","rp_2h_for_1800d")
