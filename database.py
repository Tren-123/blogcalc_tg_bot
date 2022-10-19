import sqlite3


def _create_connection_db(name_of_db):
    """ Create connection and cursor for working with SQLite db with <name_of_db> name """
    connection = sqlite3.connect(name_of_db)
    cursor = connection.cursor()
    return connection, cursor


def create_table_db(name_of_db):
    """ Create table in <name_of_db> with name user_auth """
    connection, cursor = _create_connection_db(name_of_db)
    cursor.execute(f"CREATE TABLE IF NOT EXISTS user_auth(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    return cursor


def _select_user_with_user_id_and_signal_true_or_false(name_of_db, user_id):
    """ Check if user exist in <name_of_db> and return 0 if not exist, 1 if exist in user_exist variable """
    connection, cursor = _create_connection_db(name_of_db)
    res = cursor.execute(f"SELECT COUNT(user_id) FROM user_auth WHERE user_id = {user_id}")
    user_exist = res.fetchone()[0]
    return connection, cursor, user_exist


def _insert_value_db(cursor, user_id, username, password):
    """ Insert values user_id, username and password in user_auth table """
    data = {
        "user_id" : user_id,
        "username" : username,
        "password" : password
    }
    cursor.execute("INSERT INTO user_auth VALUES (:user_id, :username, :password)", data)


def _update_value_db(cursor, user_id, username, password):
    """ Update existed values username and password in user_auth table """
    data = {
        "user_id" : user_id,
        "username" : username,
        "password" : password
    }
    cursor.execute(f"UPDATE user_auth\
                     SET username = :username, password = :password\
                     WHERE user_id = :user_id", data)


def insert_or_update_db(name_of_db, user_id, username, password):
    """ Check if user exist in <name_of_db> and choose right option insert or update values """
    connection, cursor, user_exist = _select_user_with_user_id_and_signal_true_or_false(name_of_db, user_id)
    if user_exist == 0:
        _insert_value_db(cursor, user_id, username, password)
    elif user_exist == 1:
        _update_value_db(cursor, user_id, username, password)
    connection.commit()


def get_username_and_password_from_db(name_of_db, user_id):
    """ Get username and password from <name_of_db>.user_auth for user. If user not exits in db return False instead"""
    connection, cursor, user_exist = _select_user_with_user_id_and_signal_true_or_false(name_of_db, user_id)
    data = {
        "user_id" : user_id
    }
    if user_exist == 0:
        return False, False
    elif user_exist == 1:
        res = cursor.execute(f"SELECT username, password FROM user_auth WHERE user_id = :user_id", data)
        res_tupple = res.fetchone()
        return res_tupple[0], res_tupple[1]


