#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **hint sign logic class hierarchy** (i.e., dataclasses encapsulating
all low-level Python code snippets and associated metadata required to
dynamically generate high-level Python code snippets fully type-checking various
kinds of type hints uniquely identified by common signs).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.datahinttyping import CallableStrFormat
from beartype.typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUPERCLASSES                       }....................
class HintSignLogicABC(object):
    '''
    **Hint sign logic** (i.e., dataclass encapsulating all low-level Python code
    snippets and associated metadata required to dynamically generate a
    high-level Python code snippet fully type-checking some kind of type hint
    uniquely identified by a common sign) superclass.

    Caveats
    -------
    **Python code snippets should not contain ternary conditionals.** For
    unknown reasons suggesting a critical defect in the current implementation
    of Python 3.8's assignment expressions, snippets containing one or more
    ternary conditionals raise :exc:`UnboundLocalError` exceptions resembling:

        UnboundLocalError: local variable '__beartype_pith_1' referenced before
        assignment

    In particular, the initial draft of these snippets guarded against empty
    sequences with a seemingly reasonable ternary conditional:

    .. code-block:: python

       CODE_PEP484585_SEQUENCE_ARGS_1 = \'\'\'(
       {indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
       {indent_curr}    {hint_child_placeholder} if {pith_curr_var_name} else True
       {indent_curr})\'\'\'

    That should behave as expected, but doesn't, presumably due to obscure
    scoping rules and a non-intuitive implementation of ternary conditionals in
    CPython. Ergo, the current version of this snippet guards against empty
    sequences with disjunctions and conjunctions (i.e., ``or`` and ``and``
    operators) instead. Happily, the current version is more efficient than the
    equivalent approach based on ternary conditional (albeit less intuitive).

    Attributes
    ----------
    code_format : CallableStrFormat
        :meth:`str.format` method bound to a Python code snippet fully
        type-checking the current pith against this kind of type hint. This
        snippet is expected to contain exactly these format variables:

        * ``{indent_curr}``, expanding to the current indentation.
        * ``{pith_curr_assign_expr}``, expanding to an assignment expression
          efficiently yielding the current pith.
        * ``{hint_curr_expr}``, expanding to an arbitrary expression usually
          inefficiently yielding the current pith.
        * ``{pith_curr_var_name}``, expanding to the name of the local variable
          whose value is the current pith.
        * ``{hint_child_placeholder}``, expanding to a Python code snippet
          efficiently type-checking some item of the current pith.
    is_var_random_int_needed : bool
        :data:`True` only if the Python code snippet dynamically generated by
        calling the :attr:`code_format` method requires a pseudo-random integer
        by accessing the :data:`VAR_NAME_RANDOM_INT` local. If :data:`True`, the
        body of the current wrapper function will be prefixed by a Python
        statement assigning such an integer to this local.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'code_format',
        'is_var_random_int_needed',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        code_format : CallableStrFormat
        is_var_random_int_needed : bool

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        code_format: CallableStrFormat,

        # Optional parameters.
        is_var_random_int_needed: bool = False,
    ) -> None:
        '''
        Initialize this hint sign logic.

        Parameters
        ----------
        See the class docstring for further details.
        '''

        # Classify all passed parameters.
        self.code_format = code_format
        self.is_var_random_int_needed = is_var_random_int_needed

# ....................{ SUBCLASSES                         }....................
class HintSignLogicContainerArgs1(HintSignLogicABC):
    '''
    **Single-argument container hint sign logic** (i.e., dataclass encapsulating
    all low-level Python code snippets and associated metadata required to
    dynamically generate a high-level Python code snippet fully type-checking
    some kind of :pep:`484`- and :pep:`585`-compliant container type hint
    uniquely identified by a common sign, satisfying at least the
    :class:`collections.abc.Container` protocol subscripted by exactly one child
    type hint constraining *all* items contained in that container) subclass.

    Attributes
    ----------
    pith_child_expr_format : CallableStrFormat
        :meth:`str.format` method bound to a Python expression efficiently
        yielding the value of the next item (which will then be type-checked)
        contained in the **current pith** (which is the parent container
        currently being type-checked). This snippet is expected to contain
        exactly these format variables:

        * ``{pith_curr_var_name}``, expanding to the name of the local variable
          whose value is the current pith.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'pith_child_expr_format',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        pith_child_expr_format : CallableStrFormat

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Optional parameters.
        #
        # For convenience, permit callers to avoid having to initially define
        # all possible parameters all-at-once by defaulting all parameters to
        # *REASONABLY* sane defaults.
        pith_child_expr_format: Optional[CallableStrFormat] = None,
        **kwargs
    ) -> None:
        '''
        Initialize this hint sign logic.

        Parameters
        ----------
        All passed keyword parameters are passed as is to the superclass
        :meth:`HintSignLogicABC.__init__` method.

        See the class docstring for further details.
        '''

        # PEP 484- and 585-compliant code snippet generically type-checking the
        # current pith against *any* arbitrary kind of single-argument standard
        # container type hint.
        _CODE_PEP484585_CONTAINER_ARGS_1 = '''(
{indent_curr}    # True only if this pith is of this container type *AND*...
{indent_curr}    isinstance({pith_curr_assign_expr}, {hint_curr_expr}) and
{indent_curr}    # True only if either this container is empty *OR* this container
{indent_curr}    # is both non-empty and the first item satisfies this hint.
{indent_curr}    (not {pith_curr_var_name} or {hint_child_placeholder})
{indent_curr})'''

        # Initialize our superclass.
        super().__init__(
            code_format=_CODE_PEP484585_CONTAINER_ARGS_1.format, **kwargs)

        # Classify all passed parameters.
        self.pith_child_expr_format = pith_child_expr_format  # type: ignore[assignment]


