from flask import Flask, render_template, request, redirect, url_for, flash, session, g, abort
from data_manager import *
from datetime import datetime
from functools import wraps



app = Flask(__name__)
app.secret_key = 'FuckIsNiceFuckIsFunnyManyPeopleFuckForMoney'


def protected(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(403)
        return function(*args, **kwargs)
    return decorated_function



def timestamp():
    return datetime.now().replace(microsecond=0)



@app.errorhandler(403)
def forbidden_error_403(e):
    session.pop('id', None)
    session.pop('name', None)
    return render_template('403.html'), 403



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



@app.route('/')
def entrance():
    return render_template('registration_login.html')



@app.route('/registration', methods=['POST'])
def registration():
    user_data = request.form.to_dict()
    user_data['password'] = hash_password(user_data['password'])
    register_user(user_data)
    flash('Your account has been successfully created!','green')
    return redirect(request.referrer)



@app.route('/login',methods=['POST'])
def login():
    session.pop('user',None)
    session.pop('name',None)
    user = get_user_by_email(request.form['email'])
    if user and verify_password(request.form['password'],user['password']):
        session['id'] = user['id']
        session['name'] = user['first_name']
        flash("You have successfully logged in!")
        return redirect(url_for("index"))
    flash("Log in failed","red")
    return redirect(request.referrer)



@app.route('/logout')
def logout():
    session.pop('id',None)
    session.pop('name',None)
    flash("You have been successfully logged out!","green")
    return redirect(url_for("entrance"))



@app.route('/user_page')
def user_page():
    if g.user:
        questions = get_records_by_usr_id('question',g.user)
        answers = get_records_by_usr_id('answer',g.user)
        comments = get_records_by_usr_id('comment',g.user)
        return render_template('user_page.html',
                                name=g.name,
                                questions=questions,
                                answers=answers,
                                comments=comments)



@app.before_request
def before_request():
    g.user = g.name = None
    if 'id' in session:
        g.user = session['id']
        g.name = session['name']



@app.route('/index')
@protected
def index():
    ascending = True
    questions = get_questions()
    return render_template('index.html',
                           questions = questions,
                           ascending = ascending,
                           name=g.name)


@app.route('/add_question',methods=['GET',"POST"])
@protected
def add_question():
    if request.method == 'POST':
        usr_input = request.form.to_dict()
        usr_input['submission_time'] = timestamp()
        usr_input['user_id'] = g.user
        new_question(usr_input)
        flash("Question has been successfully submitted",'green')
        return redirect(url_for('index'))
    return render_template('question_form.html',
                           question_id=None,
                           edit=None)



@app.route('/question/<int:question_id>/new-answer', methods=['GET','POST'])
@protected
def add_answer(question_id):
    if request.method == 'POST':
        usr_input = request.form.to_dict()
        usr_input['question_id'] = question_id
        usr_input['submission_time'] = timestamp()
        usr_input['user_id'] = g.user
        new_answer(usr_input)
        flash('Answer has been added!', 'green')
        return redirect(url_for('question_details',question_id=question_id))
    return render_template( 'answer_form.html',
                            edit=None,
                            question_id=question_id)



@app.route('/question/<int:question_id>')
@protected
def question_details(question_id):
    comments = get_comments(question_id)
    question = get_question_by_id(question_id)
    answers= get_answers_by_question_id(question_id)
    return render_template( 'question_detail.html',
                            user_id=g.user,
                            comments=comments,
                            answers=answers,
                            question=question)



@app.route('/list')
@protected
def ordered_list():
    if "order_by" in request.args and "order_direction" in request.args:
        aspect = request.args.get("order_by")
        ascending = True if request.args.get("order_direction")=="ascending" else False
        questions = sort_table('question', aspect, ascending)
        return render_template('index.html',
                               questions=questions,
                               ascending=ascending)
    else:
        questions = get_questions()
        print ("SHOWING THE BASIC TABLE UNORDERED")
        return render_template("index.html",
                               questions=questions)



@app.route('/question/<int:question_id>/vote-<vote>')
@protected
def vote_on_question(question_id, vote):
    vote_modifier = 1 if vote == 'up' else -1
    vote_handler(vote_modifier, 'question', question_id)
    return redirect(request.referrer)



@app.route('/answer/<answer_id>/vote-<vote>')
@protected
def vote_on_answer(answer_id, vote):
    vote_modifier = 1 if vote == 'up' else -1
    vote_handler(vote_modifier, 'answer', answer_id)
    return redirect(request.referrer)



@app.route('/question/<int:question_id>/view')
@protected
def view_count(question_id):
    view_handler(question_id)
    return redirect(url_for('question_details',question_id=question_id))



@app.route('/question/<int:question_id>/edit', methods=['GET','POST'])
@protected
def edit_question(question_id):
    if verify_ownership("question", question_id, g.user):
        if request.method == 'POST':
            usr_input = request.form.to_dict()
            usr_input['submission_time'] = timestamp()
            usr_input['question_id'] = question_id
            update_question_by_id(usr_input)
            flash('Question has been updated', 'green')
            return redirect(url_for('question_details',question_id=question_id))
        question = get_question_by_id(question_id)
        return render_template('question_form.html',
                               edit=question,
                               question_id=question_id)
    else:
        flash('Access Denied!', 'warning')
        return redirect(url_for("index"))



@app.route('/question/<int:question_id>/delete')
@protected
def delete_question(question_id):
    if verify_ownership("question", question_id, g.user):
        delete_from_table('comment', 'question_id', question_id)
        delete_from_table('answer', 'question_id', question_id)
        delete_from_table('question','id',question_id)
        flash('Question has been deleted','green')
        return redirect(url_for("index"))
    else:
        flash('Access Denied!', 'red')
        return redirect(url_for("index"))



@app.route('/<int:question_id>/answer/delete/<int:answer_id>')
@protected
def delete_answer(question_id, answer_id):
    if verify_ownership("answer", answer_id, g.user):
        delete_from_table('comment','answer_id',answer_id)
        delete_from_table('answer','id',answer_id)
        flash('Answer has been deleted','green')
        return redirect(url_for("question_details",question_id=question_id))
    else:
        flash('Access Denied!', 'warning')
        return redirect(url_for("index"))



@app.route('/delete_comment/<int:question_id>/<int:comment_id>')
@protected
def delete_comment(question_id,comment_id):
    if verify_ownership("comment", comment_id, g.user):
        delete_from_table('comment','id',comment_id)
        flash('Comment has been deleted', 'green')
        return redirect(url_for('question_details',question_id=question_id))
    else:
        flash('Access Denied!','warning')
        return redirect(url_for("index"))



@app.route('/add_comment', methods=['POST'])
@protected
def add_comment():
    usr_input = request.form.to_dict()
    usr_input['question_id'] = request.args['question_id']
    usr_input['answer_id'] = request.args['answer_id'] if 'answer_id' in request.args else None
    usr_input['submission_time'] = timestamp()
    usr_input['user_id']=g.user
    print(usr_input)
    new_comment(usr_input)
    flash('Comment has been added', 'green')
    return redirect(request.referrer)



@app.route('/search')
@protected
def search():
    keyword = request.args['keyword']
    questions = search_by_keyword_question(keyword)
    answers = search_by_keyword_answer(keyword)
    return render_template('search.html',
                           questions=questions,
                           answers=answers)



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )