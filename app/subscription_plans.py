from app.models.plan import Plan
from app.extensions import db  # your SQLAlchemy instance
import math
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
                      "title": "Founder Starter",
                      "id": "crowdfunding-founder-starter",
                      "price": 1900,
                      "badge_id": "crowdfunding-founder-starter-badge",
                      "features": [
                          "Access to exclusive founder community",
                          "Early access to new features",
                          "Special recognition on platform",
                          "High priority access",
                          "Earlier onboarding than standard founders",
                          "Supporter badge",
                          "Supporter-only updates: roadmap, infrastructure, and platform progress"
                      ],
                      "options": [{
                          "title": "Founder Starter",
                          "description": "basic project creation and collaboration access",
                          "duration_months": 2
                      },{
                          "title": "Founder Pro",
                          "description": "Advanced analytics and priority support",
                          "duration_months": 1
                      }]
                  },
                  {
                      "title": "Founder Pro Supporter",
                      "id": "crowdfunding-founder-pro",
                      "price": 4900,
                      "badge_id": "crowdfunding-founder-pro-badge",
                      "features": [
                          "Everything in Founder Starter +",
                          "Advanced analytics",
                          "Very high priority access",
                          "Advanced analytics : insights into team activity and progress",
                          "Longer duration than standard founders",
                          "Priority support",
                          "Pro supporter badge"
                      ],
                      "options": [
                          {
                              "title": "Founder Starter",
                              "description": "Basic project creation and collaboration access",
                              "duration_months": 6
                          },
                          {
                              "title": "Founder Pro",
                              "description": "Advanced analytics and priority support",
                              "duration_months": 2
                          }
                      ]
                  }, 
                  {
                      "title": "Founder Power Supporter",
                      "id": "crowdfunding-founder-power",
                      "price": 9900,
                      "badge_id": "crowdfunding-founder-power-badge",
                      "features": [
                          "Top priority access",
                          "Feature request voting",
                          "Full founder community access",
                          "Extended duration than standard founders",
                          "Dedicated supporter badge",
                          "All previous benefits included"
                      ],
                      "options": [
                          {
                              "title": "Founder Starter",
                              "description": "Basic project creation and collaboration access",
                              "duration_months": 12,
                          },
                          {
                              "title": "Founder Pro",
                              "description": "Advanced analytics and priority support",
                              "duration_months": 4,
                          },
                          {
                              "title": "Founder Scale",
                              "description": "Higher limits and advanced collaboration capacity",
                              "duration_months": 1,
                          }
                      ]
                  },
                  {
                      "title": "Founder Champion",
                      "id": "crowdfunding-founder-champion",
                      "price": 24900,
                      "badge_id": "crowdfunding-founder-champion-badge",
                      "features": [
                          "Guaranteed startup registration priority",
                          "Team collaboration tools with contributor and permission management",
                          "Up to 3 team seats included",
                          "All previous benefits included"
                      ],
                      "options": [
                          {
                              "title": "Founder Starter",
                              "description": "Basic project creation and collaboration access",
                              "duration_months": 24,
                          },
                          {
                              "title": "Founder Pro",
                              "description": "Advanced analytics and priority support",
                              "duration_months": 9,
                          },
                          {
                              "title": "Founder Scale",
                              "description": "Higher limits and advanced collaboration capacity",
                              "duration_months": 3
                          }
                      ]
                  },
                  {
                      "id": "crowdfunding-founder-patron",
                      "title": "Founder Patron",
                      "badge_id": "crowdfunding-founder-patron-badge",
                      "price": 49900,
                      "features": [
                          "Immediate access (no waiting)",
                          "Direct support channel: prioritized communication",
                          "Up to 10 team seats",
                          "Founder Patron badge: long-term supporter recognition"
                      ],
                      "options": [
                          {
                              "title": "Founder Starter",
                              "description": "Basic project creation and collaboration access",
                              "duration_months": -1
                          },
                          {
                              "title": "Founder Pro",
                              "description": "Advanced analytics and priority support",
                              "duration_months": 18
                          }, 
                          {
                              "title": "Founder Scale",
                              "description": "Higher limits and advanced collaboration capacity",
                              "duration_months": 6
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
                          "Exclusive founding partner badge",
                          "Permanent recognition (name or logo)",
                          "Monthly founder Q&A calls : direct access to leadership",
                          "Priority consideration for long-term cooperation"
                      ],
                      "options": [
                          {
                              "title": "Founder Starter",
                              "description": "Basic project creation and collaboration access",
                              "duration_months": -1
                          },
                          {
                              "title": "Founder Pro",
                              "description": "Advanced analytics and priority support",
                              "duration_months": -1
                          }, 
                          {
                              "title": "Founder Scale",
                              "description": "Higher limits and advanced collaboration capacity",
                              "duration_months": 12
                          }
                      ]
                  },
                    {
                        "title": "Strategic Supporter",
                        "id": "crowdfunding-strategic-supporter",
                        "price": 299900,
                        "badge_id": "crowdfunding-strategic-supporter-badge",
                        "features": [
                            "Lifetime Founder Starter - basic project creation and collaboration access",
                            "Lifetime Founder Pro - advanced analytics and priority support",
                            "Lifetime Founder Scale - higher limits and advanced collaboration capacity",
                            "Highest priority across SF",
                            "Prominent site & product recognition",
                            "Direct leadership discussions",
                            "Strategic collaboration opportunities"
                        ],
                        "options": [
                            {
                                "title": "Founder Starter",
                                "description": "Basic project creation and collaboration access",
                                "duration_months": -1
                            },
                            {
                                "title": "Founder Pro",
                                "description": "Advanced analytics and priority support",
                                "duration_months": -1
                            },
                            {
                                "title": "Founder Scale",
                                "description": "Higher limits and advanced collaboration capacity",
                                "duration_months": -1
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
                          "Early access priority: ahead of public rollout",
                          "0% platform fee on first $500 earned",
                          "Supporter badge",
                          "Supporter-only updates"
                      ],
                      "options": [],
                      "money_before_fee": 50000,
                  }, 
                  {
                      "title": "Builder Early",
                      "id": "builder-early",
                      "price": 900,
                      "badge_id": "builder-early-badge",
                      "features": [
                          "Higher matching & discovery priority: surfaced earlier to founders",
                          "0% platform fee on first $1500 earned",
                          "Beta feature access",
                          "Early supporter badge"
                      ],
                      "options": [],
                      "money_before_fee": 150000
                  },
                  {
                      "title": "Builder Starter",
                      "id": "builder-starter",
                      "price": 1900,
                      "badge_id": "builder-starter-badge",
                      "features": [
                          "High priority access to projects: preferred during selection",
                          "0% platform fee on first $3500 earned",
                          "Starter templates pack",
                          "Community access"
                      ],
                      "options": [],
                      "money_before_fee": 350000
                  },
                  {
                      "title": "Builder Pro Supporter",
                      "id": "builder-pro-supporter",
                      "price": 4900,
                      "badge_id": "builder-pro-supporter-badge",
                      "features": [
                          "Very high priority across SF",
                          "0% platform fee on first $10000 earned",
                          "Priority support",
                          "Premium templates"
                      ],
                      "options": [],
                      "money_before_fee": 1000000
                  },
                  {
                      "title": "Builder Power Supporter",
                      "id": "builder-power-supporter",
                      "price": 9900,
                      "badge_id": "builder-power-supporter-badge",
                      "features": [
                          "Top priority across matching, access, and features",
                          "0% platform fee on first $25000 earned",
                          "Feature request voting",
                          "Advanced analytics"
                      ],
                      "options": [],
                      "money_before_fee": 2500000
                  },
                  {
                      "title": "Builder Champion",
                      "id": "builder-champion",
                      "price": 24900,
                      "badge_id": "builder-champion-badge",
                      "features": [
                          "Guaranteed first access at launch",
                          "0% platform fee on first $85000 earned",
                          "Long-term priority status"
                      ],
                      "options": [],
                      "money_before_fee": 8500000
                  },
                  {
                      "title": "Builder Patron",
                      "id": "builder-patron",
                      "price": 49900,
                      "badge_id": "builder-patron-badge",
                      "features": [
                          "Immediate access at launch",
                          "Lifetime priority",
                          "0% platform fee on first $200000 earned",
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
                    "id": "founder-free",
                    "price": 0,
                    "duration_months": -1,
                    "features": [
                        "Create 1 project at a time",
                        "Recruit & manage contributors",
                        "Ads visible",
                        "Basic contributor search",
                        "Core collaboration tools"
                    ]
                },
                {
                    "title": "Founder Starter",
                    "id": "founder-starter",
                    "price": 4900,
                    "duration_months": 1,
                    "features": [
                        "Create up to 3 projects at a time",
                        "Recruit & manage contributors",
                        "No ads",
                        "Core collaboration tools",
                        "Increase visibility"
                    ]
                },
                {
                    "title": "Founder Pro",
                    "id": "founder-pro",
                    "price": 14900,
                    "duration_months": 1,
                    "features": [
                        "Everything in Founder Starter +",
                        "Create up to 10 projects simultaneously",
                        "High visibility",
                        "Priority contributor access",
                        "Featured placement"
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
                        "Maximum platform exposure",
                        "Higher platform limits",
                    ]
                },
                {
                    "title": "Founder Partner",
                    "id": "founder-partner",
                    "price": 49900,
                    "duration_months": 1,
                    "features": [
                        "Everything in Founder Scale +",
                        "Top-tier access & white-glove support",
                        "Early access to beta features",
                        "Dedicated account manager",
                        "Priority feedback & support"
                    ]
                }
            ]
          },
          {
            "role": "builder",
            "tiers": [
                {
                    "title": "Builder Free",
                    "id": "builder-free",
                    "price": 0,
                    "duration_months": -1,
                    "fee": 0.20,
                    "features": [
                        "Work on 1 project at a time",
                        "Core tools & dashboard",
                        "Ads visible",
                        "Basic project matching",
                        "Platform fee: 20% when earning"
                    ]
                },
                {
                    "title": "Builder Pro",
                    "id": "builder-pro",
                    "price": 900,
                    "duration_months": 1,
                    "fee": 0.10,
                    "features": [
                        "Work on up to 3 projects simultaneously", 
                        "Higher priority in project matching",
                        "Ad-free experience",
                        "Advanced filtering & search",
                        "Platform fee: 10% when earning"
                    ]
                },
                {
                    "title": "Builder Plus",
                    "id": "builder-plus",
                    "price": 1900,
                    "duration_months": 1,
                    "fee": 0.05,
                    "features": [
                        "Everything in Builder Pro +",
                        "Unlimited simultaneous projects",
                        "Top-tier project matching algorithm",
                        "Direct messaging with founders",
                        "Platform fee: 5% when earning"
                    ]
                },
                {
                    "title": "Builder Elite",
                    "id": "builder-elite",
                    "price": 4900,
                    "duration_months": 1,
                    "fee": 0.02,
                    "features": [
                        "Everything in Builder Plus +",
                        "Maximum visibility to founders",
                        "Access to high-value projects",
                        "Priority support",
                        "Platform fee: 2% when earning"
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
        # check if plan already exists to avoid duplicates
        existing = Plan.query.get(plan_data['id'])
        if existing:
            continue
        
        plan = Plan(
            id=plan_data['id'],
            title=plan_data['title'],
            description=plan_data['description'],
            price=plan_data['price'],
            currency=plan_data['currency'],
            note=plan_data.get('note'),
            stripe_price_id=plan_data['stripe_price_id'],
            accent=plan_data.get('accent'),
            highlight=plan_data.get('highlight', False),
            crown=plan_data.get('crown', False),
            cta=plan_data.get('cta'),
            features=plan_data.get('features', []),
            limit=plan_data.get('limit')
        )
        db.session.add(plan)
    db.session.commit()
    print("Default plans inserted!")
