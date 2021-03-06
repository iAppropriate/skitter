''' Flask Module for Skitter Follow Interactions '''

import re
import pymysql
from flask import Flask, request

APP = Flask(__name__)


def sanitize(user_query):
    ''' Escape user input '''

    clean_string = re.escape(user_query)

    return clean_string


@APP.route("/")
def hello():
    ''' Default landing page '''

    return "Follow/Unfollow API"


@APP.route("/UserSearch", methods=['POST'])
def user_search():
    ''' Search for users in DB that match a given string '''

    if request.form['search']:

        search_query = sanitize(request.form['search'])

        result = "False - No users match your request"

        connection = pymysql.connect(host='database',
                                     user='root',
                                     password='supersecurepass',
                                     db='skitter',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:
                sql_query = "SELECT rit_user FROM users WHERE rit_user LIKE %s"
                cursor.execute(sql_query, ('%' + search_query + '%'))
                searched_users = cursor.fetchall()

                result = ""

                for user in searched_users:
                    result += str(user['rit_user']) + " "

        finally:
            connection.close()

        return result

    return "False - You did not enter a valid query"


@APP.route("/FollowUser", methods=['POST'])
def follow_user():
    ''' Follow a given user in DB '''

    if request.form['follow'] and request.form['session_id']:

        influencer = sanitize(request.form['follow'])
        session_id = sanitize(request.form['session_id'])

        connection = pymysql.connect(host='database',
                                     user='root',
                                     password='supersecurepass',
                                     db='skitter',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        try:
            with connection.cursor() as cursor:

                sql_query = "SELECT username FROM sessions \
                WHERE session_id = %s"
                cursor.execute(sql_query, (session_id))
                follower = cursor.fetchone()['username']

                if influencer == follower:
                    return "False - You cannot follow yourself"

            with connection.cursor() as cursor:

                sql_query = "INSERT INTO follows VALUES (%s, %s)"
                cursor.execute(sql_query, (influencer, follower,))
                connection.commit()

        except pymysql.exceptions.Error:
            return "False - Unable to follow user"

        finally:
            connection.close()

        return "True - Followed user"

    return "You did not enter a valid query"


@APP.route("/UnfollowUser", methods=['POST'])
def unfollow_user():
    ''' Unfollow a given user in DB '''

    if request.form['unfollow'] and request.form['session_id']:

        influencer = sanitize(request.form['unfollow'])
        session_id = sanitize(request.form['session_id'])

        connection = pymysql.connect(host='database',
                                     user='root',
                                     password='supersecurepass',
                                     db='skitter',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:

            with connection.cursor() as cursor:

                sql_query = "SELECT username FROM sessions \
                WHERE session_id = %s"
                cursor.execute(sql_query, (session_id))
                follower = cursor.fetchone()['username']

                if influencer == follower:
                    return "False - You cannot unfollow yourself"

            with connection.cursor() as cursor:

                sql_query = "DELETE FROM follows \
                WHERE influencer = %s AND follower = %s"
                cursor.execute(sql_query, (influencer, follower,))
                connection.commit()

        except pymysql.exceptions.Error:
            return "False - Unable to unfollow user"

        finally:
            connection.close()

        return "True - Unfollowed user"

    return "You did not enter a valid query"


if __name__ == "__main__":
    APP.run(host='0.0.0.0')
