import sqlite3

import requests
import json
import click
from werkzeug.exceptions import abort
from flask import current_app, g
from flask.cli import with_appcontext

"""per il database viene usato SQLite"""


class GooglePlaces(object):
    __MyApiKey = open('static/key.txt').read()


    """
    Il metodo nearbySearch consente di cercare luoghi all'interno di un'area specifica utilizzando API di Google Places
    
    :param
        location = La latitudine/longitudine attorno alla quale recuperare le informazioni sul luogo. 
        radius = Definisce la distanza (in metri) entro la quale restituire i risultati del luogo.
                 Il raggio massimo consentito è di 50.000 metri.
        language = indica in quale lingua deve presentari il risultato
        type = restringe i risultati ai posti che combaciano con i tipi specificati
        apiKey = la chiave dell'API Google dell'applicazione
         
    :return place = file json contenente tutti i posti ricercati
    """
    @staticmethod
    def nearbySearch(location, radius, language="it", type=["bakery", "bar", "cafe", "restaurant", "food"],
                     apiKey=__MyApiKey):
        # HTTP URL per una richiesta di ricerca nelle vicinanze:
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places = []
        # parametri utilizzati per filtrare la richista
        params = {
            'location': location,
            'radius': radius,
            'language': language,
            'type': type,
            'key': apiKey
        }

        # richista
        res = requests.get(endpoint_url, params=params)

        # carica il risultato sottoforma di un json
        results = json.loads(res.content)

        # se la richiesto non è andata a buon fine viene generato un errore del protocollo HTTP
        if results['status'] != "OK":
            return abort(404, "Google API Error: {0}.".format(results.get('error_message', results['status'])))

        # carica solo il risultato
        places.extend(results['results'])

        # finchè ci sono delle pagine contenenti risultati le carica
        """while "next_page_token" in results:
            params['pagetoken'] = results['next_page_token'],
            res = requests.get(endpoint_url, params=params)
            results = json.loads(res.content)
            places.extend(results['results'])"""

        return places


    """
        Metodo che utilizza il servizio di ricerca di testo dell'API di Google Places è un servizio Web che restituisce 
        informazioni su una serie di luoghi in base a una stringa, ad esempio "pizza a New York" o "negozi di scarpe 
        vicino a Ottawa" o "123 Main Street". 
        Il servizio risponde con un elenco di posizioni corrispondenti alla stringa di testo e all'eventuale 
        distorsione di posizione impostata.

        :param
            query = La stringa di testo su cui cercare.
            language = indica in quale lingua deve presentari il risultato
            type = restringe i risultati ai posti che combaciano con i tipi specificati
            location = La latitudine/longitudine attorno alla quale recuperare le informazioni sul luogo. 
            radius = Definisce la distanza (in metri) entro la quale restituire i risultati del luogo.
                     Il raggio massimo consentito è di 50.000 metri.
            apiKey = la chiave dell'API Google dell'applicazione

        :return place = file json contenente tutti i posti ricercati
    """
    @staticmethod
    def textSearch(query, language="it", type=["bakery", "bar", "cafe", "restaurant", "food"], location=None,
                   radius=None, apiKey=__MyApiKey):
        # HTTP URL per una richiesta di ricerca dal testo:
        endpoint_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        places = []
        # parametri utilizzati per filtrare la richista
        params = {
            'query': query,
            'language': language,
            'type': type,
            'location': location,
            'radius': radius,
            'key': apiKey
        }

        # richista
        res = requests.get(endpoint_url, params=params)

        # carica il risultato sottoforma di un json
        results = json.loads(res.content)

        # se la richiesto non è andata a buon fine viene generato un errore del protocollo HTTP
        if results['status'] != "OK":
            return abort(404, "Google API Error: {0}.".format(results.get('error_message', results['status'])))

        # carica solo il risultato
        places.extend(results['results'])

        # finchè ci sono delle pagine contenenti risultati le carica
        """while "next_page_token" in results:
            params['pagetoken'] = results['next_page_token'],
            res = requests.get(endpoint_url, params=params)
            results = json.loads(res.content)
            places.extend(results['results'])"""

        return places


    """
        Metodo utilizzato per ottenere informazioni più dettagliate per i luoghi scelti
        
        :param
            place_id = identificatore unico del posto, ottenuto dal servizio web API di Google Places
            apiKey = la chiave dell'API Google dell'applicazione

        :return place = file json contenente tutti i posti ricercati
    """
    @staticmethod
    def getPlacesDetails(place_id, apiKey=__MyApiKey):
        # HTTP URL per una richiesta per i dettagli del posto:
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json?"
        res = requests.get(
            endpoint_url +
            "place_id=" +
            place_id +
            "&fields=name,geometry,formatted_address,international_phone_number,opening_hours,photos,place_id,rating,reviews,types,website&key=" +
            apiKey
        )
        # carica il risultato sottoforma di un json
        place_details = json.loads(res.content)

        # se la richiesto non è andata a buon fine viene generato un errore del protocollo HTTP
        if place_details['status'] != "OK":
            return abort(404,
                         "Google API Error: {0}.".format(place_details.get('error_message', place_details['status'])))

        # carica solo il risultato
        place_details = place_details['result']
        return place_details


    """
        Il metodo utilizza il servizio Place Photo il quale, parte dell'API di Places, è un'API di sola lettura che 
        ti consente di aggiungere contenuti fotografici di alta qualità alla tua applicazione. Il servizio Place Photo
        ti dà accesso ai milioni di foto archiviate nel database di Places. Quando si ottengono informazioni sul luogo 
        utilizzando una richiesta Dettagli luogo, i riferimenti fotografici verranno restituiti per il contenuto 
        fotografico pertinente. Le richieste Trova luogo, Ricerca nelle vicinanze e Ricerca testo restituiscono anche 
        un riferimento fotografico singolo per luogo, se pertinente. Utilizzando il servizio Foto è quindi possibile 
        accedere alle foto di riferimento e ridimensionare l'immagine alla dimensione ottimale per l'applicazione.
        
        :param
            photoreference = identificatore unico del foto, ottenuto dal servizio web API di Google Places
            apiKey = la chiave dell'API Google dell'applicazione

        :return photo = immagine corrispondente all'identificatore di input
    """
    @staticmethod
    def getPlacePhoto(photoreference, apiKey=__MyApiKey):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/photo?"
        params = {
            'photoreference': photoreference,
            'key': apiKey
        }
        res = requests.get(endpoint_url, params=params)
        photo = res.url
        return photo


"""
    Si connette al database configurato dall'applicazione. La connessione
     è univoca per ogni richiesta e verrà riutilizzata se questa viene chiamata ancora.
"""
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('DataBase/Schema')
        g.db.row_factory = sqlite3.Row

    return g.db


"""
   Chiude la connessione al database
"""
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


"""
    Cancella i dati esistenti e crea nuove tabelle.
"""
def init_db():
    db = get_db()

    with current_app.open_resource('EATLoveSchema.sql') as f:
        db.executescript(f.read().decode('utf8'))


"""
    Seleziona un utente.
    Controlla se l'utente esiste 

    :param username = identificativo dell'utente
    :return user = l'utente con tutte le info
"""
def get_user(username):

    user = get_db().execute('''SELECT u.*
                                    FROM  user u 
                                    WHERE u.username = ?''', (username,)
                            ).fetchone()
    if user is None:
        abort(404, "user id {0} doesn't exist.".format(username))

    return user


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
