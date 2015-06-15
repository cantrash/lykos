import fnmatch
import math
import random
import sqlite3
from collections import defaultdict

import botconfig
from src import events

MINIMUM_WAIT = 60
EXTRA_WAIT = 30
EXTRA_WAIT_JOIN = 0 # Add this many seconds to the waiting time for each !join
WAIT_AFTER_JOIN = 25 # Wait at least this many seconds after the last join
# !wait uses a token bucket
WAIT_TB_INIT  = 2   # initial number of tokens
WAIT_TB_DELAY = 240 # wait time between adding tokens
WAIT_TB_BURST = 3   # maximum number of tokens that can be accumulated
STATS_RATE_LIMIT = 60
VOTES_RATE_LIMIT = 60
ADMINS_RATE_LIMIT = 300
GSTATS_RATE_LIMIT = 0
PSTATS_RATE_LIMIT = 0
TIME_RATE_LIMIT = 10
START_RATE_LIMIT = 10  # (per-user)
WAIT_RATE_LIMIT = 10  # (per-user)
SHOTS_MULTIPLIER = .12  # ceil(shots_multiplier * len_players) = bullets given
SHARPSHOOTER_MULTIPLIER = 0.06
MIN_PLAYERS = 4
MAX_PLAYERS = 24
DRUNK_SHOTS_MULTIPLIER = 3
NIGHT_TIME_LIMIT = 120
NIGHT_TIME_WARN = 90  # should be less than NIGHT_TIME_LIMIT
DAY_TIME_LIMIT = 720
DAY_TIME_WARN = 600   # should be less than DAY_TIME_LIMIT
JOIN_TIME_LIMIT = 3600
# May only be set if the above are also set
SHORT_DAY_PLAYERS = 6 # Number of players left to have a short day
SHORT_DAY_LIMIT = 520
SHORT_DAY_WARN = 400
# If time lord dies, the timers get set to this instead (60s day, 30s night)
TIME_LORD_DAY_LIMIT = 60
TIME_LORD_DAY_WARN = 45
TIME_LORD_NIGHT_LIMIT = 30
TIME_LORD_NIGHT_WARN = 20
KILL_IDLE_TIME = 300
WARN_IDLE_TIME = 180
PM_WARN_IDLE_TIME = 240
PART_GRACE_TIME = 30
QUIT_GRACE_TIME = 30
ACC_GRACE_TIME = 30
START_QUIT_DELAY = 10
#  controls how many people it does in one /msg; only works for messages that are the same
MAX_PRIVMSG_TARGETS = 4
# how many mode values can be specified at once; used only as fallback
MODELIMIT = 3
LEAVE_STASIS_PENALTY = 1
IDLE_STASIS_PENALTY = 1
PART_STASIS_PENALTY = 1
ACC_STASIS_PENALTY = 1
QUIET_DEAD_PLAYERS = False
QUIET_MODE = "q" # "q" or "b"
QUIET_PREFIX = "" # "" or "~q:"
# The bot will automatically toggle those modes of people joining
AUTO_TOGGLE_MODES = ""

DYNQUIT_DURING_GAME = False # are dynamic quit messages used while a game is in progress? Note that true will break certain stats scrapers

GOAT_HERDER = True

ABSTAIN_ENABLED = True # whether village can !abstain in order to not vote anyone during day
LIMIT_ABSTAIN = True # if true, village will be limited to successfully !abstaining a vote only once
SELF_LYNCH_ALLOWED = True
HIDDEN_TRAITOR = True
HIDDEN_AMNESIAC = False # amnesiac still shows as amnesiac if killed even after turning
HIDDEN_CLONE = False
GUARDIAN_ANGEL_CAN_GUARD_SELF = True
START_WITH_DAY = False
WOLF_STEALS_GUN = True  # at night, the wolf can steal steal the victim's bullets
ROLE_REVEAL = True
LOVER_WINS_WITH_FOOL = False # if fool is lynched, does their lover win with them?
DEFAULT_SEEN_AS_VILL = True # non-wolves are seen as villager regardless of the default role

# Debug mode settings, whether or not timers and stasis should apply during debug mode
DISABLE_DEBUG_MODE_TIMERS = True
DISABLE_DEBUG_MODE_TIME_LORD = False
DISABLE_DEBUG_MODE_REAPER = True
DISABLE_DEBUG_MODE_STASIS = True

# Minimum number of players needed for mad scientist to skip over dead people when determining who is next to them
# Set to 0 to always skip over dead players. Note this is number of players that !joined, NOT number of players currently alive
MAD_SCIENTIST_SKIPS_DEAD_PLAYERS = 16

CARE_BOLD = False
CARE_COLOR = False
KILL_COLOR = False
KILL_BOLD = False

                         #       HIT    MISS    SUICIDE   HEADSHOT
GUN_CHANCES              =   (   5/7  ,  1/7  ,   1/7   ,   2/5   )
WOLF_GUN_CHANCES         =   (   5/7  ,  1/7  ,   1/7   ,   2/5   )
DRUNK_GUN_CHANCES        =   (   2/7  ,  3/7  ,   2/7   ,   2/5   )
SHARPSHOOTER_GUN_CHANCES =   (    1   ,   0   ,    0    ,    1    )

GUNNER_KILLS_WOLF_AT_NIGHT_CHANCE = 1/4
GUARDIAN_ANGEL_DIES_CHANCE = 0
BODYGUARD_DIES_CHANCE = 0
DETECTIVE_REVEALED_CHANCE = 2/5
SHARPSHOOTER_CHANCE = 1/5 # if sharpshooter is enabled, chance that a gunner will become a sharpshooter instead
FALLEN_ANGEL_KILLS_GUARDIAN_ANGEL_CHANCE = 1/2

AMNESIAC_NIGHTS = 3 # amnesiac gets to know their actual role on this night
ALPHA_WOLF_NIGHTS = 3 # alpha wolf turns the target into a wolf after this many nights (note the night they are bitten is considered night 1)

DOCTOR_IMMUNIZATION_MULTIPLIER = 0.135 # ceil(num_players * multiplier) = number of immunizations

TOTEM_ORDER   =                  (   "shaman"  , "crazed shaman" )
TOTEM_CHANCES = {       "death": (      1      ,        1        ),
                   "protection": (      1      ,        1        ),
                      "silence": (      1      ,        1        ),
                    "revealing": (      1      ,        1        ),
                  "desperation": (      1      ,        1        ),
                   "impatience": (      1      ,        1        ),
                     "pacifism": (      1      ,        1        ),
                    "influence": (      1      ,        1        ),
                   "narcolepsy": (      0      ,        1        ),
                     "exchange": (      0      ,        1        ),
                  "lycanthropy": (      0      ,        1        ),
                         "luck": (      0      ,        1        ),
                   "pestilence": (      0      ,        1        ),
                  "retribution": (      0      ,        1        ),
                 "misdirection": (      0      ,        1        ),
                }

GAME_MODES = {}
SIMPLE_NOTIFY = []  # cloaks of people who !simple, who don't want detailed instructions
SIMPLE_NOTIFY_ACCS = [] # same as above, except accounts. takes precedence
PREFER_NOTICE = []  # cloaks of people who !notice, who want everything /notice'd
PREFER_NOTICE_ACCS = [] # Same as above, except accounts. takes precedence

ACCOUNTS_ONLY = False # If True, will use only accounts for everything
DISABLE_ACCOUNTS = False # If True, all account-related features are disabled. Automatically set if we discover we do not have proper ircd support for accounts
                        # This will override ACCOUNTS_ONLY if it is set

