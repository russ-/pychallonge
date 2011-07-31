from challonge import api


def index(**params):
    """Retrieve a set of tournaments created with your account."""
    doc = api.fetch_and_parse("GET", "tournaments", **api._prepare_params(params))

    tournaments = []

    for tournament in doc:
        tournaments.append(api._dictify_element(tournament))

    return tournaments


def create(name, url, tournament_type="single elimination", **params):
    """Create a new tournament."""
    params.update({
        "name": name,
        "url": url,
        "tournament_type": tournament_type,
    })
    params = api._prepare_params(params, prefix="tournament")

    doc = api.fetch_and_parse("POST", "tournaments", **params)

    return api._dictify_element(doc)


def show(tournament_id_or_url):
    """Retrieve a single tournament record created with your account."""
    doc = api.fetch_and_parse("GET", "tournaments/%s" % tournament_id_or_url)
    return api._dictify_element(doc)


def update(tournament_id, **params):
    """Update a tournament's attributes."""
    api.fetch("PUT", "tournaments/%s" % tournament_id,
              **api._prepare_params(params, prefix="tournament"))


def destroy(tournament_id_or_url):
    """Deletes a tournament along with all its associated records.

    There is no undo, so use with care!
    """
    api.fetch("DELETE", "tournaments/%s" % tournament_id_or_url)


def publish(tournament_id_or_url):
    """Publish a tournament, making it publically accessible.

     The tournament must have at least 2 participants.
     """
    api.fetch("POST", "tournaments/publish/%s" % tournament_id_or_url)


def start(tournament_id_or_url):
    """Start a tournament, opening up matches for score reporting.

    The tournament must have at least 2 participants.
    """
    api.fetch("POST", "tournaments/start/%s" % tournament_id_or_url)


def reset(tournament_id_or_url):
    """Reset a tournament, clearing all of its scores and attachments.

    You can then add/remove/edit participants before starting the
    tournament again.
    """
    api.fetch("POST", "tournaments/reset/%s" % tournament_id_or_url)
