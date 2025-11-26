from flask import Flask, render_template, request, jsonify, send_file
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from fpdf import FPDF
import os
from datetime import datetime
import re

app = Flask(__name__)

# ----------------------------
# Load Qwen Model Once (Global)
# ----------------------------
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

print("📄 Loading Qwen model... This may take a moment.")

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
    
    generator = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.8,
        top_p=0.95,
        do_sample=True
    )
    
    print("✅ Model loaded successfully!")
    print(f"🔧 Using device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    generator = None

# ----------------------------
# PDF Generation Class
# ----------------------------

# ----------------------------
# Professional PDF Generation Class
# ----------------------------
class BusinessPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()
        
    def header(self):
        # Simple professional header
        if self.page_no() > 1:  # Only show header on content pages
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(59, 130, 246)
            self.cell(0, 10, 'SFCollab Business Intelligence', 0, 1, 'L')
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
    
    def footer(self):
        # Simple footer
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - Generated on {datetime.now().strftime("%B %d, %Y")}', 0, 0, 'C')
    
    def cover_page(self, title, subtitle, details, generation_type="ideas", business_idea=""):
        self.add_page()
        
        # Clean cover design
        self.set_fill_color(245, 247, 250)
        self.rect(0, 0, 210, 297, 'F')
        
        # Main title
        self.set_y(80)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(15, 23, 42)
        self.cell(0, 15, 'SFCollab', 0, 1, 'C')
        
        self.set_font('Helvetica', 'I', 14)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, 'Business Intelligence Report', 0, 1, 'C')
        
        # Document title
        self.ln(30)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(30, 41, 59)
        self.multi_cell(0, 12, title, 0, 'C')
        
        # Subtitle
        self.ln(10)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(71, 85, 105)
        self.multi_cell(0, 8, subtitle, 0, 'C')
        
        # Details section
        self.ln(25)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(226, 232, 240)
        self.rect(30, self.get_y(), 150, 80, 'FD')
        
        self.set_y(self.get_y() + 10)
        self.set_x(40)
        
        for key, value in details.items():
            self.set_x(40)
            self.set_font('Helvetica', 'B', 10)
            self.set_text_color(30, 41, 59)
            self.cell(50, 6, f'{key}:', 0, 0, 'L')
            self.set_font('Helvetica', '', 10)
            self.set_text_color(71, 85, 105)
            self.cell(80, 6, str(value), 0, 1, 'L')
            self.ln(2)
        
        # Business concept if available
        if business_idea and generation_type == "plan":
            self.ln(15)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(30, 41, 59)
            self.cell(0, 8, 'Business Concept:', 0, 1, 'C')
            self.set_font('Helvetica', '', 10)
            self.set_text_color(71, 85, 105)
            self.multi_cell(0, 6, business_idea, 0, 'C')
        
        # Footer
        self.set_y(-30)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, f'Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', 0, 1, 'C')
        self.cell(0, 6, 'Confidential Business Document', 0, 1, 'C')
    
    def chapter_title(self, title):
        """Clean chapter titles"""
        self.ln(15)
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, title, 0, 1, 'L')
        
        # Simple line under title
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 50, self.get_y())
        self.ln(10)
    
    def chapter_body(self, body):
        """Clean body text formatting"""
        self.set_font('Helvetica', '', 11)
        self.set_text_color(30, 41, 59)
        
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                self.ln(5)
                continue
            
            # Handle bullet points
            if re.match(r'^[-•]\s+', line):
                line = re.sub(r'^[-•]\s+', '- ', line)
                self.set_x(15)
                self.multi_cell(0, 6, line)
            
            # Handle numbered items
            elif re.match(r'^\d+\.\s+', line):
                self.set_font('Helvetica', 'B', 11)
                self.multi_cell(0, 6, line)
                self.set_font('Helvetica', '', 11)
            
            # Handle sub-headers
            elif line.endswith(':') and len(line) < 50:
                self.ln(3)
                self.set_font('Helvetica', 'B', 12)
                self.set_text_color(59, 130, 246)
                self.multi_cell(0, 7, line)
                self.set_text_color(30, 41, 59)
                self.set_font('Helvetica', '', 11)
            
            # Regular paragraph
            else:
                self.multi_cell(0, 6, line)
            
            self.ln(2)
    
    def add_section(self, title, content):
        """Add a section with clean formatting"""
        self.chapter_title(title)
        self.chapter_body(content)
        self.ln(8)
    
    def add_executive_highlights(self, highlights):
        """Simple highlights box"""
        self.ln(10)
        
        # Save current position
        current_y = self.get_y()
        
        # Highlight box
        self.set_fill_color(240, 249, 255)
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.3)
        self.rect(15, current_y, 180, 35, 'FD')
        
        # Title
        self.set_y(current_y + 8)
        self.set_x(20)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(15, 23, 42)
        self.cell(0, 8, 'Key Strategic Insights', 0, 1, 'L')
        
        # Content
        self.set_y(current_y + 16)
        self.set_x(20)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 41, 59)
        self.multi_cell(170, 5, highlights)
        
        self.ln(15)
    
    def rounded_rect(self, x, y, w, h, r, style=''):
        """Draw rounded rectangle - simplified"""
        k = self.k
        hp = self.h
        if style == 'F':
            op = 'f'
        elif style == 'FD' or style == 'DF':
            op = 'B'
        else:
            op = 'S'
        my_arc = 4/3 * (1.41421356237 - 1)
        self._out(f'{x*k:.2f} {(hp-y)*k:.2f} m')
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} l')
        self._out(f'{(x+w-r)*k:.2f} {(hp-y)*k:.2f} l')
        self._out(f'{(x+w-r)*k:.2f} {(hp-y)*k:.2f} {(x+w)*k:.2f} {(hp-(y+r))*k:.2f} c')
        self._out(f'{(x+w)*k:.2f} {(hp-(y+h-r))*k:.2f} l')
        self._out(f'{(x+w)*k:.2f} {(hp-(y+h-r))*k:.2f} {(x+w-r)*k:.2f} {(hp-(y+h))*k:.2f} c')
        self._out(f'{(x+r)*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._out(f'{(x+r)*k:.2f} {(hp-(y+h))*k:.2f} {x*k:.2f} {(hp-(y+h-r))*k:.2f} c')
        self._out(f'{x*k:.2f} {(hp-(y+r))*k:.2f} l')
        self._out(f'{x*k:.2f} {(hp-(y+r))*k:.2f} {(x+r)*k:.2f} {(hp-y)*k:.2f} c')
        self._out(op)
    
    def clean_section_title(self, title):
        """Clean section titles"""
        # Remove numbers and bullets
        title = re.sub(r'^\d+\.\s*', '', title)
        title = re.sub(r'^[-]\s*', '', title)
        
        # Simple title cleaning
        title = title.strip()
        
        # Capitalize main sections
        if len(title) <= 30:
            title = title.upper()
        
        return title
        
        
def format_content_for_display(text):
    """Format text with HTML for beautiful display"""
    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Format headers (lines ending with colon or all caps)
    text = re.sub(r'^([A-Z][A-Z\s]{3,}):?\s*$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+\.\s+[A-Z][A-Za-z\s]{5,}):?\s*$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    
    # Format bullet points
    text = re.sub(r'^[-]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', text, flags=re.DOTALL)
    
    # Format numbered lists
    text = re.sub(r'^(\d+\.)\s+(.+)$', r'<li value="\1">\2</li>', text, flags=re.MULTILINE)
    
    # Bold important terms
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Italic emphasis
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    
    # Paragraphs
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<'):
            para = f'<p>{para}</p>'
        formatted_paragraphs.append(para)
    
    return '\n'.join(formatted_paragraphs)

# ============================================
# REPLACE format_content_for_pdf (around line 385 in your app.py)
# ============================================

def format_content_for_pdf(text):
    """Clean text for PDF (remove markdown/html and handle Unicode comprehensively)"""
    if not text:
        return ""
    
    # Convert to string if needed
    text = str(text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    # Comprehensive Unicode character replacements
    replacements = {
        # Bullet points and list markers - use simple ASCII
        '\u2022': '-',   # Bullet
        '\u2023': '>',   # Triangular bullet
        '\u25E6': 'o',   # White bullet
        '\u25AA': '*',   # Black small square
        '\u25AB': '*',   # White small square
        '\u25CF': '*',   # Black circle
        '\u25CB': 'o',   # White circle
        '\u2043': '-',   # Hyphen bullet
        
        # Quotes and apostrophes
        '\u2019': "'",   # Right single quotation mark
        '\u2018': "'",   # Left single quotation mark
        '\u201c': '"',   # Left double quotation mark
        '\u201d': '"',   # Right double quotation mark
        '\u2032': "'",   # Prime
        '\u2033': '"',   # Double prime
        
        # Dashes and hyphens
        '\u2013': '-',   # En dash
        '\u2014': '--',  # Em dash
        '\u2212': '-',   # Minus sign
        '\u2010': '-',   # Hyphen
        '\u2011': '-',   # Non-breaking hyphen
        
        # Ellipsis and spaces
        '\u2026': '...',  # Ellipsis
        '\u00a0': ' ',    # Non-breaking space
        '\u2002': ' ',    # En space
        '\u2003': ' ',    # Em space
        '\u2009': ' ',    # Thin space
        
        # Mathematical and currency
        '\u20ac': 'EUR',  # Euro
        '\u00a3': 'GBP',  # Pound
        '\u00a5': 'JPY',  # Yen
        '\u00a2': 'cents', # Cent
        '\u0024': '$',    # Dollar sign
        
        # Arrows - use simple ASCII
        '\u2192': '->',   # Right arrow
        '\u2190': '<-',   # Left arrow
        '\u2191': '^',    # Up arrow
        '\u2193': 'v',    # Down arrow
        
        # Fractions
        '\u00bc': '1/4',  # 1/4
        '\u00bd': '1/2',  # 1/2
        '\u00be': '3/4',  # 3/4
        
        # Other common symbols
        '\u00ae': '(R)',  # Registered trademark
        '\u00a9': '(C)',  # Copyright
        '\u2122': '(TM)', # Trademark
        '\u2020': '+',    # Dagger
        '\u2021': '++',   # Double dagger
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    # Final safety: remove any remaining non-Latin-1 characters
    try:
        text = text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        # Ultimate fallback: pure ASCII
        text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()
    
    
def parse_sections(text):
    """Parse text into sections based on headers"""
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Check if it's a header (all caps or numbered header)
        if re.match(r'^[A-Z][A-Z\s]{5,}:?\s*$', line) or re.match(r'^\d+\.\s+[A-Z][A-Za-z\s]{5,}:?\s*$', line):
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {"title": line.rstrip(':'), "content": ""}
        else:
            current_section["content"] += line + "\n"
    
    # Add last section
    if current_section["content"].strip():
        sections.append(current_section)
    
    # If no sections found, return as single section
    if len(sections) == 0:
        sections.append({"title": "Content", "content": text})
    
    return sections

# ----------------------------
# Flask Routes
# ----------------------------
@app.route("/")
def home():
    """Render the main page with the form"""
    return render_template("qwen_index_html.html")

@app.route("/generate", methods=["POST"])
def generate():
    """Generate business ideas based on user input"""
    
    if generator is None:
        return render_template(
            "qwen_index_html.html", 
            ideas="❌ Model failed to load. Please check your installation."
        )
    
    try:
        # Get form data
        generation_type = request.form.get("generation_type", "ideas")
        industry = request.form.get("industry", "General")
        budget = request.form.get("budget", "Not specified")
        location = request.form.get("location", "Any")
        tech = request.form.get("tech", "Not specified")
        business_idea = request.form.get("business_idea", "")
        
        if generation_type == "plan":
            # Generate Business Plan
            prompt = f"""You are a business consultant. Create a comprehensive business plan.

Business Idea: {business_idea}
Industry: {industry}
Budget: {budget}
Location: {location}
Technology: {tech}

Please provide a detailed business plan with these sections:

1. EXECUTIVE SUMMARY
   - Business concept overview
   - Mission statement
   - Success factors

2. MARKET ANALYSIS
   - Target market demographics
   - Market size and trends
   - Competition analysis

3. PRODUCTS/SERVICES
   - Detailed offerings
   - Unique value proposition
   - Pricing strategy

4. MARKETING STRATEGY
   - Customer acquisition channels
   - Marketing budget allocation
   - Brand positioning

5. OPERATIONAL PLAN
   - Required resources
   - Technology infrastructure
   - Team structure

6. FINANCIAL PROJECTIONS
   - Startup costs breakdown
   - Revenue projections (Year 1-3)
   - Break-even analysis

7. RISK ANALYSIS
   - Potential challenges
   - Mitigation strategies

Provide actionable and realistic details:"""

            print(f"📊 Generating business plan for: {business_idea}...")
            
        else:
            # Generate Business Ideas
            prompt = f"""You are a startup expert. Suggest 3 innovative and realistic business ideas.

Context:
- Industry: {industry}
- Budget: {budget}
- Location: {location}
- Preferred Technology: {tech}

Each idea should include:
1. Business Name
2. Description
3. Target Market
4. Revenue Model
5. Why it could succeed

Provide clear, actionable ideas:"""

            print(f"🤖 Generating ideas for {industry}...")
        
        # Generate response
        output = generator(prompt)[0]["generated_text"]
        
        # Extract only the generated portion (remove prompt)
        response = output[len(prompt):].strip()
        
        # If response is empty, use full output
        if not response:
            response = output.strip()
        
        # Format for display
        formatted_response = format_content_for_display(response)
        
        print("✅ Generation complete!")
        
        # Store raw content in session/temp for PDF generation
        # For simplicity, we'll pass it back to template
        
        return render_template("qwen_index_html.html", 
            ideas=formatted_response,
            raw_ideas=response,  # For PDF generation
            generation_type=generation_type,
            form_data={
                "industry": industry,
                "budget": budget,
                "location": location,
                "tech": tech,
                "business_idea": business_idea
            })
    
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return render_template(
            "qwen_index_html.html", 
            ideas=f"❌ Error generating content: {str(e)}"
        )

# ============================================
# REPLACE @app.route("/download-pdf") (around line 507 in your app.py)
# ============================================
@app.route("/download-pdf", methods=["POST"])
def download_pdf():
    """Generate and download PDF"""
    try:
        content = request.form.get("content", "")
        generation_type = request.form.get("generation_type", "ideas")
        industry = request.form.get("industry", "General")
        budget = request.form.get("budget", "Not specified")
        location = request.form.get("location", "Any")
        tech = request.form.get("tech", "Not specified")
        business_idea = request.form.get("business_idea", "")
        
        # Create PDF
        pdf = BusinessPDF()
        
        # Cover page
        if generation_type == "plan":
            title = "STRATEGIC BUSINESS PLAN"
            subtitle = business_idea if business_idea else "Comprehensive Growth Strategy"
        else:
            title = "INNOVATION PORTFOLIO"
            subtitle = "Curated Business Opportunities & Market Insights"
        
        details = {
            "Industry Focus": industry,
            "Capital Strategy": budget,
            "Market Geography": location,
            "Tech Stack": tech,
            "Document Type": "Strategic Analysis",
            "Confidentiality": "Level 1 - Internal"
        }
        
        # Clean all input data for PDF before using
        title = format_content_for_pdf(title)
        subtitle = format_content_for_pdf(subtitle)
        business_idea = format_content_for_pdf(business_idea)
        
        # Clean details dictionary
        clean_details = {}
        for key, value in details.items():
            clean_details[format_content_for_pdf(key)] = format_content_for_pdf(value)
        
        # Pass cleaned data to cover_page
        pdf.cover_page(title, subtitle, clean_details, generation_type, business_idea)
        
        # Content pages
        pdf.add_page()
        
        # Add executive highlights for plans
        if generation_type == "plan":
            highlight_text = format_content_for_pdf(
                "This strategic business plan outlines a comprehensive roadmap for market entry and scalable growth. "
                "Key focus areas include customer acquisition, revenue optimization, and competitive positioning."
            )
            pdf.add_executive_highlights(highlight_text)
        
        # Clean content for PDF FIRST - this is critical
        clean_content = format_content_for_pdf(content)
        
        # Parse into sections
        sections = parse_sections(clean_content)
        
        # Add each section with robust error handling
        for section in sections:
            try:
                # Already cleaned by format_content_for_pdf above, but ensure safety
                safe_title = section["title"]
                safe_content = section["content"]
                
                # Additional safety: remove any remaining problematic characters
                safe_title = safe_title.encode('latin-1', 'ignore').decode('latin-1')
                safe_content = safe_content.encode('latin-1', 'ignore').decode('latin-1')
                
                pdf.add_section(safe_title, safe_content)
                
            except Exception as section_error:
                print(f"Warning: Skipping problematic section: {section_error}")
                # Continue with next section instead of failing entire PDF
                continue
        
        # Save PDF
        pdf_filename = f"Strategic_Blueprint_{generation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Use temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            pdf_path = tmp_file.name
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=pdf_filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
        
        
        
@app.route("/health")
def health():
    """Health check endpoint"""
    status = "healthy" if generator is not None else "model_not_loaded"
    return {"status": status, "model": MODEL_NAME}

# ----------------------------
# Run the App
# ----------------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Starting Qwen Business Idea Generator")
    print("="*50)
    print("🌐 Access at: http://localhost:5000")
    print("⌨️  Press CTRL+C to stop\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)