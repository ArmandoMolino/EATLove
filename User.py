from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.security import generate_password_hash

from DataBase.DataBase import get_user, get_db
from Model import localizzazione

bp = Blueprint('User', __name__, url_prefix='/user')

"""
    Mostra tutte le info dell'utente
"""
@bp.route('/info')
def info():
    user = get_user(request.args.get('username'))
    return render_template('user/info.html', user=user)


"""
    Con questa funzione si l'utente può modificare le sue informazioni
"""
@bp.route('/update', methods=('GET', 'POST'))
def update():
    user = get_user(request.args.get('username'))
    db = get_db()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        address = request.form['country'] + ", " + request.form['city'] + ", " + request.form['province'] + ", " + \
                  request.form['address']

        error = None

        #controlla che tutti i dati essenziali siano stati inseriti
        if not name:
            error = 'Name is required.'
        elif not surname:
            error = 'Surname is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('''SELECT email FROM user WHERE email = ? AND username != ?''', (email, user['username'],)
                        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(email)

        # se è stato inserito un indirizzo otteniamo la sua posizione tramite l'indirizzo altrimenti tramite l'ip
        if address.replace(", ", ""):
            localization = localizzazione(address)
        else:
            localization = localizzazione()
            address = None
        if error is not None:
            flash(error)
        else:
            # aggiorna i dati nel database
            db.execute('''UPDATE user 
                                SET name = ?, surname = ?, email = ?, password = ?, address = ?, localization = ?
                                WHERE username = ?''', (
            name, surname, email, generate_password_hash(password), address, localization, user['username']))
            db.commit()
            return redirect(url_for('User.info', username=user['username']))
    return render_template('user/update.html', user=user)
