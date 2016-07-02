from evennia import DefaultCharacter
from evennia.commands.cmdset import CmdSet
from base import ClassCommand
from ..objects import Seed, HydroponicBed, Fertilizer, Vegetable
from evennia.utils.spawner import spawn
from Hail.world.prototypes import PRODUCE_LIST


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
        self.add(Check())


class Plant(ClassCommand):
    """
    Plant a seed in a hydroponics bed

    Usage:
       plant <seed> <bed>
    """
    key = "plant"

    def func(self):
        args = self.args.strip().split(" ")
        try:
            seed = self.caller.search(args[0])
        except:
            self.caller.msg("What is it you want to plant?")
            return
        try:
            bed = self.caller.search(" ".join(args[1:]))
        except:
            self.caller.msg("Where do you want to plant the {seed}?".format(seed=seed))
            return
        else:
            if type(seed) != Seed:
                self.caller.msg("You can't plant that!")
            elif type(bed) != HydroponicBed:
                self.caller.msg("You can't plant the {seed} there!".format(seed=seed))
            elif bed.db.grown:
                self.caller.msg("Try harvesting from it first.")
            elif bed.db.planted:
                self.caller.msg("There's already something planted there!")
            else:
                self.caller.msg("You plant the {seed} in the {bed}".format(seed=seed, bed=bed))
                self.caller.location.msg_contents("{actor} plants the {seed} in the {bed}".format(
                    actor=self.caller,
                    seed=seed,
                    bed=bed
                ),
                    exclude=self.caller
                )
                bed.db.planted = True
                bed.db.produce = seed.db.produce
                bed.db.interval = seed.db.growth_time
                seed.delete()
                bed.scripts.add("scripts.PlantGrowth")


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
        fertilizer = self.caller.search(" ".join(args[1:]))
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
            self.caller.location.msg_contents("{actor} fertilizes {bed} with {fertilizer}".format(
                actor=self.caller,
                bed=bed,
                fertilizer=fertilizer
            ),
                exclude=self.caller
            )

class Harvest(ClassCommand):
    """
    Harvest a grown plant from a hydroponics bed

    Usage:
       harvest <bed>
    """
    key = "harvest"

    def func(self):
        bed = self.caller.search(self.args.strip())
        if not bed:
            self.caller.msg("What did you want to harvest from?")
        elif type(bed) != HydroponicBed:
            self.caller.msg("You can't harvest from that!")
        elif not bed.db.planted:
            self.caller.msg("You cannot reap what you don't sow.")
        elif not bed.db.grown:
            self.caller.msg("It's not ready to harvest yet.")
        else:
            self.caller.msg("You harvest the {produce} from the {bed}".format(
                produce=bed.db.produce.lower(),
                bed=bed))
            self.caller.location.msg_contents("{} harvests the {} from the {}".format(
                self.caller,
                bed.db.produce.lower(),
                bed
            ),
                exclude=self.caller
            )
            bed.db.grown = False
            bed.db.planted = False
            bed.db.desc = bed.db.saved_desc
            produce = spawn(PRODUCE_LIST[bed.db.produce])
            produce[0].location = self.caller


class Assess(ClassCommand):
    """
    Assess the properties of a seed or vegetable

    Usage:
       assess <seed>
       assess <vegetable>
    """
    key = "assess"

    def func(self):
        veg = self.caller.search(self.args.strip())
        if not veg:
            self.caller.msg("What do you want to assess?")
        elif type(veg) not in [Seed, Vegetable]:
            self.caller.msg("You can't assess that!")
        elif type(veg) == Seed:
            self.caller.msg("That seed will take about {} seconds to grow a mature vegetable.".format(veg.db.growth_time))
        elif type(veg) == Vegetable:
            self.caller.msg("""
            Vegetable:      {}
            ------------------
            Potassium:      {} mg
            Carbohydrates:  {} mg,
            Magnesium:      {} mg,
            Iron:           {} mg
            """.format(
                veg.key,
                veg.db.potassium,
                veg.db.carbs,
                veg.db.magnesium,
                veg.db.iron
            ))

class Check(ClassCommand):
    """
    Check the status of a growing plant

    Usage:
       check <bed>
    """
    key = "check"

    def func(self):
        bed = self.caller.search(self.args.strip())
        if not bed:
            self.caller.msg("Which bed did you want to check?")
        elif type(bed) != HydroponicBed:
            self.caller.msg("That doesn't appear to be a bed you can check.")
        else:
            try:
                self.caller.msg("That plant should take about {seconds} seconds to mature.".format(
                    seconds=bed.scripts.get("plantgrowth")[0].time_until_next_repeat()))
            except:
                self.caller.msg("That bed isn't growing anything.")
            self.caller.location.msg_contents("{} looks impatiently at the {}".format(
                self.caller,
                bed
            ),
                exclude=self.caller
            )
