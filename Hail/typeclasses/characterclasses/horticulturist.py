from evennia import DefaultCharacter
from evennia.commands.cmdset import CmdSet
from base import ClassCommand
from ..objects import Seed, HydroponicBed, Fertilizer, Vegetable


class Horticulturist(DefaultCharacter):
    pass


class CmdSetHorticulturist(CmdSet):

    key = "horticulturist_cmdset"

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(Plant())
        self.add(Fertilize())
        self.add(Harvest())
        self.add(Assess())


class Plant(ClassCommand):
    """
    Plant a seed in a hydroponics bed

    Usage:
       plant <seed> <bed>
    """
    key = "plant"

    def func(self):
        args = self.args.strip().split(" ")
        seed = self.caller.search(args[0])
        bed = self.caller.search(args[1])
        if not seed:
            self.caller.msg("What is it you want to plant?")
        elif type(seed) != Seed:
            self.caller.msg("You can't plant that!")
        elif not bed:
            self.caller.msg("Where do you want to plant the {seed}?".format(seed=seed))
        elif type(bed) != HydroponicBed:
            self.caller.msg("You can't plant the {seed} there!".format(seed=seed))
        else:
            self.caller.msg("You plant the {seed} in the {bed}".format(seed=seed, bed=bed))
            bed.db.planted = True


class Fertilize(ClassCommand):
    """
    Fertilize a plant in a hydroponics bed

    Usage:
       fertilize <bed> <fertilizer>
    """
    key = "fertilize"

    def func(self):
        args = self.args.strip().split(" ")
        bed = self.caller.search(args[0])
        fertilizer = self.caller.search(args[1])
        if not bed:
            self.caller.msg("What do you want to fertilize?")
        elif not fertilizer:
            self.caller.msg("And what do you intend to fertilize that with?")
        elif type(bed) != HydroponicBed:
            self.caller.msg("Try as you might, that cannot be fertilized.")
        elif type(fertilizer) != Fertilizer:
            self.caller.msg("That won't do much good as fertilizer.")
        else:
            self.caller.msg("You fertilize {bed} with {fertilizer}".format(bed=bed, fertilizer=fertilizer))


class Harvest(ClassCommand):
    """
    Harvest a grown plant from a hydroponics bed

    Usage:
       harvest <bed>
    """
    key = "harvest"

    def func(self):
        arg = self.caller.search(self.args.strip())
        if not arg:
            self.caller.msg("What did you want to harvest from?")
        elif type(arg) != HydroponicBed:
            self.caller.msg("You can't harvest from that!")
        elif not arg.db.planted:
            self.caller.msg("You cannot reap what you don't sow.")
        elif not arg.db.grown:
            self.caller.msg("It's not ready to harvest yet.")
        else:
            self.caller.msg("You harvest the produce from {bed}".format(bed=arg))


class Assess(ClassCommand):
    """
    Assess the properties of a seed or vegetable

    Usage:
       assess <seed>
       assess <vegetable>
    """
    key = "assess"

    def func(self):
        arg = self.caller.search(self.args.strip())
        if not arg:
            self.caller.msg("What do you want to assess?")
        elif type(arg) not in [Seed, Vegetable]:
            self.caller.msg("You can't assess that!")
        elif type(arg) == Seed:
            self.caller.msg("That seed's growth rate is {}".format(arg.db.growth_rate))
        elif type(arg) == Vegetable:
            self.caller.msg("""
            Vegetable:      {}
            ------------------
            Potassium:      {} mg
            Carbohydrates:  {} mg,
            Magnesium:      {} mg,
            Iron:           {} mg
            """)

