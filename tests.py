from __future__ import print_function
import os
import random
import string
import unittest
import challonge
from challonge import api


def _get_random_name():
    return "pychallonge_" + "".join(random.choice(string.ascii_lowercase) for x in xrange(0, 15))

def _remove_dates(d):
    """Removes created-at and updated-at attributes, for easier testing.

    This is caused by different timezones being used for dates, not because
    the dates are necessarily different.

    TODO Could be dealt with more correctly by converting params to correct datatypes
    in api._dictify_element().
    """
    if "created-at" in d:
        del d["created-at"]
    if "updated-at" in d:
        del d["updated-at"]


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.username = os.environ.get("CHALLONGE_USER")
        self.api_key = os.environ.get("CHALLONGE_KEY")
        if not self.username or not self.api_key:
            raise RuntimeError("You must add CHALLONGE_USER and CHALLONGE_KEY \
            to your environment variables to run the test suite")

    def test_set_credentials(self):
        challonge.set_credentials(self.username, self.api_key)
        self.assertEqual(api._credentials["user"], self.username)
        self.assertEqual(api._credentials["api_key"], self.api_key)

    def test_get_credentials(self):
        api._credentials["user"] = self.username
        api._credentials["api_key"] = self.api_key
        self.assertEqual(challonge.get_credentials(), (self.username, self.api_key))

    def test_call(self):
        challonge.set_credentials(self.username, self.api_key)
        challonge.fetch("GET", "tournaments")


class TournamentsTestCase(unittest.TestCase):
    def setUp(self):
        self.username = os.environ.get("CHALLONGE_USER")
        self.api_key = os.environ.get("CHALLONGE_KEY")
        challonge.set_credentials(self.username, self.api_key)
        self.random_name = _get_random_name()

        self.t = challonge.tournaments.create(self.random_name, self.random_name)

    def tearDown(self):
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ts = challonge.tournaments.index()
        ts = filter(lambda x: x["id"] == self.t["id"], ts)
        self.assertEqual(len(ts), 1)
        self.assertEqual(_remove_dates(self.t), _remove_dates(ts[0]))

    def test_show(self):
        self.assertEqual(_remove_dates(challonge.tournaments.show(self.t["id"])),
                         _remove_dates(self.t))

    def test_update(self):
        challonge.tournaments.update(self.t["id"], name="Test!")

        t = challonge.tournaments.show(self.t["id"])
        self.assertEqual(t["name"], "Test!")
        del t["name"]
        del self.t["name"]
        self.assertEqual(_remove_dates(t), _remove_dates(self.t))

    def test_publish(self):
        self.assertRaises(challonge.ChallongeException,
            challonge.tournaments.publish, self.t["id"])

        self.assertEqual(self.t["published-at"], None)
        ps = [
            challonge.participants.create(self.t["id"], "#1"),
            challonge.participants.create(self.t["id"], "#2")
        ]
        challonge.tournaments.publish(self.t["id"])
        t = challonge.tournaments.show(self.t["id"])
        self.assertNotEqual(t["published-at"], None)

    def test_start(self):
        # we have to have participants
        self.assertRaises(challonge.ChallongeException,
            challonge.tournaments.start, self.t["id"])

        self.assertEqual(self.t["started-at"], None)
        ps = [
            challonge.participants.create(self.t["id"], "#1"),
            challonge.participants.create(self.t["id"], "#2")
        ]

        # we have to publish, first
        self.assertRaises(challonge.ChallongeException,
            challonge.tournaments.start, self.t["id"])

        challonge.tournaments.publish(self.t["id"])
        challonge.tournaments.start(self.t["id"])

        t = challonge.tournaments.show(self.t["id"])
        self.assertNotEqual(t["published-at"], None)
        self.assertNotEqual(t["started-at"], None)

    def test_reset(self):
        ps = [
            challonge.participants.create(self.t["id"], "#1"),
            challonge.participants.create(self.t["id"], "#2")
        ]
        challonge.tournaments.publish(self.t["id"])
        challonge.tournaments.start(self.t["id"])

        self.assertRaises(challonge.ChallongeException,
            challonge.participants.create, self.t["id"], "name")

        challonge.tournaments.reset(self.t["id"])

        # assertNotRaises
        p = challonge.participants.create(self.t["id"], "name")

        challonge.participants.destroy(self.t["id"], p["id"])


