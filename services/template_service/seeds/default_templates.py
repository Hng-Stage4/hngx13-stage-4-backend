from app.config.database import SessionLocal
from app.models.template import Template
from app.models.version import Version
from app.models.language import Language
import uuid

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
        
        db.commit()  # Commit languages first
        
        # Seed default templates
        templates = [
            {
                "id": str(uuid.uuid4()),  # UUID for internal ID
                "logical_id": "welcome_email",  # ✅ Added logical_id
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
                "id": str(uuid.uuid4()),  # UUID for internal ID
                "logical_id": "password_reset",  # ✅ Added logical_id
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
            # Check by logical_id instead of id
            existing = db.query(Template).filter(
                Template.logical_id == template_data["logical_id"]
            ).first()
            
            if not existing:
                template = Template(**template_data)
                db.add(template)
                db.flush()  # To get the template data committed
                
                # Create initial version - use logical_id for foreign key
                version = Version(
                    template_logical_id=template.logical_id,  # ✅ Fixed: use logical_id
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
        raise  # Re-raise to see the full error in logs
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_data()