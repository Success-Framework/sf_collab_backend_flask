import torch
import re
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
import tempfile
import logging
from flask_jwt_extended import jwt_required
import gc
from fpdf import FPDF
import time
from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for business plan routes
business_plan_bp = Blueprint('business_plan', __name__, url_prefix='/api/business-plan')

# ============================================================================
# FUCKING HARDCODED PATHS
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
MODEL_PATH = PROJECT_ROOT / 'model_cache' / 'Qwen--Qwen2.5-1.5B-Instruct'

# Global variables for model
model = None
tokenizer = None
model_loaded = False
device = None

def get_device():
    """Determine the best available device"""
    global device
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"✅ Using CUDA device: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
            device = "mps"
            logger.info("✅ Using Apple MPS")
        else:
            device = "cpu"
            logger.info("⚠️  Using CPU")
    return device

def initialize_model():
    """Initialize the Qwen 2.5 1.5B model from cache"""
    global model, tokenizer, model_loaded
    
    if model_loaded:
        logger.info("✅ Model already loaded")
        return True
    
    try:
        logger.info("="*60)
        logger.info(f"🚀 LOADING QWEN 2.5-1.5B MODEL FROM: {MODEL_PATH}")
        logger.info("="*60)
        
        current_device = get_device()
        
        logger.info(f"📦 Loading tokenizer from {MODEL_PATH}...")
        tokenizer = AutoTokenizer.from_pretrained(
            str(MODEL_PATH),
            trust_remote_code=True
        )
        
        # Set padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        logger.info(f"📦 Loading model from {MODEL_PATH}...")
        
        # Load model
        if current_device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                str(MODEL_PATH),
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                str(MODEL_PATH),
                trust_remote_code=True,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            model = model.to(current_device)
        
        model.eval()
        
        model_loaded = True
        logger.info(f"✅ QWEN 2.5-1.5B MODEL LOADED on {current_device}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        logger.error(f"   Model path: {MODEL_PATH}")
        logger.error(f"   Path exists: {MODEL_PATH.exists()}")
        model_loaded = False
        raise e

def ensure_model_loaded():
    """Ensure model is loaded"""
    if not model_loaded:
        initialize_model()

def generate_text(prompt, max_tokens=1024, temperature=0.8):
    """Generate text using Qwen 2.5"""
    global model, tokenizer
    
    ensure_model_loaded()
    
    try:
        # Format prompt for Qwen 2.5 Instruct
        formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        inputs = tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        )
        
        current_device = get_device()
        inputs = {k: v.to(current_device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # Extract only the assistant's response
        if '<|im_start|>assistant' in full_response:
            parts = full_response.split('<|im_start|>assistant')
            if len(parts) > 1:
                assistant_response = parts[-1]
                if '<|im_end|>' in assistant_response:
                    assistant_response = assistant_response.split('<|im_end|>')[0]
                response = assistant_response.strip()
            else:
                response = full_response
        else:
            response = full_response
        
        # Clean up special tokens
        response = response.replace('<|im_start|>', '').replace('<|im_end|>', '').strip()
        
        logger.info(f"📝 Generated {len(response.split())} words")
        return response
        
    except Exception as e:
        logger.error(f"❌ Text generation failed: {str(e)}")
        return f"Error: {str(e)}"

# ----------------------------
# Professional PDF Generation Class
# ----------------------------
class BusinessPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.alias_nb_pages()
        
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(59, 130, 246)
            self.cell(0, 10, 'SFCollab Business Intelligence', 0, 1, 'L')
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - Generated on {datetime.now().strftime("%B %d, %Y")}', 0, 0, 'C')
    
    def cover_page(self, title, subtitle, details, generation_type="ideas", business_idea=""):
        self.add_page()
        
        self.set_fill_color(245, 247, 250)
        self.rect(0, 0, 210, 297, 'F')
        
        self.set_y(80)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(15, 23, 42)
        self.cell(0, 15, 'SFCollab', 0, 1, 'C')
        
        self.set_font('Helvetica', 'I', 14)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, 'Business Intelligence Report', 0, 1, 'C')
        
        self.ln(30)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(30, 41, 59)
        self.multi_cell(0, 12, title, 0, 'C')
        
        self.ln(10)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(71, 85, 105)
        self.multi_cell(0, 8, subtitle, 0, 'C')
        
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
        
        if business_idea and generation_type == "plan":
            self.ln(15)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(30, 41, 59)
            self.cell(0, 8, 'Business Concept:', 0, 1, 'C')
            self.set_font('Helvetica', '', 10)
            self.set_text_color(71, 85, 105)
            self.multi_cell(0, 6, business_idea, 0, 'C')
        
        self.set_y(-30)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, f'Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', 0, 1, 'C')
        self.cell(0, 6, 'Confidential Business Document', 0, 1, 'C')
    
    def chapter_title(self, title):
        self.ln(15)
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, title, 0, 1, 'L')
        
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 50, self.get_y())
        self.ln(10)
    
    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(30, 41, 59)
        
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                self.ln(5)
                continue
            
            if re.match(r'^[-•]\s+', line):
                line = re.sub(r'^[-•]\s+', '- ', line)
                self.set_x(15)
                self.multi_cell(0, 6, line)
            elif re.match(r'^\d+\.\s+', line):
                self.set_font('Helvetica', 'B', 11)
                self.multi_cell(0, 6, line)
                self.set_font('Helvetica', '', 11)
            elif line.endswith(':') and len(line) < 50:
                self.ln(3)
                self.set_font('Helvetica', 'B', 12)
                self.set_text_color(59, 130, 246)
                self.multi_cell(0, 7, line)
                self.set_text_color(30, 41, 59)
                self.set_font('Helvetica', '', 11)
            else:
                self.multi_cell(0, 6, line)
            
            self.ln(2)
    
    def add_section(self, title, content):
        self.chapter_title(title)
        self.chapter_body(content)
        self.ln(8)
    
    def add_executive_highlights(self, highlights):
        self.ln(10)
        
        current_y = self.get_y()
        
        self.set_fill_color(240, 249, 255)
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.3)
        self.rect(15, current_y, 180, 35, 'FD')
        
        self.set_y(current_y + 8)
        self.set_x(20)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(15, 23, 42)
        self.cell(0, 8, 'Key Strategic Insights', 0, 1, 'L')
        
        self.set_y(current_y + 16)
        self.set_x(20)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 41, 59)
        self.multi_cell(170, 5, highlights)
        
        self.ln(15)

