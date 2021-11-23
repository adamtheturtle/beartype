#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator code generator magic** (i.e., global constants simplifying
code generation but *not* themselves code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.error.utilerror import EXCEPTION_PLACEHOLDER

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
EXCEPTION_PREFIX = f'{EXCEPTION_PLACEHOLDER} '
'''
Human-readable substring unconditionally prefixing *all* exception messages
transitively across this subpackage, which the
:func:`beartype._util.error.utilerror.reraise_exception_placeholder` function
dynamically replaces with the name of both the currently decorated callable
*and* the currently iterated parameter or return of that callable.
'''


EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL = f'{EXCEPTION_PREFIX}wrapper parameter '
'''
Human-readable substring describing a new wrapper parameter required by the
current root type hint in exception messages.
'''


EXCEPTION_PREFIX_HINT = EXCEPTION_PREFIX
'''
Human-readable substring describing the current root type hint in exception
messages.
'''


EXCEPTION_PREFIX_HINT_GENERIC = f'{EXCEPTION_PREFIX_HINT}type hint '
'''
Human-readable substring describing the current root type hint generically
(i.e., *without* respect to the specific PEP to which this hint conforms) in
exception messages.
'''

# ....................{ NAMES ~ parameter                 }....................
# To avoid colliding with the names of arbitrary caller-defined parameters, the
# beartype-specific parameter names *MUST* be prefixed by "__beartype_".

ARG_NAME_FUNC = '__beartype_func'
'''
Name of the **private decorated callable parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the decorated
callable passed to all wrapper functions generated by the
:func:`beartype.beartype` decorator).
'''


ARG_NAME_GETRANDBITS = '__beartype_getrandbits'
'''
Name of the **private getrandbits parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the highly performant C-based
:func:`random.getrandbits` function conditionally passed to every wrapper
functions generated by the :func:`beartype.beartype` decorator internally
requiring one or more random integers).
'''


ARG_NAME_RAISE_EXCEPTION = '__beartype_raise_exception'
'''
Name of the **private exception raising parameter** (i.e.,
:mod:`beartype`-specific parameter whose default value is the
:func:`beartype._decor._error.errormain.raise_pep_call_exception`
function raising human-readable exceptions on call-time type-checking failures
passed to all wrapper functions generated by the :func:`beartype.beartype`
decorator).
'''


ARG_NAME_TYPISTRY = '__beartypistry'
'''
Name of the **private beartypistry parameter** (i.e., :mod:`beartype`-specific
parameter whose default value is the beartypistry singleton conditionally
passed to every wrapper function generated by the :func:`beartype.beartype`
decorator requiring one or more types or tuples of types cached by this
singleton).
'''

# ....................{ NAMES ~ locals                    }....................
VAR_NAME_PREFIX_PITH = '__beartype_pith_'
'''
Substring prefixing all local variables providing a **pith** (i.e., either the
current parameter or return value *or* item contained in the current parameter
or return value being type-checked by the current call).
'''


VAR_NAME_PITH_ROOT = f'{VAR_NAME_PREFIX_PITH}0'
'''
Name of the local variable providing the **root pith** (i.e., value of the
current parameter or return value being type-checked by the current call).
'''


VAR_NAME_ARGS_LEN = '__beartype_args_len'
'''
Name of the local variable providing the **positional argument count** (i.e.,
number of positional arguments passed to the current call).
'''


VAR_NAME_RANDOM_INT = '__beartype_random_int'
'''
Name of the local variable providing a **pseudo-random integer** (i.e.,
unsigned 32-bit integer pseudo-randomly generated for subsequent use in
type-checking randomly indexed container items by the current call).
'''