class ParticipantsTestCase(unittest.TestCase):
    def setUp(self):
        self.username = os.environ.get("CHALLONGE_USER")
        self.api_key = os.environ.get("CHALLONGE_KEY")
        challonge.set_credentials(self.username, self.api_key)
        self.t_name = _get_random_name()

        self.t = challonge.tournaments.create(self.t_name, self.t_name)
        self.p1_name = _get_random_name()
        self.p1 = challonge.participants.create(self.t["id"], self.p1_name)
        self.p2_name = _get_random_name()
        self.p2 = challonge.participants.create(self.t["id"], self.p2_name)

    def tearDown(self):
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ps = challonge.participants.index(self.t["id"])
        self.assertEqual(len(ps), 2)
        ps = [_remove_dates(p) for p in ps]
        self.assertTrue(_remove_dates(self.p1) == ps[0] or _remove_dates(self.p1) == ps[1])
        self.assertTrue(_remove_dates(self.p2) == ps[0] or _remove_dates(self.p2) == ps[1])

    def test_show(self):
        p1 = challonge.participants.show(self.t["id"], self.p1["id"])
        self.assertEqual(_remove_dates(p1), _remove_dates(self.p1))

    def test_update(self):
        challonge.participants.update(self.t["id"], self.p1["id"], misc="Test!")
        p1 = challonge.participants.show(self.t["id"], self.p1["id"])
        self.assertEqual(p1["misc"], "Test!")
        
        del self.p1["misc"]
        del p1["misc"]
        self.assertEqual(_remove_dates(self.p1), _remove_dates(p1))

    def test_randomize(self):
        # randomize has a 50% chance of actually being different than
        # current seeds, so we're just verifying that the method runs at all
        challonge.participants.randomize(self.t["id"])


class MatchesTestCase(unittest.TestCase):
    def setUp(self):
        self.username = os.environ.get("CHALLONGE_USER")
        self.api_key = os.environ.get("CHALLONGE_KEY")
        challonge.set_credentials(self.username, self.api_key)
        self.t_name = _get_random_name()

        self.t = challonge.tournaments.create(self.t_name, self.t_name)
        self.p1_name = _get_random_name()
        self.p1 = challonge.participants.create(self.t["id"], self.p1_name)
        self.p2_name = _get_random_name()
        self.p2 = challonge.participants.create(self.t["id"], self.p2_name)
        challonge.tournaments.publish(self.t["id"])
        challonge.tournaments.start(self.t["id"])

    def tearDown(self):
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ms = challonge.matches.index(self.t["id"])

        self.assertEqual(len(ms), 1)
        m = ms[0]

        ps = set((self.p1["id"], self.p2["id"]))
        self.assertEqual(ps, set((m["player1-id"], m["player2-id"])))
        self.assertEqual(m["state"], "open")

    def test_show(self):
        ms = challonge.matches.index(self.t["id"])
        for m in ms:
            self.assertEqual(_remove_dates(m),
                _remove_dates(challonge.matches.show(self.t["id"], m["id"])))

    def test_update(self):
        ms = challonge.matches.index(self.t["id"])
        m = ms[0]
        self.assertEqual(m["state"], "open")

        challonge.matches.update(self.t["id"], m["id"],
            scores_csv="3-2,4-1,2-2", winner_id=m["player1-id"])

        m = challonge.matches.show(self.t["id"], m["id"])
        self.assertEqual(m["state"], "complete")
        

if __name__ == "__main__":
        unittest.main()
