# influxdbclient
python lite influxdbclient
useage :
```
with InfluxDBClient("http://localhost:8086") as client:
    params={"db":"testdb","rp":"counters","precision":"m"}
    for item in souredata:
        i += 1
        if lastid<item[0]:
            lastid=item[0]
        lines +="%s.%s,service=%s,machine=%s,object=%s,instance=%s value=%i %s\n" % item[2].lower(),client.escape_tag(item[5]),item[1],item[3].upper(),client.escape_tag(item[4]),client.escape_tag(item[6]),item[7],client.convert_timestamp(item[8],'m')
        if i>1000:
            client.write(params,lines)
            #print lines
            lines=""
            i=0
    if len(lines)>2:
        client.write(params,lines)
        #print lines
        lines=""
    print 'ok'
```
