from flask import Flask, render_template, request, url_for, flash, redirect
import os
from boto3.dynamodb.conditions import Key
from boto3 import resource
from werkzeug.exceptions import abort
from dateutil.parser import parse
import random
import string
import uuid
from datetime import datetime

dynamodb = resource('dynamodb')
bookshelf_table = dynamodb.Table(os.environ["BookshelfTable"])

app = Flask(__name__)
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))

@app.route('/')
def index():
    books = ''
    
    try: 
        response = bookshelf_table.scan()
        books = response['Items']
        print('Scan returned:', len(books), 'books', flush=True)
    except Exception as error:
        print("dynamo scan failed:", error, flush=True) 
              
    return render_template('index.html', books=books) 

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        # Generate current timestamp
        timestamp = datetime.now()
        print(timestamp, flush=True)

        title = request.form['title']
        content = request.form['content']
        created = str(timestamp)
        id = uuid.uuid1()

        if not title:
            flash('Title is required!')
        else:
            print(id.int, flush=True)
            try: 
                #insert new book into dynamodb
                bookshelf_table.put_item(
                    Item={
                        'id': str(id),
                        'title': title,
                        'tags': content,
                        'created_datetime': created
                        }
                )
            except Exception as error:
                print("dynamo PUT failed", flush=True)
                print("An error occurred:", error, flush=True) 
                  
            return redirect(url_for('index'))
    return render_template('create.html')