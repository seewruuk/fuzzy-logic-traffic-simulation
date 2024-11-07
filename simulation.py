"""
Autorzy:
- Kacper Sewruk s23466
- Michał Jastrzemski s26245

Opis programu:
Symulacja skrzyżowania sterowanego sygnalizacją świetlną, która jest kontrolowana za pomocą logiki rozmytej. Czas trwania zielonego światła jest dynamicznie dostosowywany na podstawie liczby pojazdów oczekujących w różnych kierunkach.

Wejścia systemu:
1. vehicles_in_phase (liczba pojazdów oczekujących w aktualnej fazie)
2. vehicles_in_other_phase (liczba pojazdów oczekujących w przeciwnej fazie)
3. total_vehicles_waiting (łączna liczba pojazdów oczekujących na skrzyżowaniu)

Wyjście systemu:
- green_duration (czas trwania zielonego światła dla aktualnej fazy)

Wyjście zostało opisane za pomocą trzech funkcji przynależności:
- 'short' (krótki)
- 'medium' (średni)
- 'long' (długi)
"""

import random
import time
import threading
import pygame
import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Domyślne wartości timerów sygnalizacji
defaultGreen = {0: 10, 1: 10}
defaultRed = 150
defaultYellow = 5

signals = []
noOfSignals = 2  # Liczba faz
currentPhase = 0  # Wskazuje, która faza jest obecnie aktywna
currentYellow = 0  # Wskazuje, czy żółte światło jest włączone

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}  # Średnie prędkości pojazdów

# Współrzędne początkowe pojazdów
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {
    'right': {0: [], 1: [], 2: [], 'crossed': 0},
    'down': {0: [], 1: [], 2: [], 'crossed': 0},
    'left': {0: [], 1: [], 2: [], 'crossed': 0},
    'up': {0: [], 1: [], 2: [], 'crossed': 0}
}

vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'vertical', 1: 'horizontal'}
directionsInPhase = {'vertical': ['up', 'down'], 'horizontal': ['left', 'right']}

# Współrzędne obrazów sygnalizacji i timerów
signalCoods = {'up': (530, 230), 'down': (810, 570), 'left': (810, 230), 'right': (530, 570)}
signalTimerCoods = {'up': (530, 210), 'down': (810, 550), 'left': (810, 210), 'right': (530, 550)}

# Współrzędne linii zatrzymania
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Odstęp między pojazdami
stoppingGap = 15  # Odstęp przy zatrzymaniu
movingGap = 15  # Odstęp podczas ruchu

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    """
    Klasa reprezentująca sygnalizator świetlny.

    Atrybuty:
        red (int): Czas trwania czerwonego światła.
        yellow (int): Czas trwania żółtego światła.
        green (int): Czas trwania zielonego światła.
        signalText (str): Tekst wyświetlany na sygnalizatorze (np. pozostały czas).
    """
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    """
    Klasa reprezentująca pojazd w symulacji.

    Atrybuty:
        lane (int): Numer pasa ruchu.
        vehicleClass (str): Typ pojazdu (np. 'car', 'bus').
        speed (float): Prędkość pojazdu.
        direction (str): Kierunek ruchu pojazdu.
        x (float): Pozycja X pojazdu.
        y (float): Pozycja Y pojazdu.
        crossed (int): Flaga informująca, czy pojazd przekroczył linię zatrzymania.
        image (Surface): Obrazek reprezentujący pojazd.
        index (int): Indeks pojazdu w liście pojazdów na danym pasie i kierunku.
        stop (float): Pozycja, w której pojazd powinien się zatrzymać.
    """
    def __init__(self, lane, vehicleClass, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        # Ustalanie pozycji zatrzymania
        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][self.index - 1].image.get_rect().width - stoppingGap
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][self.index - 1].image.get_rect().width + stoppingGap
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][self.index - 1].image.get_rect().height - stoppingGap
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][self.index - 1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Aktualizacja pozycji startowej dla kolejnych pojazdów
        if direction == 'right':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        """
        Wyświetla pojazd na ekranie.

        Args:
            screen (Surface): Powierzchnia ekranu Pygame.
        """
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        """
        Steruje ruchem pojazdu, uwzględniając sygnalizację świetlną i pozycję innych pojazdów.
        """
        phaseDirections = directionsInPhase[directionNumbers[currentPhase]]
        if self.direction in phaseDirections:
            signalGreen = True
        else:
            signalGreen = False

        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
            if (self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (signalGreen and currentYellow == 0)) and \
               (self.index == 0 or self.x + self.image.get_rect().width < (vehicles[self.direction][self.lane][self.index - 1].x - movingGap)):
                self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
            if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (signalGreen and currentYellow == 0)) and \
               (self.index == 0 or self.y + self.image.get_rect().height < (vehicles[self.direction][self.lane][self.index - 1].y - movingGap)):
                self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
            if (self.x >= self.stop or self.crossed == 1 or (signalGreen and currentYellow == 0)) and \
               (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][self.index - 1].image.get_rect().width + movingGap)):
                self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
            if (self.y >= self.stop or self.crossed == 1 or (signalGreen and currentYellow == 0)) and \
               (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y + vehicles[self.direction][self.lane][self.index - 1].image.get_rect().height + movingGap)):
                self.y -= self.speed

def initialize():
    """
    Inicjalizuje sygnalizatory świetlne z domyślnymi wartościami i rozpoczyna pętlę sterującą sygnalizacją.
    """
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    repeat()

# Definicja zmiennych rozmytych
vehicles_in_phase = ctrl.Antecedent(np.arange(0, 61, 1), 'vehicles_in_phase')
vehicles_in_other_phase = ctrl.Antecedent(np.arange(0, 61, 1), 'vehicles_in_other_phase')
total_vehicles_waiting = ctrl.Antecedent(np.arange(0, 121, 1), 'total_vehicles_waiting')

green_duration = ctrl.Consequent(np.arange(5, 61, 1), 'green_duration')

# Funkcje przynależności dla wejść
vehicles_in_phase['low'] = fuzz.trimf(vehicles_in_phase.universe, [0, 0, 20])
vehicles_in_phase['medium'] = fuzz.trimf(vehicles_in_phase.universe, [10, 30, 50])
vehicles_in_phase['high'] = fuzz.trimf(vehicles_in_phase.universe, [40, 60, 60])

vehicles_in_other_phase['low'] = fuzz.trimf(vehicles_in_other_phase.universe, [0, 0, 20])
vehicles_in_other_phase['medium'] = fuzz.trimf(vehicles_in_other_phase.universe, [10, 30, 50])
vehicles_in_other_phase['high'] = fuzz.trimf(vehicles_in_other_phase.universe, [40, 60, 60])

total_vehicles_waiting['low'] = fuzz.trimf(total_vehicles_waiting.universe, [0, 0, 40])
total_vehicles_waiting['medium'] = fuzz.trimf(total_vehicles_waiting.universe, [30, 60, 90])
total_vehicles_waiting['high'] = fuzz.trimf(total_vehicles_waiting.universe, [80, 120, 120])

# Funkcje przynależności dla wyjścia (3 funkcje przynależności)
green_duration['short'] = fuzz.trimf(green_duration.universe, [5, 5, 25])
green_duration['medium'] = fuzz.trimf(green_duration.universe, [20, 35, 50])
green_duration['long'] = fuzz.trimf(green_duration.universe, [45, 60, 60])

# Definicja reguł rozmytych
rule1 = ctrl.Rule(vehicles_in_phase['high'] & vehicles_in_other_phase['low'], green_duration['long'])
rule2 = ctrl.Rule(vehicles_in_phase['low'] & vehicles_in_other_phase['high'], green_duration['short'])
rule3 = ctrl.Rule(vehicles_in_phase['medium'] & vehicles_in_other_phase['medium'], green_duration['medium'])
rule4 = ctrl.Rule(total_vehicles_waiting['high'] & vehicles_in_phase['high'], green_duration['medium'])
rule5 = ctrl.Rule(total_vehicles_waiting['low'], green_duration['short'])
rule6 = ctrl.Rule(total_vehicles_waiting['high'] & vehicles_in_phase['low'], green_duration['short'])
rule7 = ctrl.Rule(vehicles_in_phase['low'] & vehicles_in_other_phase['low'], green_duration['short'])
rule8 = ctrl.Rule(vehicles_in_phase['high'] & vehicles_in_other_phase['high'], green_duration['medium'])

# Tworzenie systemu sterowania
green_duration_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])
green_duration_simulation = ctrl.ControlSystemSimulation(green_duration_ctrl)

def get_vehicles_waiting_in_phase(phase):
    """
    Oblicza liczbę pojazdów oczekujących w danej fazie.

    Args:
        phase (str): Nazwa fazy ('vertical' lub 'horizontal').

    Returns:
        int: Liczba pojazdów oczekujących.
    """
    count = 0
    for direction in directionsInPhase[phase]:
        for lane in vehicles[direction]:
            if lane != 'crossed':
                for vehicle in vehicles[direction][lane]:
                    if vehicle.crossed == 0:
                        count += 1
    return count