def format_content_for_display(text):
    """Format text with HTML for beautiful display"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^([A-Z][A-Z\s]{3,}):?\s*$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^(\d+\.\s+[A-Z][A-Za-z\s]{5,}):?\s*$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^[-]\s+(.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<'):
            para = f'<p>{para}</p>'
        formatted_paragraphs.append(para)
    
    return '\n'.join(formatted_paragraphs)

def format_content_for_pdf(text):
    """Clean text for PDF"""
    if not text:
        return ""
    
    text = str(text)
    
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    replacements = {
        '\u2022': '-', '\u2023': '>', '\u25E6': 'o', '\u25AA': '*',
        '\u25AB': '*', '\u25CF': '*', '\u25CB': 'o', '\u2043': '-',
        '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '--', '\u2212': '-', '\u2010': '-',
        '\u2026': '...', '\u00a0': ' ', '\u2192': '->', '\u2190': '<-',
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    try:
        text = text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        text = text.encode('ascii', 'ignore').decode('ascii')
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def parse_sections(text):
    """Parse text into sections"""
    sections = []
    current_section = {"title": "Introduction", "content": ""}
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if re.match(r'^[A-Z][A-Z\s]{5,}:?\s*$', line) or re.match(r'^\d+\.\s+[A-Z][A-Za-z\s]{5,}:?\s*$', line):
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {"title": line.rstrip(':'), "content": ""}
        else:
            current_section["content"] += line + "\n"
    
    if current_section["content"].strip():
        sections.append(current_section)
    
    if len(sections) == 0:
        sections.append({"title": "Content", "content": text})
    
    return sections

def create_business_prompt(generation_type, industry, budget, location, tech, business_idea=""):
    """Create prompt based on generation type"""
    if generation_type == "plan":
        return f"""You are a professional business consultant. Create a comprehensive business plan:

BUSINESS OVERVIEW:
- Business Idea: {business_idea}
- Industry: {industry}
- Budget: {budget}
- Location: {location}
- Technology: {tech}

Create detailed sections for:
1. EXECUTIVE SUMMARY
2. COMPANY DESCRIPTION
3. MARKET ANALYSIS
4. PRODUCTS & SERVICES
5. MARKETING STRATEGY
6. OPERATIONS PLAN
7. FINANCIAL PROJECTIONS
8. RISK ANALYSIS
9. IMPLEMENTATION TIMELINE
10. CONCLUSION

