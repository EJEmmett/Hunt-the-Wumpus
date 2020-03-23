from collections.abc import Iterable
from random import choice
from typing import List, Dict, Union

try:
    from aima3 import logic
except ImportError:
    try:
        from importlib import import_module

        logic = import_module("aima-python.logic")
    except ImportError:
        raise ImportError("Missing requirements.")


class World(object):
    # Coordinates
    # P31 P32 P33
    # P21 P22 P33
    # P11 P12 P13
    _exprs: List[logic.Expr] = [logic.expr('P' + str(r) + str(c))
                                for r in reversed(range(1, 4))
                                for c in range(1, 4)]

    _B, _S = logic.expr("B, S")

    def __init__(self, pit_num=1):
        self._win_loss = None  # W: True, L: False, Playing: None

        self._expr_dict: Dict[str, Union[List[logic.Expr], logic.Expr]] \
            = {'w': logic.Expr, 'x': logic.Expr,
               'sb': list(), 's': list(), 'b': list(),
               'p': list(), '-': list()}
        self._grid = logic.PropKB()

        self._place_start()
        self._place_wumpus()
        self._place_pits(pit_num)

    def _place_start(self):
        start: logic.Expr = choice(World._exprs)

        self._expr_dict['x'] = start
        self._expr_dict['-'].append(start)

    def _place_wumpus(self):
        wump: logic.Expr = choice(World._exprs)

        if wump in self._flattened_values:
            self._place_wumpus()
            return

        self._grid.tell(wump)
        self._expr_dict['w'] = wump
        self._prop_bind(wump, World._S)

    def _place_pits(self, pit_num: int):
        for i in range(pit_num):
            pit: logic.Expr = choice(World._exprs)

            if self._grid.ask_if_true(pit) or pit in self._flattened_values:
                self._place_pits(pit_num - i)
                return

            self._grid.tell(pit)
            self._expr_dict['p'].append(pit)
            self._prop_bind(pit, World._B)

    def _prop_bind(self, expr: logic.Expr, effect: logic.Expr):
        """
        Implicates the Expression correlating with the location of the Wumpus or the Pit with the
        Symbols (S or B) in a plus shaped area.

          S      B
        S W S  B P B
          S      B

        :param expr: Expression correlating with the location of the Wumpus or the Pit
        :param effect: Symbol to implicate with Expression. (S or B)
        """
        r, c = map(lambda x: int(x), expr.op[1:3])

        for i in [1, -1]:
            if (i > 0 and r < 3) or (i < 0 and r > 1):
                self._grid.tell(effect | '|' | logic.expr(f"P{r + i}{c}"))

            if (i > 0 and c < 3) or (i < 0 and c > 1):
                self._grid.tell(effect | '|' | logic.expr(f"P{r}{c + i}"))

    def _to_symbol(self, op: str) -> str:
        for key, val in self._expr_dict.items() \
                if not self.is_playing else \
                [(key, val) for key, val in self._expr_dict.items() if key not in ['w', 'p']]:

            if (isinstance(val, logic.Expr) and val.op == op) or \
                    (isinstance(val, List) and logic.expr(op) in val):
                return key.upper()

        return ' '

    def print(self):
        for r in reversed(range(1, 4)):
            for c in range(1, 4):
                symb: str = self._to_symbol(f"P{r}{c}")
                print(f"{'|' if c == 1 else ''}{symb: ^2}", end="|")
            print()

    def print_model(self):
        flag = True
        for expr in self._grid.clauses:
            if "(" not in str(expr):
                if flag:
                    print("W:", expr)
                    flag = not flag
                else:
                    print("P:", expr)
            else:
                print(expr)

    def move(self, direction: str):
        r, c = map(lambda x: int(x), self._expr_dict['x'].op[1:3])

        if direction == 'n' and r < 3:
            r += 1
        elif direction == 's' and r > 1:
            r -= 1
        elif direction == 'w' and c > 1:
            c -= 1
        elif direction == 'e' and c < 3:
            c += 1

        expr = logic.expr(f"P{r}{c}")

        if expr in self._expr_dict['p']:
            self._win_loss = False
            return

        if expr == self._expr_dict['w']:
            self._win_loss = True
            return

        self._expr_dict['x'] = expr

        if expr not in self._expr_dict['-']:
            self._expr_dict['-'].append(expr)

    def process_environment(self):
        expr: logic.Expr = self._expr_dict['x']

        if (self._grid.ask_if_true(World._S | "|" | expr)
                and self._grid.ask_if_true(World._B | "|" | expr)
                and expr not in self._expr_dict['sb']):
            self._expr_dict['sb'].append(expr)

        if self._grid.ask_if_true(World._S | "|" | expr):
            if expr not in self._expr_dict['s']:
                self._expr_dict['s'].append(expr)
            print("Something foul is in the air.")

        if self._grid.ask_if_true(World._B | "|" | expr):
            if expr not in self._expr_dict['b']:
                self._expr_dict['b'].append(expr)
            print("You feel a breeze.")

    @property
    def has_won(self):
        return bool(self._win_loss)

    @property
    def is_playing(self):
        return self._win_loss is None

    @property
    def _flattened_values(self) -> List[logic.Expr]:
        return flatten(self._expr_dict.values())


def flatten(lst: Iterable) -> list:
    flat = []
    for item in lst:
        if isinstance(item, Iterable):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat
