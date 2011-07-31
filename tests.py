from __future__ import print_function
import datetime
import os
import random
import string
import unittest
import challonge
from challonge import api


username = None
api_key = None


def _get_random_name():
    return "pychallonge_" + "".join(random.choice(string.ascii_lowercase) for x in xrange(0, 15))


class APITestCase(unittest.TestCase):
    def test_set_credentials(self):
        challonge.set_credentials(username, api_key)
        self.assertEqual(api._credentials["user"], username)
        self.assertEqual(api._credentials["api_key"], api_key)

    def test_get_credentials(self):
        api._credentials["user"] = username
        api._credentials["api_key"] = api_key
        self.assertEqual(challonge.get_credentials(), (username, api_key))

    def test_call(self):
        challonge.set_credentials(username, api_key)
        self.assertNotEqual(challonge.fetch("GET", "tournaments"), '')


class TournamentsTestCase(unittest.TestCase):
    def setUp(self):
        challonge.set_credentials(username, api_key)
        self.random_name = _get_random_name()

        self.t = challonge.tournaments.create(self.random_name, self.random_name)

    def tearDown(self):
        challonge.tournaments.destroy(self.t["id"])

    def test_index(self):
        ts = challonge.tournaments.index()
        ts = filter(lambda x: x["id"] == self.t["id"], ts)
        self.assertEqual(len(ts), 1)
        self.assertEqual(self.t, ts[0])

    def test_show(self):
        self.assertEqual(challonge.tournaments.show(self.t["id"]),
                         self.t)

    def test_update(self):
        challonge.tournaments.update(self.t["id"], name="Test!")

        t = challonge.tournaments.show(self.t["id"])

        self.assertEqual(t["name"], "Test!")
        del t["name"]
        del self.t["name"]

        self.assertTrue(t["updated-at"] >= self.t["updated-at"])
        del t["updated-at"]
        del self.t["updated-at"]

        self.assertEqual(t, self.t)

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
        challonge.set_credentials(username, api_key)
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

        self.assertTrue(self.p1 == ps[0] or self.p1 == ps[1])
        self.assertTrue(self.p2 == ps[0] or self.p2 == ps[1])

    def test_show(self):
        p1 = challonge.participants.show(self.t["id"], self.p1["id"])
        self.assertEqual(p1, self.p1)

    def test_update(self):
        challonge.participants.update(self.t["id"], self.p1["id"], misc="Test!")
        p1 = challonge.participants.show(self.t["id"], self.p1["id"])

        self.assertEqual(p1["misc"], "Test!")
        del self.p1["misc"]
        del p1["misc"]

        self.assertTrue(p1["updated-at"] >= self.p1["updated-at"])
        del self.p1["updated-at"]
        del p1["updated-at"]

        self.assertEqual(self.p1, p1)

    def test_randomize(self):
        # randomize has a 50% chance of actually being different than
        # current seeds, so we're just verifying that the method runs at all
        challonge.participants.randomize(self.t["id"])


class MatchesTestCase(unittest.TestCase):
    def setUp(self):
        challonge.set_credentials(username, api_key)
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
            self.assertEqual(m, challonge.matches.show(self.t["id"], m["id"]))

    def test_update(self):
        ms = challonge.matches.index(self.t["id"])
        m = ms[0]
        self.assertEqual(m["state"], "open")

        challonge.matches.update(self.t["id"], m["id"],
            scores_csv="3-2,4-1,2-2", winner_id=m["player1-id"])

        m = challonge.matches.show(self.t["id"], m["id"])
        self.assertEqual(m["state"], "complete")



if __name__ == "__main__":
    username = os.environ.get("CHALLONGE_USER")
    api_key = os.environ.get("CHALLONGE_KEY")
    if not username or not api_key:
        raise RuntimeError("You must add CHALLONGE_USER and CHALLONGE_KEY \
            to your environment variables to run the test suite")

    unittest.main()
