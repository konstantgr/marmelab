class EmptySignal:
    """
    Реализация пустого сигнала по аналогии с PyQt
    """
    def emit(self, *args, **kwargs):
        pass

    def connect(self, *args, **kwargs):
        pass

    def disconnect(self, *args, **kwargs):
        pass

    def __getitem__(self, *args, **kwargs):
        return self