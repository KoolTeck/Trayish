"""  The system_tray module
    Initiate an instnce of the GTK module to create a system tray app
Returns:
    Nothing
"""
import os
import sys
import threading
import requests
from data_dialog import DataDialog
from gi.repository import Gtk, GdkPixbuf, GLib
import configparser
import gi
gi.require_version('Gtk', '3.0')

if getattr(sys, 'frozen', False):
    # Running from an executable produced by PyInstaller
    config_file = os.path.join(sys._MEIPASS, 'config.ini')
else:
    # Running as a script
    config_file = 'config.ini'
# Creates a ConfigParser instance
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file)

# Retrieve API keys
weather_api_key = config["API_KEYS"]["WEATHER_API_KEY"]
crypto_api_key = config["API_KEYS"]["CRYPTO_API_KEY"]


class SystemTrayApp(Gtk.Window):
    def __init__(self):
        """_summary_ the main class 
            Inherits from GTK.Window
        """
        # Create the main window
        super().__init__(title="Trayish")
        self.set_default_size(300, 200)
        self.set_border_width(10)
        # Create an overlay for the main window content
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)
        self.connect("delete-event", self.on_window_close)

        self.button_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.button_box.set_homogeneous(False)

        # Add the  hbox to the overlay, centered
        self.overlay.add_overlay(self.button_box)
        self.overlay.set_overlay_pass_through(self.button_box, True)

        # Load the icon using GdkPixbuf
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file("icon.png")

        # Create an AppIndicator
        self.indicator = Gtk.StatusIcon()
        self.indicator.set_from_pixbuf(icon_pixbuf)
        self.indicator.set_tooltip_text("Trayish")
        self.indicator.connect("activate", self.on_tray_icon_click)
        self.last_click_time = 0  # Track the time of the last click

        # Create a context menu for the tray icon
        self.menu = Gtk.Menu()

        # Button to fetch weather information (whether it will rain) in the tray icon
        weather_menu_item = Gtk.MenuItem.new_with_label("Check Weather")
        weather_menu_item.connect("activate", self.on_weather_button_clicked)
        self.menu.append(weather_menu_item)

        # Button to fetch cryptocurrency price information in the tray icon
        crypto_menu_item = Gtk.MenuItem.new_with_label("Check Crypto Price")
        crypto_menu_item.connect("activate", self.on_crypto_button_clicked)
        self.menu.append(crypto_menu_item)

        # Quit button
        self.quit_item = Gtk.MenuItem.new_with_label("Quit")
        self.quit_item.connect("activate", self.on_quit_clicked)
        self.menu.append(self.quit_item)

        self.menu.show_all()
        self.indicator.connect("popup-menu", self.on_popup_menu)

        # Create a GTK Box to hold buttons and preloader in the main window
        # Preloader
        self.preloader = Gtk.Spinner()
        self.preloader.set_size_request(24, 24)
        self.overlay.add_overlay(self.preloader)
        self.overlay.set_overlay_pass_through(self.preloader, True)
        self.preloader.hide()

        # Button to fetch weather information in the main window
        self.weather_button_main = Gtk.Button.new_with_label("Check weather")
        self.weather_button_main.set_size_request(50, 50)
        self.weather_button_main.connect(
            "clicked", self.on_weather_button_clicked)
        self.button_box.pack_start(self.weather_button_main, False, False, 0)

        # Button to fetch cryptocurrency price information in the main window
        self.crypto_button_main = Gtk.Button.new_with_label(
            "Check Crypto Price")
        self.crypto_button_main.set_size_request(50, 50)
        self.crypto_button_main.connect(
            "clicked", self.on_crypto_button_clicked)
        self.button_box.pack_start(self.crypto_button_main, False, False, 0)

        # Initialize variables for double-click detection
        self.double_click_timeout = 250

    def on_window_close(self, widget, event):
        # Hide the main window instead of quitting when the close button is clicked
        self.hide()
        return True

    def on_tray_icon_click(self, widget):
        """ Gets the current time

        Args:
            widget (GTK.widget): _description_
        """
        current_time = GLib.get_monotonic_time() // 1000  # Convert to milliseconds

        # Check for a double-click by measuring the time between clicks
        if current_time - self.last_click_time < self.double_click_timeout:
            self.on_tray_icon_double_click()
        else:
            self.on_tray_icon_single_click()
        self.last_click_time = current_time

    def on_tray_icon_single_click(self):
        #
        """Show or hide the main window when the tray icon is clicked
        """
        if self.get_visible():
            self.hide()
        else:
            self.show_all()

    def on_tray_icon_double_click(self):
        print("Double-clicked the tray icon!")

    def on_popup_menu(self, icon, button, time):
        # Show the context menu at the tray icon's position
        self.menu.popup(None, None, None, None, button, time)

    def on_quit_clicked(self, widget):
        """quits the app

        Args:
            widget (gtk widget): main widget
        """
        Gtk.main_quit()

    def on_weather_button_clicked(self, widget):
        """responds to click even on the weather_button
           starts the weather api asyncronously
        """
        # Show the preloader while fetching data
        self.preloader.start()
        self.preloader.show_all()

        # Runs the API request in a separate thread
        threading.Thread(target=self.fetch_weather_info_async).start()

    def on_crypto_button_clicked(self, widget):
        """responds to click even on the crypto_button
           starts the crypto api asyncronously
        """
        # Show the preloader while fetching data
        self.preloader.start()
        self.preloader.show_all()

        # Run the API request in a separate thread
        threading.Thread(target=self.fetch_crypto_info_async).start()

    def fetch_weather_info_async(self):
        try:
            weather_data = self.fetch_weather_info()
            GLib.idle_add(self.show_info_dialog,
                          "Weather Information", weather_data)
        except Exception as e:
            GLib.idle_add(self.show_error_dialog,
                          "Error Fetching Weather Data", str(e))

        # Stop the preloader
        self.preloader.stop()
        self.preloader.hide()

    def fetch_crypto_info_async(self):
        try:
            crypto_data = self.fetch_crypto_info()

            formatted_data = self.format_crypto_data(crypto_data)
            GLib.idle_add(self.show_crypto_dialog, formatted_data)
        except Exception as e:
            GLib.idle_add(self.show_error_dialog,
                          "Error Fetching Crypto Data", str(e))

        # Stop the preloader
        self.preloader.stop()
        self.preloader.hide()

    def format_crypto_data(self, crypto_data):
        """Format the crypto data for display in the dialog

        Args:
            crypto_data (_type_): the data to format

        Returns:
            string: the formatted data
        """
        formatted_data = []
        for crypto in crypto_data:
            crypto_name = crypto.get("name", "Unknown")
            crypto_price = crypto['quote']["USD"].get("price", "Unknown")
            crypto_change_last_hr = crypto['quote']["USD"].get(
                "percent_change_1h", "Unknown")
            formatted_data.append(
                f"Name: {crypto_name}  Price: {crypto_price}$  Change last hr: {crypto_change_last_hr}\n")
        return "\n".join(formatted_data)

    def show_crypto_dialog(self, crypto_data):
        """Shows the cryptocurrency data in a dialog

        Args:
            text (_type_): crypto_data
        """
        dialog = DataDialog(None, crypto_data)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            print("OK button clicked in crypto dialog")

    def fetch_weather_info(self):
        """fetches the weather info

        Returns:
            string: the weather info from the api endpoint
        """
        try:
            user_location = self.get_location()
            city = user_location.get("city", "Unknown")
            country = user_location.get("country", "Unknown")
            params = {
                'access_key': weather_api_key,
                'query': f'{city}, {country}'
            }
            api_result = requests.get(
                'http://api.weatherstack.com/current', params)

            api_response = api_result.json()

            weather_report = api_response.get("current")
            return f"Currently in {city}, {country} it is {weather_report['weather_descriptions']} at {weather_report['temperature']}degrees ✨"

        except Exception as err:
            return str(err)

    def fetch_crypto_info(self):
        """fetches the crypto info

        Returns:
            dict: the crypto info from the api endpoint
        """
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        parameters = {
            'start': '1',
            'limit': '50',
            'convert': 'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': crypto_api_key,
        }
        response = requests.get(url, params=parameters, headers=headers)
        data = response.json().get("data", "Unknown")
        response.raise_for_status()
        return data

    def get_location(self):
        """gets user location via there IP address

        Returns:
            dict: the users location object
        """
        try:
            response = requests.get("https://ipinfo.io")
            data = response.json()
            return data
        except Exception as err:
            return str(data)

    def show_info_dialog(self, title, message):
        """shows info to user in a dialog
        Args:
            title (str): the title of the dialog
            message (str): the dialog message
        """
        dialog = Gtk.MessageDialog(
            parent=None, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=message)
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()

    def show_error_dialog(self, title, message):
        """shows error info to user in a dialog
        Args:
            title (str): the title of the error
            message (str): the error message
        """
        dialog = Gtk.MessageDialog(
            parent=None, flags=0, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=message)
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    app = SystemTrayApp()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()
