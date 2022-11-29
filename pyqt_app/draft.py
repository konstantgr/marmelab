# importing libraries
from PyQt6.QtWidgets import *
import sys

# creating a class
# that inherits the QDialog class
class Window(QDialog):

	# constructor
	def __init__(self):
		super(Window, self).__init__()

		# setting window title
		self.setWindowTitle("Python")

		# setting geometry to the window
		self.setGeometry(100, 100, 300, 400)

		# creating a group box
		self.formGroupBox = QGroupBox("Form 1")

		# creating spin box to select age
		self.ageSpinBar = QSpinBox()

		# creating combo box to select degree
		self.degreeComboBox = QComboBox()

		# adding items to the combo box
		self.degreeComboBox.addItems(["BTech", "MTech", "PhD"])

		# creating a line edit
		self.nameLineEdit = QLineEdit()

		# calling the method that create the form
		self.createForm()


		# creating a dialog button for ok and cancel
		#self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

		# adding action when form is accepted
		#self.buttonBox.accepted.connect(self.getInfo)

		# adding action when form is rejected
		self.button = QPushButton("ok")
		self.button.clicked.connect(self.getInfo)


		# creating a vertical layout
		mainLayout = QVBoxLayout()

		# adding form group box to the layout
		mainLayout.addWidget(self.formGroupBox)

		# adding button box to the layout
		mainLayout.addWidget(self.button)

		# setting lay out
		self.setLayout(mainLayout)

	# get info method called when form is accepted
	def getInfo(self):

		# printing the form information
		print(format(self.nameLineEdit.text()))
		print("Age : {0}".format(self.ageSpinBar.text()))
		print("Degree : {0}".format(self.degreeComboBox.currentText()))

		# closing the window
		self.close()

	# creat form method
	def createForm(self):

		# creating a form layout
		layout = QFormLayout()

		# adding rows
		# for name and adding input text
		layout.addRow(QLabel("Name"), self.nameLineEdit)

		# for degree and adding combo box
		layout.addRow(QLabel("Degree"), self.degreeComboBox)

		# for age and adding spin box
		layout.addRow(QLabel("Age"), self.ageSpinBar)

		# setting layout
		self.formGroupBox.setLayout(layout)


# main method
if __name__ == '__main__':

	# create pyqt5 app
	app = QApplication(sys.argv)

	# create the instance of our Window
	window = Window()

	# showing the window
	window.show()

	# start the app
	sys.exit(app.exec())
