from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt

"""
Creates and maintains a progress widget
Written by Sai Keshav Sasanapuri
"""

class ProgressDialog(QProgressDialog):
    """
    A progress dialog that displays a busy indicator.

    This dialog is set with a range of (0, 0) so that it shows a constant,
    animated busy state. Custom range can be given to show progress as a percentage.
    """

    def __init__(self, parent, message="Processing, please wait..."):
        """
        Initializes the progress dialog.

        Args:
            parent: The parent widget (main window).
            message (str): The message to display in the progress box.
        """
        super().__init__(message, None, 0, 10, parent)
        self.setWindowTitle("Operation Progress")
        self.setWindowModality(Qt.WindowModal)
        self.setCancelButton(None)  # Remove the cancel button
        self.setRange(0, 0)  # Show immediately
        self.close()

    def start(self, message="Loading"):
        """
        Displays the progress dialog.
        """
        self.setLabelText(message)
        self.show()

    def stop(self):
        """
        Closes the progress dialog.
        """
        self.close()
