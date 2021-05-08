#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable-based validation classes** (i.e., :mod:`beartype`-specific
classes enabling callers to define PEP-compliant validators from arbitrary
caller-defined callables *not* efficiently generating stack-free code).

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeValeSubscriptionException,
    BeartypeValeLambdaWarning,
)
from beartype.vale._valeisabc import _IsABC
from beartype._vale._valesub import (
    _SubscriptedIs,
    SubscriptedIsValidator,
)
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
from beartype._util.text.utiltextrepr import (
    represent_object,
    represent_func,
)
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ subscriptable           }....................
class Is(_IsABC):
    '''
    **Beartype callable validator factory** (i.e., class that, when subscripted
    (indexed) by an arbitrary callable returning ``True`` when the object
    passed to that callable satisfies a caller-defined constraint, creates a
    new :class:`_SubscriptedIs` object encapsulating that callable suitable for
    subscripting (indexing) :attr:`typing.Annotated` type hints, enforcing that
    constraint on :mod:`beartype`-decorated callable parameters and returns
    annotated by those hints).

    This class validates that callable parameters and returns satisfy the
    arbitrary **callable validator** (i.e., callable whose signature satisfies
    ``collections.abc.Callable[[typing.Any], bool]``) subscripting (indexing)
    this class. Callable validators are caller-defined and may thus validate
    the internal integrity, consistency, and structure of arbitrary objects
    ranging from simple builtin scalars like integers and strings to complex
    data structures defined by third-party packages like NumPy arrays and
    Pandas DataFrames.

    This class creates one new :class:`_SubscriptedIs` object for each callable
    validator subscripting (indexing) this class. These objects:

    * Are **PEP-compliant** and thus guaranteed to *never* violate existing or
      future standards.
    * Are **Safely ignorable** by *all* static and runtime type checkers other
      than :mod:`beartype` itself.
    * **Less efficient** than :class:`_SubscriptedIs` objects created by
      subscripting every other :mod:`beartype.vale` class. Specifically:

      * Every :class:`_SubscriptedIs` object created by subscripting this class
        necessarily calls a callable validator and thus incurs at least one
        additional call stack frame per :mod:`beartype`-decorated callable
        call.
      * Every :class:`_SubscriptedIs` object created by subscripting every
        other :mod:`beartype.vale` class directly calls *no* callable and thus
        incurs additional call stack frames only when the active Python
        interpreter internally calls dunder methods (e.g., ``__eq__()``) to
        satisfy their validation constraint.

    Usage
    ----------
    Any :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted (indexed) by this class
    subscripted (indexed) by a callable validator (e.g.,
    ``typing.Annotated[{cls}, beartype.vale.Is[lambda obj: {expr}]]`` for any
    class ``{cls}``  and Python expression ``{expr}` evaluating to a boolean)
    validates that parameter or return value to be an instance of that class
    satisfying that callable validator.

    Specifically, callers are expected to (in order):

    #. Annotate a callable parameter or return to be validated with a `PEP
       593`_-compliant :attr:`typing.Annotated` type hint.
    #. Subscript that hint with (in order):

       #. The type expected by that parameter or return.
       #. One or more subscriptions (indexations) of this class, each itself
          subscripted (indexed) by a **callable validator** (i.e., callable
          accepting a single arbitrary object and returning either ``True`` if
          that object satisfies an arbitrary constraint *or* ``False``
          otherwise). If that hint is subscripted by:

          * Only one subscription of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * That validator returns ``True`` when passed that parameter or
              return.

          * Two or more subscriptions of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * *All* callable validators subscripting *all* subscriptions of
              this class return ``True`` when passed that parameter or return.

          Formally, the signature of each callable validator *must* resemble:

          .. code-block:: python

             def is_object_valid(obj) -> bool:
                 return bool(obj)

          Equivalently, each callable validator *must* satisfy the type hint
          ``collections.abc.Callable[[typing.Any,], bool]``. If not the case,
          an exception is raised. Note that:

          * If that parameter or return is *not* an instance of the expected
            type, **no callable validator is called.** Equivalently, each
            callable validator is called *only* when that parameter or return
            is already an instance of the expected type. Callable validators
            need *not* revalidate that type (e.g., by passing that parameter or
            return and type to the :func:`isinstance` builtin).
          * The name of each callable validator is irrelevant. For convenience,
            most callable validators are defined as nameless lambda functions.

    For example, the following type hint only accepts non-empty strings:

    .. code-block:: python

       Annotated[str, Is[lambda text: bool(text)]]

    :class:`_SubscriptedIs` objects also support an expressive domain-specific
    language (DSL) enabling callers to trivially synthesize new objects from
    existing objects with standard Pythonic math operators:

    * **Negation** (i.e., ``not``). Negating an :class:`_SubscriptedIs` object
      with the ``~`` operator synthesizes a new :class:`_SubscriptedIs` object
      whose validator returns ``True`` only when the validator of the original
      object returns ``False``. For example, the following type hint only
      accepts strings containing *no* periods:

      .. code-block:: python

         Annotated[str, ~Is[lambda text: '.' in text]]

    * **Conjunction** (i.e., ``and``). Conjunctively combining two or more
      :class:`_SubscriptedIs` objects with the ``&`` operator synthesizes a new
      :class:`_SubscriptedIs` object whose validator returns ``True`` only when
      all data validators of the original objects return ``True``. For example,
      the following type hint only accepts non-empty strings containing *no*
      periods:

      .. code-block:: python

         Annotated[str, (
              Is[lambda text: bool(text)] &
             ~Is[lambda text: '.' in text]
         )]

    * **Disjunction** (i.e., ``or``). Disjunctively combining two or more
      :class:`_SubscriptedIs` objects with the ``|`` operator synthesizes a new
      :class:`_SubscriptedIs` object whose validator returns ``True`` only
      when at least one validator of the original objects returns ``True``. For
      example, the following type hint accepts both empty strings *and*
      non-empty strings containing at least one period:

      .. code-block:: python

         Annotated[str, (
             ~Is[lambda text: bool(text)] |
              Is[lambda text: '.' in text]
         )]

    See also the **Examples** subsection below.

    Caveats
    ----------
    **This class is currently only supported by the** :func:`beartype.beartype`
    **decorator.** All other static and runtime type checkers silently ignore
    subscriptions of this class subscripting :attr:`typing.Annotated` type
    hints.

    **This class incurs a minor time performance penalty at call time.**
    Specifically, each type hint of a :mod:`beartype`-decorated callable
    subscripted by a subscription of this class adds one additional stack frame
    to each call of that callable. While negligible (in the average case), this
    cost can become non-negligible when compounded across multiple type hints
    annotating a frequently called :mod:`beartype`-decorated callable --
    especially when those type hints are subscripted by multiple subscriptions
    of this class at different nesting levels.

    **This class prohibits instantiation.** This class is *only* intended to be
    subscripted. Attempting to instantiate this class into an object will raise
    an :exc:`BeartypeValeSubscriptionException` exception.

    Examples
    ----------
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import Is
       >>> from typing import Annotated

       # Validator matching only strings with lengths ranging [4, 40].
       >>> IsRangy = Is[lambda text: 4 <= len(text) <= 40]

       # Validator matching only unquoted strings.
       >>> IsUnquoted = Is[lambda text:
       ...     text.count('"') < 2 and text.count("'") < 2]

       # Type hint matching only unquoted strings.
       >>> UnquotedString = Annotated[str, IsUnquoted]

       # Type hint matching only quoted strings.
       >>> QuotedString = Annotated[str, ~IsUnquoted]

       # Type hint matching only unquoted strings with lengths ranging [4, 40].
       >>> UnquotedRangyString = Annotated[str, IsUnquoted & IsRangy]

       # Annotate callables by those type hints.
       >>> @beartype
       ... def doublequote_text(text: UnquotedString) -> QuotedString:
       ...     """
       ...     Double-quote the passed unquoted string.
       ...     """
       ...     return f'"{text}"'  # The best things in life are one-liners.
       >>> @beartype
       ... def singlequote_prefix(text: UnquotedRangyString) -> QuotedString:
       ...     """
       ...     Single-quote the prefix spanning characters ``[0, 3]`` of the
       ...     passed unquoted string with length ranging ``[4, 40]``.
       ...     """
       ...     return f"'{text[:3]}'"  # "Guaranteed to work," says @beartype.

       # Call those callables with parameters satisfying those validators.
       >>> doublequote_text("You know anything about nuclear fusion?")
       "You know anything about nuclear fusion?"
       >>> singlequote_prefix("Not now, I'm too tired. Maybe later.")
       'Not'

       # Call those callables with parameters not satisfying those validators.
       >>> doublequote_text('''"Everybody relax, I'm here."''')
       beartype.roar._roarexc.BeartypeCallHintPepParamException: @beartyped
       doublequote_text() parameter text='"Everybody relax, I\'m here."'
       violates type hint typing.Annotated[str, Is[lambda text: text.count('"')
       < 2 and text.count("'") < 2]], as value '"Everybody relax, I\'m here."'
       violates data constraint Is[lambda text: text.count('"') < 2 and
       text.count("'") < 2].

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''

    # ..................{ DUNDERS                           }..................
    def __class_getitem__(
        cls, is_valid: SubscriptedIsValidator) -> _SubscriptedIs:
        '''
        `PEP 560`_-compliant dunder method creating and returning a new
        :class:`_SubscriptedIs` object from the passed **validator callable**
        (i.e., caller-defined callable accepting a single arbitrary object and
        returning either ``True`` if that object satisfies an arbitrary
        constraint *or* ``False`` otherwise), suitable for subscripting `PEP
        593`_-compliant :attr:`typing.Annotated` type hints.

        This method is intentionally *not* memoized, as this method is usually
        subscripted only by subscription-specific lambda functions uniquely
        defined for each subscription of this class.

        Parameters
        ----------
        is_valid : Callable[[Any,], bool]
            Validator callable to validate parameters and returns against.

        Returns
        ----------
        _SubscriptedIs
            New object encapsulating this validator callable.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either:

            * This class was subscripted by two or more arguments.
            * This class was subscripted by one argument that either:

              * Is *not* callable.
              * Is a C-based rather than pure-Python callable.
              * Is a pure-Python callable accepting two or more arguments.

        See Also
        ----------
        :class:`IsAttr`
            Usage instructions.

        .. _PEP 560:
           https://www.python.org/dev/peps/pep-0560
        .. _PEP 593:
           https://www.python.org/dev/peps/pep-0593
        '''

        # If this class was subscripted by either no arguments *OR* two or more
        # arguments, raise an exception.
        die_unless_getitem_args_one(obj=cls, args=is_valid)
        # Else, this class was subscripted by exactly one argument.

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: CallableScope = {}

        # Name of a new parameter added to the signature of each
        # @beartype-decorated wrapper function whose value is this validator,
        # enabling this validator to be called directly in the body of those
        # functions *WITHOUT* imposing additional stack frames.
        is_valid_attr_name = add_func_scope_attr(
            attr=is_valid, attr_scope=is_valid_code_locals)

        # One one-liner to rule them all and in "pdb" bind them.
        return _SubscriptedIs(
            is_valid=is_valid,
            # Python code snippet call this validator via that parameter,
            # passed an object to be interpolated into this snippet by
            # downstream logic.
            is_valid_code=f'{is_valid_attr_name}({{obj}})',
            is_valid_code_locals=is_valid_code_locals,
            get_repr=lambda: (
                f'{cls.__name__}['
                f'{represent_func(func=is_valid, warning_cls=BeartypeValeLambdaWarning)}'
                f']'
            ),
        )

# ....................{ VALIDATORS                        }....................
def die_unless_getitem_args_one(obj: Any, args: Any) -> None:
    '''
    Raise an exception unless the active Python interpreter passed exactly one
    argument to the caller dunder method accepting variadic arguments (e.g.,
    ``__class_getitem__``, ``__getitem__``) of the passed parent object.

    Equivalently, this function raises an exception if this interpreter passed
    either no *or* two or more arguments to that method.

    Parameters
    ----------
    obj : Any
        Parent object whose dunder method was passed these arguments.
    args : Any
        Variadic positional arguments to be inspected.

    Raises
    ----------
    BeartypeValeSubscriptionException
        If the caller dunder method was passed either:

        * No arguments.
        * Two or more arguments.
    '''

    # If this object was subscripted by either no arguments or two or more
    # arguments, raise an exception. Specifically...
    if isinstance(args, tuple):
        # If this object was subscripted by two or more arguments, raise a
        # human-readable exception.
        if args:
            raise BeartypeValeSubscriptionException(
                f'{repr(obj)} subscripted by two or more arguments:\n'
                f'{represent_object(args)}'
            )
        # Else, this object was subscripted by *NO* arguments. In this case,
        # raise a human-readable exception.
        else:
            raise BeartypeValeSubscriptionException(
                f'{repr(obj)} subscripted by empty tuple.')
    # Else, this object was subscripted by exactly one argument.
