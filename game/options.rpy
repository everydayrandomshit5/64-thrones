## options.rpy - Project Configurations for 64-Thrones: High-Glamour Edition (v3.2)
## Target Resolution: 1920x1080 Widescreen HD

define config.name = _("64-Thrones: High-Glamour Edition")
define gui.show_name = True
define config.version = "1.0"
define build.name = "64-thrones-sfwv2"

## Audio channels
define config.has_sound = True
define config.has_music = True
define config.has_voice = True

## Window Management
define config.window = "auto"
define config.window_show_transition = Dissolve(.2)
define config.window_hide_transition = Dissolve(.2)

## Save directory
define config.save_directory = "64-thrones-sfwv2-saves"

## Default transitions
define config.enter_transition = dissolve
define config.exit_transition = dissolve
define config.after_load_transition = dissolve
define config.end_game_transition = fade
