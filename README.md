# pychallonge

Pychallonge provides python bindings for the
[CHALLONGE!](http://challonge.com) [API](http://api.challonge.com/v1).


# Requirements

- python-dateutil==1.5


# Installation

    pip install -e git+http://github.com/russ-/pychallonge#egg=pychallonge


# Usage

```python
import challonge

# Tell pychallonge about your [CHALLONGE! API credentials](http://api.challonge.com/v1).
challonge.set_credentials("your_challonge_username", "your_api_key")

# Retrieve a tournament by its id (or its url).
tournament = challonge.tournaments.show(3272)

# Tournaments, matches, and participants are all represented as normal Python dicts.
print(tournament["id"]) # 3272
print(tournament["name"]) # My Awesome Tournament
print(tournament["started-at"]) # None

# Retrieve the participants for a given tournament.
participants = challonge.participants.index(tournament["id"])
print(len(participants)) # 13

# Start the tournament and retrieve the updated information to see the effects
# of the change.
challonge.tournaments.start(tournament["id"])
tournament = challonge.tournaments.show(tournament["id"])
print(tournament["started-at"]) # 2011-07-31 16:16:02-04:00
```

See [challonge.com](http://api.challonge.com/v1) for full API documentation.


# Running the unit tests

Pychallonge comes with a set of unit tests. The tests are not comprehensive,
but do utilize each method and verify basic functionality.

In order to test behavior of the python bindings, API calls must be made
to CHALLONGE!, which requires a username and api key. To run the tests
with your credentials, set `CHALLONGE_USER` and `CHALLONGE_KEY` appropriately
in your environment.

    $ git clone http://github.com/russ-/pychallonge pychallonge
    $ CHALLONGE_USER=my_user CHALLONGE_KEY=my_api_key python pychallonge/tests.py
    ....................
    ----------------------------------------------------------------------
    Ran 20 tests in 82.314s

    OK

Note that several tournaments are created, published, started, and completed
over the course of the unit tests. These should be cleaned up by the end, but
if any of the tests fail they may not be cleaned up. As long as the basic
functions work, you can clean up errant tournaments as follows.

    >>> import challonge
    >>> challonge.set_credentials("my_user", "my_api_key")
    >>> for t in challonge.tournaments.index():
    ...     if t["name"].startswith("pychallonge"):
    ...         challonge.tournaments.destroy(t["id"])
