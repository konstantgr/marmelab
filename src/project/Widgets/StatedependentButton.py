from ..Project import PState
from PyQt6.QtWidgets import QPushButton


class StateDepPushButton(QPushButton):
    """
    Кнопка, которая зависит от статуса
    """
    def __init__(self, state: PState, *args, **kwargs):
        super(StateDepPushButton, self).__init__(*args, **kwargs)
        self.state = state
        self.update_state()
        self.state.changed_signal.connect(self.update_state)

    def update_state(self):
        """Обновить возможность нажать на кнопку"""
        self.setEnabled(bool(self.state))
