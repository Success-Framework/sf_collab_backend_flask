# app/services/pitch_deck/themes.py

from pptx.dml.color import RGBColor


THEMES = {

    "minimal_light": {
        "background_color": RGBColor(255, 255, 255),
        "title_color": RGBColor(20, 20, 20),
        "body_color": RGBColor(60, 60, 60),
        "accent_color": RGBColor(0, 102, 204),
        "highlight_color": RGBColor(230, 245, 255),
        "font_title": "Calibri",
        "font_body": "Arial"
    },

    "dark_modern": {
        "background_color": RGBColor(28, 28, 30),
        "title_color": RGBColor(255, 255, 255),
        "body_color": RGBColor(200, 200, 200),
        "accent_color": RGBColor(0, 200, 255),
        "highlight_color": RGBColor(50, 50, 60),
        "font_title": "Calibri",
        "font_body": "Arial"
    },

    "corporate_professional": {
        "background_color": RGBColor(245, 245, 245),
        "title_color": RGBColor(0, 51, 102),
        "body_color": RGBColor(40, 40, 40),
        "accent_color": RGBColor(0, 102, 153),
        "highlight_color": RGBColor(220, 230, 241),
        "font_title": "Calibri",
        "font_body": "Arial"
    },

    "futuristic_ai": {
        "background_color": RGBColor(10, 10, 25),
        "title_color": RGBColor(0, 255, 200),
        "body_color": RGBColor(180, 255, 240),
        "accent_color": RGBColor(0, 180, 255),
        "highlight_color": RGBColor(30, 30, 60),
        "font_title": "Calibri",
        "font_body": "Arial"
    }
}


def get_theme(theme_type: str):
    """
    Returns theme configuration.
    Defaults to minimal_light.
    """
    return THEMES.get(theme_type, THEMES["minimal_light"])
