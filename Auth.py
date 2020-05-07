import functools
import sqlite3

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from DataBase.DataBase import get_db
from Model import localizzazione
from Preference import Types, UserPreferences
from numpy import array

bp = Blueprint('Auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator ridirige utenti anonomi alla pagina di login"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('Auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """
    Se un utente è memorizzato nella sessione, caricare l'oggetto utente dal database in g.user
    """
    username = session.get('username')

    if username is None:
        g.user = None
        # se l'utente non è caricato vede se sono stati caricati dei dati in UserPreference
        if UserPreferences.loaded:
            db = get_db()
            # carica i dati nella table types
            for type in Types:
                percentage = UserPreferences.getPercentage(type)
                try:
                    if percentage == 0:
                        raise Exception("percentage is 0")
                    db.execute(
                        '''INSERT INTO types (username,type,percentage) VALUES (?,?,?)''',
                        (UserPreferences.username, type.name.lower(), percentage)
                    )
                    db.commit()

                except sqlite3.IntegrityError:
                    db.execute(
                        '''UPDATE types
                                SET percentage = ?
                                WHERE username = ? AND type = ?''',
                        (percentage, UserPreferences.username, type.name.lower())
                    )
                    db.commit()
                except Exception:
                    continue
            # resetta UserPreferences
            UserPreferences.undoPreference()
    else:
        g.user = get_db().execute(
            '''SELECT * FROM user WHERE username = ?''', (username,)
        ).fetchone()
        # carica i dati in UserPreferences con i dati nella table types
        if not UserPreferences.loaded:
            UserPreferences.loaded = True
            UserPreferences.username = g.user['username']
            types = array(
                get_db().execute("SELECT type, percentage FROM types WHERE username = ?", (username,)).fetchall())
            for type in types:
                index = Types[type[0].upper()].value
                UserPreferences.preference[index]['percentage'] = float(type[1])
                UserPreferences.preference[index]['count'] = int(round(float(type[1]), 0))
                UserPreferences.tot += UserPreferences.preference[index]['count']



"""
    Registra un nuovo utente.
    Convalida che il se l'username dell'utente non è già stato utilizzato. 
    fa l'Hashing della password per sicurezza.
"""
@bp.route('/register', methods=('GET', 'POST'))
def register():


    if request.method == 'POST':

        name = request.form['name']
        surname = request.form['surname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        error = None
        """
            Controlla se sono stati immessi i seguenti dati: name, surname, username, email e password.
            Se non sono stati immessi genera un errore.
            Se l'username o l'email immessa sono gia state utilizzate genera un errore.
        """
        if not name:
            error = 'Name is required.'

        elif not surname:
            error = 'Surname is required.'

        elif not username:
            error = 'Username is required.'
        elif db.execute(
                '''SELECT username FROM user WHERE username = ?''', (username,)
        ).fetchone() is not None:
            error = 'Username {0} is already taken.'.format(username)

        elif not email:
            error = 'Email is required.'
        elif db.execute(
                '''SELECT username FROM user WHERE email = ?''', (email,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(email)

        elif not password:
            error = 'Password is required.'

        if error is None:
            # Salva il nuovo utente nel database
            db.execute(
                '''INSERT INTO user (name, surname, username, email, password) VALUES (?, ?, ?, ?, ?)''',
                (name, surname, username, email, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('Auth.moreUserInfo', username=username))

        flash(error)

    return render_template('auth/register.html')

"""
    Richiesta di informazioni supplementali riguardanti l'utente.
    Possono essere omesse. 
"""
@bp.route('/register/<string:username>', methods=('GET', 'POST'))
def moreUserInfo(username):
    if request.method == 'POST':

        address = request.form['country'] + ", " + request.form['city'] + ", " + request.form['province'] + ", " + \
                  request.form['address']
        if address.replace(", ", ""):
            localization = localizzazione()  # address)
        else:
            localization = localizzazione()
            address = None

        db = get_db()

        # Aggiunge le informazzioni supplementali all'utente nel database
        db.execute('''UPDATE user SET address = ?, localization = ? WHERE username = ?''',
                   (address, localization, username,))
        db.commit()

        return redirect(url_for('Auth.login'))

    return render_template('auth/moreUserInfo.html')


"""
    Logga un utente registrato aggiungendolo nella sessione corrente.
"""
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        loginCredentials = request.form['loginCredentials'] # può essere l'email oppure username
        password = request.form['password']

        db = get_db()
        error = None

        user = db.execute(
            '''SELECT * FROM user WHERE email = ? or username = ?''', (loginCredentials, loginCredentials)
        ).fetchone()

        if user is None:
            error = 'Incorrect email or username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # immagazzina l'identificativo dell'utente nella nuova sessione
            session.clear()
            session['username'] = user['username']
            UserPreferences.loaded = True
            UserPreferences.username = user['username']
            types = array(
                get_db().execute("SELECT type, percentage FROM types WHERE username = ?", (user['username'],)).fetchall())
            for type in types:
                index = Types[type[0].upper()].value
                UserPreferences.preference[index]['percentage'] = float(type[1])
                UserPreferences.preference[index]['count'] = int(round(float(type[1]), 0))
                UserPreferences.tot += UserPreferences.preference[index]['count']
            return redirect(url_for('Home.home'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    # cancella la sessione
    session.clear()
    db = get_db()
    # carica i dati nella table types
    for type in Types:
        percentage = UserPreferences.getPercentage(type)
        try:
            if percentage == 0:
                raise Exception("percentage is 0")
            db.execute(
                '''INSERT INTO types (username,type,percentage) VALUES (?,?,?)''',
                (UserPreferences.username, type.name.lower(), percentage)
            )
            db.commit()

        except sqlite3.IntegrityError:
            db.execute(
                '''UPDATE types
                        SET percentage = ?
                        WHERE username = ? AND type = ?''',
                (percentage, UserPreferences.username, type.name.lower())
            )
            db.commit()
        except Exception:
            continue
    # resetta UserPreferences
    UserPreferences.undoPreference()
    return redirect(url_for('Home.home'))
