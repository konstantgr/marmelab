from ..Project import PState
from PyQt6.QtWidgets import QPushButton, QCheckBox
from PyQt6.QtGui import QAction


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

class StateDepQAction(QAction):
    """
    Action, которое зависит от статуса
    """
    def __init__(self, state: PState, *args, **kwargs):
        super(StateDepQAction, self).__init__(*args, **kwargs)
        self.state = state
        self.update_state()
        self.state.changed_signal.connect(self.update_state)

    def update_state(self):
        """Обновить возможность нажать на кнопку"""
        self.setEnabled(bool(self.state))


class StateDepCheckBox(QCheckBox):
    """
    Чекбокс, который зависит от статуса
    """
    def __init__(self, state: PState, *args, **kwargs):
        super(StateDepCheckBox, self).__init__(*args, **kwargs)
        self.state = state
        self.update_state()
        self.state.changed_signal.connect(self.update_state)

    def update_state(self):
        """Обновить возможность нажать на кнопку"""
        self.setEnabled(bool(self.state))
