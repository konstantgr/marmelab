from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from pyqt_app import analyzator
from src.analyzers.analyzer_parameters import FrequencyParameters, FrequencyTypes

#import matplotlib.pyplot as plt

class Test(QWidget):
    def __init__(self):
        super(Test, self).__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
        button_go = QPushButton("Go")
        button_download = QPushButton("Download")
        layout.addWidget(button_go)
        layout.addWidget(button_download)

        button_go.clicked.connect(self.button_go)

    def button_go(self):
        analyzator.connect()

        sp = ['S11', 'S23']
        fp = FrequencyParameters(
            1000, 5000, FrequencyTypes.MHZ, 200
        )
        results = analyzator.get_scattering_parameters(
            sp, fp
        )
        print(results['S11_freq'], results['S11'])


if __name__ == "__main__":
    analyzator.connect()

    sp = ['S11', 'S23']
    fp = FrequencyParameters(
        1000, 5000, FrequencyTypes.MHZ, 200
    )
    results = analyzator.get_scattering_parameters(
        sp, fp, None
    )
    print(results['S11_freq'], results['S11'])
    for s in sp:
        x, y = results[f'{s}_freq'], results[f'{s}']
        plt.plot(x, y, label=str(s))

    plt.legend()
    plt.show()
    analyzator.disconnect()
