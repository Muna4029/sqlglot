# ruff: noqa: F401
"""
.. include:: ../README.md

----
"""

from __future__ import annotations

import logging
import typing as t

from sqlglot import expressions as exp
from sqlglot.dialects.dialect import Dialect as Dialect
from sqlglot.dialects.dialect import Dialects as Dialects
from sqlglot.diff import diff as diff
from sqlglot.errors import (
    ErrorLevel as ErrorLevel,
)
from sqlglot.errors import (
    ParseError as ParseError,
)
from sqlglot.errors import (
    TokenError as TokenError,
)
from sqlglot.errors import (
    UnsupportedError as UnsupportedError,
)
from sqlglot.expressions import (
    Expression as Expression,
)
from sqlglot.expressions import (
    alias_ as alias,
)
from sqlglot.expressions import (
    and_ as and_,
)
from sqlglot.expressions import (
    case as case,
)
from sqlglot.expressions import (
    cast as cast,
)
from sqlglot.expressions import (
    column as column,
)
from sqlglot.expressions import (
    condition as condition,
)
from sqlglot.expressions import (
    delete as delete,
)
from sqlglot.expressions import (
    except_ as except_,
)
from sqlglot.expressions import (
    from_ as from_,
)
from sqlglot.expressions import (
    func as func,
)
from sqlglot.expressions import (
    insert as insert,
)
from sqlglot.expressions import (
    intersect as intersect,
)
from sqlglot.expressions import (
    maybe_parse as maybe_parse,
)
from sqlglot.expressions import (
    merge as merge,
)
from sqlglot.expressions import (
    not_ as not_,
)
from sqlglot.expressions import (
    or_ as or_,
)
from sqlglot.expressions import (
    select as select,
)
from sqlglot.expressions import (
    subquery as subquery,
)
from sqlglot.expressions import (
    table_ as table,
)
from sqlglot.expressions import (
    to_column as to_column,
)
from sqlglot.expressions import (
    to_identifier as to_identifier,
)
from sqlglot.expressions import (
    to_table as to_table,
)
from sqlglot.expressions import (
    union as union,
)
from sqlglot.generator import Generator as Generator
from sqlglot.parser import Parser as Parser
from sqlglot.schema import MappingSchema as MappingSchema
from sqlglot.schema import Schema as Schema
from sqlglot.tokens import Token as Token
from sqlglot.tokens import Tokenizer as Tokenizer
from sqlglot.tokens import TokenType as TokenType

if t.TYPE_CHECKING:
    from sqlglot._typing import E
    from sqlglot.dialects.dialect import DialectType as DialectType

logger = logging.getLogger("sqlglot")


try:
    from sqlglot._version import __version__, __version_tuple__
except ImportError:
    logger.error(
        "Unable to set __version__, run `pip install -e .` or `python setup.py develop` first."
    )


pretty = False
"""Whether to format generated SQL by default."""


def tokenize(
    sql: str, read: DialectType = None, dialect: DialectType = None
) -> t.List[Token]:
    """
    Tokenizes the given SQL string.

    Args:
        sql: the SQL code string to tokenize.
        read: the SQL dialect to apply during tokenizing (eg. "spark", "hive", "presto", "mysql").
        dialect: the SQL dialect (alias for read).

    Returns:
        The resulting list of tokens.
    """
    return Dialect.get_or_raise(read or dialect).tokenize(sql)


def parse(
    sql: str, read: DialectType = None, dialect: DialectType = None, **opts
) -> t.List[t.Optional[Expression]]:
    """
    Parses the given SQL string into a collection of syntax trees, one per parsed SQL statement.

    Args:
        sql: the SQL code string to parse.
        read: the SQL dialect to apply during parsing (eg. "spark", "hive", "presto", "mysql").
        dialect: the SQL dialect (alias for read).
        **opts: other `sqlglot.parser.Parser` options.

    Returns:
        The resulting syntax tree collection.
    """
    return Dialect.get_or_raise(read or dialect).parse(sql, **opts)


@t.overload
def parse_one(sql: str, *, into: t.Type[E], **opts) -> E: ...


@t.overload
def parse_one(sql: str, **opts) -> Expression: ...


def parse_one(
    sql: str,
    read: DialectType = None,
    dialect: DialectType = None,
    into: t.Optional[exp.IntoType] = None,
    **opts,
) -> Expression:
    """
    Parses the given SQL string and returns a syntax tree for the first parsed SQL statement.

    Args:
        sql: the SQL code string to parse.
        read: the SQL dialect to apply during parsing (eg. "spark", "hive", "presto", "mysql").
        dialect: the SQL dialect (alias for read)
        into: the SQLGlot Expression to parse into.
        **opts: other `sqlglot.parser.Parser` options.

    Returns:
        The syntax tree for the first parsed statement.
    """

    dialect = Dialect.get_or_raise(read or dialect)

    if into:
        result = dialect.parse_into(into, sql, **opts)
    else:
        result = dialect.parse(sql, **opts)

    for expression in result:
        if not expression:
            raise ParseError(f"No expression was parsed from '{sql}'")
        return expression
    raise ParseError(f"No expression was parsed from '{sql}'")


def transpile(
    sql: str,
    read: DialectType = None,
    write: DialectType = None,
    identity: bool = True,
    error_level: t.Optional[ErrorLevel] = None,
    **opts,
) -> t.List[str]:
    """
    Parses the given SQL string in accordance with the source dialect and returns a list of SQL strings transformed
    to conform to the target dialect. Each string in the returned list represents a single transformed SQL statement.

    Args:
        sql: the SQL code string to transpile.
        read: the source dialect used to parse the input string (eg. "spark", "hive", "presto", "mysql").
        write: the target dialect into which the input should be transformed (eg. "spark", "hive", "presto", "mysql").
        identity: if set to `True` and if the target dialect is not specified the source dialect will be used as both:
            the source and the target dialect.
        error_level: the desired error level of the parser.
        **opts: other `sqlglot.generator.Generator` options.

    Returns:
        The list of transpiled SQL statements.
    """
    write = (read if write is None else write) if identity else write
    write = Dialect.get_or_raise(write)
    return [
        write.generate(expression, copy=False, **opts) if expression else ""
        for expression in parse(sql, read, error_level=error_level)
    ]
