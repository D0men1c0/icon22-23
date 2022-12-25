import xml.etree.cElementTree as ET


#LETTURA DATI DA FILE
#----------------------------------------------

tree = ET.parse('ontology/map/map_data.xml')
root = tree.getroot()
allnodes=root.findall('node')
lista_semafori = []
lista_strade = []
lista_nodi_strada = [] # nodi di una strada 
lista_dati_nodi_strada = []  
lista_id_semafori = []  # nodi che identificano i semafori


allway=root.findall('way')
type_way = ""
name = ""
id_semaforo = ""
maxspeed = ""
lanes = ""

for way in allway:
    lista_nodi_strada = []
    lista_dati_nodi_strada = []  
    lista_id_semafori = []
    for tag in way.findall('tag'): #Prendo dati sulla strada
        if tag.attrib['k'] == 'highway':
            type_way =  tag.attrib['v']

        if tag.attrib['k'] == 'name':
            name =  tag.attrib['v']

        if tag.attrib['k'] == 'maxspeed':
            maxspeed =  tag.attrib['v']

        if tag.attrib['k'] == 'lanes':
            lanes =  tag.attrib['v']

    for nd in way.findall('nd'):
        lista_nodi_strada.append("nodo_"+nd.attrib['ref'])
        for semaforo in lista_semafori:
            if nd.attrib['ref'] in lista_id_semafori:
                id_semaforo = nd.attrib['ref']

    way_i = {
        "id": way.get('id'),
        "name": name,
        "id_semaforo": id_semaforo, 
        "highway": type_way,
        "nodi": lista_nodi_strada,
        "speed": maxspeed,
        "lanes": lanes
    }
    
    lista_strade.append(way_i)

nome_strada = ""
for node in allnodes:
    for strade in lista_strade:
        if "nodo_"+node.attrib['id'] in strade["nodi"]:
            nodo_strada_i = {
                "id": "nodo_"+node.get('id'),
                "lat": node.get('lat'),
                "lon": node.get('lon')
            }
            nome_strada = strade["id"]
            lista_dati_nodi_strada.append(nodo_strada_i)

    for tag in node.findall('tag'): #Prendo dati sul nodo che identifica il semaforo
        if tag.attrib['v'] == 'traffic_signals':
            nodo_strada_i = {
                "id": node.get('id'),
                "lat": node.get('lat'),
                "lon": node.get('lon'),
                "strada": nome_strada
            }
            lista_semafori.append(nodo_strada_i)
            lista_id_semafori.append(node.get('id'))


            


#GENERAZIONE CLAUSOLE
#----------------------------------------------

with open("KB/class_template/strada.pl", "r") as f:
    contents = f.readlines()

#STRADA
strada = ""
for item in lista_strade:
    name = item["name"]
    highway = item["highway"]
    speed = item["speed"]
    lanes = item["lanes"]

    highway = item["highway"]
    name = name.lower()
    

    if highway == "primary" or highway == "trunk" :
        highway = "strada_primaria" 
        if lanes == "":
            lanes = "3"
        if speed == "":
            speed = "80"
    if highway == "secondary" :
        highway = "strada_secondaria"
        if lanes == "":
            lanes = "2"
        if speed == "":
            speed = "50"
    else:
        highway = "strada_terziaria"
        if lanes == "":
            lanes = "1"
        if speed == "":
            speed = "30"
    elementi_lista = '[{}]'.format(','.join(item["nodi"]))
    strada += "prop("+name+",subClassOf,"+highway+").\n"
    strada += "prop("+name+",nome,"+name+").\n"
    strada += "prop("+name+",num_corsie,"+lanes+").\n"
    strada += "prop("+name+",velocita_massima,"+speed+").\n"
    strada += "prop("+name+",nodi,"+elementi_lista+").\n"
    strada += "\n"

strada = strada.replace(" ", "_")
strada = strada.replace("-", "_")
contents.insert(21, strada)

