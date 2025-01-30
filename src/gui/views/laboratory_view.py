from PySide6.QtWidgets import QLabel, QVBoxLayout
from .base_view import BaseView

class LaboratoryView(BaseView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LaboratoryView")
    
    def setup_ui(self):
        label = QLabel("Laboratory View")
        label.setStyleSheet("font-size: 24px;")
        self.main_layout.addWidget(label)
        self.main_layout.addStretch()
