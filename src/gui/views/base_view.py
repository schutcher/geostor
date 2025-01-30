from PySide6.QtWidgets import QWidget, QVBoxLayout

class BaseView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
    
    def setup_ui(self):
        """Override this method in subclasses to setup the view's UI"""
        pass
    
    def on_show(self):
        """Called when the view becomes visible"""
        pass
    
    def on_hide(self):
        """Called when the view becomes hidden"""
        pass