class HintSignLogicReiterableArgs1(HintSignLogicContainerArgs1):
    '''
    **Single-argument reiterable hint sign logic** (i.e., dataclass encapsulating
    all low-level Python code snippets and associated metadata required to
    dynamically generate a high-level Python code snippet fully type-checking
    some kind of :pep:`484`- and :pep:`585`-compliant reiterable type hint
    uniquely identified by a common sign, satisfying at least the
    :class:`collections.abc.Collection` protocol subscripted by exactly one
    child type hint constraining *all* items contained in that reiterable)
    subclass.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this hint sign logic.
        '''

        # PEP 484- and 585-compliant Python expression yielding the first item of
        # the current reiterable pith.
        _CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR = (
            '''next(iter({pith_curr_var_name}))''')

        # Initialize our superclass.
        super().__init__(
            pith_child_expr_format=(
                _CODE_PEP484585_REITERABLE_ARGS_1_PITH_CHILD_EXPR.format),
        )


class HintSignLogicSequenceArgs1(HintSignLogicContainerArgs1):
    '''
    **Single-argument sequence hint sign logic** (i.e., dataclass encapsulating
    all low-level Python code snippets and associated metadata required to
    dynamically generate a high-level Python code snippet fully type-checking
    some kind of :pep:`484`- and :pep:`585`-compliant sequence type hint
    uniquely identified by a common sign, satisfying at least the
    :class:`collections.abc.Sequence` protocol subscripted by exactly one child
    type hint constraining *all* items contained in that sequence) subclass.
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this hint sign logic.
        '''

        # Defer method-specific imports.
        from beartype._check.checkmagic import VAR_NAME_RANDOM_INT

        # PEP 484- and 585-compliant Python expression yielding a randomly indexed
        # item of the current sequence pith.
        _CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR = (
            f'''{{pith_curr_var_name}}[{VAR_NAME_RANDOM_INT} % len({{pith_curr_var_name}})]''')

        # Initialize our superclass.
        super().__init__(
            # Code snippets dynamically generated by this logic require
            # pseudo-random integers to type-check random sequence items.
            is_var_random_int_needed=True,
            pith_child_expr_format=(
                _CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR.format),
        )
