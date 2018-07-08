# -*- coding: utf-8 -*-
"""
Created on Sun Jan  7 13:30:37 2018
@author: bnsmith3
"""

import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from status_checker.library_search import search_for_book, get_session_info

app = Flask(__name__, instance_relative_config=True) # create the application instance
app.config.from_pyfile('application.cfg', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    
@app.errorhandler(500)
def internal_error(e):
    app.logger.error('Internal Server Error: {}'.format(e))
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('Page Not Found Error: {}'.format(e))
    return render_template('404.html'), 404
	
@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute("select id, title, author from books where has_read='N' order by author asc")
    entries = cur.fetchall()
    return render_template('show_entries.html', page_title="Books to Read", entries=entries)

@app.route('/read')
def show_read_entries():
    db = get_db()
    cur = db.execute("select id, title, author from books where has_read='Y' order by author asc")
    entries = cur.fetchall()
    return render_template('show_entries.html', page_title="Completed Books", entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into books (title, author, has_read) values (?, ?, ?)',
                 [request.form['title'], request.form['author'], request.form['read']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def show_entry(book_id):
    db = get_db()
    
    if request.method == 'POST':
        db.execute('update books set title=?, author=?, has_read=? where id=?',
                     [request.form['title'], request.form['author'], request.form['read'], book_id])
        db.commit()
        flash('The entry was successfully updated.')        

    cur = db.execute('select title, author, has_read from books where id=(?)', (book_id,))
    entry = cur.fetchone()
    
    if not entry:
        entry = ('', '', '')
        flash('No entry was found with that id.')        
        results = {'results': []}
    else:
        try:
            results = search_for_book(entry[0])
        except Exception as e:
            return internal_error(e)
        
    return render_template('show_entry.html', title=entry[0], author=entry[1], \
                           has_read=entry[2], book_id=book_id, results=results['results'])

@app.route('/statuses', methods=['GET', 'POST'])
def show_statuses():
    db = get_db()
    if request.method == 'POST':
        ids = list(map(int, request.form.getlist('check')))
        if len(ids) > 0:
            cur = db.execute("select title from books where id in ({}) order by author asc".format(','.join(['?']*len(ids))), ids)
            entries = cur.fetchall()        
        else:
            entries = []
    else:        
        cur = db.execute("select title from books where has_read='N' order by author asc")
        entries = cur.fetchall()
        
    session = get_session_info()    
	
    try:
        results = list(map(lambda x: search_for_book(x[0], session), entries))
    except Exception as e:
    	return internal_error(e)

    return render_template('show_statuses.html', entries=results)
