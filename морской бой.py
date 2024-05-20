import random


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"


class BoardWrongShipException(BoardException):
    def __str__(self):
        return "Слишком близко к другому кораблю. Либо выход за игровое поле."


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            x, y = self.bow.x, self.bow.y
            if self.direction == 0:
                x += i
            elif self.direction == 1:
                y += i
            ship_dots.append(Dot(x, y))
        return ship_dots


class Board:
    def __init__(self, size, hid=False):
        self.size = size
        self.hid = hid
        self.board = [['O'] * size for _ in range(size)]
        self.ships = []
        self.alive_ships = 0

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or self.board[dot.x][dot.y] == '■':
                raise BoardWrongShipException()

        for dot in ship.dots():
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    x, y = dot.x + dx, dot.y + dy
                    if not self.out(Dot(x, y)) and self.board[x][y] == '■':
                        raise BoardWrongShipException

        for dot in ship.dots():
            self.board[dot.x][dot.y] = '■'
        self.ships.append(ship)
        self.alive_ships += 1
        self.contour(ship)

    def contour(self, ship, symbol='*'):
        near_dots = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots():
            for dx, dy in near_dots:
                x, y = dot.x + dx, dot.y + dy
                if not self.out(Dot(x, y)) and self.board[x][y] == 'O':
                    self.board[x][y] = symbol

    def __str__(self):
        res = "   | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10|\n"
        res += "   |---|---|---|---|---|---|---|---|---|---|\n"
        for i, row in enumerate(self.board):
            row_str = ' | '.join(row)
            res += f"{i + 1:2} | {row_str} |\n"
        return res

    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size)

    def shot(self, dot):
        if self.out(dot):
            raise ValueError("Выстрел за пределы поля!")
        if self.board[dot.x][dot.y] == 'x' or self.board[dot.x][dot.y] == 'T':
            return True, "Вы уже стреляли в эту клетку!"
        if self.board[dot.x][dot.y] == '■':
            self.board[dot.x][dot.y] = 'x'
            for ship in self.ships:
                if dot in ship.dots():
                    ship.lives -= 1
                    if ship.lives == 0:
                        self.alive_ships -= 1
                        self.contour(ship, symbol='T')
                        return True, "Вы попали! Корабль потоплен."
                    else:
                        return True, "Вы попали! Корабль еще не потоплен."
            return True, "Вы попали! Ходите еще раз."
        elif self.board[dot.x][dot.y] == '*':
            self.board[dot.x][dot.y] = 'T'
            return False, "Промах!"

        elif self.board[dot.x][dot.y] == 'O':
            self.board[dot.x][dot.y] = 'T'
            return False, "Промах!"


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                hit, message = self.enemy_board.shot(target)
                print(message)
                if not hit:
                    return
            except ValueError as e:
                print(e)
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        return Dot(random.randint(0, 9), random.randint(0, 9))


class User(Player):
    def ask(self):
        while True:
            try:
                x = int(input("Введите координату X: ")) - 1
                y = int(input("Введите координату Y: ")) - 1
                return Dot(x, y)
            except ValueError:
                print("Неверный ввод. Пожалуйста, введите числа.")

    def display_board(self):
        print("Ваша доска:")
        print(self.board)

    def place_ships(self):
        print("Разместите свои корабли.")
        ships = [3, 2, 2, 1, 1, 1, 1]
        for ship_length in ships:
            while True:
                try:
                    print(f"Разместите корабль длиной {ship_length}.")
                    x = int(input("Введите координату X начала корабля: ")) - 1
                    y = int(input("Введите координату Y начала корабля: ")) - 1
                    if ship_length == 1:
                        direction = 0
                    else:
                        while True:
                            direction = int(input("Введите направление корабля (0 - вертикально, 1 - горизонтально): "))
                            if direction in [0, 1]:
                                break
                            else:
                                print("Неверный ввод. Пожалуйста, введите 0 или 1.")
                    ship = Ship(ship_length, Dot(x, y), direction)
                    self.board.add_ship(ship)
                    self.display_board()
                    break
                except ValueError:
                    print("Ошибка ввода. Введите число от 1 до 10.")
                except BoardWrongShipException as e:
                    print(e)
                    continue


class Game:
    def __init__(self):
        self.user_board = Board(10)
        self.ai_board = Board(10, hid=True)
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    def random_board(self):
        self.user.place_ships()
        ships = [3, 2, 2, 1, 1, 1, 1]
        for ship_length in ships:
            while True:
                x = random.randint(0, 9)
                y = random.randint(0, 9)
                direction = random.choice([0, 1])
                ship = Ship(ship_length, Dot(x, y), direction)
                try:
                    self.ai_board.add_ship(ship)
                    break
                except ValueError:
                    continue
                except BoardWrongShipException as e:
                    print(e)
                    continue

    @staticmethod
    def greet():
        print("Добро пожаловать в игру Морской Бой!")
        print("Ваша задача - разместить свои корабли и потопить флот противника.")
        print("Используйте условные обозначения для понимания игрового поля:")
        print("- 'O': Пустая клетка")
        print("- '■': Местоположение корабля")
        print("- 'x': Попадание в корабль")
        print("- 'T': Промах")
        print("Вы играете против компьютера!")
        print("Начнем!")

    def loop(self):
        while True:
            print("-" * 20)
            print("Ваша доска:")
            print(self.user_board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai_board)
            print("-" * 20)
            self.user.move()
            if self.ai_board.alive_ships == 0:
                print("Поздравляем! Вы победили!")
                game_over = True
                break
            self.ai.move()
            if self.user_board.alive_ships == 0:
                print("Извините, вы проиграли. Компьютер победил!")
                game_over = True
                break

        if game_over:
            play_again = input("Хотите сыграть ещё раз? (да/нет): ").lower()
            if play_again == "да":
                self.__init__()  # Создаем новый объект игры для начала новой партии
                self.start()  # Запускаем новую игру
            else:
                print("Спасибо за игру!")
                return

    def start(self):
        self.greet()
        self.user.display_board()
        self.random_board()
        self.user.display_board()
        self.loop()


if __name__ == "__main__":
    game = Game()
    game.start()
