__author__ = 'davide'

import sqlite3
import string
import sys
from datetime import date

MESI = "ABCDEHLMPRST"
DISPARI = {"0": 1, "1": 0, "2": 5, "3": 7, "4": 9, "5": 13,
           "6": 15, "7": 17, "8": 19, "9": 21, "A": 1, "B": 0,
           "C": 5, "D": 7, "E": 9, "F": 13, "G": 15, "H": 17,
           "I": 19, "J": 21, "K": 2, "L": 4, "M": 18, "N": 20,
           "O": 11, "P": 3, "Q": 6, "R": 8, "S": 12, "T": 14,
           "U": 16, "V": 10, "W": 22, "X": 25, "Y": 24, "Z": 23}
VOCALI = set("AEIOU")
CIFRE = set(string.digits)


def pari(char):
    if char in CIFRE:
        return ord(char) - ord("0")
    return ord(char) - ord("A")


def calcola_ultimo_carattere(resto):
    return chr(ord("A") + resto)


def codifica_nome(nome, is_cognome=True):
    nome = nome.upper().replace(" ", "")

    consonanti, vocali = [], []
    for carattere in nome:
        if carattere in VOCALI:
            vocali.append(carattere)
        else:
            consonanti.append(carattere)

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
    nome_comune = nome_comune.upper()
    conn = sqlite3.connect("comuni.db")
    result_set = conn.execute("select code from comuni where name = ?", [nome_comune])
    result = result_set.fetchone()
    if result is None:
        raise ValueError("Comune non trovato!")
    else:
        return result[0]


def calcola_codice_controllo(code):
    accumulatore = 0
    dispari = True
    for carattere in code:
        if dispari:
            accumulatore += DISPARI[carattere]
        else:
            accumulatore += pari(carattere)
        dispari = not dispari
    return calcola_ultimo_carattere(accumulatore % 26)


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

    return [cognome, nome, data, sesso, comune]


def main():
    dati = parse_input()
    fmt = "Car{} {} {}, il tuo codice fiscale e'..."
    print(fmt.format("a" if dati[3] in "fF" else "o",
                     dati[1].capitalize(),
                     dati[0].capitalize()))
    print(calcola_cf(*dati))

if __name__ == "__main__":
    main()
