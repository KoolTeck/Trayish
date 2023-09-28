## Trayish

This is a solution to zuri placement recruitment task two

## Problem statement

Using GTK-3, create a small system tray application that shows you if it will rain when double-clicked. Put it on your GitHub as one of your portfolio projects. You can think of any other nifty functionality that involves calling an API instead: e.g. show a crypto price, show the Naira rate, or any other cool idea you have. Make it part of your portfolio.

## Solution

The Gtk-3 application was implemented with calling two api endpoints that fetches current weather and cryptocurrency data. To get started with app:

- Get the installer for window version here [trayish](https://drive.google.com/file/d/1SfKkv3K9Xg5f2YbII-IeOKjOgPs9Mykw/view?usp=drive_link) or :

- clone the repo

- <code>git clone https://github.com/KoolTeck/Trayish.git</code>

- <code>cd Trayish</code>

- create a 'config.ini' file at the root of the project to access the Api key used in the app

- grab the keys here [api_keys](https://docs.google.com/document/d/1kcnbLQgzGm_XzMoeufLYEgX_Fj6ZJdfQ7YRTT_zg2wc/edit?usp=sharing)

- run the tray.py file

The app should load to the system tray

Note: I was only able to package the project with window installer because I developed it using window system, time wont permit me to port the app to other platform hence the need to submit.
