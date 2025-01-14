#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural type
hint inference API** unit tests.

This submodule unit tests the public :mod:`beartype.door.infer_hint` function.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS ~ inferers                   }....................
def test_door_infer_hint(
    door_cases_infer_hint: 'Iterable[Tuple[object, object]]') -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function.

    Parameters
    ----------
    door_cases_infer_hint : Iterable[Tuple[object, object]]
        Iterable of **type hint inference cases** (i.e., 2-tuples ``(obj,
        hint)`` describing the type hint matching an arbitrary object).
    '''

    # Defer test-specific imports.
    from beartype.door import infer_hint

    # For each type hint inference case to be tested...
    for obj, hint in door_cases_infer_hint:
        # Assert this function returns the expected type hint for this object.
        assert infer_hint(obj) == hint


def test_door_infer_hint_numpy(
    door_cases_infer_hint: 'Iterable[Tuple[object, object]]',
    numpy_arrays: 'beartype_test.a00_unit.data.api.data_apinumpy._NumpyArrays',
) -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function with respect to
    third-party :mod:`numpy` arrays if :mod:`numpy` is importable *or* silently
    skip this test otherwise (i.e., if :mod:`numpy` is unimportable).

    Parameters
    ----------
    door_cases_infer_hint : Iterable[Tuple[object, object]]
        Iterable of **type hint inference cases** (i.e., 2-tuples ``(obj,
        hint)`` describing the type hint matching an arbitrary object).
    numpy_arrays : beartype_test.a00_unit.data.api.data_apinumpy._NumpyArrays
        **NumPy arrays dataclass** (i.e., well-typed and -described object
        comprising various :mod:`numpy` arrays).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import infer_hint
    from beartype.vale import (
        IsAttr,
        IsEqual,
    )
    from beartype._util.api.utilapityping import import_typing_attr_or_none
    from numpy import unsignedinteger
    from numpy.typing import NDArray

    # ....................{ LOCALS                         }....................
    # PEP 593-compliant "Annotated" type hint factory imported from either the
    # standard "typing" or third-party "typing_extensions" modules if importable
    # from at least one of those modules *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none('Annotated')

    # List of all NumPy type hint inference cases (i.e., 2-tuples "(obj, hint)"
    # describing the type hint matching a NumPy array).
    INFER_HINT_NUMPY_CASES = [
        # ..................{ NUMPY                          }..................
        # One-dimensional NumPy boolean arrays are annotated as either...
        (numpy_arrays.array_1d_boolean, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "bool" type annotated to require a one-dimensional array.
            Annotated[NDArray[bool], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[bool]
        )),
        # One-dimensional NumPy complex arrays are annotated as either...
        (numpy_arrays.array_1d_complex_128, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "complex" type annotated to require a one-dimensional
            # array.
            Annotated[NDArray[complex], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[complex]
        )),
        # One-dimensional NumPy 32-bit floating point arrays are annotated as
        # either...
        (numpy_arrays.array_1d_float_32, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "float" type annotated to require a one-dimensional array.
            Annotated[NDArray[float], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[float]
        )),
        # One-dimensional NumPy 64-bit floating point arrays are annotated as
        # either...
        (numpy_arrays.array_1d_float_64, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "float" type annotated to require a one-dimensional array.
            Annotated[NDArray[float], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[float]
        )),
        # One-dimensional NumPy 32-bit integer arrays are annotated as either...
        (numpy_arrays.array_1d_int_32, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "int" type annotated to require a one-dimensional array.
            Annotated[NDArray[int], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[int]
        )),
        # One-dimensional NumPy 64-bit integer arrays are annotated as either...
        (numpy_arrays.array_1d_int_64, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "int" type annotated to require a one-dimensional array.
            Annotated[NDArray[int], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[int]
        )),
        # One-dimensional NumPy 32-bit unsigned integer arrays are annotated as
        # either...
        (numpy_arrays.array_1d_uint_32, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # "numpy.unsignedinteger" dtype annotated to require a
            # one-dimensional array.
            Annotated[NDArray[unsignedinteger], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[unsignedinteger]
        )),
        # One-dimensional NumPy 64-bit unsigned integer arrays are annotated as
        # either...
        (numpy_arrays.array_1d_uint_64, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # "numpy.unsignedinteger" dtype annotated to require a
            # one-dimensional array.
            Annotated[NDArray[unsignedinteger], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[unsignedinteger]
        )),
        # One-dimensional NumPy array serving as a memory view over arbitrary
        # bytes all of the same length are annotated as either...
        (numpy_arrays.array_1d_memory_view, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "memoryview" type annotated to require a one-dimensional
            # array.
            Annotated[NDArray[memoryview], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[memoryview]
        )),
        # One-dimensional NumPy byte string arrays are annotated as either...
        (numpy_arrays.array_1d_string_byte, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "bytes" type annotated to require a one-dimensional array.
            Annotated[NDArray[bytes], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[bytes]
        )),
        # One-dimensional NumPy Unicode string arrays are annotated as either...
        (numpy_arrays.array_1d_string_char, (
            # If "typing(|_extensions).Annotated" is importable, the third-party
            # "numpy.typing.NDArray" type hint factory subscripted by the
            # builtin "str" type annotated to require a one-dimensional array.
            Annotated[NDArray[str], IsAttr['ndim', IsEqual[1]]]
            if Annotated is not None else
            # Else, "typing(|_extensions).Annotated" is unimportable. In this
            # case, merely this subscripted factory.
            NDArray[str]
        )),
    ]

    # ....................{ ASSERTS                        }....................
    # For each type hint inference case to be tested...
    for obj, hint in INFER_HINT_NUMPY_CASES:
        # Assert this function returns the expected type hint for this object.
        assert infer_hint(obj) == hint


@skip_unless_package('pygments')
def test_door_infer_hint_pygments() -> None:
    '''
    Test the :func:`beartype.door.infer_hint` function with respect to
    third-party :mod:`pygments` package if that package is importable *or*
    silently skip this test otherwise (i.e., if that package is unimportable).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import infer_hint
    from beartype._data.hint.pep.sign.datapepsigns import HintSignList
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
    from pygments.lexers import PythonLexer

    # ....................{ LOCALS                         }....................
    # List of all root tokens exposed by the pygments Python lexer, exercising
    # edge cases in the infer_hint() function that continued to break. Ugh!
    root_tokens = PythonLexer().tokens['root']

    # Hint inferred for this list, implicitly exercising that the infer_hint()
    # function successfully infers this hint *WITHOUT* raising an exception --
    # which it used to.
    root_tokens_hint = infer_hint(root_tokens)

    # ....................{ ASSERTS                        }....................
    # Assert that this hint is a subscripted "list[...]" hint.
    #
    # Note that we intentionally do *NOT* assert the specific child hints
    # subscripting this hint. Why? Because these child hints include references
    # to private "pygments" types (e.g., "pygments._token.TokenType") dependent
    # on the current pygments version. For that reason, we intentionally omit
    # this hint from the "door_cases_infer_hint" fixture leveraged above.
    assert get_hint_pep_sign_or_none(root_tokens_hint) is HintSignList
