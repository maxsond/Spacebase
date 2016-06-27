"""
Functions for processing input commands.

All global functions in this module whose name does not start with "_"
is considered an inputfunc. Each function must have the following
callsign:

    inputfunc(session, *args, **kwargs)

Where "options" is always one of the kwargs, containing eventual
protocol-options.
There is one special function, the "default" function, which is called
on a no-match. It has this callsign:

    default(session, cmdname, *args, **kwargs)

Evennia knows which modules to use for inputfuncs by
settings.INPUT_FUNC_MODULES.

"""
from future.utils import viewkeys

import importlib
from django.conf import settings
from evennia.commands.cmdhandler import cmdhandler
from evennia.players.models import PlayerDB
from evennia.utils.logger import log_err
from evennia.utils.utils import to_str, to_unicode

BrowserSessionStore = importlib.import_module(settings.SESSION_ENGINE).SessionStore


# always let "idle" work since we use this in the webclient
_IDLE_COMMAND = settings.IDLE_COMMAND
_IDLE_COMMAND = (_IDLE_COMMAND, ) if _IDLE_COMMAND == "idle" else (_IDLE_COMMAND, "idle")
_GA = object.__getattribute__
_SA = object.__setattr__
_NA = lambda o: "N/A"

_ERROR_INPUT = "Inputfunc {name}({session}): Wrong/unrecognized input: {inp}"


# All global functions are inputfuncs available to process inputs

def text(session, *args, **kwargs):
    """
    Main text input from the client. This will execute a command
    string on the server.

    Args:
        text (str): First arg is used as text-command input. Other
            arguments are ignored.

    """
    #from evennia.server.profiling.timetrace import timetrace
    #text = timetrace(text, "ServerSession.data_in")

    text = args[0] if args else None

    #explicitly check for None since text can be an empty string, which is
    #also valid
    if text is None:
        return
    # this is treated as a command input
    # handle the 'idle' command
    if text.strip() == _IDLE_COMMAND:
        session.update_session_counters(idle=True)
        return
    if session.player:
        # nick replacement
        puppet = session.puppet
        if puppet:
            text = puppet.nicks.nickreplace(text,
                          categories=("inputline", "channel"), include_player=True)
        else:
            text = session.player.nicks.nickreplace(text,
                        categories=("inputline", "channels"), include_player=False)
    kwargs.pop("options", None)
    cmdhandler(session, text, callertype="session", session=session, **kwargs)
    session.update_session_counters()


def echo(session, *args, **kwargs):
    """
    Echo test function
    """
    session.data_out(text="Echo returns: %s" % args)


def default(session, cmdname, *args, **kwargs):
    """
    Default catch-function. This is like all other input functions except
    it will get `cmdname` as the first argument.

    """
    err = "Session {sessid}: Input command not recognized:\n" \
            " name: '{cmdname}'\n" \
            " args, kwargs: {args}, {kwargs}".format(sessid=session.sessid,
                                                     cmdname=cmdname,
                                                     args=args,
                                                     kwargs=kwargs)
    if session.protocol_flags.get("INPUTDEBUG", False):
        session.msg(err)
    log_err(err)


def browser_sessid(session, *args, **kwargs):
    """
    This is a utility function for the webclient (only) to communicate its
    current browser session hash. This is important in order to link
    the browser session to the evennia session. Only the very first
    storage request will be accepted, the following ones will be ignored.

    Args:
        browserid (str): Browser session hash

    """
    if not session.browserid:
        print "stored browserid:", session, args[0]
        session.browserid = args[0]
        if not session.logged_in:
            # automatic log in if the django browser session already authenticated.
            browsersession = BrowserSessionStore(session_key=args[0])
            uid = browsersession.get("logged_in", None)
            if uid:
                try:
                    player =  PlayerDB.objects.get(pk=uid)
                except Exception:
                    return
                session.sessionhandler.login(session, player)





