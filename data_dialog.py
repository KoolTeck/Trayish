import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class DataDialog(Gtk.Dialog):
    def __init__(self, parent, data):
        Gtk.Dialog.__init__(self, "Live Crypto Update", parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(400, 300)
        self.set_default_response(Gtk.ResponseType.OK)

        content_area = self.get_content_area()

        # Creates a scrolled window to accommodate the text view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        content_area.pack_start(scrolled_window, True, True, 0)  # Expand and fill

        # Create a text view to display the data
        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_buffer = text_view.get_buffer()
        text_buffer.set_text(data)

        scrolled_window.add(text_view)
        self.show_all()
