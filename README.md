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

