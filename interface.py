#!/usr/bin/env python

import bokeh
import glob
import os
import pandas as pd

from flask import Flask
from flask import redirect, render_template, request, send_file, url_for
from lib import do_the_thing

app = Flask(__name__)

#df = pd.read_hdf('static/phot.hdf5', key='data')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def parse_tweetstr():
    tweet = request.form['tweet']
    tweet_id = tweet.split('status/')[1].split('/')[0]
    print(tweet_id)
    return redirect(url_for('.plot', tweet_id=tweet_id))

@app.route('/plot/<tweet_id>', methods=['GET'])
def plot(tweet_id):
    script, div = do_the_thing(tweet_id)
    return render_template('bokeh.html', script=script, div=div)


# @app.route('/results', methods=['GET'])
# def show_table_jd():
#     return render_template('index.html', table = pd.read_csv(outfile_jd, escapechar='\\').to_html(index=False))

# @app.route('/results.csv', methods=['GET'])
# def send_csv_jd():
#     return send_file(outfile_jd)

if __name__ == '__main__':
    app.debug = False # set this to false before putting on production!!!
    app.run()
