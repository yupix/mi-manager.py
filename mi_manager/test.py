import py_cui

from mi_manager.widget.create_instance import CreateInstanceCUI


class SimpleTodoList:

    def __init__(self, master: py_cui.PyCUI):
        self.master = master
        # row_span = margin-top
        self.text_block = self.master.add_text_block('Info', 0, 0, row_span=7, column_span=2)
        self.text_block.set_text(self.get_logo())
        menu_list = ['Create instance', 'Manage instance']
        self.action_menu = self.master.add_scroll_menu('Menu', 0, 2, row_span=7, column_span=2)
        self.action_menu.add_item_list(menu_list)
        self.action_menu.add_key_command(py_cui.keys.KEY_ENTER, self.menu_action)

    def menu_action(self):
        if self.action_menu.get() == 'Create instance':
            CreateInstanceCUI(self.master)

    @staticmethod
    def get_logo() -> str:
        return "███╗   ███╗██╗    ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗\n" \
               "████╗ ████║██║    ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗\n" \
               "██╔████╔██║██║    ██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝\n" \
               "██║╚██╔╝██║██║    ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗\n" \
               "██║ ╚═╝ ██║██║    ██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║\n" \
               "╚═╝     ╚═╝╚═╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝"


# Create the CUI with 7 rows 6 columns, pass it to the wrapper object, and start it
root = py_cui.PyCUI(7, 6)
root.set_title('CUI TODO List')
s = SimpleTodoList(root)
root.start()
