#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Optimize away the call to the inspect.signature() function by
#reimplementing this function to assign to instance variables of the current
#"BeartypeData" object rather than instantiating a new "Signature" object and
#then one new "Parameter" object for each parameter of the decorated callable.
#Note, for example, that we don't need to replicate that function's copying of
#parameter and return value annotations already trivially accessible via the
#"self.func.__annotations__" dunder attribute. Indeed, we only require these
#new "BeartypeData" instance variables:
#
#* "func_param_names", a tuple of all parameter names.
#* "func_param_name_to_kind", a dictionary mapping from each parameter name
#  (including the 'return' pseudo-parameter signifying the return value) to
#  that parameter's kind (e.g., keyword-only, variadic positional). Naturally,
#  parameter kinds should probably be defined as enumeration members of a
#  global public "Enum" class defined in this submodule and accessed elsewhere.
#
#Doing so will be non-trivial but entirely feasible and absolutely worthwhile,
#as the inspect.signature() function is *GUARANTEED* to be a performance
#bottleneck for us. This is low-priority for the moment and may actually never
#happen... but it really should.

# ....................{ IMPORTS                           }....................
import inspect
from beartype.cave import CallableTypes
from beartype._util.text.utiltextlabel import label_callable_decorated

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
class BeartypeData(object):
    '''
    **Beartype data** (i.e., object aggregating *all* metadata for the callable
    currently being decorated by the :func:`beartype.beartype` decorator).**

    Design
    ----------
    This the *only* object instantiated by that decorator for that callable,
    substantially reducing both space and time costs. That decorator then
    passes this object to most lower-level functions, which then:

    #. Access read-only instance variables of this object as input.
    #. Modify writable instance variables of this object as output. In
       particular, these lower-level functions typically accumulate pure-Python
       code comprising the generated wrapper function type-checking the
       decorated callable by setting various instance variables of this object.

    Attributes
    ----------
    func : CallableTypes
        **Decorated callable** (i.e., callable currently being decorated by the
        :func:`beartype.beartype` decorator).

    Attributes (List)
    ----------
    list_a : list
        Thread-safe list of arbitrary items. Callers may use this list for any
        purpose but should explicitly clear this list of all prior items by
        calling the :meth:`list.clear` method *before* each such use. This and
        the related :attr:`list_b` instance variable prevent callers from
        having to repeatedly reinstantiate lists during performance-critical
        iteration, a trivial but essential optimization.
    list_b : list
        Thread-safe list of arbitrary items distinct from :attr:`list_a` for
        external filtering purposes (e.g., :mod:`typing` types from standard
        types in PEP-compliant codepaths).

    Attributes (String)
    ----------
    func_wrapper_name : str
        Machine-readable name of the wrapper function to be generated and
        returned by this decorator. To efficiently (albeit imperfectly) avoid
        clashes with existing attributes of the module defining that function,
        this name is obfuscated while still preserving human-readability.

    Attributes (Object)
    ----------
    func_sig : inspect.Signature
        :class:`inspect.Signature` object describing this signature.

    Attributes (Private: Integer)
    ----------
    _pep_hint_placeholder_id : int
        Integer uniquely identifying the currently iterated child PEP-compliant
        type hint of the currently visited parent PEP-compliant type hint. This
        integer is internally leveraged by the
        :meth:`get_next_pep_hint_child_str` method, externally called when
        generating code type-checking PEP-compliant type hints.

    .. _PEP 563:
        https://www.python.org/dev/peps/pep-0563
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot *ALL* instance variables defined on this object to minimize space
    # and time complexity across frequently called @beartype decorations.
    __slots__ = (
        'func',
        'func_sig',
        'func_wrapper_name',
        'list_a',
        'list_b',
        '_pep_hint_placeholder_id',
    )

    # ..................{ INITIALIZERS                      }..................
    def __init__(self) -> None:
        '''
        Initialize this metadata by nullifying all instance variables.

        Caveats
        ----------
        **This class is not intended to be explicitly instantiated.** Instead,
        callers are expected to (in order):

        #. Acquire cached instances of this class via the
           :mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
        #. Call the :meth:`reinit` method on these instances to properly
           initialize these instances.
        '''

        # Initialize these lists to the empty lists. Since we guarantee these
        # lists to *ALWAYS* exist, instantiate them once here rather than
        # repeatedly in the reinit() method below.
        self.list_a = list()
        self.list_b = list()

        # Nullify all remaining instance variables.
        self.func = None
        self.func_sig = None
        self.func_wrapper_name = None
        self._pep_hint_placeholder_id = None


    def reinit(self, func: CallableTypes) -> None:
        '''
        Reinitialize this metadata from the passed callable, typically after
        acquisition of a previously cached instance of this class from the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.

        If `PEP 563`_ is conditionally active for this callable, this function
        additionally resolves all postponed annotations on this callable to
        their referents (i.e., the intended annotations to which those
        postponed annotations refer).

        Parameters
        ----------
        func : CallableTypes
            Callable currently being decorated by :func:`beartype.beartype`.

        Raises
        ----------
        BeartypeDecorPep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).

        .. _PEP 563:
           https://www.python.org/dev/peps/pep-0563
        '''
        assert callable(func), '{!r} uncallable.'.format(func)

        # Avoid circular import dependencies.
        from beartype._decor._pep563 import resolve_hints_postponed_if_needed

        # Callable currently being decorated.
        self.func = func

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = '__beartyped_' + func.__name__

        # Integer identifying the currently iterated child PEP-compliant type
        # hint of the currently visited parent PEP-compliant type hint.
        #
        # Note this ID is intentionally initialized to -1 rather than 0. Since
        # the get_next_pep_hint_child_str() method increments *BEFORE*
        # stringifying this ID, initializing this ID to -1 ensures that method
        # returns a string containing only non-negative substrings starting at
        # 0 rather than both negative and positive substrings starting at -1.
        self._pep_hint_placeholder_id = -1

        # Nullify all remaining attributes for safety *BEFORE* passing this
        # object to any functions (e.g., resolve_hints_postponed_if_needed()).
        self.func_sig = None

        # Resolve all postponed annotations if any on this callable *BEFORE*
        # parsing the actual annotations these postponed annotations refer to.
        resolve_hints_postponed_if_needed(self)

        # "Signature" instance encapsulating this callable's signature,
        # dynamically parsed by the stdlib "inspect" module from this callable.
        self.func_sig = inspect.signature(func)

    # ..................{ PROPERTIES ~ read-only            }..................
    @property
    def func_name(self) -> str:
        '''
        Human-readable name of this callable.

        This attribute is only accessed when raising exceptions (where
        efficiency is entirely ignorable) and thus intentionally declared as a
        read-only property rather than an instance variable.
        '''

        return label_callable_decorated(self.func)

    # ..................{ GETTERS                           }..................
    def get_next_pep_hint_placeholder_str(self) -> str:
        '''
        **Next placeholder hint type-checking substring** (i.e., placeholder to
        be globally replaced by a Python code snippet type-checking the current
        pith expression against the currently iterated child hint of the
        currently visited parent hint).

        This method should only be called exactly once on each hint, typically
        by the currently visited parent hint on iterating each child hint of
        that parent hint.

        This method is intentionally declared as a getter method rather than
        read-only property to emphasize that this method both returns a unique
        string on each invocation *and* mutates internal object state.
        '''

        # Increment the unique identifier of the currently iterated child hint.
        self._pep_hint_placeholder_id += 1

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Generate a unique placeholder type-checking substring, intentionally
        # prefixed and suffixed by characters that:
        #
        # * Are intentionally invalid as Python code, guaranteeing that the
        #   top-level call to the exec() builtin performed by the @beartype
        #   decorator will raise a "SyntaxError" exception if the caller fails
        #   to replace all placeholder substrings generated by this method.
        # * Protect the identifier embedded in this substring against ambiguous
        #   global replacements of larger identifiers containing this
        #   identifier. If this identifier were *NOT* protected in this manner,
        #   then the first substring "0" generated by this method would
        #   ambiguously overlap with the subsequent substring "10" generated by
        #   this method, which would then produce catastrophically erroneous
        #   and non-trivial to debug Python code.
        return '@[' + str(self._pep_hint_placeholder_id) + '}!'