STASISED = defaultdict(int)
STASISED_ACCS = defaultdict(int)

# TODO: move this to a game mode called "fixed" once we implement a way to randomize roles (and have that game mode be called "random")
DEFAULT_ROLE = "villager"
ROLE_INDEX =                      (  4  ,  6  ,  7  ,  8  ,  9  , 10  , 11  , 12  , 13  , 15  , 16  , 18  , 20  , 21  , 23  , 24  )
ROLE_GUIDE = {# village roles
              "villager"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "seer"            : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "oracle"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "augur"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ),
              "village drunk"   : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "harlot"          : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "guardian angel"  : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "bodyguard"       : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "detective"       : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "time lord"       : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "matchmaker"      : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "mad scientist"   : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "hunter"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "shaman"          : (  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "doctor"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "mystic"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              # wolf roles
              "wolf"            : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ,  2  ,  3  ,  3  ,  3  ),
              "traitor"         : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "werecrow"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "cultist"         : (  0  ,  0  ,  1  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "minion"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "hag"             : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ),
              "wolf cub"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "sorcerer"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ),
              "alpha wolf"      : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "werekitten"      : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "warlock"         : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "wolf mystic"     : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "fallen angel"    : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              # neutral roles
              "lycan"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "vengeful ghost"  : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "clone"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "crazed shaman"   : (  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "fool"            : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "jester"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "monster"         : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "amnesiac"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ),
              "piper"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              # templates
              "cursed villager" : (  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ,  2  ),
              "gunner"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ),
              # NB: for sharpshooter, numbers can't be higher than gunner, since gunners get converted to sharpshooters. This is the MAX number of gunners that can be converted.
              "sharpshooter"    : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "mayor"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ),
              "assassin"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "bureaucrat"      : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              }

# Harlot dies when visiting, seer sees as wolf, gunner kills when shooting, GA and bodyguard have a chance at dying when guarding
# If every wolf role dies, and there are no remaining traitors, the game ends and villagers win (monster may steal win)
WOLF_ROLES = ["wolf", "alpha wolf", "werecrow", "wolf cub", "werekitten", "wolf mystic", "fallen angel"]
# Access to wolfchat, and counted towards the # of wolves vs villagers when determining if a side has won
WOLFCHAT_ROLES = WOLF_ROLES + ["traitor", "hag", "sorcerer", "warlock"]
# Wins with the wolves, even if the roles are not necessarily wolves themselves
WOLFTEAM_ROLES = WOLFCHAT_ROLES + ["minion", "cultist"]
# These roles never win as a team, only ever individually (either instead of or in addition to the regular winners)
TRUE_NEUTRAL_ROLES = ["crazed shaman", "fool", "jester", "monster", "clone", "piper"]
# These are the roles that will NOT be used for when amnesiac turns, everything else is fair game! (var.DEFAULT_ROLE is also appended if not in this list)
AMNESIAC_BLACKLIST = ["monster", "minion", "matchmaker", "clone", "doctor", "villager", "cultist", "piper"]
# These roles are seen as wolf by the seer/oracle
SEEN_WOLF = WOLF_ROLES + ["monster", "mad scientist"]
# These are seen as the default role (or villager) when seen by seer (this overrides SEEN_WOLF)
SEEN_DEFAULT = ["traitor", "hag", "sorcerer", "time lord", "villager", "cultist", "minion",
                "vengeful ghost", "lycan", "clone", "fool", "jester", "werekitten", "warlock", "piper"]

# The roles in here are considered templates and will be applied on TOP of other roles. The restrictions are a list of roles that they CANNOT be applied to
# NB: if you want a template to apply to everyone, list it here but make the restrictions an empty list. Templates not listed here are considered full roles instead
TEMPLATE_RESTRICTIONS = {"cursed villager" : SEEN_WOLF + ["seer", "oracle", "fool", "jester"],
                         "gunner"          : WOLFTEAM_ROLES + ["fool", "lycan", "jester"],
                         "sharpshooter"    : [], # the above gets automatically added to the list. this list is the list of roles that can be gunner but not sharpshooter
                         "mayor"           : ["fool", "jester", "monster"],
                         "assassin"        : WOLF_ROLES + ["traitor", "seer", "augur", "oracle", "harlot", "detective", "bodyguard", "guardian angel", "lycan"],
                         "bureaucrat"      : [],
                         }

# make sharpshooter restrictions at least the same as gunner
TEMPLATE_RESTRICTIONS["sharpshooter"].extend(TEMPLATE_RESTRICTIONS["gunner"])

# fallen angel can be assassin even though they are a wolf role
TEMPLATE_RESTRICTIONS["assassin"].remove("fallen angel")

# Roles listed here cannot be used in !fgame roles=blah. If they are defined in ROLE_GUIDE they may still be used.
DISABLED_ROLES = []

NO_VICTIMS_MESSAGES = ("The body of a young penguin pet is found.",
                       "A pool of blood and wolf paw prints are found.",
                       "Traces of wolf fur are found.")
LYNCH_MESSAGES = ("The villagers, after much debate, finally decide on lynching \u0002{0}\u0002, who turned out to be... a{1} \u0002{2}\u0002.",
                  "Under a lot of noise, the pitchfork-bearing villagers lynch \u0002{0}\u0002, who turned out to be... a{1} \u0002{2}\u0002.",
                  "Despite protests, the mob drags their victim to the hanging tree. \u0002{0}\u0002 succumbs to the will of the horde, and is hanged. The villagers have killed a{1} \u0002{2}\u0002.",
                  "Resigned to the inevitable, \u0002{0}\u0002 is led to the gallows. Once the twitching stops, it is discovered that the village lynched a{1} \u0002{2}\u0002.",
                  "Before the rope is pulled, \u0002{0}\u0002, a{1} \u0002{2}\u0002, throws a grenade at the mob. The grenade explodes early.")
LYNCH_MESSAGES_NO_REVEAL = ("The villagers, after much debate, finally decide on lynching \u0002{0}\u0002.",
                            "Under a lot of noise, the pitchfork-bearing villagers lynch \u0002{0}\u0002.",
                            "Despite protests, the mob drags their victim to the hanging tree. \u0002{0}\u0002 succumbs to the will of the horde, and is hanged.",
                            "Resigned to the inevitable, \u0002{0}\u0002 is led to the gallows.",
                            "Before the rope is pulled, \u0002{0}\u0002 throws a grenade at the mob. The grenade explodes early.")
QUIT_MESSAGES= ("\u0002{0}\u0002, a{1} \u0002{2}\u0002, suddenly falls over dead before the astonished villagers.",
                "A pack of wild animals sets upon \u0002{0}\u0002. Soon the \u0002{2}\u0002 is only a pile of bones and a lump in the beasts' stomachs.",
                "\u0002{0}\u0002, a{1} \u0002{2}\u0002, fell off the roof of their house and is now dead.",
                "\u0002{0}\u0002 is crushed to death by a falling tree. The villagers desperately try to save the \u0002{2}\u0002, but it is too late.",
                "\u0002{0}\u0002 suddenly bursts into flames and is now all but a memory. The survivors bury the \u0002{2}\u0002's ashes.")
