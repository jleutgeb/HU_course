from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        if self.player.id_in_group == 1 and self.player.session.config["leadership"]:
            yield Leadership, dict(contribution=random.randint(0, 10))
        if self.player.id_in_group != 1 or not self.player.session.config["leadership"]:
            yield PggChoice, dict(
                contribution=random.randint(0, 10)
                # contribution=random.normalvariate(self.player.group.get_player_by_id(1).contribution, 1)
            )
        yield PggFeedback
        if self.player.round_number == Constants.num_rounds:
            yield PggFinalFeedback
