gro-state
=========

.. image:: https://travis-ci.org/OpenAgInitiative/gro-api.svg?branch=develop
    :target: https://travis-ci.org/OpenAgInitiative/gro-api
    :alt: Build Status

.. image:: https://coveralls.io/repos/OpenAgInitiative/gro-api/badge.svg?branch=develop&service=github
    :target: https://coveralls.io/github/OpenAgInitiative/gro-api?branch=develop
    :alt: Code Coverage

.. image:: https://requires.io/github/OpenAgInitiative/gro-api/requirements.svg?branch=develop
    :target: https://requires.io/github/OpenAgInitiative/gro-api/requirements/?branch=develop
    :alt: Requirements Status

gro-state is a REST server that manages the state of a controlled growing
environment. Every other system component should store its state information in
this server. Users can write to resources on this server to control and
configure the environment itself and can read from resources on this server to
monitor the environment.
