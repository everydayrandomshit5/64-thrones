## gui.rpy - High-Fantasy Noble Gold & Deep Violet Theme
## 64-Thrones: High-Glamour Edition (v3.2)

init -1 python:
    gui.init(1920, 1080)

## Theme Color Palette
define gui.accent_color = '#EBC364'       # Solar Gold
define gui.idle_color = '#C8C0D8'         # Muted Violet Silver
define gui.hover_color = '#FFE899'        # Brilliant Solar Highlight
define gui.selected_color = '#AF78E6'     # Umbral Violet
define gui.insensitive_color = '#605870'  # Dim Slate

## Text Colors
define gui.text_color = '#FBF8F0'         # Alabaster White
define gui.interface_text_color = '#E6E0F0'
define gui.muted_color = '#A098B5'

## Dialogue Window
define gui.textbox_height = 240
define gui.textbox_yalign = 1.0

define gui.name_xpos = 360
define gui.name_ypos = 0
define gui.name_xalign = 0.0
define gui.name_text_size = 32

define gui.dialogue_xpos = 360
define gui.dialogue_ypos = 50
define gui.dialogue_width = 1200
define gui.dialogue_text_size = 28

## Buttons
define gui.button_text_size = 24
define gui.button_text_idle_color = gui.idle_color
define gui.button_text_hover_color = gui.hover_color
define gui.button_text_selected_color = gui.selected_color

## Choice Buttons
define gui.choice_button_width = 1040
define gui.choice_button_height = None
define gui.choice_button_text_size = 28

## Navigation & Menus
define gui.navigation_xpos = 80
define gui.main_menu_title_xpos = 120
