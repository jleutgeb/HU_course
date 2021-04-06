from otree.api import *

c = Currency

doc = """
This a simple consent app. 
"""


# Constants define constant variables.
# name in url is used to create a url for web browser. subjects may see this so don't divulge information to them
# player_per_group unnecessary in consent app. every player gives consent alone
# num_rounds is 1 since we only give consent once, no repeats
class Constants(BaseConstants):
    name_in_url = 'consent'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


# player class only important class here: nothing important happens on subsession (i.e. round) or group level
class Player(BasePlayer):
    consents = models.BooleanField(  # create a consents model with a Boolean value: True or False
        label="Do you consent?",  # use label to display the question/choice that subjects have to make
        choices=[  # give subjects only one choice: consent (any other choices would be defined as list of lists)
            [1, "Yes"]  # first value is recorded in database, second is the label that is displayed to subjects
        ],
        widget=widgets.RadioSelect  # use standard otree radio select widget
    )


# PAGES
class Consent(Page):
    form_model = "player"  # tell the consent page to expect a player object to interact with it and store its data
    form_fields = ["consents"]  # tell the consent page to expect to fill the consent model


# we can leave ResultsWaitPage and Results in. will not be used
class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


# page sequence determines the sequence of pages that are displayed to subjects. Use only one: Consent
page_sequence = [Consent]
