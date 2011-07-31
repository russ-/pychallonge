# pychallonge

Pychallonge provides python bindings for the
[challonge.com](http://challonge.com) [API](http://challonge.com/api).


# Requirements

- python-dateutil==1.5


# Installation

pip install -e git+http://github.com/russ-/pychallonge


# Usage

    import challonge

    challonge.set_credentials("your_challonge_username", "your_api_key")
    tournaments = challonge.tournaments.index()

See [challonge.com](http://challonge.com/api) for full API documentation.

The methods that return objects return dicts of key, value pairs
constructed from the tag and text value of the xml elements. Index
methods return lists of dicts.

    for tournament in tournaments:
        print(tournament["name"], tournament["url"])

        # no return value:
        challonge.participants.randomize(tournament["id"])


# Running the unit tests

Pychallonge comes with a set of unit tests. The tests are not comprehensive,
but do utilize each method and verify basic functionality.

In order to test behavior of the python bindings, API calls must be made
to Challonge, which requires a username and api key. To run the tests
with your credentials, set `CHALLONGE_USER` and `CHALLONGE_KEY` appropriately
in your environment.

    $ git clone http://github.com/russ-/pychallonge pychallonge
    $ CHALLONGE_USER=russminus CHALLONGE_KEY=my_api_key python pychallonge/tests.py
    ................
    ----------------------------------------------------------------------
    Ran 16 tests in 67.103s

    OK
