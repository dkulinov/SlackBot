class CommandInput:
    def __init__(self, oldest: str, newest: str, channel_id: str, team_id: str):
        self.oldest = oldest
        self.newest = newest
        self.channel_id = channel_id
        self.team_id = team_id
