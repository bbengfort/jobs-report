# elmr.app
# A small Flask web app to serve static files
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Mar 03 09:21:32 2015 -0500
#
# Copyright (C) 2014 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: app.py [] benjamin@bengfort.com $

"""
A small Flask web app to serve static files
"""

##########################################################################
## Imports
##########################################################################

import os

from flask import Flask, render_template, send_from_directory

##########################################################################
## Configure Flask
##########################################################################

app = Flask(__name__)
app.debug = True

##########################################################################
## Configure Routes
##########################################################################


@app.route("/")
def page():
    return render_template('home.html')


@app.route('/favicon.ico')
def favicon():
    dirname = os.path.join(app.root_path, 'static')
    return send_from_directory(dirname, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