Provide specific, actionable content for each section."""

    else:
        return f"""Generate 3 innovative business ideas for:

Industry: {industry}
Budget: {budget}
Location: {location}
Technology: {tech}

For each idea provide:
- Business name and description
- Target market
- Value proposition
- Revenue model
- Requirements
- Financial projections
- Success factors

Include a comparative analysis and recommendation."""

# =============================================
# ROUTES
# =============================================

@business_plan_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_business_content():
    """Generate business ideas or plan"""
    try:
        ensure_model_loaded()
        
        data = request.get_json()
        
        generation_type = data.get('generation_type', 'ideas')
        industry = data.get('industry', 'Technology')
        budget = data.get('budget', '$50,000 - $100,000')
        location = data.get('location', 'Urban Area')
        tech = data.get('tech', 'Web/Mobile Applications')
        business_idea = data.get('business_idea', '')
        
        logger.info(f"Generating {generation_type} for industry: {industry}")
        
        prompt = create_business_prompt(generation_type, industry, budget, location, tech, business_idea)
        
        max_tokens = 1536 if generation_type == "plan" else 1024
        response = generate_text(prompt, max_tokens=max_tokens, temperature=0.8)
        
        logger.info(f"✅ Generation complete: {len(response.split())} words")
        
        return jsonify({
            'success': True,
            'type': generation_type,
            'content': response,
            'formatted_content': format_content_for_display(response),
            'model': 'Qwen2.5-1.5B-Instruct',
            'word_count': len(response.split())
        })
        
    except Exception as e:
        logger.error(f"❌ Generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@business_plan_bp.route("/download-pdf", methods=["POST"])
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
        
        pdf = BusinessPDF()
        
        if generation_type == "plan":
            title = "STRATEGIC BUSINESS PLAN"
            subtitle = business_idea if business_idea else "Comprehensive Growth Strategy"
        else:
            title = "INNOVATION PORTFOLIO"
            subtitle = "Curated Business Opportunities"
        
        details = {
            "Industry Focus": industry,
            "Capital Strategy": budget,
            "Market Geography": location,
            "Tech Stack": tech,
            "Document Type": "Strategic Analysis"
        }
        
        title = format_content_for_pdf(title)
        subtitle = format_content_for_pdf(subtitle)
        business_idea = format_content_for_pdf(business_idea)
        
        clean_details = {format_content_for_pdf(k): format_content_for_pdf(v) for k, v in details.items()}
        
        pdf.cover_page(title, subtitle, clean_details, generation_type, business_idea)
        pdf.add_page()
        
        if generation_type == "plan":
            highlight_text = format_content_for_pdf(
                "This strategic business plan outlines a comprehensive roadmap for market entry and growth."
            )
            pdf.add_executive_highlights(highlight_text)
        
        clean_content = format_content_for_pdf(content)
        sections = parse_sections(clean_content)
        
        for section in sections:
            try:
                safe_title = section["title"].encode('latin-1', 'ignore').decode('latin-1')
                safe_content = section["content"].encode('latin-1', 'ignore').decode('latin-1')
                pdf.add_section(safe_title, safe_content)
            except Exception as e:
                logger.warning(f"⚠️ Skipping section: {e}")
                continue
        
        pdf_filename = f"Business_{generation_type}_{industry.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            pdf_path = tmp_file.name
        
        logger.info(f"✅ PDF generated: {pdf_filename}")
        
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')
    
    except Exception as e:
        logger.error(f"❌ PDF error: {e}")
        return jsonify({"error": str(e)}), 500

@business_plan_bp.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded,
        'model': 'Qwen2.5-1.5B-Instruct',
        'device': get_device(),
        'model_path': str(MODEL_PATH)
    })

@business_plan_bp.route('/initialize-model', methods=['POST'])
@jwt_required()
def initialize_model_endpoint():
    """Initialize model"""
    try:
        initialize_model()
        return jsonify({
            'success': True,
            'message': 'Model initialized',
            'device': get_device()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Pre-load model on import
# logger.info("📄 Pre-loading model in background...")
# try:
#     import threading
#     def load_model_background():
#         time.sleep(3)
#         try:
#             initialize_model()
#         except Exception as e:
#             logger.warning(f"⚠️ Background loading failed: {e}")
    
#     thread = threading.Thread(target=load_model_background, daemon=True)
#     thread.start()
# except:
#     logger.warning("⚠️ Could not start background loading")