from team import Team, Deets


class Game:
    def __init__(self, gameID, mode):
        self.ready = False
        self.gameID = gameID
        self.mode = mode
        self.teams = {0: Team(0)}

    def get_deets(self):
        deets = {}
        for team in self.teams:
            deets[self.teams[team].teamID] = self.teams[team].deets
        return deets

    def put_deets(self, deets: Deets):

        try:
            self.teams[deets.teamID].deets = deets
            # self.teams[int(deets.teamID)].update  # nec?
        except:
            self.teams[deets.teamID] = Team(deets.teamID)
            self.teams[deets.teamID].deets = deets
            # self.teams[int(deets.teamID)].update  # nec?
        if deets.hit:
            self.reset_current()
        self.teams[deets.teamID].current = True
#        self.teams[int(deets.teamID)].deets.current = True

    def connected(self):
        return self.ready

    def winner(self):
        for team in self.teams:
            if self.teams[team].lives > 0:
                return team
        return None

    def all_current(self):
        for team in self.teams:
            if not self.teams[team].current:
                return False
        return True

    def reset_current(self):
        for team in self.teams:
            self.teams[team].deets.current = False
