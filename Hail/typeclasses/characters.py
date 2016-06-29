"""
Characters

Characters are (by default) Objects setup to be puppeted by Players.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from evennia.commands.cmdset import CmdSet
from evennia import Command as BaseCommand
from evennia.commands.default.cmdset_character import CharacterCmdSet

class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move - Launches the "look" command after every move.
    at_post_unpuppet(player) -  when Player disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Player has disconnected" 
                    to the room.
    at_pre_puppet - Just before Player re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "PlayerName has entered the game" to the room.

    """
    def at_object_creation(self):
        "This is called when object is first created, only."
        self.db.role = " the Citizen"
        self.cmdset.add_default(CmdSetTest, permanent=True)

    def at_pre_puppet(self, player, session=None):
        self.cmdset.add_default(CmdSetTest, permanent=True)
        self.cmdset.add(CharacterCmdSet, permanent=True)
        if self.db.prelogout_location:
            # try to recover
            self.location = self.db.prelogout_location
        if self.location is None:
            # make sure location is never None (home should always exist)
            self.location = self.home
        if self.location:
            # save location again to be sure
            self.db.prelogout_location = self.location
            self.location.at_object_receive(self, self.location)
        else:
            player.msg("{r%s has no location and no home is set.{n" % self, session=session)


    def get_display_name(self, looker, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or player that is looking
                at/getting inforamtion for this object.

        Returns:
            name (str): A string containing the name of the object,
                including the DBREF if this user is privileged to control
                said object.

        Notes:
            This function could be extended to change how object names
            appear to users in character, but be wary. This function
            does not change an object's keys or aliases when
            searching, and is expected to produce something useful for
            builders.

        """
        if self.locks.check_lockstring(looker, "perm(Builders)"):
            return "{}(#{})".format(self.name + str(self.db.role), self.id)
        return self.name + str(self.db.role)

    def control_new_character(self, session, object):
        self.player.unpuppet_object(session)
        self.player.puppet_object(object)


class TestCmd(BaseCommand):
    """
    Test building commands

    Usage:
       testme
    """
    key = "testme"
    locks = "cmd:all()"
    help_category = "general"

    def func(self):
        self.caller.msg("Hello, {}".format(self.caller))

class ReroleCmd(BaseCommand):
    """
    Change a character's title

    Usage:
       rerole <character> <new title>
    """
    key = "rerole"

    def func(self):
        args = self.args.strip().split(" ")
        obj = self.caller.search(args[0])
        title = args[1:]
        if obj.db.role:
            obj.db.role = " " + " ".join(title)
            self.caller.msg("Done!")
        else:
            self.caller.msg("Oops!")

class CmdSetTest(CmdSet):
    "CmdSet for the lightsource commands"
    key = "lightsource_cmdset"
    # this is higher than the dark cmdset - important!
    priority = 3

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(TestCmd())
        self.add(ReroleCmd())