QUIT_MESSAGES_NO_REVEAL = ("\u0002{0}\u0002 suddenly falls over dead before the astonished villagers.",
                           "A pack of wild animals sets upon \u0002{0}\u0002. Soon they are only a pile of bones and a lump in the beasts' stomachs.",
                           "\u0002{0}\u0002 fell off the roof of their house and is now dead.",
                           "\u0002{0}\u0002 is crushed to death by a falling tree. The villagers desperately try to save them, but it is too late.",
                           "\u0002{0}\u0002 suddenly bursts into flames and is now all but a memory.")

GIF_CHANCE = 1/50
FORTUNE_CHANCE = 1/25


RULES = (botconfig.CHANNEL + " channel rules: http://wolf.xnrand.com/rules")
DENY = {}
ALLOW = {}

DENY_ACCOUNTS = {}
ALLOW_ACCOUNTS = {}

# pingif-related mappings

PING_IF_PREFS = {}
PING_IF_PREFS_ACCS = {}

PING_IF_NUMS = {}
PING_IF_NUMS_ACCS = {}

is_role = lambda plyr, rol: rol in ROLES and plyr in ROLES[rol]

def is_admin(nick, cloak=None, acc=None):
    if nick in USERS.keys():
        if not cloak:
            cloak = USERS[nick]["cloak"]
        if not acc:
            acc = USERS[nick]["account"]

    if acc and acc != "*":
        for pattern in set(botconfig.OWNERS_ACCOUNTS + botconfig.ADMINS_ACCOUNTS):
            if fnmatch.fnmatch(acc.lower(), pattern.lower()):
                return True

    if cloak:
        for pattern in set(botconfig.OWNERS + botconfig.ADMINS):
            if fnmatch.fnmatch(cloak.lower(), pattern.lower()):
                return True

    return False

def is_owner(nick, cloak=None, acc=None):
    if nick in USERS.keys():
        if not cloak:
            cloak = USERS[nick]["cloak"]
        if not acc:
            acc = USERS[nick]["account"]

    if acc and acc != "*":
        for pattern in botconfig.OWNERS_ACCOUNTS:
            if fnmatch.fnmatch(acc.lower(), pattern.lower()):
                return True

    if cloak:
        for pattern in botconfig.OWNERS:
            if fnmatch.fnmatch(cloak.lower(), pattern.lower()):
                return True

    return False

def plural(role):
    bits = role.split()
    bits[-1] = {"person": "people", "wolf": "wolves"}.get(bits[-1], bits[-1] + "s")
    return " ".join(bits)

def list_players(roles = None):
    if roles == None:
        roles = ROLES.keys()
    pl = []
    for x in roles:
        if x in TEMPLATE_RESTRICTIONS.keys():
            continue
        try:
            for p in ROLES[x]:
                pl.append(p)
        except KeyError:
            pass
    return pl

def list_players_and_roles():
    plr = {}
    for x in ROLES.keys():
        if x in TEMPLATE_RESTRICTIONS.keys():
            continue # only get actual roles
        for p in ROLES[x]:
            plr[p] = x
    return plr

get_role = lambda plyr: list_players_and_roles()[plyr]

def get_reveal_role(nick):
    if HIDDEN_TRAITOR and get_role(nick) == "traitor":
        return DEFAULT_ROLE
    elif HIDDEN_AMNESIAC and nick in ORIGINAL_ROLES["amnesiac"]:
        return "amnesiac"
    elif HIDDEN_CLONE and nick in ORIGINAL_ROLES["clone"]:
        return "clone"
    else:
        return get_role(nick)

def del_player(pname):
    prole = get_role(pname)
    ROLES[prole].remove(pname)
    tpls = get_templates(pname)
    for t in tpls:
        ROLES[t].remove(pname)
    if pname in BITTEN:
        del BITTEN[pname]
    if pname in BITTEN_ROLES:
        del BITTEN_ROLES[pname]
    if pname in CHARMED:
        CHARMED.remove(pname)

def get_templates(nick):
    tpl = []
    for x in TEMPLATE_RESTRICTIONS.keys():
        try:
            if nick in ROLES[x]:
                tpl.append(x)
        except KeyError:
            pass

    return tpl

#order goes: wolfteam roles, then other roles in alphabetical order, then templates
def role_order():
    templates = list(TEMPLATE_RESTRICTIONS.keys())
    vils = [role for role in ROLE_GUIDE.keys() if role not in WOLFTEAM_ROLES+templates]
    vils.sort()
    return WOLFTEAM_ROLES + vils + templates


def break_long_message(phrases, joinstr = " "):
    message = ""
    count = 0
    for phrase in phrases:
        # IRC max is 512, but freenode splits around 380ish, make 300 to have plenty of wiggle room
        if count + len(joinstr) + len(phrase) > 300:
            message += "\n" + phrase
            count = len(phrase)
        elif message == "":
            message = phrase
            count = len(phrase)
        else:
            message += joinstr + phrase
            count += len(joinstr) + len(phrase)
    return message

class InvalidModeException(Exception): pass
def game_mode(name, minp, maxp, likelihood = 0, conceal_roles = False):
    def decor(c):
        c.name = name
        GAME_MODES[name] = (c, minp, maxp, likelihood, conceal_roles)
        return c
    return decor

def reset_roles(index):
    newguide = {}
    for role in ROLE_GUIDE:
        newguide[role] = tuple([0 for i in index])
    return newguide

# TODO: move this to src/gamemodes.py
class GameMode:
    def startup(self):
        pass

    def teardown(self):
        pass

@game_mode("roles", minp = 4, maxp = 35)
class ChangedRolesMode(GameMode):
    """Example: !fgame roles=wolf:1,seer:0,guardian angel:1"""

    def __init__(self, arg = ""):
        self.MAX_PLAYERS = 35
        self.ROLE_GUIDE = ROLE_GUIDE.copy()
        self.ROLE_INDEX = (MIN_PLAYERS,)
        pairs = arg.split(",")
        if not pairs:
            raise InvalidModeException("Invalid syntax for mode roles. arg={0}".format(arg))

        for role in self.ROLE_GUIDE.keys():
            self.ROLE_GUIDE[role] = (0,)
        for pair in pairs:
            change = pair.split(":")
            if len(change) != 2:
                raise InvalidModeException("Invalid syntax for mode roles. arg={0}".format(arg))
            role, num = change
            try:
                if role.lower() in DISABLED_ROLES:
                    raise InvalidModeException("The role \u0002{0}\u0002 has been disabled.".format(role))
                elif role.lower() in self.ROLE_GUIDE:
                    self.ROLE_GUIDE[role.lower()] = tuple([int(num)] * len(ROLE_INDEX))
                elif role.lower() == "default" and num.lower() in self.ROLE_GUIDE:
                    if num.lower() == "villager" or num.lower() == "cultist":
                        self.DEFAULT_ROLE = num.lower()
                    else:
                        raise InvalidModeException("The default role must be either \u0002villager\u0002 or \u0002cultist\u0002.")
                elif role.lower() == "role reveal" or role.lower() == "reveal roles":
                    num = num.lower()
                    if num == "on" or num == "true" or num == "yes" or num == "1":
                        self.ROLE_REVEAL = True
                    elif num == "off" or num == "false" or num == "no" or num == "0":
                        self.ROLE_REVEAL = False
                    else:
                        raise InvalidModeException("Did not recognize value \u0002{0}\u0002 for role reveal.".format(num))
                else:
                    raise InvalidModeException(("The role \u0002{0}\u0002 "+
                                                "is not valid.").format(role))
            except ValueError:
                raise InvalidModeException("A bad value was used in mode roles.")

