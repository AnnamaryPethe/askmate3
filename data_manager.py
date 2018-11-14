from connection import connection_handler
from psycopg2 import sql
import bcrypt


def hash_password(password):
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(password=None, hashed_password=None):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes_password)



@connection_handler
def get_questions(cursor):
    query = """ SELECT * FROM question;"""
    cursor.execute(query)
    return cursor.fetchall()



@connection_handler
def get_question_by_id(cursor, question_id):
    query = ''' SELECT * FROM question
                WHERE id = %(question_id)s; '''
    params = {'question_id':question_id}
    cursor.execute(query,params)
    return cursor.fetchone()


@connection_handler
def get_records_by_usr_id(cursor, table, user_id):
    query = sql.SQL(""" SELECT * FROM {}
                        WHERE user_id= %(user_id)s""").format(sql.Identifier(table))
    params = {'user_id':user_id}
    cursor.execute(query,params)
    return cursor.fetchall()


@connection_handler
def new_question(cursor, usr_input):
    query = """ insert into question (submission_time, title, message, user_id) 
                values ( %(submission_time)s, %(title)s, %(message)s, %(user_id)s ) """
    cursor.execute(query, usr_input)



@connection_handler
def new_answer(cursor, usr_input):
    query = """ insert into answer (submission_time, question_id, message, user_id) 
                values ( %(submission_time)s, %(question_id)s, %(message)s, %(user_id)s )    """
    cursor.execute(query, usr_input)



@connection_handler
def update_question_by_id(cursor, usr_input):
    query = """ UPDATE question
                SET submission_time = %(submission_time)s, title = %(title)s, message = %(message)s
                WHERE id = %(question_id)s  """
    cursor.execute(query, usr_input)



@connection_handler
def delete_from_table(cursor, table, del_by, value):
    query = sql.SQL(""" DELETE FROM {} WHERE {}=%(value)s; """).format(
        sql.Identifier(table),sql.Identifier(del_by)    )
    params = {'value':value}
    cursor.execute(query,params)



@connection_handler
def vote_handler(cursor, change, table, id):
    query = sql.SQL(""" UPDATE {} 
                        SET vote_number = vote_number + %(change)s
                        WHERE id = %(id)s   """).format(sql.Identifier(table))
    params = {'change': change, 'id': id}
    cursor.execute(query,params)



@connection_handler
def view_handler(cursor, question_id):
    query = """ UPDATE question
                SET view_number = view_number + 1
                WHERE id = %(question_id)s  """
    params = {'question_id': question_id}
    cursor.execute(query, params)



@connection_handler
def sort_table(cursor, table, column, ascending):
    if ascending is True:
        query = sql.SQL("SELECT * FROM  {0} ORDER BY {1} ASC ").format(
            sql.Identifier(table), sql.Identifier(column))
    else:
        query = sql.SQL("""SELECT * FROM  {0} ORDER BY {1} DESC """).format(
            sql.Identifier(table), sql.Identifier(column))
    cursor.execute(query)
    return cursor.fetchall()



@connection_handler
def get_answers_by_question_id(cursor, question_id):
    query = """ SELECT * FROM  answer
                WHERE question_id = %(question_id)s 
                ORDER BY vote_number DESC   """
    params = {'question_id':question_id}
    cursor.execute(query,params)
    return cursor.fetchall()



@connection_handler
def get_comments(cursor,question_id):
    query = """ SELECT * FROM comment 
                WHERE question_id=%(question_id)s   """
    params = {'question_id':question_id}
    cursor.execute(query,params)
    return cursor.fetchall()



@connection_handler
def new_comment(cursor, usr_input):
    query = """ INSERT INTO comment (question_id, answer_id, message, submission_time, user_id)
                VALUES (%(question_id)s ,%(answer_id)s, %(message)s, %(submission_time)s, %(user_id)s)"""
    cursor.execute(query, usr_input)



@connection_handler
def search_by_keyword_question(cursor, keyword):
    query = """ SELECT * FROM question
                WHERE question.title LIKE %(keyword)s OR question.message LIKE %(keyword)s; """
    params = {'keyword': '%' + keyword + '%'}
    cursor.execute(query,params)
    return cursor.fetchall()



@connection_handler
def search_by_keyword_answer(cursor, keyword):
    query = """ SELECT * FROM answer
                WHERE answer.message LIKE %(keyword)s;"""
    params = {'keyword': '%' + keyword + '%'}
    cursor.execute(query,params)
    return cursor.fetchall()



@connection_handler
def verify_ownership(cursor, table, id, user_id):
    query = sql.SQL(""" SELECT user_id from {}
                        WHERE id=%(id)s """).format(sql.Identifier(table))
    params = {'id':id }
    cursor.execute(query,params)
    return cursor.fetchone()["user_id"] == user_id



@connection_handler
def register_user(cursor, user_data):
    query = """ INSERT INTO "user" (first_name, last_name, password, email)
                VALUES (%(first_name)s, %(last_name)s, %(password)s, %(email)s) """
    cursor.execute(query,user_data)



@connection_handler
def get_user_by_email(cursor, email):
    query = """ SELECT * FROM "user"
                WHERE email=%(email)s"""
    params = {'email': email}
    cursor.execute(query,params)
    return cursor.fetchone()



@connection_handler
def get_profile_by_id(cursor, id):
    cursor.execute("""
                    SELECT * FROM "user_name" WHERE id=%(id)s""",
                   {'id': id})
    result = cursor.fetchone()
    return result