"""
This module contains a single model, :class:`Farm`, which represents a single
growing unit. It holds information about the configuration of the system,
especially in the :attr:`layout` attribute, and some of the other apps in the
project change their behavior based on the state of the current :class:`Farm`.
Because it is the top level objects for an installation of this system and
because it is only modified during system setup, it also contains the logic for
registering a system to a central entity and triggering the setup of other apps
as needed.
"""
