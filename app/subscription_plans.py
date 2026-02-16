from app.models.plan import Plan
from app.extensions import db  # your SQLAlchemy instance
PLANS = [
    {
        "category": "crowdfunding",
        "currency": "usd",
        "description": "Special early access plans for crowdfunding supporters.",
        "roles": [
            {
                "role": "founder",
                "tiers": [
                    {
                        "title": "Founder Explorer",
                        "id": "crowdfunding-founder-explorer",
                        "price": 900,
                        "badge_id": "crowdfunding-founder-explorer-badge",
                        "features": [
                            "Early supporter access (before public launch)",
                            "1 month Founder Starter included",
                            "Early feedback & product preview access",
                            "Founder Explorer badge (early backer recognition)",
                            "Support the platform from day one"
                        ],
                        "options": [{
                            "title": "Founder Starter",
                            "description": "basic project creation and collaboration access",
                            "duration_months": 1,
                            "features": [
                                    "Create up to 3 projects at a time",
                                    "Collaborators: up to 15 per project",
                                    "Storage: 20 GB",
                                    "Tasks & milestones: up to 200",
                                    "Ad-free experience",
                                    "AI tools: 1,000 credits",
                                ]
                        }]
                    },
                    {
                        "title": "Founder Starter Supporter",
                        "id": "crowdfunding-founder-starter-supporter",
                        "price": 1900,
                        "badge_id": "crowdfunding-founder-starter-supporter-badge",
                        "features": [
                            "Higher discovery & matching priority",
                            "2 months Founder Starter included",
                            "Early access to upcoming features",
                            "Supporter-only updates & roadmap insights",
                            "Founder Starter Supporter badge"
                        ],
                        "options": [{
                            "title": "Founder Starter",
                            "description": "basic project creation and collaboration access",
                            "duration_months": 2,
                            "features": [
                                "Create up to 3 projects at a time",
                                "Collaborators: up to 15 per project",
                                "Storage: 20 GB",
                                "Tasks & milestones: up to 200",
                                "Ad-free experience",
                                "AI tools: 1,000 credits",
                            ]
                        }]
                    },
                    {
                        "title": "Founder Pro Supporter",
                        "id": "crowdfunding-founder-pro",
                        "price": 4900,
                        "badge_id": "crowdfunding-founder-pro-badge",
                        "features": [
                            "Very high platform-wide priority",
                            "Priority support access",
                            "Extended plan access (choose Starter or Pro)",
                            "Early feature unlocks before general release",
                            "Founder Pro Supporter badge",
                            "All previous supporter benefits included"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": 4,
                                "features": [
                                    "Create up to 3 projects at a time",
                                    "Collaborators: up to 15 per project",
                                    "Storage: 20 GB",
                                    "Tasks & milestones: up to 200",
                                    "Ad-free experience",
                                    "AI tools: 1,000 credits",
                                ]
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": 1,
                                "features": [
                                        "Everything in Founder Starter +",
                                        "Projects: up to 10 projects active at a time",
                                        "Collaborators: up to 40 per project",
                                        "Storage: 75 GB",
                                        "Tasks & milestones: up to 500",
                                        "Advanced team roles & permissions",
                                        "AI tools: 2,500 credits",
                                ]
                            }
                        ]
                    }, 
                    {
                        "title": "Founder Power Supporter",
                        "id": "crowdfunding-founder-power",
                        "price": 9900,
                        "badge_id": "crowdfunding-founder-power-badge",
                        "features": [
                            "Top visibility priority across SF ecosystem",
                            "Feature request voting influence",
                            "Multi-tier plan flexibility (Starter / Pro / Scale)",
                            "Priority support",
                            "Power Supporter badge",
                            "All previous supporter benefits included"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": 8,
                                "features": [
                                    "Everything in Founder Starter +",
                                    "Create up to 3 projects at a time",
                                    "Collaborators: up to 15 per project",
                                    "Storage: 20 GB",
                                    "Tasks & milestones: up to 200",
                                    "Ad-free experience",
                                    "AI tools: 1,000 credits",
                                ]
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": 3,
                                "features": [
                                    "Everything in Founder Starter +",
                                    "Projects: up to 10 projects active at a time",
                                    "Collaborators: up to 40 per project",
                                    "Storage: 75 GB",
                                    "Tasks & milestones: up to 500",
                                    "Advanced team roles & permissions",
                                    "AI tools: 2,500 credits",
                                ]
                            },
                            {
                                "title": "Founder Scale",
                                "description": "Higher limits and advanced collaboration capacity",
                                "duration_months": 1,
                                "features": [
                                    "Everything in Founder Pro +",
                                    "Unlimited projects",
                                    "Collaborators: up to 100 per project",
                                    "Storage: 300 GB",
                                    "Tasks & milestones: unlimited",
                                    "Advanced analytics & reports",
                                    "Priority support",
                                    "AI tools: 7,000 credits",
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Founder Champion",
                        "id": "crowdfunding-founder-champion",
                        "price": 24900,
                        "badge_id": "crowdfunding-founder-champion-badge",
                        "features": [
                            "Guaranteed early access at full launch",
                            "Long-term priority status on the platform",
                            "Extended multi-tier access options",
                            "Direct roadmap visibility",
                            "Founder Champion badge",
                            "All previous supporter benefits included"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": 18,
                                "features": [
                                    "Everything in Founder Starter +",
                                    "Create up to 3 projects at a time",
                                    "Collaborators: up to 15 per project",
                                    "Storage: 20 GB",
                                    "Tasks & milestones: up to 200",
                                    "Ad-free experience",
                                    "AI tools: 1,000 credits",
                                ]
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": 6,
                                "features": [
                                    "Everything in Founder Starter +",
                                    "Projects: up to 10 projects active at a time",
                                    "Collaborators: up to 40 per project",
                                    "Storage: 75 GB",
                                    "Tasks & milestones: up to 500",
                                    "Advanced team roles & permissions",
                                    "AI tools: 2,500 credits",
                                ]
                            },
                            {
                                "title": "Founder Scale",
                                "description": "Higher limits and advanced collaboration capacity",
                                "duration_months": 3,
                                "features": [
                                        "Everything in Founder Pro +",
                                        "Unlimited projects",
                                        "Collaborators: up to 100 per project",
                                        "Storage: 300 GB",
                                        "Tasks & milestones: unlimited",
                                        "Advanced analytics & reports",
                                        "Priority support",
                                        "AI tools: 7,000 credits",
                                ]   
                            }
                        ]
                    },
                    {
                        "id": "crowdfunding-founder-patron",
                        "title": "Founder Patron",
                        "badge_id": "crowdfunding-founder-patron-badge",
                        "price": 49900,
                        "features": [
                            "Immediate access (no waiting period)",
                            "Direct prioritized communication channel",
                            "Up to 10 team seats included",
                            "Long-term recognition as core supporter",
                            "Founder Patron badge",
                            "All previous supporter benefits included"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": 36,
                                "features": [
                                    "Everything in Founder Starter +",
                                    "Create up to 3 projects at a time",
                                    "Collaborators: up to 15 per project",
                                    "Storage: 20 GB",
                                    "Tasks & milestones: up to 200",
                                    "Ad-free experience",
                                    "AI tools: 1,000 credits",
                                ]
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": 12,
                                "features": [
                                    "Everything in Founder Starter +",
                                    "Projects: up to 10 projects active at a time",
                                    "Collaborators: up to 40 per project",
                                    "Storage: 75 GB",
                                    "Tasks & milestones: up to 500",
                                    "Advanced team roles & permissions",
                                    "AI tools: 2,500 credits",
                                ]
                            }, 
                            {
                                "title": "Founder Scale",
                                "description": "Higher limits and advanced collaboration capacity",
                                "duration_months": 6,
                                "features": [
                                    "Everything in Founder Pro +",
                                    "Unlimited projects",
                                    "Collaborators: up to 100 per project",
                                    "Storage: 300 GB",
                                    "Tasks & milestones: unlimited",
                                    "Advanced analytics & reports",
                                    "Priority support",
                                    "AI tools: 7,000 credits",
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Founding Partner",
                        "id": "crowdfunding-founding-partner",
                        "price": 99900,
                        "badge_id": "crowdfunding-founding-partner-badge",
                        "features": [
                            "Lifetime platform access",
                            "Permanent recognition (name or logo)",
                            "Monthly private Q&A with leadership",
                            "Long-term strategic priority status",
                            "Eligibility for collaboration initiatives",
                            "Founding Partner badge",
                            "All previous supporter benefits included"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": 72,
                                "features": [
                                        "Everything in Founder Starter +",
                                        "Create up to 3 projects at a time",
                                        "Collaborators: up to 15 per project",
                                        "Storage: 20 GB",
                                        "Tasks & milestones: up to 200",
                                        "Ad-free experience",
                                        "AI tools: 1,000 credits",
                                ]
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": 24,
                                "features": [
                                        "Everything in Founder Starter +",
                                        "Projects: up to 10 projects active at a time",
                                        "Collaborators: up to 40 per project",
                                        "Storage: 75 GB",
                                        "Tasks & milestones: up to 500",
                                        "Advanced team roles & permissions",
                                        "AI tools: 2,500 credits",
                                ]
                            }, 
                            {
                                "title": "Founder Scale",
                                "description": "Higher limits and advanced collaboration capacity",
                                "duration_months": 12,
                                "features": [
                                    "Everything in Founder Pro +",
                                    "Unlimited projects",
                                    "Collaborators: up to 100 per project",
                                    "Storage: 300 GB",
                                    "Tasks & milestones: unlimited",
                                    "Advanced analytics & reports",
                                    "Priority support",
                                    "AI tools: 7,000 credits",
                                ]
                            },
                            {
                                "title": "Founder Partner",
                                "description": "Highest platform stability & limits",
                                "duration_months": 6,
                                "features": [
                                        "Everything in Founder Scale +",
                                        "Collaborators: up to 200 per project",
                                        "Storage: 500 GB",
                                        "Highest platform stability & limits",
                                        "Eligibility for SF-supported initiatives (merit-based)",
                                        "Early access to new SF domains and systems",
                                        "Dedicated support & structured feedback channel",
                                        "AI tools: 10,000 credits",
                                ]
                            }
                        ]
                    },
                    {
                        "title": "Strategic Supporter",
                        "id": "crowdfunding-strategic-supporter",
                        "price": 299900,
                        "badge_id": "crowdfunding-strategic-supporter-badge",
                        "features": [
                            "All Founding Partner benefits included",
                            "Personalized onboarding session",
                            "Dedicated account manager",
                            "Quarterly strategic business reviews",
                            "Customized feature consideration",
                            "Exclusive high-level networking access",
                            "Strategic Supporter badge"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": 120,
                                "features": [
                                        "Everything in Founder Starter +",
                                        "Create up to 3 projects at a time",
                                        "Collaborators: up to 15 per project",
                                        "Storage: 20 GB",
                                        "Tasks & milestones: up to 200",
                                        "Ad-free experience",
                                        "AI tools: 1,000 credits",
                                    ]
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": 48,
                                "features": [
                                        "Everything in Founder Pro +",
                                        "Create up to 10 projects at a time",
                                        "Collaborators: up to 50 per project",
                                        "Storage: 100 GB",
                                        "Tasks & milestones: up to 1000",
                                        "Priority support",
                                        "AI tools: 2,500 credits",
                                    ]
                            },
                            {
                                "title": "Founder Scale",
                                "description": "Higher limits and advanced collaboration capacity",
                                "duration_months": 24,
                                "features": [
                                        "Everything in Founder Scale +",
                                        "Unlimited projects",
                                        "Collaborators: up to 150 per project",
                                        "Storage: 400 GB",
                                        "Tasks & milestones: unlimited",
                                        "Advanced analytics & reports",
                                        "Priority support",
                                        "AI tools: 7,000 credits",
                                    ]
                            },
                            {
                                "title": "Founder Partner",
                                "description": "Highest platform stability & limits",
                                "duration_months": 12,
                                "features": [
                                        "Everything in Founder Partner +",
                                        "Collaborators: up to 250 per project",
                                        "Storage: 600 GB",
                                        "Highest platform stability & limits",
                                        "Eligibility for SF-supported initiatives (merit-based)",
                                        "Early access to new SF domains and systems",
                                        "Dedicated support & structured feedback channel",
                                        "AI tools: 10,000 credits",
                                    ]
                            }
                        ],
                    }
                ]
            },
            {
                "role": "builder",
                "tiers": [
                    {
                        "title": "Builder Supporter",
                        "id": "crowdfunding-builder-supporter",
                        "price": 500,
                        "badge_id": "crowdfunding-builder-supporter-badge",
                        "features": [
                            "Early platform access before public launch",
                            "0% platform fee on first $500 earned",
                            "Priority matching in early projects",
                            "Builder Supporter badge",
                            "Supporter-only updates"
                        ],
                        "options": [],
                        "money_before_fee": 50000,
                    }, 
                    {
                        "title": "Builder Early",
                        "id": "crowdfunding-builder-early",
                        "price": 900,
                        "badge_id": "crowdfunding-builder-early-badge",
                        "features": [
                            "Higher discovery & matching priority",
                            "0% platform fee on first $1,500 earned",
                            "Early feature unlocks",
                            "Builder Early badge"
                        ],
                        "options": [],
                        "money_before_fee": 150000
                    },
                    {
                        "title": "Builder Starter",
                        "id": "crowdfunding-builder-starter",
                        "price": 1900,
                        "badge_id": "crowdfunding-builder-starter-badge",
                        "features": [
                            "High project selection priority",
                            "0% platform fee on first $3,500 earned",
                            "Faster access to new opportunities",
                            "Starter Supporter badge"
                        ],
                        "options": [],
                        "money_before_fee": 350000
                    },
                    {
                        "title": "Builder Pro Supporter",
                        "id": "crowdfunding-builder-pro-supporter",
                        "price": 4900,
                        "badge_id": "crowdfunding-builder-pro-supporter-badge",
                        "features": [
                            "Very high visibility across projects",
                            "0% platform fee on first $10,000 earned",
                            "Priority support access",
                            "Pro Supporter badge"
                        ],
                        "options": [],
                        "money_before_fee": 1000000
                    },
                    {
                        "title": "Builder Power Supporter",
                        "id": "crowdfunding-builder-power-supporter",
                        "price": 9900,
                        "badge_id": "crowdfunding-builder-power-supporter-badge",
                        "features": [
                            "Top matching & visibility priority",
                            "0% platform fee on first $25,000 earned",
                            "Feature request voting",
                            "Power Supporter badge"
                        ],
                        "options": [],
                        "money_before_fee": 2500000
                    },
                    {
                        "title": "Builder Champion",
                        "id": "crowdfunding-builder-champion",
                        "price": 24900,
                        "badge_id": "crowdfunding-builder-champion-badge",
                        "features": [
                            "Guaranteed early access at launch",
                            "0% platform fee on first $85,000 earned",
                            "Long-term priority status",
                            "Champion badge"
                        ],
                        "options": [],
                        "money_before_fee": 8500000
                    },
                    {
                        "title": "Builder Patron",
                        "id": "crowdfunding-builder-patron",
                        "price": 49900,
                        "badge_id": "crowdfunding-builder-patron-badge",
                        "features": [
                            "Immediate launch access",
                            "Lifetime priority across matching & opportunities",
                            "0% platform fee on first $200,000 earned",
                            "Patron recognition badge"
                        ],
                        "options": [],
                        "money_before_fee": 20000000
                    }
                ]
            }
        ]
    },
    {
        "category": "standard",
        "currency": "usd",
        "description": "Standard subscription plans for all users.",
        "roles": [
            {
            "role": "founder",
            "tiers": [
                {
                    "title": "Founder Free",
                    "id": "",
                    "price": 0,
                    "duration_months": -1,
                    "features": [
                        "Create 1 project at a time",
                        "Recruit & manage contributors",
                        "Up to 5 collaborators per project",
                        "Storage limit: 1 GB",
                        "Tasks & milestones: up to 30",
                        "Meetings: unlimited",
                        "Core collaboration tools (tasks, milestones, files, meetings, discussions)",
                        "Basic execution & task tracking",
                        "Ads visible in the platform",
                        "AI tools: not included"
                    ]
                },
                {
                    "title": "Founder Starter",
                    "id": "founder-starter",
                    "price": 4900,
                    "duration_months": 1,
                    "features": [
                        "Everything in Founder Free +",
                        "Create up to 3 projects at a time",
                        "Collaborators: up to 15 per project",
                        "Storage: 20 GB",
                        "Tasks & milestones: up to 200",
                        "Ad-free experience",
                        "AI tools: 1000 credits/month",
                    ]
                },
                {
                    "title": "Founder Pro",
                    "id": "founder-pro",
                    "price": 14900,
                    "duration_months": 1,
                    "features": [
                        "Everything in Founder Starter +",
                        "Projects: up to 10 projects active at a time",
                        "Collaborators: up to 40 per project",
                        "Storage: 75 GB",
                        "Tasks & milestones: up to 500",
                        "Advanced team roles & permissions",
                        "AI tools: 5,000 credits/month",
                    ]
                },
                {
                    "title": "Founder Scale",
                    "id": "founder-scale",
                    "price": 29900,
                    "duration_months": 1,
                    "features": [
                        "Everything in Founder Pro +",
                        "Unlimited projects",
                        "Collaborators: up to 100 per project",
                        "Storage: 300 GB",
                        "Tasks & milestones: unlimited",
                        "Advanced analytics & reports",
                        "Priority support",
                        "AI tools: 10,000 credits/month",
                    ]
                },
                {
                    "title": "Founder Partner",
                    "id": "founder-partner",
                    "price": 49900,
                    "duration_months": 1,
                    "features": [
                        "Everything in Founder Scale +",
                        "Collaborators: up to 200 per project",
                        "Storage: 500 GB",
                        "Highest platform stability & limits",
                        "Eligibility for SF-supported initiatives (merit-based)",
                        "Early access to new SF domains and systems",
                        "Dedicated support & structured feedback channel",
                        "AI tools: 25,000 credits/month",
                    ]
                }
            ]
          },
          {
            "role": "builder",
            "tiers": [
                {
                    "title": "Builder Free",
                    "id": "",
                    "price": 0,
                    "duration_months": -1,
                    "fee": 0.20,
                    "features": [
                        "Platform fee: 20% when earning",
                        "Work on 1 project at a time",
                        "Apply to 5 projects at a time",
                        "Core tools & personal dashboard",
                        "Basic project matching",
                        "Community access",
                        "Ads visible",
                    ]
                },
                {
                    "title": "Builder Pro",
                    "id": "builder-pro",
                    "price": 900,
                    "duration_months": 1,
                    "fee": 0.10,
                    "features": [
                        "Platform Fee: 10%",
                        "Everything in Builder Free +",
                        "Work on up to 3 projects simultaneously",
                        "Apply to 15 projects at a time",
                        "Ad-free experience",
                        "Improved project matching relevance",
                        "Advanced filtering & search",
                        "Priority support access"
                    ]
                },
                {
                    "title": "Builder Plus",
                    "id": "builder-plus",
                    "price": 1900,
                    "duration_months": 1,
                    "fee": 0.05,
                    "features": [
                        "Platform Fee: 5%",
                        "Everything in Builder Pro +",
                        "Unlimited simultaneous projects",
                        "Apply to 50 projects at a time",
                        "Higher-quality project matching",
                        "Direct messaging with founders",
                        "Public portfolio & contribution showcase"
                    ]
                },
                {
                    "title": "Builder Elite",
                    "id": "builder-elite",
                    "price": 4900,
                    "duration_months": 1,
                    "fee": 0.02,
                    "features": [
                        "Platform Fee: 2%",
                        "Everything in Builder Plus +",
                        "Apply to unlimited projects at a time",
                        "Priority access to high-value projects",
                        "Highest matching priority",
                        "Skill verification & endorsements",
                        "Dedicated priority support",
                        "Best for top builders working on serious, long-term projects."
                    ]
                }
            ]
          }
        ]
    },
    {
        "category": "ai-tools",
        "currency": "usd",
        "description": "AI-powered tools subscription plans.",
        "tools": [
            {
                "id": "ai-assistant",
                "title": "AI Assistant",
                "description": "Planning, reminders, meeting summaries, email drafting/sending, voice interaction",
                "price": 3900,
                "currency": "usd",
                "duration_months": 1,
            },
            {
                "id": "business-plan-generator",
                "title": "Business Plan Generator",
                "price": 1900,
                "currency": "usd",
                "duration_months": 1,
            },
            {
                "id": "pitch-deck-generator",
                "title": "Pitch Deck Generator",
                "price": 1900,
                "currency": "usd",
                "duration_months": 1,
            },
            {
                "id": "image-generator",
                "title": "Image Generator",
                "price": 1500,
                "currency": "usd",
                "duration_months": 1,
            },
            {
                "id": "video-generator",
                "title": "Video Generator",
                "price": 2900,
                "currency": "usd",
                "duration_months": 1,
            },
            {
                "id": "ai-tools-bundle",
                "title": "AI Tools Bundle",
                "description": "All AI tools included",
                "price": 6900,
                "currency": "usd",
                "duration_months": 1,
                "bundle": True,
            }
        ]

    },
    {
        "category": "extras",
        "currency": "usd",
        "description": "Additional extras and add-ons.",
        "extras": [
          {
            "title": "Social Media Extras",
            "items": [
                {
                    "title": "Social Media Manager",
                    "price": 2900,
                    "duration_months": 1,
                    "description": "Plan, schedule, publish, basic analytics"
                },
                {
                    "title": "Social Media Content Creator",
                    "price": 1900,
                    "duration_months": 1,
                    "description": "Captions, post ideas, visuals (AI-assisted)"
                }
            ]
          },
          {
            "title": "Storage Extras",
            "items": [
                {
                    "title": "+25 GB",
                    "price": 500,
                    "duration_months": 1
                },
                {
                    "title": "+100 GB",
                    "price": 1500,
                    "duration_months": 1
                },
                {
                    "title": "+300 GB",
                    "price": 2900,
                    "duration_months": 1
                }
            ]
          },
          {
            "title": "Infrastructure Extras",
            "items": [
                {
                    "title": "Domains",
                    "description": "provider cost / year"
                },
                {
                    "title": "Hosting",
                    "description": "base monthly + usage"
                },
                {
                    "title": "Email mailboxes",
                    "description": "per mailbox / month"
                },
                {
                    "title": "Email sending",
                    "description": "metered (credits)"
                }
            ]
          }
        ]
    },
    {
        "category": "credits",
        "currency": "usd",
        "description": "Usage-based credits for AI, automation, and processing.",
        "credit_packs": [
            {
                "type": "monthly",
                "title": "Monthly Credit Pack - 1,000",
                "id": "credits-monthly-1000",
                "credits": 1000,
                "price": 1900,
                "duration_months": 1,
            },
            {
                "type": "monthly",
                "title": "Monthly Credit Pack - 3,000",
                "id": "credits-monthly-3000",
                "credits": 3000,
                "price": 4900,
                "duration_months": 1,
            },
            {
                "type": "monthly",
                "title": "Monthly Credit Pack - 7,000",
                "id": "credits-monthly-7000",
                "credits": 7000,
                "price": 9900,
                "duration_months": 1,
            },
            {
                "type": "monthly",
                "title": "Monthly Credit Pack - 16,000",
                "id": "credits-monthly-16000",
                "credits": 16000,
                "price": 19900,
                "duration_months": 1,
            }
        ],
        "topups": [
            {
                "type": "topup",
                "title": "Top-Up - 500 Credits",
                "id": "credits-topup-500",
                "credits": 500,
                "price": 1000,
            },
            {
                "type": "topup",
                "title": "Top-Up - 1,500 Credits",
                "id": "credits-topup-1500",
                "credits": 1500,
                "price": 2500,
            },
            {
                "type": "topup",
                "title": "Top-Up - 5,000 Credits",
                "id": "credits-topup-5000",
                "credits": 5000,
                "price": 7900,
            },
            {
                "type": "topup",
                "title": "Top-Up - 15,000 Credits",
                "id": "credits-topup-15000",
                "credits": 15000,
                "price": 19900,
            }
        ],
        "description_details": "Credits are used for AI (text, image, video, voice), automation, heavy processing, and external APIs. Core collaboration never uses credits."
    },
]

def insert_default_plans():
    for plan_data in PLANS:
        # 1. Use 'title' or 'id' since 'name' seems to be missing in your data
        identifier = plan_data.get('title') or plan_data.get('id')
        
        if not identifier:
            print(f"Skipping a plan with missing identifying data: {plan_data}")
            continue

        # 2. Check if plan already exists using the title
        existing = Plan.query.filter_by(title=identifier).first()
        if existing:
            continue
        
        # 3. Create the plan using the keys we know exist in your PLANS list
        plan = Plan(
            id=plan_data.get('id'), # Use .get() just in case 'id' is also missing
            title=plan_data.get('title'),
            description=plan_data.get('description'),
            price=plan_data.get('price', 0),
            currency=plan_data.get('currency', 'USD'),
            note=plan_data.get('note'),
            stripe_price_id=plan_data.get('stripe_price_id'),
            accent=plan_data.get('accent'),
            highlight=plan_data.get('highlight', False),
            crown=plan_data.get('crown', False),
            cta=plan_data.get('cta'),
            features=plan_data.get('features', []),
            limit=plan_data.get('limit')
        )
        db.session.add(plan)
        
    try:
        db.session.commit()
        print("✓ Default plans checked and inserted!")
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting plans: {e}")