def client_options(session, *args, **kwargs):
    """
    This allows the client an OOB way to inform us about its name and capabilities.
    This will be integrated into the session settings

    Kwargs:
        get (bool): If this is true, return the settings as a dict
            (ignore all other kwargs).
        client (str): A client identifier, like "mushclient".
        version (str): A client version
        ansi (bool): Supports ansi colors
        xterm256 (bool): Supports xterm256 colors or not
        mxp (bool): Supports MXP or not
        utf-8 (bool): Supports UTF-8 or not
        screenreader (bool): Screen-reader mode on/off
        mccp (bool): MCCP compression on/off
        screenheight (int): Screen height in lines
        screenwidth (int): Screen width in characters
        inputdebug (bool): Debug input functions
        nomarkup (bool): Strip markup
        raw (bool): Turn off parsing

    """
    flags = session.protocol_flags
    if not kwargs or kwargs.get("get", False):
        # return current settings
        options = dict((key, flags[key]) for key in flags
                if key.upper() in ("ANSI", "XTERM256", "MXP",
                           "UTF-8", "SCREENREADER", "ENCODING",
                           "MCCP", "SCREENHEIGHT",
                           "SCREENWIDTH", "INPUTDEBUG",
                           "RAW", "NOMARKUP"))
        session.msg(client_options=options)
        return

    def validate_encoding(val):
        # helper: change encoding
        try:
            to_str(to_unicode("test-string"), encoding=val)
        except LookupError:
            raise RuntimeError("The encoding '|w%s|n' is invalid. " % val)
        return val

    def validate_size(val):
        return {0: int(val)}

    def validate_bool(val):
        if isinstance(val, basestring):
            return True if val.lower() in ("true", "on", "1") else False
        return bool(val)

    for key, value in kwargs.iteritems():
        key = key.lower()
        if key == "client":
            flags["CLIENTNAME"] = to_str(value)
        elif key == "version":
            if "CLIENTNAME" in flags:
                flags["CLIENTNAME"] = "%s %s" % (flags["CLIENTNAME"], to_str(value))
        elif key == "ENCODING":
            flags["ENCODING"] = validate_encoding(value)
        elif key == "ansi":
            flags["ANSI"] = validate_bool(value)
        elif key == "xterm256":
            flags["XTERM256"] = validate_bool(value)
        elif key == "mxp":
            flags["MXP"] = validate_bool(value)
        elif key == "utf-8":
            flags["UTF-8"] = validate_bool(value)
        elif key == "screenreader":
            flags["SCREENREADER"] = validate_bool(value)
        elif key == "mccp":
            flags["MCCP"] = validate_bool(value)
        elif key == "screenheight":
            flags["SCREENHEIGHT"] = validate_size(value)
        elif key == "screenwidth":
            flags["SCREENWIDTH"] = validate_size(value)
        elif key == "inputdebug":
            flags["INPUTDEBUG"] = validate_bool(value)
        elif key == "nomarkup":
            flags["NOMARKUP"] = validate_bool(value)
        elif key == "raw":
            flags["RAW"] = validate_bool(value)
        elif key in ('Char 1', 'Char.Skills 1', 'Char.Items 1',
                'Room 1', 'IRE.Rift 1', 'IRE.Composer 1'):
            # ignore mudlet's default send (aimed at IRE games)
            pass
        elif not key in ("options", "cmdid"):
            err = _ERROR_INPUT.format(
                    name="client_settings", session=session, inp=key)
            session.msg(text=err)
    session.protocol_flags = flags
    # we must update the portal as well
    session.sessionhandler.session_portal_sync(session)

# GMCP alias
hello = client_options
supports_set = client_options


def get_client_options(session, *args, **kwargs):
    """
    Alias wrapper for getting options.
    """
    client_options(session, get=True)


def get_inputfuncs(session, *args, **kwargs):
    """
    Get the keys of all available inputfuncs. Note that we don't get
    it from this module alone since multiple modules could be added.
    So we get it from the sessionhandler.
    """
    inputfuncsdict = dict((key, func.__doc__) for key, func
                          in session.sessionhandler.get_inputfuncs().iteritems())
    session.msg(get_inputfuncs=inputfuncsdict)


