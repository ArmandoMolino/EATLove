from flask import (
    Blueprint, render_template, request, json
)

from DataBase.DataBase import GooglePlaces
from Preference import Types, UserPreferences

bp = Blueprint('Place', __name__, url_prefix='/place')

"""
    Mostra tutte le informazioni dettagliate di un posto.
    Essi sono ottenuti da un file json, i quale è un risultato di una chiamata manuale all'API Google Place
"""
@bp.route('/static')
def staticPlace():
    place_id = request.args.get('place_id')
    with open('static/json/StaticPlaceDetail.json', 'r', encoding="utf8") as f:
        results = json.load(f)['results'] # carica i risultati
        # cerca il posto tramite l'identificativo unico(place_id)
        for result in results:
            if result['place_id'] == place_id:
                results = result
                break
        photos = []

        # vengono fatti dei calcoli per conoscere le preferenze dell'utente
        UserPreferences.tot += 1    # incremento il totale dei posti visionati nel sito
        for type in results['types']:   # cicla tutti i tipi del posto selezionato se non è presente tra i tipi possibli
                                        # passa all' iterazione successiva
            try:
                UserPreferences.incrementCount(Types[type.upper()])  # incrementa  il totale dei posti visionati nel sito del tipo selezionato
            except:
                continue

        for type in Types:
            UserPreferences.setPercentage(type) # ricalcola la percentuale di preferenza del tipo

        # carica le foto del posto
        for photo in results['photos']:
            photos.append(GooglePlaces.getPlacePhoto(photo['photo_reference']))
        frontPhoto = photos.pop(0)
        return render_template('place/info.html', place=results, photos=photos, frontPhoto=frontPhoto)


"""
    Mostra tutte le informazioni dettagliate di un posto.
    Le info vengono ottenute tramite l'utilizzo del web service Google Place API
"""
@bp.route('/')
def place():
    place_id = request.args.get('place_id')
    photos = []
    # cerca il posto tramite l'identificativo unico(place_id)
    result = GooglePlaces.getPlacesDetails(place_id)

    # vengono fatti dei calcoli per conoscere le preferenze dell'utente
    UserPreferences.tot += 1    # incremento il totale dei posti visionati nel sito
    for type in result.get('types'):    # cicla tutti i tipi del posto selezionato se non è presente tra i tipi possibli
                                        # passa all' iterazione successiva
        try:
            UserPreferences.incrementCount(Types[type.upper()])  # incrementa  il totale dei posti visionati nel sito del tipo selezionato
        except:
            continue

    for type in Types:
        UserPreferences.setPercentage(type) # ricalcola la percentuale di preferenza del tipo

    # carica le foto del posto
    for photo in result.get('photos'):
        photos.append(GooglePlaces.getPlacePhoto(photo.get('photo_reference')))
    frontPhoto = photos.pop(0)
    return render_template('place/info.html', place=result, photos=photos, frontPhoto=frontPhoto)

