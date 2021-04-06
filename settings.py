from os import environ


# session configs need:
# a name (for internal storage)
# a display name (for display to experimenter panel)
# a number of demo participants (to tell otree how many demo participants it should start when
# starting a session through the demo tab
# a sequence of apps
# any other session variables for treatments: can be switched on and off when starting a session
# good idea to create session configs for different treatments with correct treatments already enabled
SESSION_CONFIGS = [
    dict(
        name="course_leadership",
        display_name="Course (Leadership)",
        num_demo_participants=3,
        app_sequence=["consent", "pgg"],
        leadership=True,
        real_world_currency_per_point=0.1,
        participation_fee=5.00
    ),
    dict(
        name="course_noleadership",
        display_name="Course (No Leadership)",
        num_demo_participants=3,
        app_sequence=["consent", "pgg"],
        leadership=False
    ),
    dict(
        name="course_bots",
        display_name="Course (Bots)",
        num_demo_participants=3,
        app_sequence=["consent", "pgg"],
        leadership=False,
        use_browser_bots=True
    )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'de'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'Groschen'

# this is just a comment
ROOMS = [
    dict(
        name='TU_WZB',
        display_name='TU-WZB Laboratory Session',
        participant_label_file='_rooms/TU-WZB.txt',
        use_secure_urls=False
    ),
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '8032099788074'

INSTALLED_APPS = ['otree']