@game_mode("default", minp = 4, maxp = 24, likelihood = 20)
class DefaultMode(GameMode):
    """Default game mode."""
    def __init__(self):
        # No extra settings, just an explicit way to revert to default settings
        pass

@game_mode("foolish", minp = 8, maxp = 24, likelihood = 8)
class FoolishMode(GameMode):
    """Contains the fool, be careful not to lynch them!"""
    def __init__(self):
        self.ROLE_INDEX =         (  8  ,  9  ,  10 , 11  , 12  , 15  , 17  , 20  , 21  , 22  , 24  )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
              "oracle"          : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "harlot"          : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ,  2 ,   2  ),
              "bodyguard"       : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ),
              "augur"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "hunter"          : (  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "shaman"          : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              # wolf roles
              "wolf"            : (  1  ,  1  ,  2  ,  2  ,  2  ,  2  ,  3  ,  3  ,  3  ,  3  ,  4  ),
              "traitor"         : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ),
              "wolf cub"        : (  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "sorcerer"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              # neutral roles
              "clone"           : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "fool"            : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              # templates
              "cursed villager" : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "gunner"          : (  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ),
              "sharpshooter"    : (  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "mayor"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              })

@game_mode("mad", minp = 7, maxp = 22, likelihood = 8)
class MadMode(GameMode):
    """This game mode has mad scientist and many things that may kill you."""
    def __init__(self):
        self.SHOTS_MULTIPLIER = 0.0001 # gunner and sharpshooter always get 0 bullets
        self.SHARPSHOOTER_MULTIPLIER = 0.0001
        self.ROLE_INDEX =         (  7  ,  8  ,  10 , 12  , 14  , 15  , 17  , 18  , 20  )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
              "seer"            : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "mad scientist"   : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "detective"       : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "guardian angel"  : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ),
              "hunter"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ),
              "harlot"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ),
              "village drunk"   : (  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              # wolf roles
              "wolf"            : (  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ,  2  ,  2  ),
              "traitor"         : (  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "werecrow"        : (  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "wolf cub"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  2  ),
              "cultist"         : (  1  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              # neutral roles
              "vengeful ghost"  : (  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "jester"          : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ),
              # templates
              "cursed villager" : (  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "gunner"          : (  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "sharpshooter"    : (  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "assassin"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ),
              })

@game_mode("evilvillage", minp = 6, maxp = 18, likelihood = 1)
class EvilVillageMode(GameMode):
    """Majority of the village is wolf aligned, safes must secretly try to kill the wolves."""
    def __init__(self):
        self.DEFAULT_ROLE = "cultist"
        self.DEFAULT_SEEN_AS_VILL = False
        self.ABSTAIN_ENABLED = False
        self.ROLE_INDEX =         (   6   ,   8   ,  10   ,  12   ,  15   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
              "seer"            : (   0   ,   1   ,   1   ,   1   ,   1   ),
              "guardian angel"  : (   0   ,   0   ,   1   ,   1   ,   1   ),
              "shaman"          : (   0   ,   0   ,   0   ,   1   ,   1   ),
              "hunter"          : (   1   ,   1   ,   1   ,   1   ,   2   ),
              # wolf roles
              "wolf"            : (   1   ,   1   ,   1   ,   1   ,   2   ),
              "minion"          : (   0   ,   0   ,   1   ,   1   ,   1   ),
              # neutral roles
              "fool"            : (   0   ,   0   ,   1   ,   1   ,   1   ),
              # templates
              "cursed villager" : (   0   ,   1   ,   1   ,   1   ,   1   ),
              "mayor"           : (   0   ,   0   ,   0   ,   1   ,   1   ),
              })

    def startup(self):
        events.add_listener("chk_win", self.chk_win, 1)

    def teardown(self):
        events.remove_listener("chk_win", self.chk_win, 1)

    def chk_win(self, evt, var, lpl, lwolves, lrealwolves):
        lsafes = len(var.list_players(["oracle", "seer", "guardian angel", "shaman", "hunter", "villager"]))
        lcultists = len(var.list_players(["cultist"]))
        evt.stop_processing = True

        try:
            if lrealwolves == 0 and lsafes == 0:
                evt.data["winner"] = "none"
                evt.data["message"] = ("Game over! All the villagers are dead, but the cult needed to sacrifice " +
                                     "the wolves to accomplish that. The cult disperses shortly thereafter, " +
                                     "and nobody wins.")
            elif lrealwolves == 0:
                evt.data["winner"] = "villagers"
                evt.data["message"] = ("Game over! All the wolves are dead! The villagers " +
                                       "round up the remaining cultists, hang them, and live " +
                                       "happily ever after.")
            elif lsafes == 0:
                evt.data["winner"] = "wolves"
                evt.data["message"] = ("Game over! All the villagers are dead! The cultists rejoice " +
                                       "with their wolf buddies and start plotting to take over the " +
                                       "next village.")
            elif lcultists == 0:
                evt.data["winner"] = "villagers"
                evt.data["message"] = ("Game over! All the cultists are dead! The now-exposed wolves " +
                                       "are captured and killed by the remaining villagers. A BBQ party " +
                                       "commences shortly thereafter.")
            elif lsafes >= lpl / 2:
                evt.data["winner"] = "villagers"
                evt.data["message"] = ("Game over! There are {0} villagers {1} cultists. They " +
                                       "manage to regain control of the village and dispose of the remaining " +
                                       "cultists.").format("more" if lsafes > lpl / 2 else "the same number of",
                                                           "than" if lsafes > lpl / 2 else "as")
            elif evt.data["winner"][0] != "@":
                evt.data["winner"] = None
        except TypeError: # means that evt.data["winner"] isn't a string or something else subscriptable
            evt.data["winner"] = None


@game_mode("classic", minp = 7, maxp = 21, likelihood = 4)
class ClassicMode(GameMode):
    """Classic game mode from before all the changes."""
    def __init__(self):
        self.ABSTAIN_ENABLED = False
        self.ROLE_INDEX =         (   4   ,   6   ,   8   ,  10   ,  12   ,  15   ,  17   ,  18   ,  20   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
              "seer"            : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              "village drunk"   : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              "harlot"          : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              "bodyguard"       : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
              "detective"       : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              # wolf roles
              "wolf"            : (   1   ,   1   ,   1   ,   2   ,   2   ,   3   ,   3   ,   3   ,   4   ),
              "traitor"         : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              "werecrow"        : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              # templates
              "cursed villager" : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ),
              "gunner"          : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
              })

