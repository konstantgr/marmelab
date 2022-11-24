from PyQt6.QtWidgets import QFrame


class BasePanel(QFrame):
    """
    This class makes base construction for all panel
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.Shape.StyledPanel)