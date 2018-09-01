from PySide import QtCore, QtGui

class DialogUtil:

	@staticmethod
	def errorMessage(message):
		dialog=QtGui.QMessageBox(QtGui.QMessageBox.Critical,'Error',message)
		dialog.setWindowModality(QtCore.Qt.ApplicationModal)
		dialog.exec_()