@game_mode("rapidfire", minp = 6, maxp = 24, likelihood = 0)
class RapidFireMode(GameMode):
    """Many roles that lead to multiple chain deaths."""
    def __init__(self):
        self.SHARPSHOOTER_CHANCE = 1
        self.DAY_TIME_LIMIT = 480
        self.DAY_TIME_WARN = 360
        self.SHORT_DAY_LIMIT = 240
        self.SHORT_DAY_WARN = 180
        self.ROLE_INDEX =         (   6   ,   8   ,  10   ,  12   ,  15   ,  18   ,  22   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
            "seer"              : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "mad scientist"     : (   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            "matchmaker"        : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   2   ),
            "hunter"            : (   0   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            "augur"             : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "time lord"         : (   0   ,   0   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            # wolf roles
            "wolf"              : (   1   ,   1   ,   1   ,   2   ,   2   ,   3   ,   4   ),
            "wolf cub"          : (   0   ,   1   ,   1   ,   1   ,   2   ,   2   ,   2   ),
            "traitor"           : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            # neutral roles
            "vengeful ghost"    : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   2   ),
            "amnesiac"          : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            # templates
            "cursed villager"   : (   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            "assassin"          : (   0   ,   1   ,   1   ,   1   ,   2   ,   2   ,   2   ),
            "gunner"            : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "sharpshooter"      : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            })

@game_mode("drunkfire", minp = 8, maxp = 17, likelihood = 0)
class DrunkFireMode(GameMode):
    """Most players get a gun, quickly shoot all the wolves!"""
    def __init__(self):
        self.SHARPSHOOTER_CHANCE = 1
        self.DAY_TIME_LIMIT = 480
        self.DAY_TIME_WARN = 360
        self.SHORT_DAY_LIMIT = 240
        self.SHORT_DAY_WARN = 180
        self.NIGHT_TIME_LIMIT = 60
        self.NIGHT_TIME_WARN = 40     #     HIT    MISS    SUICIDE   HEADSHOT
        self.GUN_CHANCES              = (   3/7  ,  3/7  ,   1/7   ,   4/5   )
        self.WOLF_GUN_CHANCES         = (   4/7  ,  3/7  ,   0/7   ,   1     )
        self.ROLE_INDEX =         (   8   ,   10  ,  12   ,  14   ,  16   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
            "seer"              : (   1   ,   1   ,   1   ,   2   ,   2   ),
            "village drunk"     : (   2   ,   3   ,   4   ,   4   ,   5   ),
            # wolf roles
            "wolf"              : (   1   ,   2   ,   2   ,   3   ,   3   ),
            "traitor"           : (   1   ,   1   ,   1   ,   1   ,   2   ),
            "hag"               : (   0   ,   0   ,   1   ,   1   ,   1   ),
            # neutral roles
            "crazed shaman"     : (   0   ,   0   ,   1   ,   1   ,   1   ),
            # templates
            "cursed villager"   : (   1   ,   1   ,   1   ,   1   ,   1   ),
            "assassin"          : (   0   ,   0   ,   0   ,   1   ,   1   ),
            "gunner"            : (   5   ,   6   ,   7   ,   8   ,   9   ),
            "sharpshooter"      : (   2   ,   2   ,   3   ,   3   ,   4   ),
            })

@game_mode("noreveal", minp = 4, maxp = 21, likelihood = 2)
class NoRevealMode(GameMode):
    """Roles are not revealed when players die."""
    def __init__(self):
        self.ROLE_REVEAL = False
        self.ROLE_INDEX =         (   4   ,   6   ,   8   ,  10   ,  12   ,  15   ,  17   ,  19   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
            "seer"              : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "guardian angel"    : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ),
            "mystic"            : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "detective"         : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "hunter"            : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            # wolf roles
            "wolf"              : (   1   ,   1   ,   1   ,   1   ,   2   ,   2   ,   2   ,   3   ),
            "wolf mystic"       : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "traitor"           : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "werecrow"          : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            # neutral roles
            "clone"             : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "lycan"             : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ),
            "amnesiac"          : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ),
            # templates
            "cursed villager"   : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            })

@game_mode("lycan", minp = 7, maxp = 21, likelihood = 6)
class LycanMode(GameMode):
    """Many lycans will turn into wolves. Hunt them down before the wolves overpower the village."""
    def __init__(self):
        self.ROLE_INDEX =         (   7   ,   8  ,    9   ,   10  ,   11  ,   12  ,  15   ,  17   ,  20   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
            "seer"              : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "guardian angel"    : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "detective"         : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "matchmaker"        : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "hunter"            : (   1   ,   1   ,   1   ,   2   ,   2   ,   2   ,   2   ,   2   ,   2   ),
            # wolf roles
            "wolf"              : (   1   ,   1   ,   1   ,   2   ,   2   ,   2   ,   2   ,   2   ,   2   ),
            "traitor"           : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            # neutral roles
            "clone"             : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            "lycan"             : (   1   ,   1   ,   2   ,   2   ,   2   ,   3   ,   4   ,   4   ,   5   ),
            # templates
            "cursed villager"   : (   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ,   2   ,   2   ),
            "gunner"            : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ),
            "sharpshooter"      : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ),
            "mayor"             : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            })

@game_mode("valentines", minp = 8, maxp = 24, likelihood = 0)
class MatchmakerMode(GameMode):
    """Love is in the air!"""
    def __init__(self):
        self.ROLE_INDEX = range(8, 25)
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({
            "wolf"          : [math.ceil((i ** 1.4) * 0.06) for i in self.ROLE_INDEX],
            "matchmaker"    : [i - math.ceil((i ** 1.4) * 0.06) - (i >= 12) - (i >= 18) for i in self.ROLE_INDEX],
            "monster"       : [i >= 12 for i in self.ROLE_INDEX],
            "mad scientist" : [i >= 18 for i in self.ROLE_INDEX],
            })

@game_mode("random", minp = 8, maxp = 24, likelihood = 0, conceal_roles = True)
class RandomMode(GameMode):
    """Completely random and hidden roles."""
    def __init__(self):
        self.LOVER_WINS_WITH_FOOL = True
        self.MAD_SCIENTIST_SKIPS_DEAD_PLAYERS = 0 # always make it happen
        self.ALPHA_WOLF_NIGHTS = 2
        self.ROLE_REVEAL = False
        self.TEMPLATE_RESTRICTIONS = {template: [] for template in TEMPLATE_RESTRICTIONS}

        self.TOTEM_CHANCES = { #  shaman , crazed
                        "death": (   8   ,   1   ),
                   "protection": (   6   ,   1   ),
                      "silence": (   4   ,   1   ),
                    "revealing": (   2   ,   1   ),
                  "desperation": (   4   ,   1   ),
                   "impatience": (   7   ,   1   ),
                     "pacifism": (   7   ,   1   ),
                    "influence": (   7   ,   1   ),
                   "narcolepsy": (   4   ,   1   ),
                     "exchange": (   1   ,   1   ),
                  "lycanthropy": (   1   ,   1   ),
                         "luck": (   6   ,   1   ),
                   "pestilence": (   3   ,   1   ),
                  "retribution": (   5   ,   1   ),
                 "misdirection": (   6   ,   1   ),
                            }

    def startup(self):
        events.add_listener("role_attribution", self.role_attribution, 1)

    def teardown(self):
        events.remove_listener("role_attribution", self.role_attribution, 1)

    def role_attribution(self, evt, cli, var, villagers):
        lpl = len(villagers) - 1
        addroles = evt.data["addroles"]
        for role in var.ROLE_GUIDE:
            addroles[role] = 0

        wolves = var.WOLF_ROLES[:]
        wolves.remove("wolf cub")
        addroles[random.choice(wolves)] += 1 # make sure there's at least one wolf role
        roles = list(var.ROLE_GUIDE.keys() - (list(var.TEMPLATE_RESTRICTIONS) + ["villager", "cultist", "amnesiac"]))
        while lpl:
            addroles[random.choice(roles)] += 1
            lpl -= 1

        addroles["gunner"] = random.randrange(int(len(villagers) ** 1.2 / 4))
        addroles["assassin"] = random.randrange(int(len(villagers) ** 1.2 / 8))

        evt.prevent_default = True