def login(session, *args, **kwargs):
    """
    Peform a login. This only works if session is currently not logged
    in. This will also automatically throttle too quick attempts.

    Kwargs:
        name (str): Player name
        password (str): Plain-text password

    """
    if not session.logged_in and "name" in kwargs and "password" in kwargs:
        from evennia.commands.default.unloggedin import create_normal_player
        player = create_normal_player(session, kwargs["name"], kwargs["password"])
        if player:
            session.sessionhandler.login(session, player)

_gettable = {
    "name": lambda obj: obj.key,
    "key": lambda obj: obj.key,
    "location": lambda obj: obj.location.key if obj.location else "None",
    "servername": lambda obj: settings.SERVERNAME
}

def get_value(session, *args, **kwargs):
    """
    Return the value of a given attribute or db_property on the
    session's current player or character.

    Kwargs:
      name (str): Name of info value to return. Only names
        in the _gettable dictionary earlier in this module
        are accepted.

    """
    name = kwargs.get("name", "")
    obj = session.puppet or session.player
    if name in _gettable:
        session.msg(get_value=_gettable[name](obj))


def _testrepeat(**kwargs):
    """
    This is a test function for using with the repeat
    inputfunc.

    Kwargs:
        session (Session): Session to return to.
    """
    import time
    kwargs["session"].msg(repeat="Repeat called: %s" % time.time())


_repeatable = {"test1": _testrepeat,  # example only
               "test2": _testrepeat}  #      "


def repeat(session, *args, **kwargs):
    """
    Call a named function repeatedly. Note that
    this is meant as an example of limiting the number of
    possible call functions.

    Kwargs:
        callback (str): The function to call. Only functions
            from the _repeatable dictionary earlier in this
            module are available.
        interval (int): How often to call function (s).
            Defaults to once every 60 seconds with a minimum
                of 5 seconds.
        stop (bool): Stop a previously assigned ticker with
            the above settings.

    """
    from evennia.scripts.tickerhandler import TICKER_HANDLER
    name = kwargs.get("callback", "")
    interval = max(5, int(kwargs.get("interval", 60)))

    if name in _repeatable:
        if kwargs.get("stop", False):
            TICKER_HANDLER.remove(interval, _repeatable[name], idstring=session.sessid, persistent=False)
        else:
            TICKER_HANDLER.add(interval, _repeatable[name], idstring=session.sessid, persistent=False, session=session)
    else:
        session.msg("Allowed repeating functions are: %s" % (", ".join(_repeatable)))



def unrepeat(session, *args, **kwargs):
    "Wrapper for OOB use"
    kwargs["stop"] = True
    repeat(session, *args, **kwargs)


_monitorable = {
    "name": "db_key",
    "location": "db_location",
    "desc": "desc"
}


def _on_monitor_change(**kwargs):
    fieldname = kwargs["fieldname"]
    obj = kwargs["obj"]
    name = kwargs["name"]
    session = kwargs["session"]
    session.msg(monitor={"name": name, "value": _GA(obj, fieldname)})


def monitor(session, *args, **kwargs):
    """
    Adds monitoring to a given property or Attribute.

    Kwargs:
      name (str): The name of the property or Attribute
        to report. No db_* prefix is needed. Only names
        in the _monitorable dict earlier in this module
        are accepted.
      stop (bool): Stop monitoring the above name.

    """
    from evennia.scripts.monitorhandler import MONITOR_HANDLER
    name = kwargs.get("name", None)
    if name and name in _monitorable and session.puppet:
        field_name = _monitorable[name]
        obj = session.puppet
        if kwargs.get("stop", False):
            MONITOR_HANDLER.remove(obj, field_name, idstring=session.sessid)
        else:
            # the handler will add fieldname and obj to the kwargs automatically
            MONITOR_HANDLER.add(obj, field_name, _on_monitor_change, idstring=session.sessid,
                            persistent=False, name=name, session=session)


def unmonitor(session, *args, **kwargs):
    """
    Wrapper for turning off monitoring
    """
    kwargs["stop"] = True
    monitor(session, *args, **kwargs)
