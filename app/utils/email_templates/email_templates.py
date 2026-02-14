from typing import Optional, Dict, Any
import os
styles = """
  :root {
    --primary: #3b82f6;
    --primary-dark: #1e40af;
    --secondary: #a855f7;
    --secondary-dark: #7c3aed;
    --background: #0a0a0a;
    --surface: #1a1a1a;
    --surface-light: #262626;
    --text-primary: #ffffff;
    --text-secondary: #a3a3a3;
    --border: #404040;
    --accent-blue: #60a5fa;
    --accent-purple: #c084fc;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: var(--text-primary);
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    padding: 20px;
    margin: 0;
  }

  .header {
    width: 100%;
    height: 50px;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-bottom: 20px;
  }

  .header img {
    height: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
    margin: 0 !important;
    border: 2px solid var(--accent-blue);
  }

  .container {
    width: calc(100% - 40px);
    margin: 0 auto;
    background: var(--surface);
    padding: 30px;
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
  }

  h1 {
    color: var(--text-primary);
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    margin: 20px 0;
    background: linear-gradient(to right, #60a5fa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  h2 {
    text-align: center;
    color: var(--accent-blue);
    font-size: 24px;
    font-weight: 600;
    margin: 20px 0;
  }

  p {
    font-size: 1em;
    line-height: 1.6;
    color: var(--text-secondary);
    margin: 12px 0;
  }

  .button {
    display: inline-block;
    padding: 12px 24px;
    background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
    color: var(--text-primary);
    text-decoration: none;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
    border: 1px solid rgba(59, 130, 246, 0.5);
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .button:hover {
    border-color: rgba(168, 85, 247, 0.8);
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    transform: translateY(-2px);
  }

  .footer {
    margin-top: 30px;
    padding: 20px;
    font-size: 0.85em;
    color: var(--text-secondary);
    text-align: center;
    border-radius: 12px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    backdrop-filter: blur(10px);
  }

  a {
    font-family: inherit;
    color: var(--accent-blue);
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s ease;
  }

  a:hover {
    color: var(--accent-purple);
  }

  a.button {
    text-decoration: none;
    color: var(--text-primary);
  }
"""
brand_name = os.getenv("BRAND_NAME", "SFCollab")
support_email = os.getenv("SUPPORT_EMAIL", "sfmanagers333@gmail.com")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
footer = f"""
  <div class='footer'>
  <p>If you did not sign up for {brand_name}, please ignore this email or contact us to let us know.</p>
  <p>If you have any questions or need assistance, feel free to reply to this email or <a href="mailto:{support_email}">contact us here</a>.</p>
  <p>Thank you for being part of our community!</p>
  <p>For more information, reach out to our support team or <a target='_blank' href="{frontend_url}/contact">contact us</a></p>
  </div>
"""

logo_sf = '/logo.png'

class DataType:
  def __init__(self, startup: Optional[Dict[str, Any]] = None, user: Optional[Dict[str, Any]] = None,
   mentor: Optional[Dict[str, Any]] = None, resources: Optional[Dict[str, Any]] = None,
   feedback: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None):
    self.startup = startup
    self.user = user
    self.mentor = mentor
    self.resources = resources
    self.feedback = feedback
    self.metadata = metadata

def thank_email_template(data: DataType, see_email_template: bool = False) -> str:
  return f"""
    <html>
      <head>
      <style>
  {styles}
      </style>
      </head>
      <body>
      <div class="container">
  <div class='header'>
  <img loading="lazy" src='{"cid:logo@sf" if not see_email_template else logo_sf}' alt='Logo of {brand_name}' title='Logo of {brand_name}'/>
  </div>
  <h1>Thank You for Joining {brand_name}!</h1>
  <p>Hello <strong>{data['user'].get('name', 'startup enthusiast')}</strong>,</p>
  <p>We are excited that you have decided to be part of our community dedicated to helping startups scale.</p>
  <p>At {brand_name}, we believe in the potential of startups to innovate and transform industries.</p>
  <p>In our platform, you will find all the resources you need to grow your startup in one place.</p>
  <p>As a new member, you will have access to a wealth of resources, insights, and connections that we know will benefit you.</p>
  <p>To get started:</p>
  <a target='_blank' href="{frontend_url}/dashboard"><button class='button'>Explore Our Resources</button></a>
  {footer}
      </div>
      </body>
    </html>
    """

def verification_code_email_template(data: DataType, see_email_template: bool = False) -> str:
  return f"""
    <html>
      <head>
      <style>
  {styles}
      </style>
      </head>
      <body>
      <div class="container">
  <div class='header'>
  <img loading="lazy" src='{"cid:logo@sf" if not see_email_template else logo_sf}' alt='Logo of {brand_name}' title='Logo of {brand_name}'/>
  </div>
  <h1>Verify Your Email</h1>
  <p>Hello <strong>{data['user'].get('name', 'user')}</strong>,</p>
  <p>Thank you for signing up with {brand_name}! To complete your registration, please use the verification code below:</p>
  <h2>{data['metadata'].get('verification_code', '000000')}</h2>
  <p>This code is valid for the next 15 minutes. If you did not request this verification, please ignore this email.</p>
  <p>If you have any questions or need assistance, feel free to reply to this email or <a href="mailto:{support_email}">contact us here</a>.</p>
  {footer}
      </div>
      </body>
    </html>
    """