# Credits to Metacity for designing and current name
# Blame arkiwitect for the original name of KrabbyPatty
@game_mode("aleatoire", minp = 8, maxp = 24, likelihood = 4)
class AleatoireMode(GameMode):
    """Game mode created by Metacity and balanced by woffle."""
    def __init__(self):
        self.SHARPSHOOTER_CHANCE = 1
                                              #    SHAMAN   , CRAZED SHAMAN
        self.TOTEM_CHANCES = {       "death": (      4      ,      1      ),
                                "protection": (      8      ,      1      ),
                                   "silence": (      2      ,      1      ),
                                 "revealing": (      0      ,      1      ),
                               "desperation": (      1      ,      1      ),
                                "impatience": (      0      ,      1      ),
                                  "pacifism": (      0      ,      1      ),
                                 "influence": (      0      ,      1      ),
                                "narcolepsy": (      0      ,      1      ),
                                  "exchange": (      0      ,      1      ),
                               "lycanthropy": (      0      ,      1      ),
                                      "luck": (      0      ,      1      ),
                                "pestilence": (      1      ,      1      ),
                               "retribution": (      4      ,      1      ),
                              "misdirection": (      0      ,      1      ),
                             }
        self.ROLE_INDEX =         (   8   ,  10   ,  12   ,  15   ,  18   ,  21   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({ # village roles
            "seer"              : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "shaman"            : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "matchmaker"        : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "hunter"            : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "augur"             : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "time lord"         : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ),
            "guardian angel"    : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            # wolf roles
            "wolf"              : (   1   ,   2   ,   2   ,   2   ,   2   ,   2   ),
            "wolf cub"          : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ),
            "traitor"           : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "werecrow"          : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            "hag"               : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ),
            # neutral roles
            "vengeful ghost"    : (   0   ,   1   ,   1   ,   1   ,   2   ,   2   ),
            "amnesiac"          : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ),
            "lycan"             : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            # templates
            "cursed villager"   : (   2   ,   2   ,   2   ,   2   ,   2   ,   2   ),
            "assassin"          : (   0   ,   1   ,   2   ,   2   ,   2   ,   2   ),
            "gunner"            : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "sharpshooter"      : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ),
            "bureaucrat"        : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ),
            "mayor"             : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            })

