# Jobs Report (ELMR)

[![Stories in Ready](https://badge.waffle.io/mclumd/jobs-report.png?label=ready&title=Ready)](https://waffle.io/mclumd/jobs-report) [![Build Status](https://travis-ci.org/mclumd/jobs-report.svg)](https://travis-ci.org/mclumd/jobs-report)

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

        $ git clone git@github.com:mclumd/jobs-report.git
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
