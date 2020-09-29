#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartypistry** (i.e., singleton dictionary mapping from the fully-qualified
classnames of all type hints annotating callables decorated by the
:func:`beartype.beartype` decorator to those types).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: For efficiency, register tuples under their numeric hashes rather than
#strings embedding numeric hashes formatted as "+{numeric_hash}". Ergo:
#* Tuples would be registered instead with numeric hashes.
#* Types would continue to be registered with fully-qualified classnames.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    _BeartypeCallBeartypistryException,
    _BeartypeDecorBeartypistryException,
)
from beartype._decor._code.codemain import PARAM_NAME_TYPISTRY
from beartype._util.utilobject import (
    MODULE_NAME_BUILTINS,
    get_object_module_name_or_none,
    get_object_name_qualified,
    get_object_name_unqualified,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_TYPISTRY_HINT_NAME_TUPLE_PREFIX = '+'
'''
**Beartypistry tuple key prefix** (i.e., substring prefixing the keys of all
beartypistry key-value pairs whose values are tuples).

Since fully-qualified classnames are guaranteed *not* to be prefixed by this
prefix, this prefix suffices to uniquely distinguish key-value pairs whose
values are types from pairs whose values are tuples.
'''

# ....................{ CONSTANTS ~ code                  }....................
_CODE_TYPISTRY_HINT_NAME_TO_HINT_PREFIX = PARAM_NAME_TYPISTRY + '['
'''
Substring prefixing a Python expression mapping from the subsequent string to
an arbitrary object cached by the beartypistry singleton via the private
beartypistry parameter.
'''


_CODE_TYPISTRY_HINT_NAME_TO_HINT_SUFFIX = ']'
'''
Substring prefixing a Python expression mapping from the subsequent string to
an arbitrary object cached by the beartypistry singleton via the private
beartypistry parameter.
'''

# ....................{ REGISTRARS                        }....................
@callable_cached
def register_typistry_type(hint: type) -> str:
    '''
    Register the passed **PEP-noncompliant type** (i.e., class neither defined
    by the :mod:`typing` module *nor* subclassing such a class) with the
    beartypistry singleton *and* return a Python expression evaluating to this
    type when accessed via the private ``__beartypistry`` parameter implicitly
    passed to all wrapper functions generated by the :func:`beartype.beartype`
    decorator.

    This function is syntactic sugar improving consistency throughout the
    codebase, but is otherwise roughly equivalent to:

        >>> from beartype._decor._typistry import bear_typistry
        >>> from beartype._util.utilobject import get_object_name_qualified
        >>> bear_typistry[get_object_name_qualified(hint)] = hint

    This function is memoized for efficiency.

    Parameters
    ----------
    hint : type
        PEP-noncompliant type to be registered.

    Returns
    ----------
    str
        Python expression evaluating to this type when accessed via the private
        ``__beartypistry`` parameter implicitly passed to all wrapper functions
        generated by the :func:`beartype.beartype` decorator.

    Raises
    ----------
    _BeartypeDecorBeartypistryException
        If this object is either:

        * *Not* a type.
        * **PEP-compliant** (i.e., either a class defined by the :mod:`typing`
          module *or* subclass of such a class and thus a PEP-compliant type
          hint, which all violate standard type semantics and thus require
          PEP-specific handling).
    '''

    # If this object is *NOT* a type, raise an exception.
    if not isinstance(hint, type):
        raise _BeartypeDecorBeartypistryException(
            'Beartypistry type {!r} not a type.'.format(hint))
    # Else, this object is a type.
    #
    # Note that we defer all further validation of this type to the
    # Beartypistry.__setitem__() method, implicitly invoked on subsequently
    # assigning a "bear_typistry" key-value pair.

    # Unqualified name of this type.
    hint_basename = get_object_name_unqualified(hint)

    # Fully-qualified name of the module defining this class if this class is
    # defined by a module *OR* "None" otherwise.
    hint_module_name = get_object_module_name_or_none(hint)

    # If...
    if (
        # This type is a builtin (i.e., is defined by the pseudo "builtins"
        # module whose attributes are globally available by default) *AND*...
        hint_module_name == MODULE_NAME_BUILTINS and
        # This type is *NOT* the type of the "None" singleton. Unlike all other
        # builtin types, the type of the "None" singleton is *NOT* globally
        # accessible despite being declared to be builtin.
        #     >>> import builtins
        #     >>> type(None).__name__
        #     'NoneType'
        #     >>> type(None).__module__
        #     'builtins'
        #     >>> NoneType
        #     NameError: name 'NoneType' is not defined   <---- this is balls
        #
        # This inconsistency almost certainly constitutes a bug in the CPython
        # interpreter, but it seems doubtful that anyone else would see it that
        # way and almost certain that everyone else would attempt to defend
        # this edge case. In short, we have no choice but to register this type
        # as if it were a normal type. (Hardly the worst thing to happen.)
        hint_basename != 'NoneType'
    # ...then this type does *NOT* require registration. In this case, return
    # the unqualified name of this type as is.
    ):
        return hint_basename
    # Else, this type is *NOT* a builtin and thus requires registration.
    # assert hint_basename != 'NoneType'

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5
    #support, which are the optimal means of performing string formatting.

    # Fully-qualified name of this type.
    hint_name = hint_module_name + '.' + hint_basename

    # If this type has *NOT* yet been registered with the beartypistry
    # singleton, do so.
    #
    # Note that the beartypistry singleton's __setitem__() dunder method
    # intentionally raises exceptions on attempts to re-register the same
    # object twice, as tuple re-registration requires special handling to avoid
    # hash collisions. Nonetheless, this is a non-issue. Why? Since this
    # function is memoized, re-registration should *NEVER* happen.
    bear_typistry[hint_name] = hint

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Return a Python expression evaluating to this type.
    return (
        _CODE_TYPISTRY_HINT_NAME_TO_HINT_PREFIX + repr(hint_name) +
        _CODE_TYPISTRY_HINT_NAME_TO_HINT_SUFFIX
    )

# ....................{ REGISTRARS ~ tuple                }....................
@callable_cached
def register_typistry_tuple(
    # Mandatory parameters.
    hint: tuple,

    # Optional parameters.
    is_types_unique: bool = False,
) -> type:
    '''
    Register the passed tuple of one or more **PEP-noncompliant types** (i.e.,
    classes neither defined by the :mod:`typing` module *nor* subclassing such
    classes) with the beartypistry singleton *and* return a Python
    expression evaluating to this tuple when accessed via the private
    ``__beartypistry`` parameter implicitly passed to all wrapper functions
    generated by the :func:`beartype.beartype` decorator.

    This function is memoized for efficiency.

    Design
    ----------
    Unlike types, tuples are commonly dynamically constructed on-the-fly by
    various tuple factories (e.g., :attr:`beartype.cave.NoneTypeOr`,
    :attr:`typing.Optional`) and hence have no reliable fully-qualified names.
    Instead, this function synthesizes the string uniquely identifying this
    tuple as the concatenation of:

    * The magic substring :data:`_TYPISTRY_HINT_NAME_TUPLE_PREFIX`. Since
      fully-qualified classnames uniquely identifying types as beartypistry
      keys are guaranteed to *never* contain this substring, this substring
      prevents collisions between tuple and type names.
    * This tuple's hash. Note that this tuple's object ID is intentionally
      *not* embedded in this string. Two tuples with the same items are
      typically different objects and thus have different object IDs, despite
      producing identical hashes: e.g.,

          >>> ('Das', 'Kapitel',) is ('Das', 'Kapitel',)
          False
          >>> id(('Das', 'Kapitel',)) == id(('Das', 'Kapitel',))
          False
          >>> hash(('Das', 'Kapitel',)) == hash(('Das', 'Kapitel',))
          True

      The exception is the empty tuple, which is a singleton and thus *always*
      has the same object ID and hash: e.g.,

          >>> () is ()
          True
          >>> id(()) == id(())
          True
          >>> hash(()) == hash(())
          True

    Identifying tuples by their hashes enables the beartypistry singleton to
    transparently cache duplicate tuple unions having distinct object IDs as
    the same underlying object, reducing space consumption. While hashing
    tuples *does* impact time performance, the tangible gains are considered
    worth the cost.

    Parameters
    ----------
    hint : tuple
        Tuple of all PEP-noncompliant types to be registered.
    is_types_unique : bool
        ``True`` only if the caller guarantees this tuple to contain *no*
        duplicates. If ``False``, this function assumes this tuple to contain
        duplicates by internally:

        #. Coercing this tuple into a set, thus implicitly ignoring both
           duplicates and ordering of types in this tuple.
        #. Coercing that set back into another tuple.
        #. If these two tuples differ, the passed tuple contains one or more
           duplicates; in this case, the duplicate-free tuple is registered.
        #. Else, the passed tuple contains no duplicates; in this case, the
           passed tuple is registered.

        Ergo, this boolean does *not* simply enable an edge-case optimization
        (though it certainly does do that). This boolean enables callers to
        guarantee that this function registers the passed tuple rather than a
        new tuple internally created by this function.

    Returns
    ----------
    str
        Python expression evaluating to this tuple when accessed via the
        private ``__beartypistry`` parameter implicitly passed to all wrapper
        functions generated by the :func:`beartype.beartype` decorator.

    Raises
    ----------
    _BeartypeDecorBeartypistryException
        If this tuple is either:

        * *Not* a tuple.
        * Is a tuple containing one or more items that are either:

          * *Not* types.
          * **PEP-compliant types** (i.e., either classes defined by the
            :mod:`typing` module *or* subclasses of such classes and thus
            PEP-compliant type hints, which all violate standard type semantics
            and thus require PEP-specific handling).

    See Also
    ----------
    :func:`register_typistry_tuple_from_frozenset`
        Further details.
    '''
    assert is_types_unique.__class__ is bool, (
        '{!r} not boolean.'.format(is_types_unique))

    # If this object is *NOT* a tuple, raise an exception.
    if not isinstance(hint, tuple):
        raise _BeartypeDecorBeartypistryException(
            'Beartypistry tuple {!r} not a tuple.'.format(hint))
    # Else, this object is a tuple.
    #
    # Note that we defer all further validation of this tuple and its contents
    # to the Beartypistry.__setitem__() method, implicitly invoked on
    # subsequently assigning a "bear_typistry" key-value pair.

    # If this tuple only contains one type, register only this type.
    if len(hint) == 1:
        return register_typistry_type(hint[0])
    # Else, this tuple either contains no types or two or more types.

    # If the caller failed to guarantee this tuple to be duplicate-free...
    if not is_types_unique:
        # Coerce this tuple into a set (thus ignoring duplicates and ordering).
        hint_set = set(hint)

        # Coerce this set back into a duplicate-free tuple, replacing the
        # passed tuple with this tuple.
        hint = tuple(hint_set)
    # This tuple is now guaranteed to be duplicate-free.

    # Name uniquely identifying this tuple as a beartypistry key.
    hint_name = _TYPISTRY_HINT_NAME_TUPLE_PREFIX + str(hash(hint))

    #FIXME: *WOOPS.* Memoization doesn't help us much here, as we need to
    #explicitly test for differing tuple objects that have the same items.
    #FIXME: *UNIT TEST* this up, please.

    # While this name collides with an existing name of a tuple previously
    # registered with the beartypistry singleton, iteratively disambiguate this
    # name by appending an arbitrary character to this name.
    #
    # Note that, if this name *DOES* collide with one or more existing names of
    # tuples previously registered with the beartypistry singleton, the passed
    # tuple is guaranteed to *NOT* be those tuples. Why? Because this function
    # is memoized, the passed tuple is necessarily distinct from those passed
    # to all prior calls of this function and thus requires registration.
    while hint_name in bear_typistry:
        hint_name += '~'

    # Register this tuple with the beartypistry singleton.
    bear_typistry[hint_name] = hint

    # Return a Python expression evaluating to this tuple.
    return (
        _CODE_TYPISTRY_HINT_NAME_TO_HINT_PREFIX + repr(hint_name) +
        _CODE_TYPISTRY_HINT_NAME_TO_HINT_SUFFIX
    )

# ....................{ CLASSES                           }....................
class Beartypistry(dict):
    '''
    **Beartypistry** (i.e., singleton dictionary mapping from strings uniquely
    identifying PEP-noncompliant type hints annotating callables decorated
    by the :func:`beartype.beartype` decorator to those hints).**

    This dictionary implements a global registry for **PEP-noncompliant type
    hints** (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs), including:

    * Non-:mod:`typing` types (i.e., classes *not* defined by the :mod:`typing`
      module, which are PEP-compliant type hints that fail to comply with
      standard type semantics and are thus beyond the limited scope of this
      PEP-noncompliant-specific dictionary).
    * Tuples of non-:mod:`typing` types, commonly referred to as **tuple
      unions** in :mod:`beartype` jargon.

    This dictionary efficiently shares these hints across all type-checking
    wrapper functions generated by this decorator, enabling these functions to:

    * Obtain type and tuple objects at wrapper runtime given only the strings
      uniquely identifying those objects hard-coded into the bodies of those
      wrappers at decoration time.
    * Resolve **forward references** (i.e., type hints whose values are strings
      uniquely identifying type and tuple objects) at wrapper runtime, which
      this dictionary supports by defining a :meth:`__missing__` dunder method
      dynamically adding a new mapping from each such reference to the
      corresponding object on the first attempt to access that reference.
    '''

    # ..................{ DUNDERS                           }..................
    def __setitem__(self, hint_name: str, hint: object) -> None:
        '''
        Dunder method explicitly called by the superclass on setting the passed
        key-value pair with``[``- and ``]``-delimited syntax, mapping the
        passed string uniquely identifying the passed PEP-noncompliant type
        hint to that hint.

        Parameters
        ----------
        hint_name: str : str
            String uniquely identifying this hint in a manner dependent on the
            type of this hint. Specifically, if this hint is:

            * A non-:mod:`typing` type, this is the fully-qualified classname
              of the module attribute defining this type.
            * A tuple of non-:mod:`typing` types, this is a string:

              * Prefixed by the :data:`_TYPISTRY_HINT_NAME_TUPLE_PREFIX`
                substring distinguishing this string from fully-qualified
                classnames.
              * Hash of these types (ignoring duplicate types and type order in
                this tuple).

        Raises
        ----------
        TypeError
            If this hint is **unhashable** (i.e., *not* hashable by the builtin
            :func:`hash` function and thus unusable in hash-based containers
            like dictionaries and sets). All supported type hints are hashable.
        _BeartypeDecorBeartypistryException
            If either:

            * This name is either:

              * *Not* a string.
              * Is an existing string key of this dictionary, implying this
                name has already been registered, implying a key collision
                between the type or tuple already registered under this key and
                this passed type or tuple to be reregistered under this key.
                Since the high-level :func:`register_typistry_type` and
                :func:`register_typistry_tuple` functions implicitly calling
                this low-level dunder method are memoized *and* since the
                latter function explicitly avoids key collisions by detecting
                and uniquifying colliding keys, every call to this method
                should be passed a unique key.

            * This hint is either:

              * A type but either:

                * This name is *not* the fully-qualified classname of this
                  type.
                * This type is **PEP-compliant** (i.e., either a class defined
                  by the :mod:`typing` module *or* subclass of such a class and
                  thus a PEP-compliant type hint, which all violate standard
                  type semantics and thus require PEP-specific handling).

              * A tuple but either:

                * This name is *not* prefixed by the magic substring
                  :data:`_TYPISTRY_HINT_NAME_TUPLE_PREFIX`.
                * This tuple contains one or more items that are either:

                  * *Not* types.
                  * PEP-compliant types.
        '''

        # If this name is *NOT* a string, raise an exception.
        if hint_name.__class__ is not str:
            raise _BeartypeDecorBeartypistryException(
                'Beartypistry key {!r} not string.'.format(hint_name))
        # Else, this name is a string.
        #
        # If this name is an existing key of this dictionary, this name has
        # already been registered, implying a key collision between the type or
        # tuple already registered under this key and the passed type or
        # tuple to be reregistered under this key. In this case, raise an
        # exception.
        elif hint_name in self:
            raise _BeartypeDecorBeartypistryException(
                'Beartypistry key "{}" already registered (i.e., '
                'key collision between '
                'prior registered value {!r} and '
                'to-be registered value {!r}).'.format(
                    hint_name, self[hint_name], hint))

        # If this hint is *NOT* PEP-noncompliant, raise an exception.
        die_unless_hint_nonpep(
            hint=hint,

            #FIXME: Refactor to leverage f-strings after dropping Python 3.5
            #support, which are the optimal means of performing string
            #formatting.
            hint_label='Beartypistry value ' + repr(hint),

            #FIXME: Actually, we eventually want to permit this to enable
            #trivial resolution of forward references. For now, this is fine.
            is_str_valid=False,

            # Raise a decoration- rather than call-specific exception, as this
            # setter should *ONLY* be called at decoration time (e.g., by
            # registration functions defined above).
            exception_cls=_BeartypeDecorBeartypistryException,
        )

        # If this hint is a type...
        if isinstance(hint, type):
            # Fully-qualified classname of this type as declared by this type.
            hint_clsname = get_object_name_qualified(hint)

            # If...
            if (
                # The passed name is not this classname *AND*...
                hint_name != hint_clsname and
                # This classname does not imply this type to be a builtin...
                #
                # Note that builtin types are registered under their
                # unqualified basenames (e.g., "list" rather than
                # "builtins.list") for runtime efficiency, a core optimization
                # requiring manual whitelisting here.
                not hint_clsname.startswith(MODULE_NAME_BUILTINS + '.')
            # Then raise an exception.
            ):
                raise _BeartypeDecorBeartypistryException(
                    'Beartypistry key "{}" not '
                    'fully-qualified classname "{}" of type {!r}.'.format(
                        hint_name, hint_clsname, hint))
        # Else if this hint is a tuple...
        elif hint.__class__ is tuple:
            # If this tuple's name is *NOT* prefixed by a magic substring
            # uniquely identifying this hint as a tuple, raise an exception.
            #
            # Ideally, this block would strictly validate this name to be the
            # concatenation of this prefix followed by this tuple's hash.
            # Sadly, Python fails to cache tuple hashes (for largely spurious
            # reasons, like usual):
            #     https://bugs.python.org/issue9685
            #
            # Potentially introducing a performance bottleneck for mostly
            # redundant validation is a bad premise, given that we mostly
            # trust callers to call the higher-level
            # :func:`register_typistry_tuple` function instead, which already
            # guarantees this constraint to be the case.
            if not hint_name.startswith(_TYPISTRY_HINT_NAME_TUPLE_PREFIX):
                raise _BeartypeDecorBeartypistryException(
                    'Beartypistry key "{}" not '
                    'prefixed by "{}" for tuple {!r}.'.format(
                        hint_name, _TYPISTRY_HINT_NAME_TUPLE_PREFIX, hint))
        # Else, something has gone terribly awry. Raise us up the exception!
        else:
            raise _BeartypeDecorBeartypistryException(
                'Beartypistry key "{}" value {!r} invalid '
                '(i.e., neither type nor tuple).'.format(hint_name, hint))

        # Cache this object under this name.
        super().__setitem__(hint_name, hint)


    #FIXME: Uncomment when implementing forward referencing support.
    # def __missing__(self, hint_name: str) -> type:
    #     '''
    #     Dunder method explicitly called by the superclass
    #     :meth:`dict.__getitem__` method implicitly called on getting the passed
    #     missing key with ``[``- and ``]``-delimited syntax.
    #
    #     This method treats this attempt to get this missing key as the
    #     intentional resolution of a forward reference whose fully-qualified
    #     classname is this key. Specifically, this method:
    #
    #     #.
    #
    #     Parameters
    #     ----------
    #     hint_name : str
    #         **Name** (i.e., fully-qualified name of the module attribute
    #         declaring this hint) of this hint to be resolved as a forward
    #         reference.
    #
    #     Returns
    #     ----------
    #     object
    #         :mod:`beartype`-supported type hint whose fully-qualified module
    #         attribute name is this missing key.
    #
    #     Raises
    #     ----------
    #     _BeartypeDecorBeartypistryException
    #         If this name is either:
    #
    #         * *Not* a fully-qualified classname.
    #         * A fully-qualified classname but the object to which this name
    #           refers is *not* a **PEP-noncompliant class** (i.e., class neither
    #           defined by the :mod:`typing` module *nor* subclassing a class
    #           defined by the :mod:`typing` module).
    #     '''
    #
    #     # If this name is *NOT* a string, raise an exception.
    #     if not isinstance(hint_name, str):
    #         raise _BeartypeDecorBeartypistryException(
    #             'Beartypistry key {!r} not a '
    #             'fully-qualified module attribute name.'.format(hint_name))
    #
    #     #FIXME: Dynamically import this object here.
    #     # Type hint dynamically imported from this name.
    #     hint = None
    #
    #     # If this hint is *NOT* a valid PEP-noncompliant type hint, raise an
    #     # exception.
    #     die_unless_hint_nonpep(
    #         hint=hint,
    #         hint_label='Beartypistry value {!r}'.format(hint),
    #         is_str_valid=False,
    #         exception_cls=_BeartypeCallBeartypistryException,
    #     )
    #
    #     # Return this hint.
    #     #
    #     # The superclass dict.__getitem__() dunder method then implicitly maps
    #     # the passed missing key to this class by effectively:
    #     #     self[hint_name] = hint
    #     return hint

# ....................{ SINGLETONS                        }....................
bear_typistry = Beartypistry()
'''
**Beartypistry** (i.e., singleton dictionary mapping from the fully-qualified
classnames of all type hints annotating callables decorated by the
:func:`beartype.beartype` decorator to those types).**

See Also
----------
:class:`Beartypistry`
    Further details.
'''
