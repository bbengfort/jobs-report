# Jobs Report (ELMR)

[![Stories in Ready](https://badge.waffle.io/bbengfort/jobs-report.png?label=ready&title=Ready)](https://waffle.io/bbengfort/jobs-report) [![Build Status](https://travis-ci.org/bbengfort/jobs-report.svg)](https://travis-ci.org/bbengfort/jobs-report) [![Documentation Status](https://readthedocs.org/projects/jobs-report/badge/?version=latest)](https://readthedocs.org/projects/jobs-report/?badge=latest)


[![Census punch card reader](docs/images/punch_card_reader.jpg)](https://flic.kr/p/6525aR)

**Visualization of the monthly jobs report by the BLS**

You can find ELMR online as well as help documentation at the following links:

- [ELMR Application](https://elmr.herokuapp.com/)
- [ELMR Read the Docs](http://jobs-report.readthedocs.org/en/latest/)

Note that pushing to the `master` branch of this repository will automatically redeploy the app to Heroku. Pushes will also update the documentation on ReadTheDocs.org.

## Components

This project consists of the following:

- An ingestion system that fetches data from the Bureau of Labor Statistics
- A simple Flask application that serves data with a RESTful API
- A front end visualization created with D3 and Bootstrap

## Getting Started

Here's the quick steps to get the server running so you can start developing on your local machine. Open up a terminal and run the following commands.

1. Clone the repository

        $ git clone git@github.com:bbengfort/jobs-report.git
        $ cd jobs-report

2. If you haven't already, it's a good idea to install virtualenv

        $ pip install virtualenv

    Note that you might need the `sudo` command for this.

3. Create your virtualenv

        $ virtualenv venv

    This will make a directory called venv in your work directory.

4. Activate the virtual environment

        $ source venv/bin/activate
        (venv)$

    You should now see a "venv" in parentheses before your prompt.

5. Install the dependencies into your environment

        (venv)$ pip install -r requirements.txt

6. Create a database for the ELMR app (ensure PostgreSQL is installed)

        (venv)$ psql -c "CREATE DATABASE elmr;"
        (venv)$ bin/elmr-admin.py createdb

7. Migrate the to the latest version of the database

        (venv)$ bin/elmr-admin.py upgrade

8. Run the tests to make sure everything is set to go.

        (venv)$ make test

9. Run the ingestion tool to fetch the latest data.

        (venv)$ bin/elmr-admin.py ingest

10. Copy the ingested data to the data folder of the app (this step will be deprecated soon).

        (venv)$ cp fixtures/ingest-DATE/elmr.json elmr/static/data/elmr.json

11. Run the server

        (venv)$ bin/elmr-admin.py runserver

12. Open a browser to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Dependencies and Development

This section describes some of the tools used in the project, as well as giving some tips and advice for quickly changing elements of the page.

### Preloader Animation

The preloader animation that currently says "Loading Visualization ..." was created by [Preloaders.net](http://preloaders.net/en/letters_numbers_words). You can choose an animation, then customize the text, colors, animation speed, and size on their webpage. Download the gif and place it into `elmr/static/img/loader.gif` to update it if you'd like.

Note: the current color matches the "info" text scheme, if you'd like to use it, the hexadecimal is `#31708f`.

### Javascript Libraries

- [moment.js](http://momentjs.com/) handles the parsing and manipulation of time
- [moment-range](https://github.com/gf3/moment-range) handles time intervals and is crucial for the slider controller

- [D3](http://d3js.org/) generates the interactive graphs and data docs.

- [jQuery-UI](https://jqueryui.com/slider/#range) provides the slider control and maybe the DatePicker. I prefer to not use this library, but in the case of the slider, there isn't really too much choice. Minimize the amount this library is used!

- [Underscore](http://underscorejs.org/) (`_`) and [jQuery](http://jquery.com/) (`$`) provide most of the tools and functional calls in the code.

### Style Libraries

- [FontAwesome](http://fortawesome.github.io/Font-Awesome/icons/) is a collection of icons. Most, if not all, of the icons are provided by font-awesome. To add an icon, enter an html tag as follows:

        <i class="fa fa-icon-class"></i>

    Where "icon class" is the name of the icon from the list of icons at the link provided. Icons can be colored and sized using CSS font-size and color attributes.

- [Bootstrap](http://getbootstrap.com/css/) handles the grid layout and most of the non-javascript components on the page. If you don't know Bootstrap, then you'll have trouble dealing with the HTML.


## About

This project was developed as part of a course project at the University of Maryland.

ELMR = Economic Labor Measurement Report

The image used in this README, [Census punch card reader](https://flic.kr/p/6525aR) by [Andrew Shieh](https://www.flickr.com/photos/shandrew/), is licensed by [CC BY-NC-2.0](https://creativecommons.org/licenses/by-nc/2.0/).
