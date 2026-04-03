"""Database schema design and code generation for EoStudio.

Provides dataclasses for modeling relational database schemas and
generators that emit SQL DDL, SQLAlchemy ORM models, Prisma schema
files, Django models, and ASCII-art ERDs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------------
# Schema dataclasses
# ------------------------------------------------------------------

@dataclass
class DatabaseColumn:
    """A single column within a database table."""

    name: str
    type_str: str = "TEXT"
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    default: Optional[str] = None
    foreign_key: Optional[str] = None  # "other_table.column"


@dataclass
class DatabaseTable:
    """A database table with columns and optional indexes."""

    name: str
    columns: List[DatabaseColumn] = field(default_factory=list)
    indexes: List[List[str]] = field(default_factory=list)


@dataclass
class DatabaseRelation:
    """A foreign-key relationship between two tables."""

    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relation_type: str = "many-to-one"  # one-to-one | many-to-one | many-to-many


@dataclass
class DatabaseSchema:
    """Complete relational database schema."""

    name: str
    tables: List[DatabaseTable] = field(default_factory=list)
    relations: List[DatabaseRelation] = field(default_factory=list)

    def add_table(self, table: DatabaseTable) -> None:
        self.tables.append(table)

    def add_relation(self, relation: DatabaseRelation) -> None:
        self.relations.append(relation)

    def validate(self) -> List[str]:
        """Return a list of validation error strings (empty if valid)."""
        errors: List[str] = []
        table_names = {t.name for t in self.tables}

        for table in self.tables:
            if not table.columns:
                errors.append(f"Table '{table.name}' has no columns.")
            pk_count = sum(1 for c in table.columns if c.primary_key)
            if pk_count == 0:
                errors.append(
                    f"Table '{table.name}' has no primary key column."
                )
            col_names = [c.name for c in table.columns]
            dupes = {n for n in col_names if col_names.count(n) > 1}
            for d in dupes:
                errors.append(
                    f"Table '{table.name}' has duplicate column '{d}'."
                )
            for idx_cols in table.indexes:
                for ic in idx_cols:
                    if ic not in col_names:
                        errors.append(
                            f"Index on '{table.name}' references "
                            f"unknown column '{ic}'."
                        )
            for col in table.columns:
                if col.foreign_key:
                    parts = col.foreign_key.split(".")
                    if len(parts) != 2:
                        errors.append(
                            f"Column '{table.name}.{col.name}' has "
                            f"malformed foreign_key '{col.foreign_key}'."
                        )
                    elif parts[0] not in table_names:
                        errors.append(
                            f"Column '{table.name}.{col.name}' references "
                            f"unknown table '{parts[0]}'."
                        )

        for rel in self.relations:
            if rel.from_table not in table_names:
                errors.append(
                    f"Relation references unknown table '{rel.from_table}'."
                )
            if rel.to_table not in table_names:
                errors.append(
                    f"Relation references unknown table '{rel.to_table}'."
                )

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the schema to a plain dict."""
        return {
            "name": self.name,
            "tables": [
                {
                    "name": t.name,
                    "columns": [
                        {
                            "name": c.name,
                            "type_str": c.type_str,
                            "primary_key": c.primary_key,
                            "nullable": c.nullable,
                            "unique": c.unique,
                            "default": c.default,
                            "foreign_key": c.foreign_key,
                        }
                        for c in t.columns
                    ],
                    "indexes": t.indexes,
                }
                for t in self.tables
            ],
            "relations": [
                {
                    "from_table": r.from_table,
                    "from_column": r.from_column,
                    "to_table": r.to_table,
                    "to_column": r.to_column,
                    "relation_type": r.relation_type,
                }
                for r in self.relations
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatabaseSchema":
        """Deserialise a schema from a plain dict."""
        tables = []
        for td in data.get("tables", []):
            columns = [
                DatabaseColumn(
                    name=cd["name"],
                    type_str=cd.get("type_str", "TEXT"),
                    primary_key=cd.get("primary_key", False),
                    nullable=cd.get("nullable", True),
                    unique=cd.get("unique", False),
                    default=cd.get("default"),
                    foreign_key=cd.get("foreign_key"),
                )
                for cd in td.get("columns", [])
            ]
            tables.append(
                DatabaseTable(
                    name=td["name"],
                    columns=columns,
                    indexes=td.get("indexes", []),
                )
            )
        relations = [
            DatabaseRelation(
                from_table=rd["from_table"],
                from_column=rd["from_column"],
                to_table=rd["to_table"],
                to_column=rd["to_column"],
                relation_type=rd.get("relation_type", "many-to-one"),
            )
            for rd in data.get("relations", [])
        ]
        return cls(name=data.get("name", "db"), tables=tables, relations=relations)


# ------------------------------------------------------------------
# SQL type mapping helpers
# ------------------------------------------------------------------

_SQL_TYPE_MAP: Dict[str, Dict[str, str]] = {
    "sqlite": {
        "INTEGER": "INTEGER",
        "INT": "INTEGER",
        "BIGINT": "INTEGER",
        "SMALLINT": "INTEGER",
        "TEXT": "TEXT",
        "VARCHAR": "TEXT",
        "CHAR": "TEXT",
        "BOOLEAN": "INTEGER",
        "BOOL": "INTEGER",
        "FLOAT": "REAL",
        "DOUBLE": "REAL",
        "REAL": "REAL",
        "DECIMAL": "REAL",
        "NUMERIC": "REAL",
        "DATE": "TEXT",
        "DATETIME": "TEXT",
        "TIMESTAMP": "TEXT",
        "BLOB": "BLOB",
        "JSON": "TEXT",
        "UUID": "TEXT",
        "SERIAL": "INTEGER",
    },
    "postgresql": {
        "INTEGER": "INTEGER",
        "INT": "INTEGER",
        "BIGINT": "BIGINT",
        "SMALLINT": "SMALLINT",
        "TEXT": "TEXT",
        "VARCHAR": "VARCHAR(255)",
        "CHAR": "CHAR(1)",
        "BOOLEAN": "BOOLEAN",
        "BOOL": "BOOLEAN",
        "FLOAT": "DOUBLE PRECISION",
        "DOUBLE": "DOUBLE PRECISION",
        "REAL": "REAL",
        "DECIMAL": "NUMERIC",
        "NUMERIC": "NUMERIC",
        "DATE": "DATE",
        "DATETIME": "TIMESTAMP",
        "TIMESTAMP": "TIMESTAMP",
        "BLOB": "BYTEA",
        "JSON": "JSONB",
        "UUID": "UUID",
        "SERIAL": "SERIAL",
    },
    "mysql": {
        "INTEGER": "INT",
        "INT": "INT",
        "BIGINT": "BIGINT",
        "SMALLINT": "SMALLINT",
        "TEXT": "TEXT",
        "VARCHAR": "VARCHAR(255)",
        "CHAR": "CHAR(1)",
        "BOOLEAN": "TINYINT(1)",
        "BOOL": "TINYINT(1)",
        "FLOAT": "FLOAT",
        "DOUBLE": "DOUBLE",
        "REAL": "DOUBLE",
        "DECIMAL": "DECIMAL(10,2)",
        "NUMERIC": "DECIMAL(10,2)",
        "DATE": "DATE",
        "DATETIME": "DATETIME",
        "TIMESTAMP": "TIMESTAMP",
        "BLOB": "LONGBLOB",
        "JSON": "JSON",
        "UUID": "CHAR(36)",
        "SERIAL": "INT AUTO_INCREMENT",
    },
}


def _map_sql_type(type_str: str, dialect: str) -> str:
    """Map a generic type string to a dialect-specific SQL type."""
    upper = type_str.upper().strip()
    mapping = _SQL_TYPE_MAP.get(dialect, _SQL_TYPE_MAP["sqlite"])
    return mapping.get(upper, type_str)


# ------------------------------------------------------------------
# SQL DDL generator
# ------------------------------------------------------------------

def generate_sql(schema: DatabaseSchema, dialect: str = "sqlite") -> str:
    """Generate SQL CREATE TABLE statements.

    Args:
        schema: The database schema to generate DDL for.
        dialect: One of ``sqlite``, ``postgresql``, ``mysql``.

    Returns:
        A string containing all CREATE TABLE, foreign key, and
        CREATE INDEX statements.
    """
    if dialect not in ("sqlite", "postgresql", "mysql"):
        raise ValueError(
            f"Unsupported SQL dialect {dialect!r}. "
            "Supported: sqlite, postgresql, mysql"
        )

    lines: List[str] = []
    lines.append(f"-- {schema.name} schema ({dialect})")
    lines.append("-- Generated by EoStudio\n")

    for table in schema.tables:
        col_defs: List[str] = []
        fk_defs: List[str] = []

        for col in table.columns:
            sql_type = _map_sql_type(col.type_str, dialect)
            parts = [f"    {col.name} {sql_type}"]

            if col.primary_key:
                if dialect == "sqlite" and sql_type == "INTEGER":
                    parts.append("PRIMARY KEY AUTOINCREMENT")
                elif dialect == "postgresql" and col.type_str.upper() == "SERIAL":
                    parts = [f"    {col.name} SERIAL PRIMARY KEY"]
                elif dialect == "mysql" and col.type_str.upper() == "SERIAL":
                    parts = [f"    {col.name} INT AUTO_INCREMENT PRIMARY KEY"]
                else:
                    parts.append("PRIMARY KEY")
            else:
                if not col.nullable:
                    parts.append("NOT NULL")
                if col.unique:
                    parts.append("UNIQUE")
                if col.default is not None:
                    parts.append(f"DEFAULT {col.default}")

            col_defs.append(" ".join(parts))

            if col.foreign_key:
                ref_table, ref_col = col.foreign_key.split(".")
                fk_defs.append(
                    f"    FOREIGN KEY ({col.name}) "
                    f"REFERENCES {ref_table}({ref_col})"
                )

        all_defs = col_defs + fk_defs
        lines.append(f"CREATE TABLE {table.name} (")
        lines.append(",\n".join(all_defs))
        lines.append(");\n")

        for idx_cols in table.indexes:
            idx_name = f"idx_{table.name}_{'_'.join(idx_cols)}"
            cols_str = ", ".join(idx_cols)
            lines.append(
                f"CREATE INDEX {idx_name} ON {table.name} ({cols_str});\n"
            )

    return "\n".join(lines)


# ------------------------------------------------------------------
# SQLAlchemy ORM generator
# ------------------------------------------------------------------

_SA_TYPE_MAP: Dict[str, str] = {
    "INTEGER": "Integer",
    "INT": "Integer",
    "BIGINT": "BigInteger",
    "SMALLINT": "SmallInteger",
    "TEXT": "Text",
    "VARCHAR": "String(255)",
    "CHAR": "String(1)",
    "BOOLEAN": "Boolean",
    "BOOL": "Boolean",
    "FLOAT": "Float",
    "DOUBLE": "Float",
    "REAL": "Float",
    "DECIMAL": "Numeric",
    "NUMERIC": "Numeric",
    "DATE": "Date",
    "DATETIME": "DateTime",
    "TIMESTAMP": "DateTime",
    "BLOB": "LargeBinary",
    "JSON": "JSON",
    "UUID": "String(36)",
    "SERIAL": "Integer",
}


def generate_sqlalchemy(schema: DatabaseSchema) -> str:
    """Generate SQLAlchemy ORM model classes.

    Args:
        schema: The database schema.

    Returns:
        Python source code defining SQLAlchemy ORM models.
    """
    lines: List[str] = [
        '"""SQLAlchemy ORM models for {name}."""'.format(name=schema.name),
        "",
        "from sqlalchemy import (",
        "    Column, ForeignKey, Index,",
        "    BigInteger, Boolean, Date, DateTime, Float,",
        "    Integer, JSON, LargeBinary, Numeric,",
        "    SmallInteger, String, Text,",
        ")",
        "from sqlalchemy.orm import DeclarativeBase, relationship",
        "",
        "",
        "class Base(DeclarativeBase):",
        "    pass",
        "",
    ]

    for table in schema.tables:
        class_name = _pascal(table.name)
        lines.append("")
        lines.append(f"class {class_name}(Base):")
        lines.append(f'    __tablename__ = "{table.name}"')
        lines.append("")

        for col in table.columns:
            sa_type = _SA_TYPE_MAP.get(
                col.type_str.upper().strip(), "String(255)"
            )
            args: List[str] = [sa_type]

            if col.foreign_key:
                args.append(f'ForeignKey("{col.foreign_key}")')
            kw: List[str] = []
            if col.primary_key:
                kw.append("primary_key=True")
            if not col.nullable and not col.primary_key:
                kw.append("nullable=False")
            if col.unique and not col.primary_key:
                kw.append("unique=True")
            if col.default is not None:
                kw.append(f"default={col.default}")

            all_args = ", ".join(args + kw)
            lines.append(f"    {col.name} = Column({all_args})")

        # relationships
        for rel in schema.relations:
            if rel.from_table == table.name:
                target_cls = _pascal(rel.to_table)
                lines.append(
                    f'    {rel.to_table} = relationship("{target_cls}")'
                )

        # indexes
        if table.indexes:
            lines.append("")
            lines.append("    __table_args__ = (")
            for idx_cols in table.indexes:
                idx_name = f"idx_{table.name}_{'_'.join(idx_cols)}"
                cols_str = ", ".join(f'"{c}"' for c in idx_cols)
                lines.append(
                    f'        Index("{idx_name}", {cols_str}),'
                )
            lines.append("    )")

        lines.append("")

    return "\n".join(lines)


# ------------------------------------------------------------------
# Prisma schema generator
# ------------------------------------------------------------------

_PRISMA_TYPE_MAP: Dict[str, str] = {
    "INTEGER": "Int",
    "INT": "Int",
    "BIGINT": "BigInt",
    "SMALLINT": "Int",
    "TEXT": "String",
    "VARCHAR": "String",
    "CHAR": "String",
    "BOOLEAN": "Boolean",
    "BOOL": "Boolean",
    "FLOAT": "Float",
    "DOUBLE": "Float",
    "REAL": "Float",
    "DECIMAL": "Decimal",
    "NUMERIC": "Decimal",
    "DATE": "DateTime",
    "DATETIME": "DateTime",
    "TIMESTAMP": "DateTime",
    "BLOB": "Bytes",
    "JSON": "Json",
    "UUID": "String",
    "SERIAL": "Int",
}


def generate_prisma(schema: DatabaseSchema) -> str:
    """Generate a Prisma schema file.

    Args:
        schema: The database schema.

    Returns:
        A string containing a complete ``schema.prisma`` file.
    """
    lines: List[str] = [
        "// Prisma schema for " + schema.name,
        "// Generated by EoStudio",
        "",
        "generator client {",
        '  provider = "prisma-client-js"',
        "}",
        "",
        "datasource db {",
        '  provider = "postgresql"',
        '  url      = env("DATABASE_URL")',
        "}",
        "",
    ]

    for table in schema.tables:
        model_name = _pascal(table.name)
        lines.append(f"model {model_name} {{")

        for col in table.columns:
            prisma_type = _PRISMA_TYPE_MAP.get(
                col.type_str.upper().strip(), "String"
            )
            attrs: List[str] = []

            if col.primary_key:
                attrs.append("@id")
                if col.type_str.upper() in ("SERIAL", "INTEGER", "INT"):
                    attrs.append("@default(autoincrement())")
            elif col.type_str.upper() == "UUID":
                if col.unique:
                    attrs.append("@unique")
                attrs.append("@default(uuid())")
            else:
                if col.unique:
                    attrs.append("@unique")
                if col.default is not None:
                    attrs.append(f"@default({col.default})")

            if col.foreign_key:
                ref_table, ref_col = col.foreign_key.split(".")
                ref_model = _pascal(ref_table)
                attrs.append(
                    f'@relation(fields: [{col.name}], references: [{ref_col}])'
                )

            optional = "?" if col.nullable and not col.primary_key else ""
            attr_str = " ".join(attrs)
            spacing = " " if attr_str else ""
            lines.append(
                f"  {col.name} {prisma_type}{optional}{spacing}{attr_str}"
            )

        # relation fields
        for rel in schema.relations:
            if rel.from_table == table.name:
                ref_model = _pascal(rel.to_table)
                lines.append(
                    f"  {rel.to_table} {ref_model}?"
                    f" @relation(fields: [{rel.from_column}],"
                    f" references: [{rel.to_column}])"
                )
            elif rel.to_table == table.name and rel.relation_type in (
                "one-to-one",
                "many-to-one",
            ):
                from_model = _pascal(rel.from_table)
                lines.append(f"  {rel.from_table}s {from_model}[]")

        # indexes
        if table.indexes:
            for idx_cols in table.indexes:
                cols_str = ", ".join(idx_cols)
                lines.append(f"  @@index([{cols_str}])")

        lines.append(f'  @@map("{table.name}")')
        lines.append("}")
        lines.append("")

    return "\n".join(lines)


# ------------------------------------------------------------------
# Django models generator
# ------------------------------------------------------------------

_DJANGO_TYPE_MAP: Dict[str, str] = {
    "INTEGER": "models.IntegerField()",
    "INT": "models.IntegerField()",
    "BIGINT": "models.BigIntegerField()",
    "SMALLINT": "models.SmallIntegerField()",
    "TEXT": "models.TextField()",
    "VARCHAR": "models.CharField(max_length=255)",
    "CHAR": "models.CharField(max_length=1)",
    "BOOLEAN": "models.BooleanField(default=False)",
    "BOOL": "models.BooleanField(default=False)",
    "FLOAT": "models.FloatField()",
    "DOUBLE": "models.FloatField()",
    "REAL": "models.FloatField()",
    "DECIMAL": "models.DecimalField(max_digits=10, decimal_places=2)",
    "NUMERIC": "models.DecimalField(max_digits=10, decimal_places=2)",
    "DATE": "models.DateField()",
    "DATETIME": "models.DateTimeField()",
    "TIMESTAMP": "models.DateTimeField()",
    "BLOB": "models.BinaryField()",
    "JSON": "models.JSONField(default=dict)",
    "UUID": "models.UUIDField()",
    "SERIAL": "models.AutoField(primary_key=True)",
}


def generate_django_models(schema: DatabaseSchema) -> str:
    """Generate Django model classes.

    Args:
        schema: The database schema.

    Returns:
        Python source code for a Django ``models.py`` file.
    """
    lines: List[str] = [
        f'"""Django models for {schema.name}."""',
        "",
        "from django.db import models",
        "",
    ]

    for table in schema.tables:
        class_name = _pascal(table.name)
        lines.append("")
        lines.append(f"class {class_name}(models.Model):")

        for col in table.columns:
            upper = col.type_str.upper().strip()

            if col.primary_key and upper in ("SERIAL", "INTEGER", "INT"):
                lines.append(
                    f"    {col.name} = models.AutoField(primary_key=True)"
                )
                continue

            if col.foreign_key:
                ref_table, ref_col = col.foreign_key.split(".")
                ref_model = _pascal(ref_table)
                on_delete = "models.CASCADE"
                lines.append(
                    f"    {col.name} = models.ForeignKey("
                    f'"{ref_model}", on_delete={on_delete}, '
                    f'db_column="{col.name}"'
                    + (", null=True, blank=True" if col.nullable else "")
                    + ")"
                )
                continue

            dj_type = _DJANGO_TYPE_MAP.get(upper, "models.CharField(max_length=255)")

            if col.primary_key:
                base = dj_type.rstrip(")")
                if "primary_key" not in base:
                    dj_type = base + (", " if "(" in base and not base.endswith("(") else "") + "primary_key=True)"

            extras: List[str] = []
            if col.unique and not col.primary_key:
                extras.append("unique=True")
            if not col.nullable and not col.primary_key:
                extras.append("null=False")
                extras.append("blank=False")
            elif col.nullable and not col.primary_key:
                extras.append("null=True")
                extras.append("blank=True")
            if col.default is not None and not col.primary_key:
                extras.append(f"default={col.default}")

            if extras:
                base = dj_type.rstrip(")")
                extra_str = ", ".join(extras)
                if base.endswith("("):
                    dj_type = base + extra_str + ")"
                else:
                    dj_type = base + ", " + extra_str + ")"

            lines.append(f"    {col.name} = {dj_type}")

        lines.append("")
        lines.append("    class Meta:")
        lines.append(f'        db_table = "{table.name}"')

        if table.indexes:
            idx_list: List[str] = []
            for idx_cols in table.indexes:
                cols_str = ", ".join(f'"{c}"' for c in idx_cols)
                idx_list.append(f"            models.Index(fields=[{cols_str}])")
            lines.append("        indexes = [")
            lines.append(",\n".join(idx_list))
            lines.append("        ]")

        lines.append("")
        lines.append("    def __str__(self):")
        first_text_col = None
        for c in table.columns:
            if c.type_str.upper() in ("TEXT", "VARCHAR", "CHAR") and not c.primary_key:
                first_text_col = c.name
                break
        if first_text_col:
            lines.append(f"        return str(self.{first_text_col})")
        else:
            lines.append("        return str(self.pk)")
        lines.append("")

    return "\n".join(lines)


# ------------------------------------------------------------------
# ASCII ERD generator
# ------------------------------------------------------------------

def generate_erd_ascii(schema: DatabaseSchema) -> str:
    """Generate an ASCII-art Entity-Relationship Diagram.

    Args:
        schema: The database schema.

    Returns:
        A multi-line string depicting tables, columns, and relations.
    """
    lines: List[str] = []
    lines.append(f"  Entity-Relationship Diagram: {schema.name}")
    lines.append("  " + "=" * 50)
    lines.append("")

    table_boxes: Dict[str, List[str]] = {}
    for table in schema.tables:
        box: List[str] = []
        max_width = len(table.name) + 4
        for col in table.columns:
            col_line = _erd_col_line(col)
            max_width = max(max_width, len(col_line) + 4)

        border = "+" + "-" * (max_width + 2) + "+"
        title = f"| {table.name.center(max_width)} |"
        separator = "+" + "=" * (max_width + 2) + "+"

        box.append(border)
        box.append(title)
        box.append(separator)

        for col in table.columns:
            col_line = _erd_col_line(col)
            box.append(f"| {col_line.ljust(max_width)} |")

        box.append(border)
        table_boxes[table.name] = box

    for tname, box in table_boxes.items():
        for line in box:
            lines.append("  " + line)
        lines.append("")

    if schema.relations:
        lines.append("  Relationships:")
        lines.append("  " + "-" * 50)
        for rel in schema.relations:
            arrow = _erd_arrow(rel.relation_type)
            lines.append(
                f"  {rel.from_table}.{rel.from_column} "
                f"{arrow} {rel.to_table}.{rel.to_column}"
                f"  [{rel.relation_type}]"
            )
        lines.append("")

    return "\n".join(lines)


def _erd_col_line(col: DatabaseColumn) -> str:
    """Format a single column for the ERD box."""
    markers: List[str] = []
    if col.primary_key:
        markers.append("PK")
    if col.foreign_key:
        markers.append("FK")
    if col.unique:
        markers.append("UQ")
    if not col.nullable and not col.primary_key:
        markers.append("NN")
    marker_str = " ".join(markers)
    prefix = f"[{marker_str}] " if marker_str else "    "
    return f"{prefix}{col.name}: {col.type_str}"


def _erd_arrow(relation_type: str) -> str:
    """Return an ASCII arrow for a relation type."""
    arrows = {
        "one-to-one": "1---1",
        "many-to-one": "*---1",
        "one-to-many": "1---*",
        "many-to-many": "*---*",
    }
    return arrows.get(relation_type, "----->")


# ------------------------------------------------------------------
# Naming helpers
# ------------------------------------------------------------------

def _pascal(name: str) -> str:
    """Convert a name to PascalCase."""
    return "".join(
        w.capitalize()
        for w in name.replace("-", " ").replace("_", " ").split()
    )
