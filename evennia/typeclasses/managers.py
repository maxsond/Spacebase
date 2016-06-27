"""
This implements the common managers that are used by the
abstract models in dbobjects.py (and which are thus shared by
all Attributes and TypedObjects).

"""
from functools import update_wrapper
from django.db.models import Q
from evennia.utils import idmapper
from evennia.utils.utils import make_iter, variable_from_module

__all__ = ("TypedObjectManager", )
_GA = object.__getattribute__
_Tag = None

#
# Decorators
#

def returns_typeclass_list(method):
    """
    Decorator: Always returns a list, even if it is empty.

    """
    def func(self, *args, **kwargs):
        self.__doc__ = method.__doc__
        raw_queryset = kwargs.pop('raw_queryset', False)
        result = method(self, *args, **kwargs)
        if raw_queryset:
            return result
        else:
            return list(result)
    return update_wrapper(func, method)


def returns_typeclass(method):
    """
    Decorator: Returns a single typeclass match or None.

    """
    def func(self, *args, **kwargs):
        self.__doc__ = method.__doc__
        query = method(self, *args, **kwargs)
        if hasattr(query, "__iter__"):
            result = list(query)
            return result[0] if result else None
        else:
            return query
    return update_wrapper(func, method)

# Managers

class TypedObjectManager(idmapper.manager.SharedMemoryManager):
    """
    Common ObjectManager for all dbobjects.

    """
    # common methods for all typed managers. These are used
    # in other methods. Returns querysets.


    # Attribute manager methods
    def get_attribute(self, key=None, category=None, value=None, strvalue=None, obj=None, attrtype=None):
        """
        Return Attribute objects by key, by category, by value, by
        strvalue, by object (it is stored on) or with a combination of
        those criteria.

        Attrs:
            key (str, optional): The attribute's key to search for
            category (str, optional): The category of the attribute(s)
                to search for.
            value (str, optional): The attribute value to search for.
                Note that this is not a very efficient operation since it
                will query for a pickled entity. Mutually exclusive to
                `strvalue`.
            strvalue (str, optional): The str-value to search for.
                Most Attributes will not have strvalue set. This is
                mutually exclusive to the `value` keyword and will take
                precedence if given.
            obj (Object, optional): On which object the Attribute to
                search for is.
            attrype (str, optional): An attribute-type to search for.
                By default this is either `None` (normal Attributes) or
                `"nick"`.

        Returns:
            attributes (list): The matching Attributes.

        """
        query = [("attribute__db_attrtype", attrtype)]
        if obj:
            query.append(("%s__id" % self.model.__name__.lower(), obj.id))
        if key:
            query.append(("attribute__db_key", key))
        if category:
            query.append(("attribute__db_category", category))
        if strvalue:
            query.append(("attribute__db_strvalue", strvalue))
        elif value:
            # strvalue and value are mutually exclusive
            query.append(("attribute__db_value", value))
        return [th.attribute for th in self.model.db_attributes.through.objects.filter(**dict(query))]

    def get_nick(self, key=None, category=None, value=None, strvalue=None, obj=None):
        """
        Get a nick, in parallel to `get_attribute`.

        Attrs:
            key (str, optional): The nicks's key to search for
            category (str, optional): The category of the nicks(s) to search for.
            value (str, optional): The attribute value to search for. Note that this
                is not a very efficient operation since it will query for a pickled
                entity. Mutually exclusive to `strvalue`.
            strvalue (str, optional): The str-value to search for. Most Attributes
                will not have strvalue set. This is mutually exclusive to the `value`
                keyword and will take precedence if given.
            obj (Object, optional): On which object the Attribute to search for is.

        Returns:
            nicks (list): The matching Nicks.

        """
        return self.get_attribute(key=key, category=category, value=value, strvalue=strvalue, obj=obj)

    @returns_typeclass_list
    def get_by_attribute(self, key=None, category=None, value=None, strvalue=None, attrtype=None):
        """
        Return objects having attributes with the given key, category,
        value, strvalue or combination of those criteria.

        Args:
            key (str, optional): The attribute's key to search for
            category (str, optional): The category of the attribute
                to search for.
            value (str, optional): The attribute value to search for.
                Note that this is not a very efficient operation since it
                will query for a pickled entity. Mutually exclusive to
                `strvalue`.
            strvalue (str, optional): The str-value to search for.
                Most Attributes will not have strvalue set. This is
                mutually exclusive to the `value` keyword and will take
                precedence if given.
            attrype (str, optional): An attribute-type to search for.
                By default this is either `None` (normal Attributes) or
                `"nick"`.

        Returns:
            obj (list): Objects having the matching Attributes.

        """
        query = [("db_attributes__db_attrtype", attrtype)]
        if key:
            query.append(("db_attributes__db_key", key))
        if category:
            query.append(("db_attributes__db_category", category))
        if strvalue:
            query.append(("db_attributes__db_strvalue", strvalue))
        elif value:
            # strvalue and value are mutually exclusive
            query.append(("db_attributes__db_value", value))
        return self.filter(**dict(query))

    def get_by_nick(self, key=None, nick=None, category="inputline"):
        """
        Get object based on its key or nick.

        Args:
            key (str, optional): The attribute's key to search for
            nick (str, optional): The nickname to search for
            category (str, optional): The category of the nick
                to search for.

        Returns:
            obj (list): Objects having the matching Nicks.

        """
        return self.get_by_attribute(key=key, category=category, strvalue=nick, attrtype="nick")

    # Tag manager methods

    def get_tag(self, key=None, category=None, obj=None, tagtype=None, global_search=False):
        """
        Return Tag objects by key, by category, by object (it is
        stored on) or with a combination of those criteria.

        Attrs:
            key (str, optional): The Tag's key to search for
            category (str, optional): The Tag of the attribute(s)
                to search for.
            obj (Object, optional): On which object the Tag to
                search for is.
            tagtype (str, optional): One of None (normal tags),
                "alias" or "permission"
            global_search (bool, optional): Include all possible tags,
                not just tags on this object

        Returns:
            tag (list): The matching Tags.

        """
        global _Tag
        if not _Tag:
            from evennia.typeclasses.models import Tag as _Tag
        if global_search:
            # search all tags using the Tag model
            query = [("db_tagtype", tagtype)]
            if obj:
                query.append(("id", obj.id))
            if key:
                query.append(("db_key", key))
            if category:
                query.append(("db_category", category))
            return _Tag.objects.filter(**dict(query))
        else:
            # search only among tags stored on on this model
            query = [("tag__db_tagtype", tagtype)]
            if obj:
                query.append(("%s__id" % self.model.__name__.lower(), obj.id))
            if key:
                query.append(("tag__db_key", key))
            if category:
                query.append(("tag__db_category", category))
            return [th.tag for th in self.model.db_tags.through.objects.filter(**dict(query))]

    def get_permission(self, key=None, category=None, obj=None):
        """
        Get a permission from the database.

        Args:
            key (str, optional): The permission's identifier.
            category (str, optional): The permission's category.
            obj (object, optional): The object on which this Tag is set.

        Returns:
            permission (list): Permission objects.

        """
        return self.get_tag(key=key, category=category, obj=obj, tagtype="permission")

    def get_alias(self, key=None, category=None, obj=None):
        """
        Get an alias from the database.

        Args:
            key (str, optional): The permission's identifier.
            category (str, optional): The permission's category.
            obj (object, optional): The object on which this Tag is set.

        Returns:
            alias (list): Alias objects.

        """
        return self.get_tag(key=key, category=category, obj=obj, tagtype="alias")

    @returns_typeclass_list
    def get_by_tag(self, key=None, category=None, tagtype=None):
        """
        Return objects having tags with a given key or category or
        combination of the two.

        Args:
            key (str, optional): Tag key. Not case sensitive.
            category (str, optional): Tag category. Not case sensitive.
            tagtype (str or None, optional): 'type' of Tag, by default
                this is either `None` (a normal Tag), `alias` or
                `permission`.
        Returns:
            objects (list): Objects with matching tag.
        """
        query = [("db_tags__db_tagtype", tagtype)]
        if key:
            query.append(("db_tags__db_key", key.lower()))
        if category:
            query.append(("db_tags__db_category", category.lower()))
        return self.filter(**dict(query))

    def get_by_permission(self, key=None, category=None):
        """
        Return objects having permissions with a given key or category or
        combination of the two.

        Args:
            key (str, optional): Permissions key. Not case sensitive.
            category (str, optional): Permission category. Not case sensitive.
        Returns:
            objects (list): Objects with matching permission.
        """
        return self.get_by_tag(key=key, category=category, tagtype="permission")

    def get_by_alias(self, key=None, category=None):
        """
        Return objects having aliases with a given key or category or
        combination of the two.

        Args:
            key (str, optional): Alias key. Not case sensitive.
            category (str, optional): Alias category. Not case sensitive.
        Returns:
            objects (list): Objects with matching alias.
        """
        return self.get_by_tag(key=key, category=category, tagtype="alias")

    def create_tag(self, key=None, category=None, data=None, tagtype=None):
        """
        Create a new Tag of the base type associated with this
        object.  This makes sure to create case-insensitive tags.
        If the exact same tag configuration (key+category+tagtype)
        exists on the model, a new tag will not be created, but an old
        one returned.


        Args:
            key (str, optional): Tag key. Not case sensitive.
            category (str, optional): Tag category. Not case sensitive.
            data (str, optional): Extra information about the tag.
            tagtype (str or None, optional): 'type' of Tag, by default
                this is either `None` (a normal Tag), `alias` or
                `permission`.

        Notes:
            The `data` field is not part of the uniqueness of the tag:
            Setting `data` on an existing tag will overwrite the old
            data field. It is intended only as a way to carry
            information about the tag (like a help text), not to carry
            any information about the tagged objects themselves.

        """
        data = str(data) if data is not None else None
        # try to get old tag

        tag = self.get_tag(key=key, category=category, tagtype=tagtype, global_search=True)
        if tag and data is not None:
            # overload data on tag
            tag.db_data = data
            tag.save()
        elif not tag:
            # create a new tag
            global _Tag
            if not _Tag:
                from evennia.typeclasses.models import Tag as _Tag
            tag = _Tag.objects.create(
                db_key=key.strip().lower() if key is not None else None,
                db_category=category.strip().lower() if category and key is not None else None,
                db_data=data,
                db_tagtype=tagtype.strip().lower() if tagtype is not None else None)
            tag.save()
        return make_iter(tag)[0]

    # object-manager methods

    def dbref(self, dbref, reqhash=True):
        """
        Determing if input is a valid dbref.

        Args:
            dbref (str or int): A possible dbref.
            reqhash (bool, optional): If the "#" is required for this
                to be considered a valid hash.

        Returns:
            dbref (int or None): The integer part of the dbref.

        Notes:
            Valid forms of dbref (database reference number) are
            either a string '#N' or an integer N.

        """
        if reqhash and not (isinstance(dbref, basestring) and dbref.startswith("#")):
            return None
        if isinstance(dbref, basestring):
            dbref = dbref.lstrip('#')
        try:
            if int(dbref) < 0:
                return None
        except Exception:
            return None
        return dbref

    @returns_typeclass
    def get_id(self, dbref):
        """
        Find object with given dbref.

        Args:
            dbref (str or int): The id to search for.

        Returns:
            object (TypedObject): The matched object.

        """
        dbref = self.dbref(dbref, reqhash=False)
        try:
            return self.get(id=dbref)
        except self.model.DoesNotExist:
            pass
        return None

    def dbref_search(self, dbref):
        """
        Alias to get_id.

        Args:
            dbref (str or int): The id to search for.

        Returns:
            object (TypedObject): The matched object.

        """
        return self.get_id(dbref)

    @returns_typeclass_list
    def get_dbref_range(self, min_dbref=None, max_dbref=None):
        """
        Get objects within a certain range of dbrefs.

        Args:
            min_dbref (int): Start of dbref range.
            max_dbref (int): End of dbref range (inclusive)

        Returns:
            objects (list): TypedObjects with dbrefs within
                the given dbref ranges.

        """
        retval = super(TypedObjectManager, self).all()
        if min_dbref is not None:
            retval = retval.filter(id__gte=self.dbref(min_dbref, reqhash=False))
        if max_dbref is not None:
            retval = retval.filter(id__lte=self.dbref(max_dbref, reqhash=False))
        return retval

    def object_totals(self):
        """
        Get info about database statistics.

        Returns:
            census (dict): A dictionary `{typeclass_path: number, ...}` with
                all the typeclasses active in-game as well as the number
                of such objects defined (i.e. the number of database
                object having that typeclass set on themselves).

        """
        dbtotals = {}
        typeclass_paths = set(self.values_list('db_typeclass_path', flat=True))
        for typeclass_path in typeclass_paths:
            dbtotals[typeclass_path] = \
               self.filter(db_typeclass_path=typeclass_path).count()
        return dbtotals

    @returns_typeclass_list
    def typeclass_search(self, typeclass, include_children=False, include_parents=False):
        """
        Searches through all objects returning those which has a
        certain typeclass. If location is set, limit search to objects
        in that location.

        Args:
            typeclass (str or class): A typeclass class or a python path to a typeclass.
            include_children (bool, optional): Return objects with
                given typeclass *and* all children inheriting from this
                typeclass. Mutuall exclusive to `include_parents`.
            include_parents (bool, optional): Return objects with
                given typeclass *and* all parents to this typeclass.
                Mutually exclusive to `include_children`.

        Returns:
            objects (list): The objects found with the given typeclasses.

        """

        if callable(typeclass):
            cls = typeclass.__class__
            typeclass = "%s.%s" % (cls.__module__, cls.__name__)
        elif not isinstance(typeclass, basestring) and hasattr(typeclass, "path"):
            typeclass = typeclass.path

        # query objects of exact typeclass
        query = Q(db_typeclass_path__exact=typeclass)

        if include_children:
            # build requests for child typeclass objects
            clsmodule, clsname = typeclass.rsplit(".", 1)
            cls = variable_from_module(clsmodule, clsname)
            subclasses = cls.__subclasses__()
            if subclasses:
                for child in (child for child in subclasses if hasattr(child, "path")):
                    query = query | Q(db_typeclass_path__exact=child.path)
        elif include_parents:
            # build requests for parent typeclass objects
            clsmodule, clsname = typeclass.rsplit(".", 1)
            cls = variable_from_module(clsmodule, clsname)
            parents = cls.__mro__
            if parents:
                for parent in (parent for parent in parents if hasattr(parent, "path")):
                    query = query | Q(db_typeclass_path__exact=parent.path)
        # actually query the database
        return self.filter(query)