@game_mode("alpha", minp = 7, maxp = 24, likelihood = 5)
class AlphaMode(GameMode):
    """Features the alpha wolf who can turn other people into wolves, be careful whom you trust!"""
    def __init__(self):
        self.ROLE_INDEX =         (   7   ,   8   ,  10   ,  11   ,  12   ,  14   ,  15   ,  17   ,  18   ,  20   ,  21   ,  24   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({
            #village roles
            "oracle"            : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "matchmaker"        : (   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "village drunk"     : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "guardian angel"    : (   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "doctor"            : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "harlot"            : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "augur"             : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            # wolf roles
            "wolf"              : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ,   3   ,   3   ,   4   ,   5   ),
            "alpha wolf"        : (   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "traitor"           : (   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            "werecrow"          : (   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ),
            # neutral roles
            "lycan"             : (   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   1   ,   2   ,   2   ,   2   ,   2   ,   2   ),
            "clone"             : (   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   0   ,   1   ,   1   ,   1   ),
            # templates
            "cursed villager"   : (   1   ,   1   ,   1   ,   1   ,   2   ,   2   ,   2   ,   2   ,   3   ,   3   ,   3   ,   4   ),
            })

# original idea by Rossweisse, implemented by Vgr with help from woffle and jacob1
@game_mode("guardian", minp = 8, maxp = 16, likelihood = 0)
class GuardianMode(GameMode):
    """Game mode full of guardian angels, wolves need to pick them apart!"""
    def __init__(self):
        self.LIMIT_ABSTAIN = False
        self.ROLE_INDEX =         (   8   ,   10   ,  12   ,  13   ,  15   )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({
            # village roles
            "bodyguard"         : (   0   ,   0   ,   0   ,   0   ,   1   ),
            "guardian angel"    : (   1   ,   1   ,   2   ,   2   ,   2   ),
            "shaman"            : (   0   ,   1   ,   1   ,   1   ,   1   ),
            "seer"              : (   1   ,   1   ,   1   ,   1   ,   1   ),
            # wolf roles
            "wolf"              : (   1   ,   1   ,   1   ,   1   ,   2   ),
            "werecrow"          : (   0   ,   1   ,   1   ,   1   ,   1   ),
            "werekitten"        : (   1   ,   1   ,   1   ,   1   ,   1   ),
            "alpha wolf"        : (   0   ,   0   ,   1   ,   1   ,   1   ),
            # neutral roles
            "jester"            : (   0   ,   0   ,   0   ,   1   ,   1   ),
            # templates
            "gunner"            : (   0   ,   0   ,   0   ,   1   ,   1   ),
            "cursed villager"   : (   1   ,   1   ,   2   ,   2   ,   2   ),
            })

        self.TOTEM_CHANCES = { #  shaman , crazed
                        "death": (   4   ,   1   ),
                   "protection": (   8   ,   1   ),
                      "silence": (   2   ,   1   ),
                    "revealing": (   0   ,   1   ),
                  "desperation": (   0   ,   1   ),
                   "impatience": (   0   ,   1   ),
                     "pacifism": (   0   ,   1   ),
                    "influence": (   0   ,   1   ),
                   "narcolepsy": (   0   ,   1   ),
                     "exchange": (   0   ,   1   ),
                  "lycanthropy": (   0   ,   1   ),
                         "luck": (   3   ,   1   ),
                   "pestilence": (   0   ,   1   ),
                  "retribution": (   6   ,   1   ),
                 "misdirection": (   4   ,   1   ),
                                 }

    def startup(self):
        events.add_listener("chk_win", self.chk_win, 1)

    def teardown(self):
        events.remove_listener("chk_win", self.chk_win, 1)

    def chk_win(self, evt, var, lpl, lwolves, lrealwolves):
        lguardians = len(var.list_players(["guardian angel", "bodyguard"]))

        if lpl < 1:
            # handled by default win cond checking
            return
        elif not lguardians and lwolves > lpl / 2:
            evt.data["winner"] = "wolves"
            evt.data["message"] = ("Game over! There are more wolves than uninjured villagers. With the ancestral " +
                                   "guardians dead, the wolves overpower the defenseless villagers and win.")
        elif not lguardians and lwolves == lpl / 2:
            evt.data["winner"] = "wolves"
            evt.data["message"] = ("Game over! There are the same number of wolves as uninjured villagers. With the ancestral " +
                                   "guardians dead, the wolves overpower the defenseless villagers and win.")
        elif not lrealwolves and lguardians:
            evt.data["winner"] = "villagers"
            evt.data["message"] = ("Game over! All the wolves are dead! The remaining villagers throw a party in honor " +
                                   "of the guardian angels that watched over the village, and live happily ever after.")
        elif not lrealwolves and not lguardians:
            evt.data["winner"] = "none"
            evt.data["message"] = ("Game over! The remaining villagers managed to destroy the wolves, however the guardians " +
                                   "that used to watch over the village are nowhere to be found. The village lives on in an " +
                                   "uneasy peace, not knowing when they will be destroyed completely now that they are " +
                                   "defenseless. Nobody wins.")
        elif lwolves == lguardians and lpl - lwolves - lguardians == 0:
            evt.data["winner"] = "none"
            evt.data["message"] = ("Game over! The guardians, angered by the loss of everyone they were meant to guard, " +
                                   "engage the wolves in battle and mutually assured destruction. After the dust settles " +
                                   "the village is completely dead, and nobody wins.")
        else:
            evt.data["winner"] = None

@game_mode("charming", minp = 5, maxp = 24, likelihood = 4)
class CharmingMode(GameMode):
    """Charmed players must band together to find the piper in this game mode."""
    def __init__(self):
        self.ROLE_INDEX =         (  5  ,  6  ,  8 ,  10  , 11  , 12  , 14  , 16  , 18  , 19  , 22  , 24  )
        self.ROLE_GUIDE = reset_roles(self.ROLE_INDEX)
        self.ROLE_GUIDE.update({# village roles
              "seer"            : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "harlot"          : (  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "shaman"          : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ),
              "detective"       : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "bodyguard"       : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  2  ,  2  ,  2  ,  2  ),
              # wolf roles
              "wolf"            : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ,  2  ,  2  ,  3  ,  3  ),
              "traitor"         : (  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "werekitten"      : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "warlock"         : (  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "sorcerer"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ),
              # neutral roles
              "piper"           : (  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "vengeful ghost"  : (  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              # templates
              "cursed villager" : (  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "gunner"          : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ),
              "sharpshooter"    : (  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ,  2  ),
              "mayor"           : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              "assassin"        : (  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  0  ,  1  ,  1  ,  1  ,  1  ,  1  ),
              })

# Persistence



conn = sqlite3.connect("data.sqlite3", check_same_thread = False)
c = conn.cursor()

def init_db():
    with conn:

        c.execute('CREATE TABLE IF NOT EXISTS simple_role_notify (cloak TEXT)') # people who understand each role (hostmasks - backup)

        c.execute('CREATE TABLE IF NOT EXISTS simple_role_accs (acc TEXT)') # people who understand each role (accounts - primary)

        c.execute('CREATE TABLE IF NOT EXISTS prefer_notice (cloak TEXT)') # people who prefer /notice (hostmasks - backup)

        c.execute('CREATE TABLE IF NOT EXISTS prefer_notice_acc (acc TEXT)') # people who prefer /notice (accounts - primary)

        c.execute('CREATE TABLE IF NOT EXISTS stasised (cloak TEXT, games INTEGER, UNIQUE(cloak))') # stasised people (cloaks)

        c.execute('CREATE TABLE IF NOT EXISTS stasised_accs (acc TEXT, games INTEGER, UNIQUE(acc))') # stasised people (accounts - takes precedence)

        c.execute('CREATE TABLE IF NOT EXISTS denied (cloak TEXT, command TEXT, UNIQUE(cloak, command))') # DENY

        c.execute('CREATE TABLE IF NOT EXISTS denied_accs (acc TEXT, command TEXT, UNIQUE(acc, command))') # DENY_ACCOUNTS

        c.execute('CREATE TABLE IF NOT EXISTS allowed (cloak TEXT, command TEXT, UNIQUE(cloak, command))') # ALLOW

        c.execute('CREATE TABLE IF NOT EXISTS allowed_accs (acc TEXT, command TEXT, UNIQUE(acc, command))') # ALLOW_ACCOUNTS

        c.execute('CREATE TABLE IF NOT EXISTS pingif_prefs (user TEXT, is_account BOOLEAN, players INTEGER, PRIMARY KEY(user, is_account))') # pingif player count preferences
        c.execute('CREATE INDEX IF NOT EXISTS ix_ping_prefs_pingif ON pingif_prefs (players ASC)') # index apparently makes it faster

        c.execute('PRAGMA table_info(pre_restart_state)')
        try:
            next(c)
        except StopIteration:
            c.execute('CREATE TABLE pre_restart_state (players TEXT)')
            c.execute('INSERT INTO pre_restart_state (players) VALUES (NULL)')

        c.execute('SELECT * FROM simple_role_notify')
        for row in c:
            SIMPLE_NOTIFY.append(row[0])

        c.execute('SELECT * FROM simple_role_accs')
        for row in c:
            SIMPLE_NOTIFY_ACCS.append(row[0])

        c.execute('SELECT * FROM prefer_notice')
        for row in c:
            PREFER_NOTICE.append(row[0])

        c.execute('SELECT * FROM prefer_notice_acc')
        for row in c:
            PREFER_NOTICE_ACCS.append(row[0])

        c.execute('SELECT * FROM stasised')
        for row in c:
            STASISED[row[0]] = row[1]

        c.execute('SELECT * FROM stasised_accs')
        for row in c:
            STASISED_ACCS[row[0]] = row[1]

        c.execute('SELECT * FROM denied')
        for row in c:
            if row[0] not in DENY:
                DENY[row[0]] = []
            DENY[row[0]].append(row[1])

        c.execute('SELECT * FROM denied_accs')
        for row in c:
            if row[0] not in DENY_ACCOUNTS:
                DENY_ACCOUNTS[row[0]] = []
            DENY_ACCOUNTS[row[0]].append(row[1])

        c.execute('SELECT * FROM allowed')
        for row in c:
            if row[0] not in ALLOW:
                ALLOW[row[0]] = []
            ALLOW[row[0]].append(row[1])

        c.execute('SELECT * FROM allowed_accs')
        for row in c:
            if row[0] not in ALLOW_ACCOUNTS:
                ALLOW_ACCOUNTS[row[0]] = []
            ALLOW_ACCOUNTS[row[0]].append(row[1])

        c.execute('SELECT * FROM pingif_prefs')
        for row in c:
            # is an account
            if row[1]:
                if row[0] not in PING_IF_PREFS_ACCS:
                    PING_IF_PREFS_ACCS[row[0]] = row[2]
                if row[2] not in PING_IF_NUMS_ACCS:
                    PING_IF_NUMS_ACCS[row[2]] = []
                PING_IF_NUMS_ACCS[row[2]].append(row[0])
            # is a host
            else:
                if row[0] not in PING_IF_PREFS:
                    PING_IF_PREFS[row[0]] = row[2]
                if row[2] not in PING_IF_NUMS:
                    PING_IF_NUMS[row[2]] = []
                PING_IF_NUMS[row[2]].append(row[0])

        # populate the roles table
        c.execute('DROP TABLE IF EXISTS roles')
        c.execute('CREATE TABLE roles (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT)')

        for x in list(ROLE_GUIDE.keys()):
            c.execute("INSERT OR REPLACE INTO roles (role) VALUES (?)", (x,))


        c.execute(('CREATE TABLE IF NOT EXISTS rolestats (player TEXT, role TEXT, '+
            'teamwins SMALLINT, individualwins SMALLINT, totalgames SMALLINT, '+
            'UNIQUE(player, role))'))


        c.execute(('CREATE TABLE IF NOT EXISTS gamestats (gamemode TEXT, size SMALLINT, villagewins SMALLINT, ' +
            'wolfwins SMALLINT, monsterwins SMALLINT, foolwins SMALLINT, piperwins SMALLINT, totalgames SMALLINT, UNIQUE(gamemode, size))'))


def remove_simple_rolemsg(clk):
    with conn:
        c.execute('DELETE from simple_role_notify where cloak=?', (clk,))

def add_simple_rolemsg(clk):
    with conn:
        c.execute('INSERT into simple_role_notify VALUES (?)', (clk,))

def remove_simple_rolemsg_acc(acc):
    with conn:
        c.execute('DELETE from simple_role_accs where acc=?', (acc,))

def add_simple_rolemsg_acc(acc):
    with conn:
        c.execute('INSERT into simple_role_accs VALUES (?)', (acc,))

def remove_prefer_notice(clk):
    with conn:
        c.execute('DELETE from prefer_notice where cloak=?', (clk,))

def add_prefer_notice(clk):
    with conn:
        c.execute('INSERT into prefer_notice VALUES (?)', (clk,))

def remove_prefer_notice_acc(acc):
    with conn:
        c.execute('DELETE from prefer_notice_acc where acc=?', (acc,))

def add_prefer_notice_acc(acc):
    with conn:
        c.execute('INSERT into prefer_notice_acc VALUES (?)', (acc,))

def set_stasis(clk, games):
    with conn:
        if games <= 0:
            c.execute('DELETE FROM stasised WHERE cloak=?', (clk,))
        else:
            c.execute('INSERT OR REPLACE INTO stasised VALUES (?,?)', (clk, games))

def set_stasis_acc(acc, games):
    with conn:
        if games <= 0:
            c.execute('DELETE FROM stasised_accs WHERE acc=?', (acc,))
        else:
            c.execute('INSERT OR REPLACE INTO stasised_accs VALUES (?,?)', (acc, games))

def add_deny(clk, command):
    with conn:
        c.execute('INSERT OR IGNORE INTO denied VALUES (?,?)', (clk, command))

def remove_deny(clk, command):
    with conn:
        c.execute('DELETE FROM denied WHERE cloak=? AND command=?', (clk, command))

def add_deny_acc(acc, command):
    with conn:
        c.execute('INSERT OR IGNORE INTO denied_accs VALUES (?,?)', (acc, command))

def remove_deny_acc(acc, command):
    with conn:
        c.execute('DELETE FROM denied_accs WHERE acc=? AND command=?', (acc, command))

def add_allow(clk, command):
    with conn:
        c.execute('INSERT OR IGNORE INTO allowed VALUES (?,?)', (clk, command))

def remove_allow(clk, command):
    with conn:
        c.execute('DELETE FROM allowed WHERE cloak=? AND command=?', (clk, command))

def add_allow_acc(acc, command):
    with conn:
        c.execute('INSERT OR IGNORE INTO allowed_accs VALUES (?,?)', (acc, command))

def remove_allow_acc(acc, command):
    with conn:
        c.execute('DELETE FROM allowed_accs WHERE acc=? AND command=?', (acc, command))

def set_pingif_status(user, is_account, players):
    with conn:
        c.execute('DELETE FROM pingif_prefs WHERE user=? AND is_account=?', (user, is_account))
        if players != 0:
            c.execute('INSERT OR REPLACE INTO pingif_prefs VALUES (?,?,?)', (user, is_account, players))

def update_role_stats(acc, role, won, iwon):
    with conn:
        wins, iwins, total = 0, 0, 0

        c.execute(("SELECT teamwins, individualwins, totalgames FROM rolestats "+
                   "WHERE player=? AND role=?"), (acc, role))
        row = c.fetchone()
        if row:
            wins, iwins, total = row

        if won:
            wins += 1
        if iwon:
            iwins += 1
        total += 1

        c.execute("INSERT OR REPLACE INTO rolestats VALUES (?,?,?,?,?)",
                  (acc, role, wins, iwins, total))

def update_game_stats(gamemode, size, winner):
    with conn:
        vwins, wwins, mwins, fwins, pwins, total = 0, 0, 0, 0, 0, 0

        c.execute("SELECT villagewins, wolfwins, monsterwins, foolwins, totalgames "+
                    "FROM gamestats WHERE gamemode=? AND size=?", (gamemode, size))
        row = c.fetchone()
        if row:
            vwins, wwins, mwins, fwins, total = row

        if winner == "wolves":
            wwins += 1
        elif winner == "villagers":
            vwins += 1
        elif winner == "monsters":
            mwins += 1
        elif winner == "pipers":
            pwins += 1
        elif winner.startswith("@"):
            fwins += 1
        total += 1

        c.execute("INSERT OR REPLACE INTO gamestats VALUES (?,?,?,?,?,?,?,?)",
                    (gamemode, size, vwins, wwins, mwins, fwins, pwins, total))

def get_player_stats(acc, role):
    if role.lower() not in [k.lower() for k in ROLE_GUIDE.keys()] and role != "lover":
        return "No such role: {0}".format(role)
    with conn:
        c.execute("SELECT player FROM rolestats WHERE player=? COLLATE NOCASE", (acc,))
        player = c.fetchone()
        if player:
            for row in c.execute("SELECT * FROM rolestats WHERE player=? COLLATE NOCASE AND role=? COLLATE NOCASE", (acc, role)):
                msg = "\u0002{0}\u0002 as \u0002{1}\u0002 | Team wins: {2} (%d%%), Individual wins: {3} (%d%%), Total games: {4}".format(*row)
                return msg % (round(row[2]/row[4] * 100), round(row[3]/row[4] * 100))
            else:
                return "No stats for {0} as {1}.".format(player[0], role)
        return "{0} has not played any games.".format(acc)

def get_player_totals(acc):
    role_totals = []
    with conn:
        c.execute("SELECT player FROM rolestats WHERE player=? COLLATE NOCASE", (acc,))
        player = c.fetchone()
        if player:
            c.execute("SELECT role, totalgames FROM rolestats WHERE player=? COLLATE NOCASE ORDER BY totalgames DESC", (acc,))
            role_tmp = defaultdict(int)
            totalgames = 0
            while True:
                row = c.fetchone()
                if row:
                    role_tmp[row[0]] += row[1]
                    if row[0] not in TEMPLATE_RESTRICTIONS and row[0] != "lover":
                        totalgames += row[1]
                else:
                    break
            order = role_order()
            #ordered role stats
            role_totals = ["\u0002{0}\u0002: {1}".format(role, role_tmp[role]) for role in order if role in role_tmp]
            #lover or any other special stats
            role_totals += ["\u0002{0}\u0002: {1}".format(role, count) for role, count in role_tmp.items() if role not in order]
            return "\u0002{0}\u0002's totals | \u0002{1}\u0002 games | {2}".format(player[0], totalgames, break_long_message(role_totals, ", "))
        else:
            return "\u0002{0}\u0002 has not played any games.".format(acc)

def get_game_stats(gamemode, size):
    with conn:
        for row in c.execute("SELECT * FROM gamestats WHERE gamemode=? AND size=?", (gamemode, size)):
            msg = "\u0002%d\u0002 player games | Village wins: %d (%d%%), Wolf wins: %d (%d%%)" % (row[1], row[2], round(row[2]/row[7] * 100), row[3], round(row[3]/row[7] * 100))
            if row[4] > 0:
                msg += ", Monster wins: %d (%d%%)" % (row[4], round(row[4]/row[7] * 100))
            if row[5] > 0:
                msg += ", Fool wins: %d (%d%%)" % (row[5], round(row[5]/row[7] * 100))
            if row[6] > 0:
                msg += ", Piper wins: %d (%d%%)" % (row[6], round(row[6]/row[7] * 100))
            return msg + ", Total games: {0}".format(row[7])
        else:
            return "No stats for \u0002{0}\u0002 player games.".format(size)

def get_game_totals(gamemode):
    size_totals = []
    total = 0
    with conn:
        for size in range(MIN_PLAYERS, MAX_PLAYERS + 1):
            c.execute("SELECT size, totalgames FROM gamestats WHERE gamemode=? AND size=?", (gamemode, size))
            row = c.fetchone()
            if row:
                size_totals.append("\u0002{0}p\u0002: {1}".format(*row))
                total += row[1]

    if len(size_totals) == 0:
        return "No games have been played in the {0} game mode.".format(gamemode)
    else:
        return "Total games ({0}) | {1}".format(total, ", ".join(size_totals))

# vim: set expandtab:sw=4:ts=4:
