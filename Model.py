import requests
from PIL import Image

from DataBase.DataBase import GooglePlaces

typeSortCriteria = lambda x: x['percentage']

"""
    ricerca la posizione latitudine/longitudine dall'indirizzo ip oppure dall'indirizzo
    :param address indirizzo 
    :return latitudine e longitudine
"""
def localizzazione(address=None):
    if address is None:
        ip_request = requests.get('https://get.geojs.io/v1/ip.json')
        my_ip = ip_request.json()['ip']  # ip_request.json() => {ip: 'XXX.XXX.XX.X'}

        geo_request_url = 'https://get.geojs.io/v1/ip/geo/' + my_ip + '.json'
        geo_request = requests.get(geo_request_url)
        geo_data = geo_request.json()

        return geo_data['latitude'] + ',' + geo_data['longitude']

    else:
        place = GooglePlaces.textSearch(address, type=[])

        return place[0]['geometry']['location']['lat'] + ',' + place[0]['geometry']['location']['lng']


"""
    Dato un posto tramite l'utilizzo del web service di google ritorna la foto relativa al posto in input
    :param places = posto da cui ricecare la foto.
    :return photo = ritorna la foto del posto di input, se la foto non è presente allora ritorna la 
            foto "static/no-img-placeholder.png"
"""
def photoKeyErrorControl(places):
    photo = {}
    for place in places:
        try:
            photo[place['place_id']] = GooglePlaces.getPlacePhoto(place['photos'][0]['photo_reference'])
        except KeyError:
            photo[place['place_id']] = Image.open("static/no-img-placeholder.png")
            continue
    return photo
