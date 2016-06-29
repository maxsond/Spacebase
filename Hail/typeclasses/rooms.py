"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia import Command as BaseCommand
from evennia.commands.cmdset import CmdSet


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    pass

class ChargenRoom(DefaultRoom):

    def at_object_receive(self, character, source_location):
        character.player.msg("""
        Welcome to SpaceBase! To begin, you'll need to select a role aboard the base.

        1) Artificial Intelligence
        2) Chef
        3) Chemist
        4) Doctor
        5) Engineer
        6) Horticulturist

        Commands
        ---
        DETAILS # : Get information about a class
        SELECT #  : Choose your class
        CHARGEN   : Review this message
        ---
        """)

    def at_object_creation(self):
        self.cmdset.add_default(ChargenCmdSet)

class Chargen(BaseCommand):
    """
    Display the chargen menu

    Usage:
       chargen

    """
    key = "chargen"

    def func(self):
        self.caller.msg("""
        Welcome to SpaceBase! To begin, you'll need to select a role aboard the base.

        1) Artificial Intelligence
        2) Chef
        3) Chemist
        4) Doctor
        5) Engineer
        6) Horticulturist

        Commands
        ---
        DETAILS # : Get information about a class
        SELECT #  : Choose your class
        CHARGEN   : Review this message
        ---
        """)


class Details(BaseCommand):
    """
    Display details of a character class

    Usage:
       details <class #>
    """
    key = "details"

    def func(self):
        roles = [
            """
            Artificial Intelligence
            ---

            The AI is free of physical constraints. It can manipulate machinery aboard the base
            without needing to be physically present in the room. It also has the fastest hacking
            time of all the classes. However, it can be incapacitated by an engineer who destroys
            its vulnerable interface sockets.
            """,
            """
            Chef
            ---

            The chef has free access to the kitchen, which houses the base's supply of food and a
            fair number of potentially dangerous implements. The chef will rely on the horticulturist
            to provide a supply of fresh vegetables, and will in turn be responsible for feeding the
            other colonists.
            """,
            """
            Chemist
            ---

            The chemist can experiment with different combinations of materials to craft new inventions.
            The chemist will rely on the engineer to provide the raw materials for these experiments
            once the initial supplies begin to run low.
            """,
            """
            Doctor
            ---

            The doctor controls access to the medical bay and can heal the other base staff. Or poison
            them. All character will rely on the doctor to keep them healthy and the doctor will rely on
            the chemist and horticulturist to provide the necessary medical supplies.
            """,
            """
            Engineer
            ---

            The engineer can harvest materials outside the spacebase which the chemist can turn into
            useful materials, as well as manipulating the machinery around the base. The engineer will
            rely on the chemist to provide the materials he requires for his job.
            """,
            """
            Horticulturist
            ---

            The horticulturist controls access to hydroponics and is responsible for growing the renewable
            materials the spacebase will require. The horticulturist will depend on the engineer and chemist
            to supply fertilizer to keep the plants growing.
            """
        ]
        try:
            index = int(self.args.strip()) - 1
            if index >= 0:
                msg = roles[int(self.args.strip()) - 1]
                self.caller.msg(msg)
            else:
                self.caller.msg("That's not a valid number!")
        except:
            self.caller.msg("That's not a valid number!")


class Select(BaseCommand):
    """
    Select a class

    Usage:
       select <class #>
    """
    key = "select"

    def func(self):
        roles = [
            "Artificial Intelligence",
            "Chef",
            "Chemist",
            "Doctor",
            "Engineer",
            "Horticulturist"
        ]
        try:
            index = int(self.args.strip()) - 1
            if index >= 0:
                role = " the " + roles[int(self.args.strip()) - 1]
                self.caller.db.role = role
            else:
                self.caller.msg("That's not a valid number!")
        except:
            self.caller.msg("That's not a valid number!")


class ChargenCmdSet(CmdSet):
    key = "chargen_cmdset"

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(Chargen())
        self.add(Details())
        self.add(Select())
