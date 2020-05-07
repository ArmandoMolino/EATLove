import enum


class Types(enum.Enum):
    BAKERY = 0
    BAR = 1
    CAFE = 2
    RESTAURANT = 3
    FOOD = 4

class UserPreferences(object):

    loaded = False
    tot = 0
    username = ""
    preference = [
        {'type': 'bakery', 'percentage': 0, 'count': 0},
        {'type': 'bar', 'percentage': 0, 'count': 0},
        {'type': 'cafe', 'percentage': 0, 'count': 0},
        {'type': 'restaurant', 'percentage': 0, 'count': 0},
        {'type': 'food', 'percentage': 0, 'count': 0},
    ]

    """
        Viene ricalcolata la percentuale di preferenza del tipo dato in input
        :argument t = enumeratore che identifica i tipi di posti possibili
        :except ZeroDivisionError = imposta la preferenza a 0
    """
    @staticmethod
    def setPercentage(t: Types):
        try:
            UserPreferences.preference[t.value]['percentage'] = round(((UserPreferences.preference[t.value]['count'] * 100) / UserPreferences.tot), 2)
        except ZeroDivisionError:
            UserPreferences.preference[t.value]['percentage'] = 0

    @staticmethod
    def incrementCount(t: Types):
        UserPreferences.preference[t.value]['count'] += 1

    @staticmethod
    def getPercentage(t: Types):
        return UserPreferences.preference[t.value]['percentage']

    @staticmethod
    def getCount(t: Types):
        return UserPreferences.preference[t.value]['count']

    # Memento utilizzato per ritornare alla situazione iniziale
    @staticmethod
    def undoPreference():
        UserPreferences.tot = 0
        UserPreferences.preference = [
            {'type': 'bakery', 'percentage': 0, 'count': 0},
            {'type': 'bar', 'percentage': 0, 'count': 0},
            {'type': 'cafe', 'percentage': 0, 'count': 0},
            {'type': 'restaurant', 'percentage': 0, 'count': 0},
            {'type': 'food', 'percentage': 0, 'count': 0},
        ]
        UserPreferences.username = ""
        UserPreferences.loaded = False

    """
        Controlla se i tipi di un posto rientrano nelle preferenze dell'utente
        :return True se corrisponde alla preferenze dell'utente se no ritorna False
    """
    @staticmethod
    def checkPreference(typesToCheck):
        count = 0
        for typeToCheck in typesToCheck:
            try:
                index = Types[typeToCheck.upper()].value
                count += UserPreferences.preference[index]['percentage']
            except:
                continue
        return count >= 50