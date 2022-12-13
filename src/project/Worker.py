from PyQt6.QtCore import QRunnable


class Worker(QRunnable):
    """
    Класс воркера
    """
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()

        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Запуск функции
        """
        self.func(*self.args, **self.kwargs)
