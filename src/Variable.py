from dataclasses import dataclass, fields
from typing import Union, Type


SUPERSCRIPTS = ['⁰', '¹',  '²',  '³',  '⁴',  '⁵',  '⁶',  '⁷',  '⁸',  '⁹']


@dataclass
class Unit:
    """
    Класс единиц измерений
    """
    m: int = 0
    s: int = 0
    kg: int = 0
    Hz: int = 0
    B: int = 0

    def __str__(self):
        """
        Красиво выводит единицы измерения
        """
        up = []
        down = []
        down_len = 0
        for name, power in self.__dict__.items():
            if power > 1:
                up.append(name + "".join(SUPERSCRIPTS[i] for i in map(int, str(power))))
            elif power == 1:
                up.append(name)
            elif power == -1:
                down.append(name)
                down_len += 1
            elif power < -1:
                down.append(name + "".join(SUPERSCRIPTS[i] for i in map(int, str(-power))))
                down_len += 1
        if down_len == 0:
            return '⋅'.join(up)
        elif down_len == 1:
            return f"{'⋅'.join(up)}/{'⋅'.join(down)}"
        else:
            return f"{'⋅'.join(up)}/({'⋅'.join(down)})"


# TODO: использовать kw_only=True, чтобы избежать =None в дочерних классах
@dataclass
class _Variable:
    """
    Базовый класс переменной
    """
    name: str
    unit: Unit
    description: str = ''
    type: Union[Type[int], Type[float]] = float


@dataclass
class Variable(_Variable):
    """
    Класс переменной
    """
    value: Union[int, float] = None


@dataclass
class Setting(_Variable):
    """
    Класс настройки
    """
    default_value: Union[int, float] = None