def repeat():
    """
    Główna pętla sterująca sygnalizacją świetlną, wykorzystująca logikę rozmytą do dynamicznego dostosowania czasu zielonego światła.
    """
    global currentPhase, currentYellow
    while True:
        # Pobranie liczby pojazdów oczekujących
        vehicles_in_current_phase = get_vehicles_waiting_in_phase(directionNumbers[currentPhase])
        vehicles_in_other_phase = get_vehicles_waiting_in_phase(directionNumbers[(currentPhase + 1) % noOfSignals])
        total_vehicles = vehicles_in_current_phase + vehicles_in_other_phase

        # Ustawienie wejść dla kontrolera rozmytego
        green_duration_simulation.input['vehicles_in_phase'] = vehicles_in_current_phase
        green_duration_simulation.input['vehicles_in_other_phase'] = vehicles_in_other_phase
        green_duration_simulation.input['total_vehicles_waiting'] = total_vehicles

        # Obliczenie czasu zielonego światła
        green_duration_simulation.compute()

        calculated_green_duration = green_duration_simulation.output['green_duration']
        signals[currentPhase].green = int(calculated_green_duration)
        print("Czas trwania zielonego światła dla fazy", currentPhase, "ustawiony na", signals[currentPhase].green, "sekund.")

        # Uruchomienie zielonego światła
        while signals[currentPhase].green > 0:
            updateValues()
            time.sleep(1)
        currentYellow = 1  # Włączenie żółtego światła

        # Resetowanie pozycji zatrzymania pojazdów
        for phaseDirection in directionsInPhase[directionNumbers[currentPhase]]:
            for i in range(0, 3):
                for vehicle in vehicles[phaseDirection][i]:
                    vehicle.stop = defaultStop[phaseDirection]
        while signals[currentPhase].yellow > 0:
            updateValues()
            time.sleep(1)
        currentYellow = 0  # Wyłączenie żółtego światła

        # Resetowanie czasów sygnałów
        signals[currentPhase].yellow = defaultYellow
        signals[currentPhase].red = defaultRed

        currentPhase = (currentPhase + 1) % noOfSignals  # Przełączenie na następną fazę

def updateValues():
    """
    Aktualizuje wartości timerów sygnalizacji świetlnej.
    """
    for i in range(0, noOfSignals):
        if i == currentPhase:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    """
    Generuje pojazdy w losowych kierunkach i typach, symulując ruch drogowy.
    """
    while True:
        vehicle_type = random.randint(0, 3)
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 99)
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction = 'right'
        elif temp < dist[1]:
            direction = 'down'
        elif temp < dist[2]:
            direction = 'left'
        else:
            direction = 'up'
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction)
        time.sleep(1)

class Main:
    """
    Główna klasa programu, inicjalizuje symulację i obsługuje pętlę główną Pygame.
    """
    thread1 = threading.Thread(name="initialization", target=initialize, args=())  # Inicjalizacja
    thread1.daemon = True
    thread1.start()

    # Kolory
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Rozmiar ekranu
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Wczytywanie tła skrzyżowania
    background = pygame.image.load('images/intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("Symulacja skrzyżowania")

    # Wczytywanie obrazów sygnalizacji i czcionki
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generowanie pojazdów
    thread2.daemon = True
    thread2.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))  # Wyświetlanie tła symulacji

        # Wyświetlanie sygnalizacji świetlnej
        for direction in ['up', 'down', 'left', 'right']:
            if direction in directionsInPhase[directionNumbers[currentPhase]]:
                if currentYellow == 1:
                    signals[currentPhase].signalText = signals[currentPhase].yellow
                    screen.blit(yellowSignal, signalCoods[direction])
                else:
                    signals[currentPhase].signalText = signals[currentPhase].green
                    screen.blit(greenSignal, signalCoods[direction])
            else:
                if signals[(currentPhase + 1) % noOfSignals].red <= 10:
                    signals[(currentPhase + 1) % noOfSignals].signalText = signals[(currentPhase + 1) % noOfSignals].red
                else:
                    signals[(currentPhase + 1) % noOfSignals].signalText = "---"
                screen.blit(redSignal, signalCoods[direction])
        signalTexts = {"up": "", "down": "", "left": "", "right": ""}

        # Wyświetlanie timerów sygnalizacji
        for direction in ['up', 'down', 'left', 'right']:
            if direction in directionsInPhase[directionNumbers[currentPhase]]:
                signalTexts[direction] = font.render(str(signals[currentPhase].signalText), True, white, black)
                screen.blit(signalTexts[direction], signalTimerCoods[direction])
            else:
                signalTexts[direction] = font.render(str("---"), True, white, black)
                screen.blit(signalTexts[direction], signalTimerCoods[direction])

        # Wyświetlanie pojazdów
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()

Main()
