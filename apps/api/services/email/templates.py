"""
HTML and Plain Text email templates for DocuMind AI notifications.
Utilizes premium minimal styling consistent with DocuMind's design system.
"""

def get_welcome_template(name: str) -> tuple[str, str]:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #fafafa; color: #171717; margin: 0; padding: 40px 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e5e5e5; }}
            .logo {{ font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }}
            h1 {{ font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }}
            p {{ font-size: 15px; line-height: 1.6; color: #404040; margin-bottom: 24px; }}
            .button {{ display: inline-block; background-color: #0f172a; color: #ffffff !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px; }}
            .footer {{ margin-top: 40px; padding-top: 24px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #737373; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">DocuMind AI</div>
            <h1>Welcome to DocuMind AI, {name}!</h1>
            <p>We are thrilled to welcome you to the next generation of document intelligence. DocuMind AI analyzes your enterprise agreements, documents, and transcripts with production-grade RAG pipelines, trust assessment models, and automatic conflict detection.</p>
            <p>Get started by uploading your first document in your personal workspace:</p>
            <a href="http://localhost:3000" class="button">Go to Dashboard</a>
            <div class="footer">
                &copy; 2026 DocuMind AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    text = f"""
    Welcome to DocuMind AI, {name}!

    We are thrilled to welcome you to the next generation of document intelligence. 
    DocuMind AI analyzes your enterprise agreements, documents, and transcripts with production-grade RAG pipelines.

    Get started by uploading your first document in your personal workspace:
    http://localhost:3000
    """
    return html.strip(), text.strip()


def get_password_reset_template(reset_url: str) -> tuple[str, str]:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #fafafa; color: #171717; margin: 0; padding: 40px 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e5e5e5; }}
            .logo {{ font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }}
            h1 {{ font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }}
            p {{ font-size: 15px; line-height: 1.6; color: #404040; margin-bottom: 24px; }}
            .button {{ display: inline-block; background-color: #0f172a; color: #ffffff !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px; }}
            .footer {{ margin-top: 40px; padding-top: 24px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #737373; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">DocuMind AI</div>
            <h1>Reset your password</h1>
            <p>You recently requested to reset your password for your DocuMind AI account. Click the button below to set a new password. This link is valid for 24 hours.</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p style="margin-top: 24px; font-size: 13px; color: #737373;">If you did not request this password reset, please ignore this email.</p>
            <div class="footer">
                &copy; 2026 DocuMind AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    text = f"""
    Reset your password

    You recently requested to reset your password for your DocuMind AI account. 
    Click the link below to set a new password. This link is valid for 24 hours.

    {reset_url}

    If you did not request this password reset, please ignore this email.
    """
    return html.strip(), text.strip()


def get_org_invitation_template(org_name: str, inviter_name: str, invite_url: str) -> tuple[str, str]:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #fafafa; color: #171717; margin: 0; padding: 40px 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e5e5e5; }}
            .logo {{ font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }}
            h1 {{ font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }}
            p {{ font-size: 15px; line-height: 1.6; color: #404040; margin-bottom: 24px; }}
            .button {{ display: inline-block; background-color: #0f172a; color: #ffffff !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px; }}
            .footer {{ margin-top: 40px; padding-top: 24px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #737373; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">DocuMind AI</div>
            <h1>Join organization {org_name}</h1>
            <p>{inviter_name} has invited you to join the **{org_name}** organization workspace on DocuMind AI.</p>
            <p>Collaborate with your team on conversational document RAG analysis, requirements matrices, and trust score assessments.</p>
            <a href="{invite_url}" class="button">Accept Invitation</a>
            <div class="footer">
                &copy; 2026 DocuMind AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    text = f"""
    Join organization {org_name}

    {inviter_name} has invited you to join the {org_name} organization workspace on DocuMind AI.
    Collaborate with your team on document conversational RAG analysis, requirements, and trust scores.

    Accept the invitation by visiting:
    {invite_url}
    """
    return html.strip(), text.strip()


def get_analysis_completed_template(doc_name: str, score: float, dashboard_url: str) -> tuple[str, str]:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #fafafa; color: #171717; margin: 0; padding: 40px 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e5e5e5; }}
            .logo {{ font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }}
            h1 {{ font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }}
            p {{ font-size: 15px; line-height: 1.6; color: #404040; margin-bottom: 24px; }}
            .score-badge {{ display: inline-block; background-color: #f1f5f9; padding: 12px 20px; border-radius: 6px; font-size: 18px; font-weight: 700; color: #0f172a; margin: 16px 0; }}
            .button {{ display: inline-block; background-color: #0f172a; color: #ffffff !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px; }}
            .footer {{ margin-top: 40px; padding-top: 24px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #737373; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">DocuMind AI</div>
            <h1>Analysis Completed</h1>
            <p>Great news! The document intelligence pipeline has completed execution for **{doc_name}**.</p>
            <p>Our contradiction checking engine, entity consistency validator, and trust score model successfully evaluated the file.</p>
            <div class="score-badge">Computed Trust Score: {score}%</div>
            <br/>
            <a href="{dashboard_url}" class="button">View Report & Chat</a>
            <div class="footer">
                &copy; 2026 DocuMind AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    text = f"""
    Analysis Completed

    Great news! The document intelligence pipeline has completed execution for: {doc_name}.
    Our contradiction checking engine, entity consistency validator, and trust score model successfully evaluated the file.

    Computed Trust Score: {score}%

    View the report and chat:
    {dashboard_url}
    """
    return html.strip(), text.strip()


def get_processing_completed_template(doc_name: str, dashboard_url: str) -> tuple[str, str]:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #fafafa; color: #171717; margin: 0; padding: 40px 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e5e5e5; }}
            .logo {{ font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }}
            h1 {{ font-size: 24px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }}
            p {{ font-size: 15px; line-height: 1.6; color: #404040; margin-bottom: 24px; }}
            .button {{ display: inline-block; background-color: #0f172a; color: #ffffff !important; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 14px; }}
            .footer {{ margin-top: 40px; padding-top: 24px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #737373; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">DocuMind AI</div>
            <h1>Document Processing Completed</h1>
            <p>The document ingestion pipeline has completed execution for **{doc_name}**.</p>
            <p>Your document is now fully parsed, chunked, and embedded into our semantic vector store. You can now execute natural language queries and retrieve contextual RAG responses from it.</p>
            <a href="{dashboard_url}" class="button">Start Conversational Chat</a>
            <div class="footer">
                &copy; 2026 DocuMind AI. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    text = f"""
    Document Processing Completed

    The document ingestion pipeline has completed execution for: {doc_name}.
    Your document is now fully parsed, chunked, and embedded into our semantic vector store. You can now execute queries.

    Start conversational chat:
    {dashboard_url}
    """
    return html.strip(), text.strip()
