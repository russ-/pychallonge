from challonge import api


def index(tournament_id_or_url):
    """Retrieve a tournament's participant list."""
    doc = api.fetch_and_parse("GET",
        "tournaments/%s/participants" % tournament_id_or_url)

    participants = []

    for participant in doc:
        participants.append(api._dictify_element(participant))

    return participants


def create(tournament_id_or_url, name, **params):
    """Add a participant to a tournament."""
    params.update({"name": name})

    doc = api.fetch_and_parse("POST",
        "tournaments/%s/participants" % tournament_id_or_url, "participant",
        **params)

    return api._dictify_element(doc)


def show(tournament_id_or_url, participant_id):
    """Retrieve a single participant record for a tournament."""
    doc = api.fetch_and_parse("GET",
        "tournaments/%s/participants/%s" % (tournament_id_or_url, participant_id))

    return api._dictify_element(doc)


def update(tournament_id_or_url, participant_id, **params):
    """Update the attributes of a tournament participant."""
    api.fetch("PUT",
        "tournaments/%s/participants/%s" % (tournament_id_or_url, participant_id),
        "participant", **params)


def destroy(tournament_id_or_url, participant_id):
    """Destroys or deactivates a participant.

    If tournament has not started, delete a participant, automatically
    filling in the abandoned seed number.

    If tournament is underway, mark a participant inactive, automatically
    forfeiting his/her remaining matches.
    """
    api.fetch("DELETE",
        "tournaments/%s/participants/%s" % (tournament_id_or_url, participant_id))


def randomize(tournament_id_or_url):
    """Randomize seeds among participants.

    Only applicable before a tournament has started.
    """
    api.fetch("POST",
        "tournaments/%s/participants/randomize" % tournament_id_or_url)
