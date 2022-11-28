from PyQt6.QtCore import Qt, QThreadPool, QRunnable, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from pyqt_app import analyzator, scanner
from src.analyzator.analyzator_parameters import FrequencyParameters, FrequencyTypes

from src.scanner import BaseAxes
import logging
logger = logging.getLogger()


class Worker(QRunnable):
    '''
    Worker thread
    '''

    @pyqtSlot()
    def run(self):
        '''
        Your code goes in this function
        '''

        sp = ['S11', 'S23']
        fp = FrequencyParameters(
            1000, 5000, FrequencyTypes.MHZ, 200
        )
        pos = BaseAxes(x=1000, y=1000)
        d_pos = BaseAxes(x=100)
        with open('results.txt', 'w') as f:
            for i in range(10):
                scanner.goto(pos)
                logger.info(f'pos: {scanner.position()}')
                pos += d_pos
                results = analyzator.get_scattering_parameters(
                    sp, fp, None
                )
                f.write(",".join(results['S11']))
                f.write("\n")
                # print(results['S11_freq'], results['S11'])


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
        self.threadpool = QThreadPool()
        button_go.clicked.connect(self.button_go)

    def button_go(self):
        worker = Worker()
        self.threadpool.start(worker)


if __name__ == "__main__":
    analyzator.connect()
    # import matplotlib.pyplot as plt
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
        # plt.plot(x, y, label=str(s))

    # plt.legend()
    # plt.show()
    analyzator.disconnect()