class TypeclassManager(TypedObjectManager):
    """
    Manager for the typeclasses. The main purpose of this manager is
    to limit database queries to the given typeclass despite all
    typeclasses technically being defined in the same core database
    model.

    """

    def get(self, *args, **kwargs):
        """
        Overload the standard get. This will limit itself to only
        return the current typeclass.

        Args:
            args (any): These are passed on as arguments to the default
                django get method.
        Kwargs:
            kwargs (any): These are passed on as normal arguments
                to the default django get method
        Returns:
            object (object): The object found.

        Raises:
            ObjectNotFound: The exact name of this exception depends
                on the model base used.

        """
        kwargs.update({"db_typeclass_path":self.model.path})
        return super(TypedObjectManager, self).get(**kwargs)

    def filter(self, *args, **kwargs):
        """
        Overload of the standard filter function. This filter will
        limit itself to only the current typeclass.

        Args:
            args (any): These are passed on as arguments to the default
                django filter method.
        Kwargs:
            kwargs (any): These are passed on as normal arguments
                to the default django filter method.
        Returns:
            objects (queryset): The objects found.

        """
        kwargs.update({"db_typeclass_path":self.model.path})
        return super(TypedObjectManager, self).filter(*args, **kwargs)

    def all(self):
        """
        Overload method to return all matches, filtering for typeclass.

        Returns:
            objects (queryset): The objects found.

        """
        return super(TypedObjectManager, self).all().filter(db_typeclass_path=self.model.path)

    def _get_subclasses(self, cls):
        """
        Recursively get all subclasses to a class.

        Args:
            cls (classoject): A class to get subclasses from.
        """
        all_subclasses = cls.__subclasses__()
        for subclass in all_subclasses:
            all_subclasses.extend(self._get_subclasses(subclass))
        return all_subclasses

    def get_family(self, **kwargs):
        """
        Variation of get that not only returns the current typeclass
        but also all subclasses of that typeclass.

        Kwargs:
            kwargs (any): These are passed on as normal arguments
                to the default django get method.
        Returns:
            objects (list): The objects found.

        Raises:
            ObjectNotFound: The exact name of this exception depends
                on the model base used.

        """
        paths = [self.model.path] + ["%s.%s" % (cls.__module__, cls.__name__)
                         for cls in self._get_subclasses(self.model)]
        kwargs.update({"db_typeclass_path__in":paths})
        return super(TypedObjectManager, self).get(**kwargs)

    def filter_family(self, *args, **kwargs):
        """
        Variation of filter that allows results both from typeclass
        and from subclasses of typeclass

        Args:
            args (any): These are passed on as arguments to the default
                django filter method.
        Kwargs:
            kwargs (any): These are passed on as normal arguments
                to the default django filter method.
        Returns:
            objects (list): The objects found.

        """
        # query, including all subclasses
        paths = [self.model.path] + ["%s.%s" % (cls.__module__, cls.__name__)
                         for cls in self._get_subclasses(self.model)]
        kwargs.update({"db_typeclass_path__in":paths})
        return super(TypedObjectManager, self).filter(*args, **kwargs)

    def all_family(self):
        """
        Return all matches, allowing matches from all subclasses of
        the typeclass.

        Returns:
            objects (list): The objects found.

        """
        paths = [self.model.path] + ["%s.%s" % (cls.__module__, cls.__name__)
                         for cls in self._get_subclasses(self.model)]
        return super(TypedObjectManager, self).all().filter(db_typeclass_path__in=paths)


