from app.config.database import SessionLocal
from app.models.template import Template
from app.models.version import Version
from app.models.language import Language

def seed_default_data():
    db = SessionLocal()
    try:
        # Seed languages
        languages = [
            Language(code="en", name="English", direction="ltr"),
            Language(code="es", name="Spanish", direction="ltr"),
            Language(code="ar", name="Arabic", direction="rtl"),
        ]
        
        for lang in languages:
            existing = db.query(Language).filter(Language.code == lang.code).first()
            if not existing:
                db.add(lang)
        
        # Seed default templates
        templates = [
            {
                "id": "welcome_email",
                "name": "Welcome Email",
                "subject": "Welcome to {{company_name}}!",
                "body": """
                <h1>Welcome {{user_name}}!</h1>
                <p>Thank you for joining {{company_name}}. We're excited to have you on board.</p>
                <p>Your account has been successfully created and you can now access all our features.</p>
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
                <p>Best regards,<br>The {{company_name}} Team</p>
                """,
                "language": "en"
            },
            {
                "id": "password_reset",
                "name": "Password Reset",
                "subject": "Reset Your Password",
                "body": """
                <h1>Password Reset Request</h1>
                <p>Hello {{user_name}},</p>
                <p>You have requested to reset your password. Click the link below to set a new password:</p>
                <p><a href="{{reset_link}}">Reset Password</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't request this reset, please ignore this email.</p>
                <p>Best regards,<br>The {{company_name}} Team</p>
                """,
                "language": "en"
            }
        ]
        
        for template_data in templates:
            existing = db.query(Template).filter(Template.id == template_data["id"]).first()
            if not existing:
                template = Template(**template_data)
                db.add(template)
                db.flush()  # To get the ID
                
                # Create initial version
                version = Version(
                    template_id=template.id,
                    version_number=1,
                    subject=template.subject,
                    body=template.body,
                    changes="Initial version"
                )
                db.add(version)
        
        db.commit()
        print("Default data seeded successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_data()
