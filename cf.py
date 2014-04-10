__author__ = 'davide'

import sqlite3
import string
import sys
import operator
from functools import partial
from datetime import date

MESI = "ABCDEHLMPRST"
DISPARI = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18,
           20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23]
ORD_0 = ord("0")
ORD_A = ord("A")

vocale_pred = partial(operator.contains, set("AEIOU"))


def pari(char):
    if char.isdigit():
        return ord(char) - ORD_0
    else:
        return ord(char) - ORD_A


def dispari(char):
    if char.isdigit():
        return DISPARI[ord(char) - ORD_0]
    else:
        return DISPARI[ord(char) - ORD_A]


def calcola_ultimo_carattere(resto):
    return chr(ORD_A + resto)


def partition(pred, iterable):
    partitions = [],[]
    for c in iterable:
        partitions[int(pred(c))].append(c)
    return partitions            


def codifica_nome(nome, is_cognome=True):
    nome = nome.upper().replace(" ", "")

    consonanti, vocali = partition(vocale_pred, nome)    

    if not is_cognome and len(consonanti) > 3:
        del consonanti[1]

    nome = "".join(consonanti + vocali)[:3]
    return nome.ljust(3, "X")


def codifica_data(data, sesso):
    offset = 40 if sesso in "fF" else 0
    return "{:>02}{}{:>02}".format(data.year % 100,
                                   MESI[data.month - 1],
                                   data.day + offset)


def codifica_comune(nome_comune):
    try:
        nome_comune = nome_comune.upper()
        conn = sqlite3.connect("comuni.db")
        result_set = conn.execute("select code from comuni where name = ?", [nome_comune])
        result = result_set.fetchone()
        return result[0]
    except TypeError:  # result is None
        raise ValueError("Comune non trovato!")


def calcola_codice_controllo(code):
    acc_d = sum(dispari(x) for x in code[::2])
    acc_p = sum(pari(x) for x in code[1::2])
    return calcola_ultimo_carattere((acc_d + acc_p) % 26)


def calcola_cf(cognome, nome, data, sesso, comune):
    codice = "{}{}{}{}".format(codifica_nome(cognome),
                               codifica_nome(nome, is_cognome=False),
                               codifica_data(data, sesso),
                               codifica_comune(comune))
    return "".join([codice, calcola_codice_controllo(codice)])


def parse_input():
    if 1 < len(sys.argv) < 6:
        exit("Numero di parametri insufficiente")
    elif len(sys.argv) == 1:
        nome = input("Nome>")
        cognome = input("Cognome>")
        sesso = input("Sesso (M/F)>")
        data = input("Data (gg/mm/aaaa)>")
        comune = input("Comune>")
    else:
        nome, cognome, sesso, data, comune = sys.argv[1:]

    if sesso not in "mMfF" or len(sesso) != 1:
        exit("Sesso non valido!")

    try:
        giorno, mese, anno = map(int, data.split("/"))
        data = date(anno, mese, giorno)
    except ValueError:
        exit("Data non valida!")

    return cognome, nome, data, sesso, comune


def main():
    dati = parse_input()
    fmt = "Car{} {} {}, il tuo codice fiscale e'..."
    print(fmt.format("a" if dati[3] in "fF" else "o",
                     dati[1].capitalize(),
                     dati[0].capitalize()))
    print(calcola_cf(*dati))


if __name__ == "__main__":
    main()
