# Enums
import enum

class UserStatus(enum.Enum):
    active = "active"
    deleted = "deleted"
    banned = "banned"
    
class UserRoles(enum.Enum):
    founder = "founder"
    contributor = "contributor"
    investor = "investor"
    advisor = "advisor"
    mentor = "mentor"
    partner = "partner"
    admin = "admin"
    moderator = "moderator"
    member = "member"
    technical_lead = "technical_lead"
    engineering_manager = "engineering_manager"
    influencer = "influencer"
    content_creator = "content_creator"
    community_manager = "community_manager"
    hr_specialist = "hr_specialist"

    # Software Engineering
    backend_engineer = "backend_engineer"
    frontend_engineer = "frontend_engineer"
    fullstack_engineer = "fullstack_engineer"
    mobile_engineer = "mobile_engineer"
    software_architect = "software_architect"
    qa_engineer = "qa_engineer"
    test_automation_engineer = "test_automation_engineer"

    # DevOps / Infrastructure
    devops_engineer = "devops_engineer"
    cloud_engineer = "cloud_engineer"
    sre = "sre"  # Site Reliability Engineer
    infrastructure_engineer = "infrastructure_engineer"
    platform_engineer = "platform_engineer"
    cybersecurity_engineer = "cybersecurity_engineer"

    # Data & AI
    data_scientist = "data_scientist"
    data_engineer = "data_engineer"
    machine_learning_engineer = "machine_learning_engineer"
    ai_engineer = "ai_engineer"
    mlops_engineer = "mlops_engineer"
    data_analyst = "data_analyst"
    ai_researcher = "ai_researcher"

    # Product & Design
    product_manager = "product_manager"
    product_owner = "product_owner"
    ux_designer = "ux_designer"
    ui_designer = "ui_designer"
    product_designer = "product_designer"
    ux_researcher = "ux_researcher"

    # Growth & Marketing
    growth_engineer = "growth_engineer"
    growth_marketer = "growth_marketer"
    seo_specialist = "seo_specialist"
    content_strategist = "content_strategist"


class Privacy(enum.Enum):
    public = "public"
    private = "private"

class Theme(enum.Enum):
    light = "light"
    dark = "dark"

class EmailDigest(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class ResourceStatus(enum.Enum):
    active = "active"
    inactive = "inactive"

class SuggestionStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class StartupStage(enum.Enum):
    idea = "idea"
    validation = "validation"
    early = "early"
    growth = "growth"
    scale = "scale"

class JoinRequestStatus(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"

class StoryType(enum.Enum):
    image = "image"
    video = "video"

class PostType(enum.Enum):
    professional = "professional"
    social = "social"
    image = "image"
    video = "video"
    text = "text"

class ConnectionStatus(enum.Enum):
    connected = "connected"
    pending = "pending"
    blocked = "blocked"