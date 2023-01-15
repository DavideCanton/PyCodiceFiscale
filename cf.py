"""Tax code calculation in Python 3.x.

The program allows you to calculate the tax code interactively
(that is, by entering the data from the command line) or by passing it
as parameters to the command line by invoking the command.
"""
from __future__ import annotations
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum
import operator
import sqlite3
from datetime import date, datetime
from functools import partial
from typing import Callable, Iterable

__author__ = "DavideCanton"

MONTHS = "ABCDEHLMPRST"
"""Months string defining the month character for each month.

Uses zero-based month indexing, so the character corresponding to January
is stored in position 0.
"""
# fmt: off
ODD_VALUES = [
    1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18,
    20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23
]
"""Values required to compute the checksum for characters in odd
positions."""
# fmt: on


class Sex(str, Enum):
    """Enum defining sex values."""

    M = "M"
    """Male"""
    F = "F"
    """Female"""


@dataclass
class Input:
    """Input values class."""

    name: str
    """The name."""
    surname: str
    """The surname."""
    sex: Sex
    """The sex."""
    dob: date
    """The date of birth."""
    comune: str
    """The comune of birth."""

    @classmethod
    def Make(cls, name: str, surname: str, sex: str, dob: str, comune: str) -> Input:
        """Creates an ``Input`` value from the arguments."""
        sex_enum = Sex(sex.upper())
        dob_d = datetime.strptime(dob, "%d/%m/%Y").date()
        return Input(name, surname, sex_enum, dob_d, comune)


is_vowel: Callable[[str], bool] = partial(operator.contains, set("AEIOUÀÈÉÌÒÙ"))
"""Returns True if the character is a vowel."""


def even_char(char: str) -> int:
    """Computes the control value for characters in even position."""
    return ord(char) - (ord("0") if char.isdigit() else ord("A"))


def odd_char(char: str) -> int:
    """Computes the control value for characters in odd position."""
    return ODD_VALUES[ord(char) - (ord("0") if char.isdigit() else ord("A"))]


def partition(
    pred: Callable[[str], bool], iterable: Iterable[str]
) -> tuple[list[str], list[str]]:
    """Splits the iterable into two lists containing respectively:
    - the elements for which the predicate is False;
    - the elements for which the predicate is True.
    """
    partitions = [], []
    for element in iterable:
        partitions[int(pred(element))].append(element)
    return partitions


def encode_name(name: str, is_surname: bool) -> str:
    """Encodes name and surname in tax code format.

    If ``is_surname`` is False, removes the second consonant
    if there are more than 3 consonants in the name.
    """
    name = name.upper().replace(" ", "")

    consonants, vowels = partition(is_vowel, name)

    if not is_surname and len(consonants) > 3:
        del consonants[1]

    name = "".join(consonants + vowels)[:3]
    return name.ljust(3, "X")


def encode_date(dob: date, sex: Sex) -> str:
    """Encodes the date of birth."""
    year = dob.year % 100
    month = MONTHS[dob.month - 1]
    offset = 40 if sex is Sex.F else 0
    day = dob.day + offset
    return f"{year:>02}{month}{day:>02}"


def encode_comune(comune: str) -> str:
    """Retrieves the comune's code from the database."""
    try:
        conn = sqlite3.connect("comuni.db")
        result_set = conn.execute(
            "select code from comuni where upper(name) = ?", [comune.upper()]
        )
        result = result_set.fetchone()
        return result[0]
    except TypeError:  # result is None
        raise ValueError(f"Comune with name {comune} not found!")


def compute_control_code(tax_code: str) -> str:
    """Computes the control code."""
    acc_d = sum(odd_char(x) for x in tax_code[::2])
    acc_p = sum(even_char(x) for x in tax_code[1::2])
    rem = (acc_d + acc_p) % 26
    return chr(ord("A") + rem)


def compute_tax_code(data: Input) -> str:
    """Computes the tax code from the input."""
    tax_code = "".join(
        [
            encode_name(data.surname, is_surname=True),
            encode_name(data.name, is_surname=False),
            encode_date(data.dob, data.sex),
            encode_comune(data.comune),
        ]
    )
    return tax_code + compute_control_code(tax_code)


def make_parser() -> ArgumentParser:
    """Creates the argument parser."""
    parser = ArgumentParser(description="Tax code calculation in Python")

    subparsers = parser.add_subparsers(help="Subcommands")
    parser_args = subparsers.add_parser("args", help="Reads inputs from args")
    parser_args.add_argument("name", help="The name.", type=str)
    parser_args.add_argument("surname", help="The surname.", type=str)
    parser_args.add_argument("sex", help="The sex.", type=str, choices=list("fFmM"))
    parser_args.add_argument(
        "dob", help="The date of birth in DD/MM/YYYY format.", type=str
    )
    parser_args.add_argument("comune", help="The comune.", type=str)
    parser_args.set_defaults(func=read_args)

    parser_input = subparsers.add_parser("input", help="Reads inputs from stdin")
    parser_input.set_defaults(func=read_input)

    return parser


def read_input(_args) -> Input:
    """Reads the input from stdin."""
    name = input("Nome> ")
    surname = input("Cognome> ")
    sex_s = input("Sesso (M/F)> ")
    dob_s = input("Data (gg/mm/aaaa)> ")
    comune = input("Comune> ")
    return Input.Make(name, surname, sex_s, dob_s, comune)


def read_args(args) -> Input:
    """Reads the input from command line arguments."""
    return Input.Make(args.name, args.surname, args.sex, args.dob, args.comune)


def main():
    """Main routine."""
    parser = make_parser()
    args = parser.parse_args()
    input_data: Input = args.func(args)
    fmt = "Car{} {} {}, il tuo codice fiscale è..."
    print(
        fmt.format(
            "a" if input_data.sex is Sex.F else "o",
            input_data.name.capitalize(),
            input_data.surname.capitalize(),
        )
    )
    print(compute_tax_code(input_data))


if __name__ == "__main__":
    main()
