from flask import (
    Blueprint, g, render_template,
    json, request, url_for, redirect, session)

from DataBase.DataBase import GooglePlaces, get_db
from Model import localizzazione, photoKeyErrorControl
from Preference import UserPreferences

bp = Blueprint('Home', __name__, url_prefix='/home')



"""
    Mostra i seguenti posti:
        - Quelli più vicini alla posizione impostata come casa
        - Quelli con la votazione più alta
        - Quelli suggeriti
    Essi sono ottenuti da un file json, i quale è un risultato di una chiamata manuale all'API Google Place
"""
@bp.route('/static', methods=['GET', 'POST'])
def staticHome():

    if request.method == 'POST':
        return redirect(url_for('Home.search', searchQuery=request.form['query']))

    with open('static/json/StaticPlaceSearch.json', 'r') as f:
        results = json.load(f)['results']
        nearby = results
        nearbyPhoto = photoKeyErrorControl(nearby)

        mostPopular = [place for place in results if place['rating'] >= 4.5]
        mostPopularPhoto = photoKeyErrorControl(mostPopular)

        recommend = [place for place in results if UserPreferences.checkPreference(place['types'])]
        recommendPhoto = photoKeyErrorControl(recommend)
        return render_template('home/index.html', ratings=[1, 2, 3, 4, 5], recommend=recommend,
                               recommendPhoto=recommendPhoto, nearby=nearby, nearbyPhoto=nearbyPhoto,
                               mostPopular=mostPopular, mostPopularPhoto=mostPopularPhoto)


"""
    Mostra i seguenti posti:
        - Quelli più vicini alla posizione impostata come casa
        - Quelli con la votazione più alta
        - Quelli suggeriti
    Essi sono ottenuti utilizzando il web service Google Place API
"""
@bp.route('/')
def home():
    if request.method == 'POST':
        return redirect(url_for('Home.search', searchQuery=request.form['query']))

    recommendPhoto = {}
    recommend = []
    try:
        loc = get_db().execute("SELECT localization FROM user WHERE username = ?", (session['username'],)).fetchone()[0]
        if not loc:
            raise Exception()
    except:
        loc = localizzazione()

    results = GooglePlaces.nearbySearch(loc, 10000)

    if g.user is not None:
        recommend = [place for place in results if UserPreferences.checkPreference(place.get('types'))]  # posti suggeriti
        recommendPhoto = photoKeyErrorControl(recommend)    # foto

    nearby = results     # posti vicini
    nearbyPhoto = photoKeyErrorControl(nearby)  # foto

    mostPopular = [place for place in results if place['rating'] > 4.5]  # posti con maggior votazione
    mostPopularPhoto = photoKeyErrorControl(mostPopular)    # foto
    for result in results:
        print(result)

    return render_template('home/index.html', ratings=[1, 2, 3, 4, 5], recommend=recommend, recommendPhoto=recommendPhoto, nearby=nearby, nearbyPhoto=nearbyPhoto, mostPopular=mostPopular, mostPopularPhoto=mostPopularPhoto)


"""
    Cerca i posti che più corrispondono ai dati di ricerca
"""
@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        return redirect(url_for('Home.search', searchQuery=request.form['query']))

    type = request.args.get('type')     # tipi di posti da ricercare
    searchQuery = request.args.get('searchQuery')   # query del posto da ricercare

    try:
        location = get_db().execute("SELECT localization FROM user WHERE username = ?", (session['username'],)).fetchone()[0]
        if not location:
            raise Exception()
    except:
        location = localizzazione()

    # cerca i posti e li ordina per la valutazione
    places = GooglePlaces.textSearch(searchQuery, type=type, location=location, radius=3000) if type else GooglePlaces.textSearch(searchQuery, location=location, radius=3000)
    places.sort(reverse=True, key=lambda x: x['rating'])
    photo = photoKeyErrorControl(places)

    return render_template('home/search.html', ratings=[1, 2, 3, 4, 5], places=places, photo=photo)
