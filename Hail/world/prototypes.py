import sys

"""
Prototypes

A prototype is a simple way to create individualized instances of a
given `Typeclass`. For example, you might have a Sword typeclass that
implements everything a Sword would need to do. The only difference
between different individual Swords would be their key, description
and some Attributes. The Prototype system allows to create a range of
such Swords with only minor variations. Prototypes can also inherit
and combine together to form entire hierarchies (such as giving all
Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a
hierarchy of typeclasses instead.

Example prototypes are read by the `@spawn` command but is also easily
available to use from code via `evennia.spawn` or `evennia.utils.spawner`.
Each prototype should be a dictionary. Use the same name as the
variable to refer to other prototypes.

Possible keywords are:
    prototype - string pointing to parent prototype of this structure.
    key - string, the main object identifier.
    typeclass - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
    location - this should be a valid object or #dbref.
    home - valid object or #dbref.
    destination - only valid for exits (object or dbref).

    permissions - string or list of permission strings.
    locks - a lock-string.
    aliases - string or list of strings.

    ndb_<name> - value of a nattribute (the "ndb_" part is ignored).
    any other keywords are interpreted as Attributes and their values.

See the `@spawn` command and `evennia.utils.spawner` for more info.

"""

def proto(proto_str):
    return getattr(sys.modules[__name__], proto_str)

#########
# Seeds #
#########

SEED = {
    "typeclass": "typeclasses.objects.Seed",
    "key": "seed",
    "growth_time": 10,
    "produce": "VEGETABLE",
    "desc": "A generic seed."
}

CARROTSEED = {
    "prototype": "SEED",
    "key": "carrot top",
    "produce": "CARROT",
    "desc": "The top of a carrot, good for regrowing."
}

KALESEED = {
    "prototype": "SEED",
    "key": "kale seed",
    "produce": "KALE",
    "desc": "A small seed for a nutritious leafy green."
}

POTATOSEED = {
    "prototype": "SEED",
    "key": "potato eye",
    "produce": "POTATO",
    "desc": "The eye of a potato, ready for replanting."
}

##############
# Vegetables #
##############

VEGETABLE = {
    "typeclass": "typeclasses.objects.Vegetable",
    "key": "vegetable",
    "potassium": 0.1,
    "carbs": 0.1,
    "magnesium": 0.1,
    "iron": 0.1,
    "produce": "VEGFOOD",
    "desc": "A generic vegetable."
}

CARROT = {
    "prototype": "VEGETABLE",
    "key": "carrot",
    "produce": "CARROTFOOD",
    "seed": "CARROTSEED",
    "desc": "A long orange root."
}

KALE = {
    "prototype": "VEGETABLE",
    "key": "leaf of kale",
    "alias": "kale",
    "produce": "KALEFOOD",
    "seed": "KALESEED",
    "desc": "A dark green leaf of nutritious kale."
}

POTATO = {
    "prototype": "VEGETABLE",
    "key": "potato",
    "produce": "POTATOFOOD",
    "seed": "POTATOSEED",
    "desc": "A humble-looking spud."
}

PRODUCE_LIST = {
    "VEGETABLE": VEGETABLE,
    "CARROT": CARROT,
    "KALE": KALE,
    "POTATO": POTATO
}

###################
# Hydroponics Bed #
###################

HYDROBED = {
    "typeclass": "typeclasses.objects.HydroponicBed",
    "key": "hydroponics bed",
    "aliases": ["bed"],
    "desc": "A utilitarian bed for hydroponic growing of edible produce."
}

###############
# Comestibles #
###############

FOOD = {
    "typeclass": "typeclasses.objects.Food",
    "key": "food",
    "desc": "A form of food so generic it doesn't even warrant description."
}

VEGFOOD = {
    "prototype": "FOOD",
    "key": "edible vegetable",
    "desc": "A generic edible vegetable."
}

CARROTFOOD = {
    "prototype": "VEGFOOD",
    "key": "carrot chunks",
    "desc": "A handful of delicious carrot chunks."
}

KALEFOOD = {
    "prototype": "VEGFOOD",
    "key": "prepared kale leaf",
    "desc": "A deep green leaf filled with nutrients and prepared for consumption."
}

POTATOFOOD = {
    "prototpe": "VEGFOOD",
    "key": "prepared potato",
    "desc": "A potato prepared for eating."
}

EDIBLEVEGS = {
    "CARROTFOOD": CARROTFOOD,
    "KALEFOOD": KALEFOOD,
    "POTATOFOOD": POTATOFOOD
}