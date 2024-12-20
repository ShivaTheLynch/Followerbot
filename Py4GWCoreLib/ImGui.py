import Py4GW
import PyImGui

from .Overlay import Overlay


class ImGui:
    def show_tooltip(text: str):
        """
        Purpose: Display a tooltip with the provided text.
        Args:
            text (str): The text to display in the tooltip.
        Returns: None
        """
        if PyImGui.is_item_hovered():
            PyImGui.begin_tooltip()
            PyImGui.text(text)
            PyImGui.end_tooltip()


    def toggle_button(label: str, v: bool, width=0, height =0) -> bool:
        """
        Purpose: Create a toggle button that changes its state and color based on the current state.
        Args:
            label (str): The label of the button.
            v (bool): The current toggle state (True for on, False for off).
        Returns: bool: The new state of the button after being clicked.
        """
        clicked = False

        if v:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button, (0.153, 0.318, 0.929, 1.0))  # On color
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (0.6, 0.6, 0.9, 1.0))  # Hover color
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive, (0.6, 0.6, 0.6, 1.0))
            if width != 0 and height != 0:
                clicked = PyImGui.button(label, width, height)
            else:
                clicked = PyImGui.button(label)
            PyImGui.pop_style_color(3)
        else:
            if width != 0 and height != 0:
                clicked = PyImGui.button(label, width, height)
            else:
                clicked = PyImGui.button(label)

        if clicked:
            v = not v

        return v

    def table(title, headers, data):
        """
        Purpose: Display a table using PyImGui.
        Args:
            title (str): The title of the table.
            headers (list of str): The header names for the table columns.
            data (list of values or tuples): The data to display in the table. 
                - If it's a list of single values, display them in one column.
                - If it's a list of tuples, display them across multiple columns.
        Returns: None
        """
        if len(data) == 0:
            return  # No data to display

        first_row = data[0]
        if isinstance(first_row, tuple):
            num_columns = len(first_row)
        else:
            num_columns = 1  # Single values will be displayed in one column

        # Start the table with dynamic number of columns
        if PyImGui.begin_table(title, num_columns, PyImGui.TableFlags.Borders):
            for i, header in enumerate(headers):
                PyImGui.table_setup_column(header)
            PyImGui.table_headers_row()

            for row in data:
                PyImGui.table_next_row()
                if isinstance(row, tuple):
                    for i, cell in enumerate(row):
                        PyImGui.table_set_column_index(i)
                        PyImGui.text(str(cell))
                else:
                    PyImGui.table_set_column_index(0)
                    PyImGui.text(str(row))

            PyImGui.end_table()


    def DrawTextWithTitle(title, text_content, lines_visible=10):
        """
        Function to display a title and multi-line text in a scrollable and configurable area.
        Width is based on the main window's width with a margin.
        Height is based on the number of lines_visible.
        """
        margin = 20
        max_lines = 10
        line_padding = 4  # Add a bit of padding for readability

        # Display the title first
        PyImGui.text(title)

        # Get the current window size and adjust for margin to calculate content width
        window_width = PyImGui.get_window_size()[0]
        if window_width < 100:
            window_width = 100
        content_width = window_width - margin
        text_block = text_content + "\n" + Py4GW.Console.GetCredits()

        # Split the text content into lines by newline
        lines = text_block.split("\n")
        total_lines = len(lines)

        # Limit total lines to max_lines if provided
        if max_lines is not None:
            total_lines = min(total_lines, max_lines)

        # Get the line height from ImGui
        line_height = PyImGui.get_text_line_height()
        if line_height == 0:
            line_height = 10  # Set default line height if it's not valid

        # Add padding between lines and calculate content height based on visible lines
        content_height = (lines_visible * line_height) + ((lines_visible - 1) * line_padding)
        if content_height< 100:
            content_height = 100

        # Set up the scrollable child window with dynamic width and height
        if PyImGui.begin_child(f"ScrollableTextArea_{title}", size=(content_width, content_height), border=True, flags=PyImGui.WindowFlags.HorizontalScrollbar):

            # Get the scrolling position and window size for visibility checks
            scroll_y = PyImGui.get_scroll_y()
            scroll_max_y = PyImGui.get_scroll_max_y()
            window_size_y = PyImGui.get_window_size()[1]
            window_pos_y = PyImGui.get_cursor_pos_y()

            # Display each line only if it's visible based on scroll position
            for index, line in enumerate(lines):
                # Calculate the Y position of the line based on index
                line_start_y = window_pos_y + (index * (line_height + line_padding))

                # Calculate visibility boundaries
                line_end_y = line_start_y + line_height

                # Skip rendering if the line is above or below the visible area
                if line_end_y < scroll_y or line_start_y > scroll_y + window_size_y:
                    continue

                # Render the line if it's within the visible scroll area
                PyImGui.text_wrapped(line)
                PyImGui.spacing()  # Add spacing between lines for better readability

            # End the scrollable child window
            PyImGui.end_child()


    class WindowModule:
        def __init__(self, module_name, window_name="", window_size=(100,100), window_pos=(0,0), window_flags=PyImGui.WindowFlags.NoFlag):
            self.module_name = module_name
            self.window_name = window_name if window_name else module_name
            self.window_size = window_size
            if window_pos == (0,0):
                overlay = Overlay()
                screen_width, screen_height = overlay.GetDisplaySize().x, overlay.GetDisplaySize().y
                #set position to the middle of the screen
                self.window_pos = (screen_width / 2 - window_size[0] / 2, screen_height / 2 - window_size[1] / 2)
            else:
                self.window_pos = window_pos
            self.window_flags = window_flags
            self.first_run = True