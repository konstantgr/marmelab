# ITMO-PROJ-FALL-PT

## Poetry
Poetry поможет синхронизировать версии пакетов, которые используются при разработки.
Чтобы уставновить, можно использовать

```
pip install poetry
```
Также можно найти в интернете, как подключить poetry к пайчарму.


После установки, в папке с проектом, необходимо использовать 
```
poetry install
```
для установки всех библиотек нужной версии, которые указаны в файле `pyproject.toml`.


Чтобы добавить новую библиотеку в проект, вместо `pip install <X>` нужно использовать 
```
poetry add <X>
```
Если эта библиотека нужна только для разработки, например `pytest`, то следуюет указать ключ `--dev`.


Чтобы удалить библиоеку:
```
poetry remove <X>
```
Ключ `--dev` иммет тот же смысл.

Чтобы запустить какой-то кусок, вместо `python main.py` следует использовать
```
poetry run python main.py
```

Запуск сервера при помощи uvicorn выглядит так 
```
poetry run uvicorn web_app:app
```

Прочитать про poetry [хабр](https://habr.com/ru/post/593529/) и [документация](https://python-poetry.org/docs/cli/)

## Scanner

Пример подключения сканера:

```python
from src.scanner.TRIM import TRIMScanner

sc = TRIMScanner(ip="127.0.0.1", port=9000)
sc.connect()
```

Запуск эмулятора (TBD)
```python
from tests.TRIM_emulator import run
run(blocking=False)
```
и после этого кода можно подключить сам сканер.
Кроме того, можно запустить через poetry: `poetry run server` (работает очень плохо). Можно через питон `python .\tests\TRIM_emulator.py
`

Отправить команду на перемещение на новую точку:

```python
from src.scanner import Position

new_position = Position(x=100, y=200)
sc.goto(new_position)
```
Передать дефолтные настройки

```python
from src.scanner.TRIM import DEFAULT_SETTINGS

sc.set_settings(DEFAULT_SETTINGS, )
```

Узнать координаты сканера
```python
current_position = sc.position()

print('x: ', current_position.x)
print('y: ', current_position.y)
print('z: ', current_position.z)
```
Аналогично можно узнать скорость, ускорение и замедление. 

## pytest

```commandline
poetry run pytest
```

## Стек

* Python
* Poetry как менеджер пакетов
* PyQT для создания десктопного приложения
* Pytest для тестов

## Создание моделей и виджетов

### Модель

Все модели должны наследоваться от классов, определенных в `src\project\Project.py` (то есть `PScanner`, `PPath`, `PExperiment` и тд).
В создаваемом классе модели необходимо реализовать все абстрактные методы, существующие у класса-родителя.
У всех моделей, (кромер `Pscanner` и `PAnalyzer`, вообще говоря у всех, которые является дочерним классом класса `PBase`) долен быть реализован метод класса `reproduce`.
Этот метод принимает имя `name` и проект `project`, экземпляр класса `Project`, и возвращает экземпляр реализуемой модели.
Пример реализации игрушечного пути:

```python
from ..Project import PPath, ProjectType
import numpy as np

class ToyPath(PPath):
    def __init__(self, name: str):
        super(ToyPath, self).__init__(name=name)

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'ToyPath':
        return cls(name=name)
    
    # Реализация абстрактного метода. Возвращает название осей координат
    def get_points_axes(self) -> tuple[str, ...]:
        return "y", "x"
    
    # Реализация абстрактного метода. Возвращает точки, по которым необходимо ехать
    def get_points_ndarray(self) -> np.ndarray:
        return np.array([[1, 0], [1, 1], [0, 1]])
```
В этом примере аргумент `project` не используется.
Он может понадобится, например, чтобы использовать сканер в модели:

```python
from ..Project import PPath, ProjectType, PScanner
import numpy as np

class ToyPath(PPath):
    def __init__(self, name: str, scanner: PScanner):
        super(ToyPath, self).__init__(name=name)
        self.scanner = scanner

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'ToyPath':
        return cls(name=name, scanner=project.scanner)
    
    # Реализация абстрактного метода. Возвращает название осей координат
    def get_points_axes(self) -> tuple[str, ...]:
        return "y", "x"
    
    # Реализация абстрактного метода. Возвращает точки, по которым необходимо ехать
    def get_points_ndarray(self) -> np.ndarray:
        # зачем-то получаем реальные текущие сканера
        current_position = self.scanner
        # ...
        return np.array([[1, 0], [1, 1], [0, 1]])
```

Идеология создания модели:
* Модель должна хранить данные, которые ввел пользователь.
Это может быть кастомная реализация в разумных пределах.
Главное, чтобы данные хранились именно в модели.
* Все алгоритмы (бизнес-логика) должны быть реализованы в модели.
Для каждой операции с данными создается отдельная функция.
Можно использовать сеттеры (имеется в виду функция, которая называется "set_...", без излишеств).
* Модель должна технически запускаться без интерфейса, использоваться без интерфейса.
* Вьюшки взаимодействуют с моделью при помощи вызова функций модели.
Пример: если пользователь поставил какую-то галочку, то вьюшка вызовет функцию модели: `self.model.set_checkbox_state(state: bool)`.
* Модель рассказывает вьюшкам о том, что что-то нужно перерисовать при помощи сигналов.
Пример: если пользователь поставил какую-то галочку, то вьюшка вызовет функцию модели: `self.model.set_checkbox_state(state: bool)`, внутри этой функции модель обновляет значение `self.checkbox_state = state` и делает эмит сигнала, например `self.signals.display_changed.emit()`.
Все вьюшки, которые подписались на данный сигнал, получат информацию о том, что что-то поменялось, и спросят у модели: `self.model.checkbox_state` и в зависимоти от логики вьюшки что-то перерисуют.
* Одна модель может иметь несколько вьюшек, но каждой вьюшке соответвует одна модель!

### Вью

Чтобы создать вьюшку для этой модели, необходимо отнаследоваться от класса `BaseView`.
