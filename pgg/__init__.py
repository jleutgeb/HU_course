from otree.api import *
import random

c = Currency

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'pgg'
    players_per_group = 3  # every group has three players
    num_rounds = 2  # play the game for 2 rounds
    budget = cu(10)  # give subjects a budget of 10 currency units
    multiplier = 0.4  # subjects receive 40% of whatever is in the group accound


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total = models.CurrencyField()  # this group variable sums up all contributions by players in a group
    # no labels, min or max necessary since subjects don't interact with this variable directly


class Player(BasePlayer):
    contribution = models.CurrencyField(  # use a currencyfield here: otree automatically knows to use currency/points
        label="How much do you want to put into the group account?",
        min=0,  # if subjects try to enter an amount less than zero or more than their budget, return error
        max=Constants.budget
    )
    eyes = models.BooleanField()  # treatment variable. If eyes is true, player is in treatment eyes
    dropout = models.BooleanField()  # dropout variable. If true, player has dropped out


# the FUNCTIONS block contains functions that can be called from other places in the code
# FUNCTIONS
def calc_payoffs(group):  # payoffs are calculated on the group object
    # collect budget and multiplier from Constants and store in local variables. deleted after function has finished
    budget = Constants.budget
    multiplier = Constants.multiplier
    # get a list of players playing in the group from the group object.
    players = group.get_players()  # use oTree default get_players() function
    # construct a list of contributions. for every player element in players, save contribution to a list
    contributions = [p.contribution for p in players]
    # sum up the contributions and save it to the group total variable (will be saved in database)
    group.total = sum(contributions)
    # calculate payouts to participants as local variable
    payout = group.total * multiplier
    # in oTree every player element has payoff field by default, no need to declare it
    # for every player in the group, calculate payoff
    for p in players:
        p.payoff = budget - p.contribution + payout


# creating_session function called automatically when creating all the rounds
def creating_session(subsession):
    # only in round number 1: group all participants randomly into groups and then randomly assign treatment
    if subsession.round_number == 1:
        subsession.group_randomly()
        # create a list of all groups in the current subsession
        groups = subsession.get_groups()
        # loop through all groups
        for g in groups:
            # draw a random number from a uniform distribution (0,1)
            # if the number is greater than 0.5, put entire group into the eyes treatment (50% chance)
            eyes = random.random() > 0.5
            # get a list of all players in the group we're currently looping through
            players = g.get_players()
            # loop through all players in the current group.
            # and assign to every participant in the group the treatment (which was drawn on the group level)
            # and the initial dropout value (initially none of the participants have dropped out)
            # store those values in the participant's variables (dictionary that participants carry through all apps)
            for p in players:
                p.participant.vars['eyes'] = eyes
                p.participant.vars['dropout'] = False
    # if we are not in round == 1, shuffle players within their groups
    # => groups remain stable, but someone else gets id=1 and becomes leader
    else:
        # initially, group every round > 1 like in round 1
        subsession.group_like_round(1)
        # get the current group matrix (functionally a list of lists: every element in the matrix is a group,
        # which has a list of players within it)
        matrix = subsession.get_group_matrix()
        # loop through all groups in the matrix and randomly shuffle it. this function automatically saves result.
        for group in matrix:
            random.shuffle(group)
        # finally, set the shuffled group matrix as the new grouping matrix for this round
        subsession.set_group_matrix(matrix)

    # in all rounds assign player's eyes treatment as the value of his participant variable
    groups = subsession.get_groups()
    for g in groups:
        players = g.get_players()
        for p in players:
            p.eyes = p.participant.vars['eyes']


# PAGES
class PggChoice(Page):
    form_model = "player"
    form_fields = ["contribution"]
    # timeout_seconds = 10  # set the timeout to 10 seconds

    # use the vars for template function to push data to the html page
    @staticmethod
    def vars_for_template(player: Player):
        # set leader contribution as an empty variable initially
        # only if we are in leadership treatment, fill it with player 1's contribution
        # else: there is no leader whose contribution we could push to the page
        leader_contribution = []
        # get session config by asking the player to ask the session to ask the config to return value for leadership
        # session config is a dictionary
        if player.session.config["leadership"]:
            leader_contribution = player.group.get_player_by_id(1).contribution
        # send a dictionary to the html page. LHS is the name we will use to access data, RHS is the value
        return dict(
            eyes=player.eyes,
            current_round=player.round_number,
            total_number_rounds=Constants.num_rounds,
            budget=Constants.budget,
            multiplier=Constants.multiplier,
            leader_contribution=leader_contribution,
            leadership=player.session.config["leadership"]
        )

    # use the is_displayed function to only display this page to some people
    # if this function returns a True value, it is displayed
    # only display this page if we are either not in the leadership treatment, or if the player is not the leader
    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group != 1 or not player.session.config["leadership"]

    # use the before_next_page function to execute any code before the subject continues to the next page
    # in this case: if a timeout happened, set participant's dropout variable to True
    # afterwards (no matter if a timeout happened or not) record participant variable in player variable (so it's saved
    # in the database)
    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.participant.vars['dropout'] = True
        player.dropout = player.participant.vars['dropout']


class Leadership(Page):
    form_model = "player"
    form_fields = ["contribution"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            current_round=player.round_number,
            total_number_rounds=Constants.num_rounds,
            budget=Constants.budget,
            multiplier=Constants.multiplier
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1 and player.session.config["leadership"]


# this waitpage is only used if we are in the leadership treatment. if not, there is nothing to wait for
class LeadershipWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.session.config["leadership"]


# PggWaitpage is a good place to calculate payoffs. All players have to wait for each other and everybody has made
# their choice
class PggWaitPage(WaitPage):
    after_all_players_arrive = calc_payoffs


class PggFeedback(Page):
    # use the js_vars function to push information to the javascript part of the website
    @staticmethod
    def js_vars(player: Player):
        return dict(
            # first, construct a range of all rounds that have happened till now. remember, range (x, y) does not
            # include y but only works UP TO y
            # range(1, current round + 1)
            # for every round in this range: ask the current player which player they were in the given round.
            # record this old player's contribution and their group's total in a list
            allGroupContributions=[player.in_round(r).group.total for r in range(1, player.round_number+1)],
            allMyContributions=[player.in_round(r).contribution for r in range(1, player.round_number+1)]
        )

    # you can use the get_timeout_seconds function to set timeouts conditional on some variables
    # here: if the player has dropped out in the PggChoice page, skip the feedback page (0 second means
    # immediate timeout)
    @staticmethod
    def get_timeout_seconds(player: Player):
        if player.participant.vars['dropout']:
            return 0

    @staticmethod
    def vars_for_template(player: Player):
        # for every player, get the list of every other player in their group and save it in a local variable
        others = player.get_others_in_group()
        # for every player in this list, save their contribution and their payoff in a list
        others_contribs = [o.contribution for o in others]
        others_payoffs = [o.payoff for o in others]
        return dict(
            current_round=player.round_number,
            total_number_rounds=Constants.num_rounds,
            budget=Constants.budget,
            contribution=player.contribution,
            payoff=player.payoff,
            others_contribs=others_contribs,
            others_payoffs=others_payoffs,
            total=player.group.total,
            multiplier=Constants.multiplier
        )


class PggFinalFeedback(Page):
    @staticmethod
    def is_displayed(player: Player):
        # only display this page if we are in the final round
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        round1 = player.in_round(player.round_number-1).payoff
        return dict(
            total_payoff=player.participant.payoff,
            round1=round1,
            round2=player.payoff
        )


page_sequence = [
    Leadership,
    LeadershipWaitPage,
    PggChoice,
    PggWaitPage,
    PggFeedback,
    PggFinalFeedback
]
