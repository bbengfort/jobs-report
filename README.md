# Jobs Report (ELMR)

[![Stories in Ready](https://badge.waffle.io/bbengfort/jobs-report.png?label=ready&title=Ready)](https://waffle.io/bbengfort/jobs-report) [![Build Status](https://travis-ci.org/bbengfort/jobs-report.svg)](https://travis-ci.org/bbengfort/jobs-report)

[![Census punch card reader](docs/images/punch_card_reader.jpg)](https://flic.kr/p/6525aR)

**Visualization of the monthly jobs report by the BLS**

ELMR = Economic Labor Measurement Report

Just a temporary name for now - but thought it might be cute for a start.

## Components

This project consists of the following:

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

6. Run the server

        (venv)$ make runserver

    You can also simply run `python elmr/app.py` if you wish.

7. Open a browser to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

8. You can run the tests as follows:

        (venv)$ make test

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

This project was developed as part of a course project at the University of Maryland

The image in this README, [Census punch card reader](https://flic.kr/p/6525aR) by [Andrew Shieh](https://www.flickr.com/photos/shandrew/) is licensed by [CC BY-NC-2.0](https://creativecommons.org/licenses/by-nc/2.0/).
