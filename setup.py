from cx_Freeze import setup, Executable

executables = [Executable("trayish.py")]

setup(
    name="Trayish",
    version="1.0",
    description="tray app",
    executables=executables
)
