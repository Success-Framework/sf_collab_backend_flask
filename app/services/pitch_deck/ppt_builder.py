# app/services/pitch_deck/ppt_builder.py

import os
from datetime import datetime
from flask import current_app
from pptx import Presentation, slide
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.dml.color import RGBColor
from pptx.util import Cm
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
import re


from app.services.pitch_deck.themes import get_theme


class PitchDeckPPTBuilder:

    def __init__(self, deck_json, theme_type, deck_id):
        self.deck_json = deck_json
        self.theme = get_theme(theme_type)
        self.deck_id = deck_id
        self.prs = Presentation()

        self.output_folder = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")),
            "uploads",
            "pitch_decks"
        )

        base_upload_folder = current_app.config.get("UPLOAD_FOLDER")

        self.output_folder = os.path.join(base_upload_folder, "pitch_decks")
        
        os.makedirs(self.output_folder, exist_ok=True)

    # --------------------------------------------------

    def build(self):

        for slide_data in self.deck_json["slides"]:
            self._add_slide(slide_data)

        filename = f"{self.deck_id}.pptx"
        filepath = os.path.join(self.output_folder, filename)

        self.prs.save(filepath)

        return filepath

    # --------------------------------------------------

    def _add_slide(self, slide_data):
    
        slide_layout = self.prs.slide_layouts[1]  # Title + Content
        slide = self.prs.slides.add_slide(slide_layout)
    
        self._apply_background(slide)
        self._add_accent_bar(slide)
        self._add_slide_label(slide, slide_data["type"])
        self._add_title(slide, slide_data["title"])
    
        
        if slide_data["type"] == "cover":
            self._add_cover_slide(slide, slide_data)
        elif slide_data["type"] == "financials":
            self._add_financial_chart(slide, slide_data["bullets"])
        else:
            bullets = slide_data.get("bullets", [])[:3]
            self._add_bullets(slide, bullets)


        


    # --------------------------------------------------

    def _apply_background(self, slide):

        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = self.theme["background_color"]

    # --------------------------------------------------

    def _add_title(self, slide, title_text):

        left = Inches(1)
        top = Inches(0.9)
        width = Inches(8)
        height = Inches(1.2)
    
        title_box = slide.shapes.add_textbox(left, top, width, height)
        tf = title_box.text_frame
        tf.clear()
    
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(42)
        p.font.bold = True
        p.font.name = self.theme["font_title"]
        p.font.color.rgb = self.theme["title_color"]


    # --------------------------------------------------

    def _add_bullets(self, slide, bullets):
    
        content = slide.placeholders[1]
        tf = content.text_frame
        tf.clear()
    
        for i, bullet in enumerate(bullets):
    
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
    
            p.text = bullet
            p.level = 0
            p.font.size = Pt(22)
            p.font.name = self.theme["font_body"]
            p.font.color.rgb = self.theme["body_color"]





    # --------------------------------------------------

    def _add_highlight_box(self, slide, highlight_text):

        left = Inches(1)
        top = Inches(5.6)
        width = Inches(8)
        height = Inches(1)
    
        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
            left,
            top,
            width,
            height
        )
    
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.theme["highlight_color"]
    
        shape.line.color.rgb = self.theme["accent_color"]
        shape.line.width = Pt(1.5)
    
        tf = shape.text_frame
        tf.clear()
    
        p = tf.paragraphs[0]
        p.text = highlight_text
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.name = self.theme["font_body"]
        p.font.color.rgb = self.theme["accent_color"]
        p.alignment = PP_ALIGN.CENTER

   
   
   
    def _add_accent_bar(self, slide):

        left = Inches(0)
        top = Inches(0)
        width = Inches(0.3)
        height = Inches(7.5)
    
        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            left,
            top,
            width,
            height
        )
    
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.theme["accent_color"]
        shape.line.fill.background()
        
    def _add_slide_label(self, slide, slide_type):

        left = Inches(1)
        top = Inches(0.4)
        width = Inches(5)
        height = Inches(0.5)
    
        label_box = slide.shapes.add_textbox(left, top, width, height)
        tf = label_box.text_frame
        tf.clear()
    
        p = tf.paragraphs[0]
        p.text = slide_type.replace("_", " ").upper()
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.name = self.theme["font_body"]
        p.font.color.rgb = self.theme["accent_color"]
 
 
    

    def _add_financial_chart(self, slide, bullets):
    
        # Try extracting 3 year revenue values
        years = []
        values = []
    
        for bullet in bullets:
            match = re.search(r"Year\s*(\d+).*?\$([\d\.]+)", bullet, re.IGNORECASE)
            if match:
                year = f"Year {match.group(1)}"
                value = float(match.group(2))
                years.append(year)
                values.append(value)
    
        # Fallback if parsing fails
        if len(years) < 3:
            years = ["Year 1", "Year 2", "Year 3"]
            values = [100, 300, 800]
    
        chart_data = ChartData()
        chart_data.categories = years
        chart_data.add_series("Revenue", values)
    
        left = Inches(1)
        top = Inches(2.2)
        width = Inches(8)
        height = Inches(3.5)
    
        chart = slide.shapes.add_chart(
            XL_CHART_TYPE.COLUMN_CLUSTERED,
            left,
            top,
            width,
            height,
            chart_data
        ).chart
    
        chart.has_legend = False
    
        # Style chart bars with accent color
        for series in chart.series:
            for point in series.points:
                point.format.fill.solid()
                point.format.fill.fore_color.rgb = self.theme["accent_color"]
                
    def _add_cover_slide(self, slide, slide_data):

        # Large centered title
        left = Inches(1)
        top = Inches(2.5)
        width = Inches(8)
        height = Inches(2)
    
        title_box = slide.shapes.add_textbox(left, top, width, height)
        tf = title_box.text_frame
        tf.clear()
    
        p = tf.paragraphs[0]
        p.text = slide_data["title"]
        p.font.size = Pt(54)
        p.font.bold = True
        p.font.name = self.theme["font_title"]
        p.font.color.rgb = self.theme["title_color"]
        p.alignment = PP_ALIGN.CENTER
    
        # Subtitle (from first bullet if exists)
        bullets = slide_data.get("bullets", [])
        if bullets:
            subtitle_box = slide.shapes.add_textbox(
                Inches(1),
                Inches(4),
                Inches(8),
                Inches(1)
            )
            tf2 = subtitle_box.text_frame
            tf2.clear()
    
            p2 = tf2.paragraphs[0]
            p2.text = bullets[0]
            p2.font.size = Pt(24)
            p2.font.name = self.theme["font_body"]
            p2.font.color.rgb = self.theme["body_color"]
            p2.alignment = PP_ALIGN.CENTER
    
        # Large accent rectangle at bottom
        slide_width = self.prs.slide_width

        shape = slide.shapes.add_shape(
            MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            0,
            Inches(6.8),
            slide_width,
            Inches(0.6)
        )
    
        shape.fill.solid()
        shape.fill.fore_color.rgb = self.theme["accent_color"]
        shape.line.fill.background()
    

