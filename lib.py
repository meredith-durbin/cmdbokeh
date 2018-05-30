#!/usr/bin/env python

import auth
import matplotlib.path as mplPath
import numpy as np
import pandas as pd
import tweepy

from astropy.wcs import WCS

from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, Circle
from bokeh.plotting import figure
from bokeh.palettes import RdYlBu11
from bokeh.embed import components

oauth = tweepy.OAuthHandler(auth.CONSUMER_KEY, auth.CONSUMER_SECRET)
oauth.set_access_token(auth.ACCESS_TOKEN, auth.ACCESS_TOKEN_SECRET)

api = tweepy.API(oauth)

df = pd.read_hdf('static/phat_trim.hdf5', key='data')

def get_wcs(wcsfile):
    with open(wcsfile) as f:
        wcs = WCS(header=f.read())
    return wcs

def get_pix(pxstr, full_height=22230):
    c1 = pxstr.split(': ')[1].split('. ')
    x,y = map(float, c1[0].split(','))
    w,h = map(float, [c1[1].split('x')[0], c1[1].split('x')[1][:-1]])
    return np.array([x, full_height-y, w, h])

def get_coords(wcs, xc, yc, w, h):
    ra0,dec0 = wcs.all_pix2world(xc,yc,0)
    ra1,dec1 = wcs.all_pix2world(xc,yc-h,0)
    ra2,dec2 = wcs.all_pix2world(xc+w,yc-h,0)
    ra3,dec3 = wcs.all_pix2world(xc+w,yc,0)
    ra = np.hstack([ra0,ra1,ra2,ra3,ra0])
    dec = np.hstack([dec0,dec1,dec2,dec3,dec0])
    return ra, dec

def get_cpath(coords):
    cpath = mplPath.Path(np.array([coords[0],coords[1]]).T)
    return cpath


def do_a_plot(source):
    TOOLS = "pan,wheel_zoom,box_zoom,box_select,lasso_select,reset"

    left = figure(tools=TOOLS, plot_width=400, plot_height=400, title=None)

    for t in left.tools:
        if hasattr(t, 'select_every_mousemove'):
            t.select_every_mousemove = False
    r_left = left.circle('color', 'f814w_vega', source=source, fill_color='black', line_color='black',
                line_alpha=0.2, fill_alpha=0.1, size=2)
    left.y_range.flipped = True

    right = figure(tools=TOOLS, plot_width=400, plot_height=400, title=None)
    for t in right.tools:
        if hasattr(t, 'select_every_mousemove'):
            t.select_every_mousemove = False
    r_right = right.circle('x', 'y', source=source, line_color='color_label', fill_color='color_label',
                           line_alpha=0.8, fill_alpha=0.9, size='marker_size')
    right.background_fill_color = "black"

    select_left = Circle(fill_color='black', line_color='black', line_alpha=0.2, fill_alpha=0.1, size=2)
    nonselect_left = Circle(fill_color='black', line_color='black', line_alpha=0.05, fill_alpha=0.01, size=2)

    r_left.selection_glyph = select_left
    r_left.nonselection_glyph = nonselect_left

    select_right = Circle(fill_color='color_label', line_color='white',
                          line_alpha=0.9, fill_alpha=1, size='marker_size')
    nonselect_right = Circle(fill_color='color_label', line_color='color_label',
                             line_alpha=0.5, fill_alpha=0.3, size='marker_size')

    r_right.selection_glyph = select_right
    r_right.nonselection_glyph = nonselect_right

    p = gridplot([[left, right]])
    script, div = components(p)
    return script, div

def do_the_thing(tweet_id):
    most_recent = api.get_status(tweet_id)
    txt = most_recent._json['text'].split(' http')[0]
    wcs = get_wcs('static/wcs.head')
    pix = get_pix(txt)
    coords = get_coords(wcs, *pix)
    cpath = get_cpath(coords)
    inpath = cpath.contains_points(df[['ra','dec']].values)
    nstars = inpath.sum()
    if nstars == 0:
        raise Exception('Nothing found in image region.')
    df_cut = df[inpath]
    if df_cut.shape[0] == 0:
        raise Exception('Empty dataframe.')
    source = ColumnDataSource(data=df_cut)
    script, div = do_a_plot(source)
    return script, div

