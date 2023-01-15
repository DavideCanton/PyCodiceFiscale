# PyCodiceFiscale

Tax code calculation in Python 3.x.

The program allows you to calculate the tax code interactively (that is, by entering the data from the stdin) or by passing it as parameters to the command line by invoking the command.

## Input from command line

```
$ python cf.py args first_name last_name sex date_of_birth comune_of_birth
```

## Input from stdin

```
$ python cf.py input
Nome>
Cognome>
Sesso (M/F)>
Data (gg/mm/aaaa)>
Comune>
```

## Notes on inputs

`sex` must be one of the following alternatives:

- `m/M` if you want to indicate male sex;
- `f/F` if you want to indicate female sex.

`date of birth` must be in the form `dd/mm/yyyy`.
