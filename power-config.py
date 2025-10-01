# ~/.config/qtile/config.py
# Qtile ALT-центрик, X11
# Зависимости по желанию: rofi, picom, nm-applet, blueman-applet, JetBrainsMono Nerd Font

from libqtile import bar, layout, widget, hook
from libqtile.config import Key, Group, Match, Screen, ScratchPad, DropDown
from libqtile.lazy import lazy
import os, subprocess

# ── Параметры ──────────────────────────────────────────────────────────────────
mod = "mod1"                   # ALT
terminal = "alacritty"
launcher = "rofi -show drun"
browser = "firefox"
fileman = "thunar"

# ── Клавиши ────────────────────────────────────────────────────────────────────
keys = [
    # Приложения
    Key([mod], "Return", lazy.spawn(terminal), desc="Terminal"),
    Key([mod], "d", lazy.spawn(launcher), desc="Launcher"),
    Key([mod], "b", lazy.spawn(browser), desc="Browser"),
    Key([mod], "e", lazy.spawn(fileman), desc="File manager"),

    # Окна и фокус (vim-стрелки)
    Key([mod], "h", lazy.layout.left(), desc="Focus left"),
    Key([mod], "l", lazy.layout.right(), desc="Focus right"),
    Key([mod], "j", lazy.layout.down(), desc="Focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Focus up"),
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(), desc="Move left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(), desc="Move right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move up"),

    # Размеры/раскладка
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(), desc="Grow right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow up"),
    Key([mod], "equal", lazy.layout.normalize(), desc="Normalize sizes"),
    Key([mod], "Tab", lazy.next_layout(), desc="Next layout"),

    # Окно
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Fullscreen"),
    Key([mod], "space", lazy.window.toggle_floating(), desc="Toggle float"),
    Key([mod], "w", lazy.window.kill(), desc="Kill"),
    Key([mod], "y", lazy.window.toggle_minimize(), desc="Minimize"),

    # Экраны/бар
    Key([mod], "comma", lazy.prev_screen(), desc="Prev screen"),
    Key([mod], "period", lazy.next_screen(), desc="Next screen"),
    Key([mod], "minus", lazy.hide_show_bar("top"), desc="Toggle bar"),

    # Сервис
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload config"),
    Key([mod, "shift"], "q", lazy.shutdown(), desc="Logout Qtile"),
    Key([mod], "p", lazy.spawncmd(), desc="Spawn command"),
]

# ── Группы (рабочие столы) ─────────────────────────────────────────────────────
groups = [
    Group("1", label="", matches=[Match(wm_class="Alacritty")]),
    Group("2", label="", matches=[Match(wm_class="firefox")]),
    Group("3", label=""),
    Group("4", label="", matches=[Match(wm_class="TelegramDesktop")]),
    Group("5", label=""),
    Group("6", label=""),
    Group("7", label=""),
    Group("8", label=""),
    Group("9", label=""),
]

for i, g in enumerate(groups, 1):
    keys += [
        Key([mod], str(i), lazy.group[g.name].toscreen()),
        Key([mod, "shift"], str(i), lazy.window.togroup(g.name, switch_group=True)),
    ]

# ── ScratchPad (quake-терминал и пр.) ──────────────────────────────────────────
groups += [
    ScratchPad("scratch", [
        DropDown("term", terminal, width=0.9, height=0.5, x=0.05, y=0.1, opacity=0.95),
        DropDown("mixer", "pavucontrol", width=0.5, height=0.6, x=0.25, y=0.2, opacity=0.95),
    ])
]
keys += [
    Key([mod], "s", lazy.group["scratch"].dropdown_toggle("term"), desc="Scratch terminal"),
    Key([mod, "shift"], "s", lazy.group["scratch"].dropdown_toggle("mixer"), desc="Audio mixer"),
]

# ── Лэйауты ────────────────────────────────────────────────────────────────────
layout_theme = dict(margin=8, border_width=2, border_focus="#8bd5ca", border_normal="#444444")
layouts = [
    layout.MonadTall(**layout_theme),
    layout.Columns(**layout_theme),
    layout.Max(),
    layout.Floating(**layout_theme),
]

floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="pavucontrol"),
        Match(wm_class="blueman-manager"),
        Match(wm_class="nm-connection-editor"),
        Match(wm_class="Lxappearance"),
        Match(title="Confirmation"),
        Match(title="Qalculate!"),
        Match(role="pop-up"),
    ],
    border_focus="#8bd5ca",
)

# ── Внешний вид баров ──────────────────────────────────────────────────────────
widget_defaults = dict(font="JetBrainsMono Nerd Font", fontsize=12, padding=6)
extension_defaults = widget_defaults.copy()

def top_bar(primary: bool) -> bar.Bar:
    items = [
        widget.CurrentLayoutIcon(scale=0.7),
        widget.GroupBox(
            highlight_method="block",
            rounded=False,
            this_current_screen_border="#8bd5ca",
            this_screen_border="#555555",
            inactive="#777777",
            active="#dddddd",
        ),
        widget.Prompt(),
        widget.WindowName(max_chars=60, fmt="{}"),
        widget.Spacer(),
        widget.Net(format="{down} ↓↑ {up}", interface=None, update_interval=2),
        widget.CPU(format="CPU {load_percent}%"),
        widget.Memory(measure_mem='G', format="MEM {MemUsed:.1f}/{MemTotal:.0f}G"),
        widget.Clock(format="%Y-%m-%d %H:%M"),
    ]
    if primary:
        items.insert(-1, widget.Systray())  # трэй только на основном экране
    return bar.Bar(items, 28, margin=[0, 0, 0, 0])

screens = [
    Screen(top=top_bar(primary=True)),
]

# Если есть второй/третий экран, Qtile добавит их из xrandr; бар можно продублировать так:
@hook.subscribe.screen_change
def _restart_on_randr(event):
    lazy.restart()  # простая стабильная стратегия

# ── Мышь ───────────────────────────────────────────────────────────────────────
from libqtile.config import Drag, Click
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

# ── Автостарт ──────────────────────────────────────────────────────────────────
@hook.subscribe.startup_once
def _autostart():
    home = os.path.expanduser("~/.config/qtile/autostart.sh")
    if os.path.exists(home):
        subprocess.Popen([home])

# ── Политики ───────────────────────────────────────────────────────────────────
auto_fullscreen = True
focus_on_window_activation = "smart"
bring_front_click = True
cursor_warp = False
wmname = "LG3D"  # java-fix

