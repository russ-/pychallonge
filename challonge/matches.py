from challonge import api


def index(tournament_id_or_url, **params):
    """Retrieve a tournament's match list."""
    doc = api.fetch_and_parse("GET",
        "tournaments/%s/matches" % tournament_id_or_url,
        **params)

    matches = []

    for match in doc:
        matches.append(api._dictify_element(match))

    return matches


def show(tournament_id_or_url, match_id):
    """Retrieve a single match record for a tournament."""
    doc = api.fetch_and_parse("GET",
        "tournaments/%s/matches/%s" % (tournament_id_or_url, match_id))

    return api._dictify_element(doc)


def update(tournament_id_or_url, match_id, **params):
    """Update/submit the score(s) for a match."""
    api.fetch_and_parse("PUT",
        "tournaments/%s/matches/%s" % (tournament_id_or_url, match_id),
        **api._verbosify_parameters(params, "match"))
