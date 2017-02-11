from lists.services.tor import bridges


def update(skip_update=False):
    bridges.update(skip_update)
