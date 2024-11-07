# Symulacja skrzyżowania sterowana logiką rozmytą

## Opis projektu

Ten projekt to symulacja ruchu drogowego na skrzyżowaniu, w której sygnalizacja świetlna jest sterowana za pomocą **logiki rozmytej**. Celem jest dynamiczne dostosowywanie czasu trwania zielonego światła w zależności od aktualnego natężenia ruchu, co pozwala na bardziej płynny i efektywny przepływ pojazdów.

Projekt został stworzony przez:

- Kacper Sewruk s23466
- Michał Jastrzemski s26245

![fuzzy-logic-1](https://github.com/user-attachments/assets/693d7f67-b74e-4c57-97b9-de24bcbd2af1)


## Wymagania

- Python 3.x
- Biblioteki Python:
  - `pygame`
  - `numpy`
  - `scikit-fuzzy`

## Instalacja

Aby uruchomić program, upewnij się, że masz zainstalowane wymagane biblioteki. Możesz je zainstalować za pomocą `pip`:

```bash
pip install pygame numpy scikit-fuzzy
```


## Funkcjonalność

Program symuluje ruch pojazdów na skrzyżowaniu, gdzie sygnalizacja świetlna jest sterowana za pomocą logiki rozmytej. Pojazdy są generowane losowo w różnych kierunkach i poruszają się zgodnie z zasadami ruchu drogowego.

Sygnalizacja działa w dwóch fazach:
- Faza pionowa (vertical): Zielone światło dla kierunków "góra" i "dół".
- Faza pozioma (horizontal): Zielone światło dla kierunków "lewo" i "prawo".

Czas trwania zielonego światła jest dynamicznie dostosowywany na podstawie liczby pojazdów oczekujących w danej fazie.

## Logika rozmyta

Sterowanie sygnalizacją świetlną odbywa się za pomocą systemu rozmytego, który dostosowuje czas trwania zielonego światła w zależności od aktualnego natężenia ruchu.

Wejścia systemu rozmytego
- **vehicles_in_phase**: Liczba pojazdów oczekujących w aktualnie aktywnej fazie sygnalizacji.
- **vehicles_in_other_phase**: Liczba pojazdów oczekujących w przeciwnej fazie sygnalizacji.
- **total_vehicles_waiting**: Łączna liczba pojazdów oczekujących na skrzyżowaniu.

Wyjście systemu rozmytego
- **green_duration**: Czas trwania zielonego światła dla aktualnej fazy sygnalizacji

## Funkcje przynależności (Membership Functions)

**Dla wejść:**
1. vehicles_in_phase:
   - low (mało): Gdy liczba pojazdów w fazie jest niska (0-20).
   - medium (średnio): Gdy liczba pojazdów jest umiarkowana (10-50).
   - high (dużo): Gdy liczba pojazdów jest wysoka (40-60).
2. vehicles_in_other_phase:
   - low (mało): (0-20).
   - medium (średnio): (10-50).
   - high (dużo): (40-60).
3. total_vehicles_waiting:
   - low (mało): Niskie natężenie ruchu (0-40).
   - medium (średnio): Umiarkowane natężenie ruchu (30-90).
   - high (dużo): Wysokie natężenie ruchu (80-120).
  
4. Dla wyjścia:
   - green_duration:
     - short (krótki): Krótki czas zielonego światła (5-25 sekund).
     - medium (średni): Średni czas zielonego światła (20-50 sekund).
     - long (długi): Długi czas zielonego światła (45-60 sekund).
    

## Przykład działania

Jeśli w aktualnej fazie oczekuje 10 pojazdów (kategoria medium), a w przeciwnej fazie 50 pojazdów (kategoria high), to zgodnie z regułami logiki rozmytej, czas zielonego światła będzie short.