f.close()




#NODI STRADA    
nodo = ""
for item in lista_dati_nodi_strada:
    nodo_id = item["id"]
    lat = item["lat"]
    lon = item["lon"]
    
    contents.append( "\n")
    contents.append( "prop("+nodo_id+",type,nodo).\n")
    contents.append( "prop("+nodo_id+",id,"+nodo_id+").\n")
    contents.append( "prop("+nodo_id+",latitudine,"+lat+").\n")
    contents.append( "prop("+nodo_id+",longitudine,"+lon+").\n")
    contents.append("\n")


with open("KB/class_value/strada.pl", "w") as f:
    contents = "".join(contents)
    f.write(contents)




#NODI SEMAFORO
with open("KB/class_template/semaforo.pl", "r") as f:
    contents = f.readlines()

semaforo = ""
for item in lista_semafori:
    nodo_id = "nodo_"+item["id"]
    lat = item["lat"]
    lon = item["lon"]
    strada = item["strada"]

    semaforo += "\n"
    semaforo += "prop("+nodo_id+",subClassOf,semaforo).\n"
    semaforo += "prop("+nodo_id+",is_in,"+strada+").\n"
    semaforo += "prop("+nodo_id+",colore,).\n"
    semaforo += "prop("+nodo_id+",timer_verde,0).\n"
    semaforo += "prop("+nodo_id+",timer_giallo,0).\n"
    semaforo += "prop("+nodo_id+",timer_rosso,0).\n"
    semaforo += "\n"

semaforo = semaforo.replace(" ", "")
contents.insert(10, semaforo)

f.close()

with open("KB/class_value/semaforo.pl", "w") as f:
    contents = "".join(contents)
    f.write(contents)


#INCROCI
with open("KB/class_template/incrocio.pl", "r") as f:
    contents = f.readlines()
    
    
lista_strade_incrocio = []
nodi_in_comune_lista = "" 
latitudine_nodo_comune = ""
longitudine_nodo_comune = ""
lista_semafori = ""
nodi_comune = []
semafori_comuni = []
strade_incroci = []
incrocio = ""

for strada_1 in lista_strade:
    for strada_2 in lista_strade:
        nodi_in_comune_lista = set(strada_1["nodi"]).intersection(strada_2["nodi"])
        if len(nodi_in_comune_lista) > 0 and len(nodi_in_comune_lista) < 2 and nodi_in_comune_lista != "":
            for nodo in lista_dati_nodi_strada:
                if nodo['id'] in nodi_in_comune_lista:
                    nodi_in_comune = nodo['id']
                    if strada_1["id"] not in strade_incroci:
                        strade_incroci.append(strada_1["id"])
                    latitudine_nodo_comune = nodo['lat']
                    longitudine_nodo_comune = nodo['lon']
    for semaforo in lista_semafori:
        if strada_1['id'] == semaforo["strada"]:
            semafori_comuni.append(semaforo["id"])
                    
semafori_comuni = '[{}]'.format(','.join(semafori_comuni))
strade_incroci = '[{}]'.format(','.join(strade_incroci))

incrocio += "\n"
incrocio += "prop("+nodi_in_comune+",subClassOf,incrocio).\n"
incrocio += "prop("+nodi_in_comune+",strade,"+strade_incroci+").\n"
incrocio += "prop("+nodi_in_comune+",semafori,"+semafori_comuni+").\n"
incrocio += "prop("+nodi_in_comune+",lat,"+latitudine_nodo_comune+").\n"
incrocio += "prop("+nodi_in_comune+",lon,"+longitudine_nodo_comune+").\n"
incrocio += "\n"

incrocio = incrocio.replace(" ", "_")
contents.insert(10, incrocio)

f.close()

with open("KB/class_value/incrocio.pl", "w") as f:
    contents = "".join(contents)
    f.write(contents)







