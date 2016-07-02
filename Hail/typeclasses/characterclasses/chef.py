from evennia import DefaultCharacter
from evennia.commands.cmdset import CmdSet
from evennia import Command as BaseCommand
from evennia.utils.spawner import spawn

from Hail.typeclasses.objects import Vegetable

class Chef(DefaultCharacter):
    pass

class CmdSetChef(CmdSet):

    key = "chef_cmdset"

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(Chop())

class Chop(BaseCommand):
    """
    Chop up a vegetable to create edible and regrowable parts

    Usage:
       chop <vegetable>
    """

    key = "chop"

    def func(self):

        veg = self.args.strip()

        if not veg:
            self.caller.msg("What do you want to chop up?")
        elif type(veg) != Vegetable:
            self.caller.msg("That's not a vegetable.")
        else:
            self.caller.msg("You chop up the {}".format(veg.lower()))
            self.caller.location.msg_contents("{} chops up the {}".format(
                self.caller,
                veg.lower()
            ))
            spawn()