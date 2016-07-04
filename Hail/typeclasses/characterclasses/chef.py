from evennia import DefaultCharacter
from evennia.commands.cmdset import CmdSet
from evennia import Command as BaseCommand
from evennia.utils.spawner import spawn

from typeclasses.objects import Vegetable
from world import prototypes

class Chef(DefaultCharacter):
    pass

class CmdSetChef(CmdSet):

    key = "chef_cmdset"

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(Prepare())
        self.add(Grate())
        self.add(Recipes())

class Prepare(BaseCommand):
    """
    Chop up a vegetable to create edible and regrowable parts

    Usage:
       chop <vegetable>
    """

    key = "prepare"
    help_category = "class abilities"

    def func(self):

        veg = self.args.strip()
        veg = self.caller.search(veg)
        if not veg:
            self.caller.msg("What do you want to chop up?")
        elif type(veg) != Vegetable:
            self.caller.msg("That's not a vegetable. It's  {}".format(type(veg)))
        elif veg.db.produce.upper() not in prototypes.EDIBLEVEGS:
            self.caller.msg("You don't know how to prepare that vegetable. {}".format(prototypes.EDIBLEVEGS))
        else:
            self.caller.msg("You chop up the {}".format(veg.key.lower()))
            self.caller.location.msg_contents("{} chops up the {}".format(
                self.caller,
                veg.key.lower()
            ),
                exclude=self.caller
            )

            food = spawn(prototypes.proto(veg.db.produce))[0]
            seed = spawn(prototypes.proto(veg.db.seed))[0]
            veg.delete()
            seed.location = self.caller
            food.location = self.caller

class Grate(BaseCommand):
    """
        Grate a vegetable

        Usage:
           chop <vegetable>
        """

    key = "grate"
    help_category = "class abilities"

    def func(self):

        veg = self.args.strip()
        veg = self.caller.search(veg)
        if not veg:
            self.caller.msg("What do you want to grate?")
        elif type(veg) != Vegetable:
            self.caller.msg("That's not a vegetable!")
        elif veg.db.produce.upper() not in prototypes.EDIBLEVEGS:
            self.caller.msg("You don't know how to prepare that vegetable.")
        else:
            self.caller.msg("You chop up the {}".format(veg.key.lower()))
            self.caller.location.msg_contents("{} chops up the {}".format(
                self.caller,
                veg.key.lower()
            ),
                exclude=self.caller
            )

            food = spawn(prototypes.proto(veg.db.produce))[0]
            seed = spawn(prototypes.proto(veg.db.seed))[0]
            veg.delete()
            seed.location = self.caller
            food.location = self.caller

class Recipes(BaseCommand):

    key = "recipes"
    help_category = "class abilities"

    def func(self):
        """
        Refer to your known recipes

        Usage:
           recipes
        """
        self.caller.msg("""
        MASHED POTATOES AND CARROTS
        ---

        1 handful of carrot chunks
        2 prepared potatoes

        Combine for a tasty salad.
        """)