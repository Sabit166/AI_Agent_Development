import logfire
import os
from dotenv import load_dotenv

def setup_logfire():
    """Configure Logfire with enhanced settings"""
    # Load environment variables
    load_dotenv()
    
    # Get Logfire token
    logfire_token = os.getenv("LOGFIRE_TOKEN")
    
    if logfire_token:
        try:
            # Configure Logfire
            logfire.configure(
                token=logfire_token,
                service_name="news-intelligence-system",
                service_version="1.0.0",
                environment=os.getenv("ENVIRONMENT", "development")
            )
            
            # Instrument OpenAI and other services
            logfire.instrument_openai()
            logfire.instrument_httpx()
            logfire.instrument_requests()
            
            print("✅ Logfire configured successfully")
            
        except Exception as e:
            print(f"⚠️  Error configuring Logfire: {str(e)}")
            
    else:
        print("⚠️  LOGFIRE_TOKEN not found in environment variables")

# Context managers for structured logging
class LogContext:
    """Context manager for logfire spans"""
    
    def __init__(self, operation_name: str, **attributes):
        self.operation_name = operation_name
        self.attributes = attributes
        self.span = None
    
    def __enter__(self):
        self.span = logfire.span(self.operation_name)
        self.span.__enter__()
        
        # Set attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
            
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.record_exception(exc_val)
        self.span.__exit__(exc_type, exc_val, exc_tb)

# Convenience functions for common logging patterns
def log_user_action(action: str, user_session: str, **extra_data):
    """Log user actions with standard format"""
    try:
        logfire.info(f"User action: {action}", extra={
            "action": action,
            "user_session": user_session,
            "event_type": "user_action",
            **extra_data
        })
    except:
        print(f"User action: {action}")

def log_error(error_type: str, error_message: str, **extra_data):
    """Log errors with standard format"""
    try:
        logfire.error(f"Error: {error_type}", extra={
            "error_type": error_type,
            "error_message": error_message,
            "event_type": "error",
            **extra_data
        })
    except:
        print(f"Error: {error_type} - {error_message}")