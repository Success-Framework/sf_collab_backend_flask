# app/services/pitch_deck/ppt_builder.py

import os
import re
from flask import current_app
from pptx import Presentation
# from pptx.chart.data import ChartData
# from pptx.enum.chart import XL_CHART_TYPE
# from pptx.util import Inches
# from app.config import Config
# from pptx.enum.shapes import PP_PLACEHOLDER
# from app.services.pitch_deck.themes import get_theme

TEMPLATE_MAP = {
    "creative": "creative.pptx",
    "startup": "startup.pptx",
    "corporate": "corporate.pptx"
}



class PitchDeckPPTBuilder:

    def __init__(self, deck_json, theme_type, deck_id):
        self.deck_json = deck_json
        self.deck_id = deck_id

        TEMPLATE_MAP = {
            "creative": "creative.pptx",
            "startup": "startup.pptx",
            "corporate": "corporate.pptx"
        }

        template_filename = TEMPLATE_MAP.get(theme_type, "startup.pptx")

# Get project root safely
        project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)
        # base_uplaod_folder = "uploads/pitch-deck-gen/"

        template_path = os.path.join(
            project_root,
            "app",
            "uploads",
            "pitch-deck-gen",
            template_filename
        )

        # print("Project root:", Config.PITCH_DECK_TEMPLATE_FOLDER)
        print("Template path:", template_path)

        if not os.path.exists(template_path):
            raise Exception(f"Template file not found at: {template_path}")

        self.prs = Presentation(template_path)
        



        self.output_folder = os.path.join(project_root,"app","uploads","pitch-deck-gen","output")
        os.makedirs(self.output_folder, exist_ok=True)

    # --------------------------------------------------

    # app/services/pitch_deck/ppt_builder.py


    # --------------------------------------------------

    def build(self):

        slides = self.prs.slides
        ai_slides = self.deck_json.get("slides", [])

        for index, ai_slide in enumerate(ai_slides):

            if index >= len(slides):
                break  # do not add new slides

            template_slide = slides[index]

            self._inject_content(template_slide, ai_slide)

        filename = f"{self.deck_id}.pptx"
        filepath = os.path.join(self.output_folder, filename)
        self.prs.save(filepath)

        return filepath

    # --------------------------------------------------

    def _inject_content(self, slide, ai_slide):

        title = ai_slide.get("title", "")
        bullets = ai_slide.get("bullets", [])
        slide_type = ai_slide.get("type")

        text_shapes = []

        # Collect all text shapes
        for shape in slide.shapes:
            if shape.has_text_frame:
                text_shapes.append(shape)

        # Replace first big text as title
        if text_shapes:
            text_shapes[0].text_frame.clear()
            text_shapes[0].text = title

        # Replace Lorem ipsum or bullet placeholders
        bullet_index = 0

        for shape in text_shapes[1:]:

            if bullet_index >= len(bullets):
                break

            if "Lorem ipsum" in shape.text or shape.text.strip() == "":
                shape.text_frame.clear()
                shape.text = bullets[bullet_index]
                bullet_index += 1

        # Handle financial slide chart update
        if slide_type == "financials":
            self._update_chart(slide, bullets)

    # --------------------------------------------------

    def _update_chart(self, slide, bullets):

        years = []
        values = []

        for bullet in bullets:
            match = re.search(r"(Year\s*\d+|\d{4}).*?\$([\d\.]+)", bullet, re.IGNORECASE)
            if match:
                years.append(match.group(1))
                values.append(float(match.group(2)))

        if not years or not values:
            return

        for shape in slide.shapes:
            if shape.has_chart:
                chart = shape.chart
                chart_data = chart.chart_data

                for i, point in enumerate(values[:len(chart.series[0].points)]):
                    chart.series[0].points[i].data_label.text_frame.text = ""
                    chart.series[0].values[i] = point

                break
