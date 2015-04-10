# Development

In this document, we discuss specifics of how to develop for ELMR. If you're not a Python programmer or JavaScript developer (e.g. just a user of the ELMR app), please feel free to skip this section.

ELMR has three primary components:

- An ingestion system that fetches data from the Bureau of Labor Statistics (ingestion)
- A simple Flask application that serves data with a RESTful API (back-end)
- A front end visualization created with D3 and Bootstrap (front-end)

Development can be on one or more of these modules, referred to as "ingestion", "back-end", and "front-end" respectively. Development on the ingestion module will have most of the work done on the `elmr.ingest` module. Development on the front-end will have work done on the `elmr.static` and `elmr.templates` modules. Finally work on the backend will take place in one or more `elmr` modules.

Note there is also a command line script that handles tasks, found in `bin/elmr-admin.py` - this script runs the development server, or ingests data to the local host.

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

## Contributing

ELMR is open source, but because this is an academic project, we would appreciate it if you would let us know how you intend to use the software (other than simply copying and pasting code so that you can use it in your own projects). If you would like to contribute (especially if you are a student at either the University of Maryland or Wright State), you can do so in the following ways:

1. Add issues or bugs to the bug tracker: [https://github.com/mclumd/kyudo/issues](https://github.com/mclumd/kyudo/issues)
2. Work on a card on the dev board: [https://waffle.io/mclumd/kyudo](https://waffle.io/mclumd/kyudo)
3. Create a pull request in Github: [https://github.com/mclumd/kyudo/pulls](https://github.com/mclumd/kyudo/pulls)

If you are a member of the CMSC 734 visualization group, you have direct access to the repository, which is set up in a typical production/release/development cycle as described in _[A Successful Git Branching Model](http://nvie.com/posts/a-successful-git-branching-model/)_. A typical workflow is as follows:

1. Select a card from the [dev board](https://waffle.io/mclumd/kyudo) - preferably one that is "ready" then move it to "in-progress".

2. Create a branch off of develop called "feature-[feature name]", work and commit into that branch.

        ~$ git checkout -b feature-myfeature develop

3. Once you are done working (and everything is tested) merge your feature into develop.

        ~$ git checkout develop
        ~$ git merge --no-ff feature-myfeature
        ~$ git branch -d feature-myfeature
        ~$ git push origin develop

4. Repeat. Releases will be routinely pushed into master via release branches, then deployed to the server.

## Databases

We're using a PostgreSQL database to power the application, allowing for analytics inside of the web application as well as making ingestion and querying easier. Using PostgreSQL adds a bit of overhead, but it's well worth it.

Models are defined in `models.py` using the SQLAlchemy model code. If you make changes to `models.py` you need to update those changes for the database by using _migrations_. Migrations are managed by Flask-Migrate, and a few commands well help you get started.

To create the database:

    $ psql -c "CREATE DATABASE elmr;"
    $ bin/elmr-admin.py createdb

This command will cause PSQL to create a database with the owner as the currently logged in user. The `createdb` command will create the versioning table in the database as well as create the migrations folder if it doesn't already exist. Once you make changes:

    $ bin/elmr-admin.py migrate

This will create a migration file in the `elmr.migrations.versions` module. This Python script will be used to perform the migration on demand. Upgrade (or downgrade) the database as follows:

    $ bin/elmr-admin.py upgrade

Note that you'll have to run this as many times as it takes to get the DB version to spec. 

## Dependencies

This section describes some of the tools used in the project, as well as giving some tips and advice for quickly changing elements of the page. Note that Flask powers the backend, and the front end is a jQuery/Bootstrap javascript application.

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
