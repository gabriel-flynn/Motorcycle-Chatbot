

class UserData:

    """
    :param name: user's name
    :param closest_track: closest track to the user
    :param motorcycles: a list of motorcycles that have been recommended to the user
    """
    def __init__(self, name, closest_track, motorcycles):
        self.name = name
        self.closest_track = closest_track
        self.motorcycles = motorcycles
