from evennia import DefaultCharacter
from evennia.commands.cmdset import CmdSet
from evennia import Command as BaseCommand

class Doctor(DefaultCharacter):
    pass

class CmdSetDoctor(CmdSet):

    key = "doctor_cmdset"

    def at_cmdset_creation(self):
        "called at cmdset creation"
        self.add(Diagnose())
        self.add(Inject())

class Diagnose(BaseCommand):

    """
    Diagnose a character's health and nutrition levels

    Usage:
       diagnose <subject>
    """

    key = "diagnose"

    help_category = "class abilities"

    def func(self):
        try:
            target = self.caller.search(self.args.strip())
        except:
            self.caller.msg("That's not a thing.")
            return
        # if type(target) != Character:
        #     self.caller.msg("Dammit, Jim, you're a doctor! Not a... whatever would diagnose that.")
        else:
            self.caller.msg("""
            Subject: {t}
            ---

            Potassium levels    :   {p}
            Carbohydrate levels :   {c}
            Magnesium levels    :   {m}
            Iron levels         :   {i}

            Disorders:
            ---
            {d}
            """.format(
                t=target,
                p=target.db.potassium,
                c=target.db.carbs,
                m=target.db.magnesium,
                i=target.db.iron,
                d=target.db.disorders
            ))

class Inject(BaseCommand):
    """
    Pump a (un?)willing subject full of mystery chemicals

    Usage:
       inject <subject> <syringe>
    """

    key = "inject"
    help_category = "class abilities"

    def func(self):
        args = self.args.strip().split()
        try:
            subject = args[0]
        except Exception as e:
            self.caller.msg("Who did you want to pump full of mystery chemicals?")
            print e
            return
        try:
            syringe = " ".join(args[1:])
        except Exception as e:
            self.caller.msg("Which mystery chemicals did you want to pump them full of?")
            print e
            return
        subject = self.caller.search(subject)
        if not subject:
            self.caller.msg("They don't seem to be here.")
            return
        syringe = self.caller.search(syringe)
        if not syringe:
            self.caller.msg("That's not a valid vector for mystery chemicals.")
        elif not syringe.db.contents:
            self.caller.msg("As much as you like sticking people with needles, there's really no point to sticking them with an empty one.")
        else:
            self.caller.msg("You stick {} with the needle!".format(subject))