def password_reset_email_template(data: DataType, see_email_template: bool = False) -> str:
  return f"""
    <html>
      <head>
      <style>
  {styles}
      </style>
      </head>
      <body>
      <div class="container">
  <div class='header'>
  <img loading="lazy" src='{"cid:logo@meridian" if not see_email_template else logo_sf}' alt='Logo of {brand_name}' title='Logo of {brand_name}'/>
  </div>
  <h1>Password Reset Request</h1>
  <p>Hello <strong>{data['user'].get('name', 'user')}</strong>,</p>
  <p>We received a request to reset your password for your {brand_name} account.</p>
  <p>Please click the button below to reset your password:</p>
  <a target='_blank' href="{data['metadata'].get('reset_link', '#')}"><button class='button'>Reset Password</button></a>
  <p>If you did not request a password reset, please ignore this email or contact us to let us know.</p>
  <p>If you have any questions or need assistance, feel free to reply to this email or <a href="mailto:{support_email}">contact us here</a>.</p>
  {footer}
      </div>
      </body>
    </html>
    """
def welcome_email_template(data: DataType, see_email_template: bool = False) -> str:
  return f"""
    <html>
      <head>
      <style>
  {styles}
      </style>
      </head>
      <body>
      <div class="container">
  <div class='header'>
  <img loading="lazy" src='{"cid:logo@sf" if not see_email_template else logo_sf}' alt='Logo of {brand_name}' title='Logo of {brand_name}'/>
  </div>
  <h1>Welcome to {brand_name}!</h1>
  <p>Hello <strong>{data.get('name', 'user')}</strong>,</p>
  <p>Welcome to the {brand_name} community! We're thrilled to have you on board.</p>
  <p>As a member, you'll have access to a wealth of resources, insights, and connections designed to help you succeed.</p>
  <p>To get started, we recommend exploring our platform and taking advantage of the tools available to you.</p>
  <a target='_blank' href="{frontend_url}/dashboard"><button class='button'>Go to Your Dashboard</button></a>
  <p>If you have any questions or need assistance, feel free to reply to this email or <a href="mailto:{support_email}">contact us here</a>.</p>
  {footer}
      </div>
      </body>
    </html>
    """
# Additional templates can be defined similarly...

def contact_form_email_template(data: DataType, see_email_template: bool = False) -> str:
  return f"""
    <html>
      <head>
      <style>
  {styles}
      </style>
      </head>
      <body>
      <div class="container">
  <div class='header'>
  <img loading="lazy" src='{"cid:logo@sf" if not see_email_template else logo_sf}' alt='Logo of {brand_name}' title='Logo of {brand_name}'/>
  </div>
  <h1>New Contact Form Submission</h1>
  <p>You have received a new message from the contact form on your website.</p>
  <p><strong>Name:</strong> {data['user'].get('name', 'N/A')}</p>
  <p><strong>Email:</strong> {data['user'].get('email', 'N/A')}</p>
  <p><strong>Message:</strong></p>
  <p>{data['metadata'].get('message', 'N/A')}</p>
  {footer}
      </div>
      </body>
    </html>
    """
def transaction_bill_email_template(transaction, see_email_template: bool = False) -> str:
  transaction_type = transaction.type.title()
  amount = transaction.amount / 100  # Assuming amount is stored in cents
  currency = transaction.currency.upper()
  transaction_id = transaction.id or 'N/A'
  date = transaction.created_at.isoformat() if transaction.created_at else 'N/A'
  parsed_date = transaction.created_at.strftime("%B %d, %Y") if transaction.created_at else 'N/A'
  recipient = "SF Collab"
  description = transaction.donation_message or ''
  plan_id = transaction.plan_id or ''
  def replace_dashes_and_title_case(s: str) -> str:
    return s.replace('-', ' ').title()
  if transaction_type == 'subscription' and plan_id:
    transaction_type = f"Subscription - {replace_dashes_and_title_case(plan_id)}"
  is_donation = transaction_type.lower() == 'donation'
  title = "Donation Receipt" if is_donation else "Crowdfunding Contribution Receipt"
  
  return f"""
    <html>
      <head>
      <style>
  {styles}
      </style>
      </head>
      <body>
      <div class="container">
  <div class='header'>
  <img loading="lazy" src='{"cid:logo@sf" if not see_email_template else logo_sf}' alt='Logo of {brand_name}' title='Logo of {brand_name}' style="height: 50px;"/>
  </div>
  <h1>{title}</h1>
  <p>Hello <strong>{f'{transaction.user.first_name} {transaction.user.last_name}' if transaction.user else 'Supporter'}</strong>,</p>
  <p>Thank you for your generous {'donation' if is_donation else 'contribution'} to {brand_name}!</p>
  <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 20px; border-radius: 12px; margin: 20px 0;">
    <p><strong>Transaction Details:</strong></p>
    <p><strong>Type:</strong> {transaction_type}</p>
    {transaction_id and plan_id and f'<p><strong>Plan:</strong> {replace_dashes_and_title_case(plan_id)}</p>' or ''}
    <p><strong>Amount:</strong> {currency} {amount:.2f}</p>
    <p><strong>Transaction ID:</strong> {transaction_id}</p>
    <p><strong>Date:</strong> {parsed_date}</p>
    <p><strong>Recipient:</strong> {recipient}</p>
    {f'<p><strong>Message:</strong> {description}</p>' if description else ''}
  </div>
  <p>Your {'donation' if is_donation else 'contribution'} will help us continue to support startups and innovators in our community.</p>
  <a target='_blank' href="{frontend_url}/dashboard"><button class='button'>View Your Account</button></a>
  <p>For tax purposes, please keep this email as your receipt.</p>
  {footer}
      </div>
      </body>
    </html>
    """
templates = {
  "thank_email": thank_email_template,
  "verification_code_email": verification_code_email_template,
  "password_reset_email": password_reset_email_template,
  "welcome_email": welcome_email_template,
  "contact_form_email": contact_form_email_template,
  "transaction_bill_email": transaction_bill_email_template
}

# Exporting the templates
if __name__ == "__main__":
  pass