from flask import Flask, render_template, g, request, session, redirect, url_for, jsonify
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template_string
import os

import json
import requests
import string
import re
import nltk
import string
import itertools
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import traceback
from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor
import lt_core_news_sm
import pke
import spacy
#############################################


from question_g import tokenize_sentences, tokenize_sentences, get_sentences_for_keyword, get_fill_in_the_blanks, get_noun_adj_verb
 
###########################################


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['SECRET_KEY'] = os.urandom(24)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def get_current_user():
    user_result = None

    if 'user' in session:
        user = session['user']

        db = get_db()
        user_cur = db.execute('select id, name, password, expert, admin from users where name = ?', [user])
        user_result = user_cur.fetchone()

    return user_result

@app.route('/')
def index():
    user = get_current_user()
    db = get_db()

    questions_cur = db.execute('''select 
                                      questions.id as question_id, 
                                      questions.question_text, 
                                      askers.name as asker_name, 
                                      experts.name as expert_name 
                                  from questions 
                                  join users as askers on askers.id = questions.asked_by_id 
                                  join users as experts on experts.id = questions.expert_id 
                                  where questions.answer_text is not null''')

    questions_result = questions_cur.fetchall()

    return render_template('home.html', user=user, questions=questions_result)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()

    if request.method == 'POST':

        db = get_db()
        existing_user_cur = db.execute('select id from users where name = ?', [request.form['name']])
        existing_user = existing_user_cur.fetchone()

        if existing_user:
            return render_template('register.html', user=user, error='User already exists!')

        hashed_password = generate_password_hash(request.form['password'], method='sha256')
        db.execute('insert into users (name, password, expert, admin) values (?, ?, ?, ?)', [request.form['name'], hashed_password, '0', '0'])
        db.commit()

        session['user'] = request.form['name']

        return redirect(url_for('index'))

    return render_template('register.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    error = None

    if request.method == 'POST':
        db = get_db()

        name = request.form['name']
        password = request.form['password']

        user_cur = db.execute('select id, name, password from users where name = ?', [name])
        user_result = user_cur.fetchone()

        if user_result:

            if check_password_hash(user_result['password'], password):
                session['user'] = user_result['name']
                return redirect(url_for('index'))
            else:
                error = 'The password is incorrect.'
        else:
            error = 'The username is incorrect'

    return render_template('login.html', user=user, error=error)

@app.route('/question/<question_id>')
def question(question_id):
    user = get_current_user()
    db = get_db()

    question_cur = db.execute('''select 
                                     questions.question_text, 
                                     questions.answer_text, 
                                     askers.name as asker_name, 
                                     experts.name as expert_name 
                                 from questions 
                                 join users as askers on askers.id = questions.asked_by_id 
                                 join users as experts on experts.id = questions.expert_id 
                                 where questions.id = ?''', [question_id])

    question = question_cur.fetchone()

    return render_template('question.html', user=user, question=question)

@app.route('/answer/<question_id>', methods=['GET', 'POST'])
def answer(question_id):
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    if request.method == 'POST':
        db.execute('update questions set answer_text = ? where id = ?', [request.form['answer'], question_id])
        db.commit()

        return redirect(url_for('unanswered'))

    question_cur = db.execute('select id, question_text from questions where id = ?', [question_id])
    question = question_cur.fetchone()

    return render_template('answer.html', user=user, question=question)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_current_user()
    
    if not user:
        return redirect(url_for('login'))

    db = get_db()
    
    expert_cur = db.execute('select id, name from users where expert = 1')
    expert_results = expert_cur.fetchall()     
    
    if request.method == 'POST':

        #if request.form['submit'] == 'generate':
        if 'question_gen' in request.form:
            
        
            db.execute('insert into questions (question_text, asked_by_id, expert_id) values (?, ?, ?)', [request.form['question'], user['id'], request.form['expert']])
            db.commit()

            default_value = ''
            df5 = request.form.get('question', default_value)
            text_data2 = str(df5)

            sentences = tokenize_sentences(text_data2)
            noun_verbs_adj = get_noun_adj_verb(text_data2)

            keyword_sentence_mapping_noun_verbs_adj = get_sentences_for_keyword(noun_verbs_adj, sentences)

            fill_in_the_blanks = get_fill_in_the_blanks(keyword_sentence_mapping_noun_verbs_adj)
            results = fill_in_the_blanks

            sakiniai = results['sentences']
            raktazodziai = results['keys']
            #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            print(sakiniai)

            #return sakiniai, raktazodziai

            #sakiniai = ''
            #raktazodziai = ''
            #if request.form.action == 'Download':
            #if 'Komentuoti' in request.form:

        #if request.form['submit'] == 'Komentuoti':
        elif 'Komentuoti' in request.form:
            
                db.execute('insert into comments (comment_text, commented_by_id) values (?, ?)', [request.form['comments'], user['id']])
                db.commit()
                print('ok')
                sakiniai = ''
                raktazodziai = ''
        else:
            pass

    elif request.method == 'GET':
        sakiniai = ''
        raktazodziai = ''
    
    return render_template('ask.html', user=user, experts=expert_results, sakiniai=sakiniai, raktazodziai=raktazodziai) 

##############################################################################################################################


@app.route('/unanswered')
def unanswered():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    questions_cur = db.execute('''select questions.id, questions.question_text, users.name 
                                  from questions 
                                  join users on users.id = questions.asked_by_id 
                                  where questions.answer_text is null and questions.expert_id = ?''', [user['id']])
    
    questions = questions_cur.fetchall()

    return render_template('unanswered.html', user=user, questions=questions)

@app.route('/users')
def users():
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('index'))

    db = get_db()
    users_cur = db.execute('select id, name, expert, admin from users')
    users_results = users_cur.fetchall()

    return render_template('users.html', user=user, users=users_results)

@app.route('/promote/<user_id>')
def promote(user_id):
    user = get_current_user()

    if not user:
        return redirect(url_for('login'))

    if user['admin'] == 0:
        return redirect(url_for('index'))

    db = get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()

    return redirect(url_for('users'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()