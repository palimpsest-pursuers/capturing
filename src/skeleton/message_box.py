from PyQt5.QtWidgets import QMessageBox, QWidget

"""
Creates and displays message and error dialogs
Written by Sai Keshav Sasanapuri
"""

class MessageBox:
    """
    A utility class for showing message and error dialogs.
    """
    
    def __init__(self, parent):
        """
        Initializes the message box class.

        Args:
            parent: The parent widget (main window).
        """
        self.parent = parent
    
    def show_info(self, title="Information", message="Operation completed successfully."):
        """
        Shows an informational message box.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
        """
        QMessageBox.information(self.parent, title, message)

    def show_warning(self, title="Warning", message="Please check your input."):
        """
        Shows a warning message box.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
        """
        QMessageBox.warning(self.parent, title, message)

    def show_error(self, title="Error", message="An error has occurred."):
        """
        Shows a critical error message box.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
        """
        QMessageBox.critical(self.parent, title, message)

    def show_question(self, title="Confirm", message="Are you sure you want to proceed?") -> bool:
        """
        Shows a question dialog box with Yes/No options.

        Args:
            title (str): The title of the dialog.
            message (str): The message to display.

        Returns:
            bool: True if user clicked Yes, False otherwise.
        """
        reply = QMessageBox.question(self.parent, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes
