from PyQt5.QtWidgets import QApplication

from gui.window import (
    Window
)
from sgi.world import (
    World
)

app = QApplication([])

world = World()
window = Window(world)

app.exec_()
