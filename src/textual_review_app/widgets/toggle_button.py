from textual.reactive import reactive
from textual.widgets import Button


class ToggleButton(Button):
    checked = reactive(False)

    def on_button_pressed(self):
        self.checked = not self.checked
        self.set_class(self.checked, 'responsebtn-checked')

    def set_selected(self, selected: bool):
        self.checked = selected
        self.set_class(self.checked, 'responsebtn-checked')
