gro-API
=======

.. image:: https://travis-ci.org/OpenAgInitiative/gro-api.svg?branch=master
    :target: https://travis-ci.org/OpenAgInitiative/gro-api
    :alt: Build Status

.. image:: https://coveralls.io/repos/OpenAgInitiative/gro-api/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/OpenAgInitiative/gro-api?branch=master
    :alt: Code Coverage

.. image:: https://requires.io/github/OpenAgInitiative/gro-api/requirements.svg?branch=master
    :target: https://requires.io/github/OpenAgInitiative/gro-api/requirements/?branch=master
    :alt: Requirements Status

**DEPRECATED** This repository is no longer being actively maintained.

The gro-API is a REST server that manages an instance of a controlled growing
environment. Users can write to resources on the server to control and monitor
the environment itself, and firmware in the environment should write data to
and read instructions from the server during normal operation.

Installation
------------

First clone the repository::

    git clone https://github.com/OpenAgInitiative/gro-api.git

Then, install the Python package globally::

    cd gro-api
    sudo pip3 install .

You will have to create a directory for holding the log files::

    sudo mkdir /var/log/gro_api

Then, configure the package as follows::

    sudo gro_api_configure
    sudo gro_api_call_command migrate
    sudo gro_api_call_command createsuperuser

Now, you can run the API as follows::

    sudo gro_api_call_command runserver

Log into the API as the superuser you created during setup by posting its
credentials to the `/auth/login/` endpoint::

    curl -X POST http://localhost:8000/auth/login/ --data "username=<username>&password=<password>"

This will give you a token which you must send in all future requests to the
API. Now, you must update the `farm` singleton object located at `/farm/1` in
the api::

    curl -X PUT http://localhost:8000/farm/1/ -H "Authorization: Token <token>" --data "layout=tray"

Setting the `layout` of your farm to `tray` tells the API that your system is a
food computer with a single tray, allowing it to set up some things in the
database.

Now, if you are working on a version 1 food computer, there is a fixture you
can load which creates records on the database for the sensors and actuators in
that system::

    sudo gro_api_call_command loaddata pfc_data
