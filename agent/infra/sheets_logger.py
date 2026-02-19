"""Google Sheets integration for tracking prospects"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, List, Optional
import agent.infra.config as config


class ProspectTracker:
    """Track prospects in Google Sheets"""
    
    def __init__(self):
        self.client = None
        self.sheet = None
        self.worksheet = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets
        
        Returns:
            True if successful
        """
        if not config.GOOGLE_SHEETS_CREDENTIALS_PATH:
            print("⚠️ Google Sheets credentials not configured")
            return False
        
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                config.GOOGLE_SHEETS_CREDENTIALS_PATH,
                scope
            )
            
            self.client = gspread.authorize(creds)
            print("✅ Authenticated with Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets auth error: {str(e)}")
            return False
    
    def get_or_create_sheet(self) -> bool:
        """
        Get existing sheet or create new one
        
        Returns:
            True if successful
        """
        try:
            # Try to open existing sheet
            try:
                self.sheet = self.client.open(config.GOOGLE_SHEET_NAME)
                print(f"✅ Opened existing sheet: {config.GOOGLE_SHEET_NAME}")
            except:
                # Create new sheet
                self.sheet = self.client.create(config.GOOGLE_SHEET_NAME)
                print(f"✅ Created new sheet: {config.GOOGLE_SHEET_NAME}")
            
            # Get first worksheet
            self.worksheet = self.sheet.sheet1
            
            # Set up headers if empty
            if not self.worksheet.row_values(1):
                headers = [
                    'Date',
                    'Company',
                    'Contact Name',
                    'Title',
                    'Email',
                    'LinkedIn',
                    'Qualification Score',
                    'Status',
                    'Email Sent',
                    'LinkedIn Request',
                    'Response',
                    'Notes'
                ]
                self.worksheet.append_row(headers)
                print("✅ Added headers to sheet")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up sheet: {str(e)}")
            return False
    
    def log_prospect(self, prospect_data: Dict) -> bool:
        """
        Log a prospect to the sheet
        
        Args:
            prospect_data: Dictionary with prospect information
            
        Returns:
            True if successful
        """
        if not self.worksheet:
            print("❌ Worksheet not initialized")
            return False
        
        try:
            row = [
                datetime.now().strftime('%Y-%m-%d %H:%M'),
                prospect_data.get('company', ''),
                prospect_data.get('contact_name', ''),
                prospect_data.get('title', ''),
                prospect_data.get('email', ''),
                prospect_data.get('linkedin', ''),
                prospect_data.get('qualification_score', ''),
                prospect_data.get('status', 'New'),
                prospect_data.get('email_sent', 'No'),
                prospect_data.get('linkedin_request', 'No'),
                prospect_data.get('response', ''),
                prospect_data.get('notes', '')
            ]
            
            self.worksheet.append_row(row)
            print(f"✅ Logged prospect: {prospect_data.get('company')}")
            return True
            
        except Exception as e:
            print(f"❌ Error logging prospect: {str(e)}")
            return False
    
    def update_prospect_status(self, email: str, status: str, notes: str = "") -> bool:
        """
        Update status of an existing prospect
        
        Args:
            email: Email to find prospect
            status: New status
            notes: Additional notes
            
        Returns:
            True if successful
        """
        if not self.worksheet:
            return False
        
        try:
            # Find the row with this email
            cell = self.worksheet.find(email)
            
            if cell:
                row_num = cell.row
                
                # Update status column (column 8)
                self.worksheet.update_cell(row_num, 8, status)
                
                # Update notes if provided
                if notes:
                    existing_notes = self.worksheet.cell(row_num, 12).value or ""
                    new_notes = f"{existing_notes}\n{datetime.now().strftime('%Y-%m-%d')}: {notes}"
                    self.worksheet.update_cell(row_num, 12, new_notes)
                
                print(f"✅ Updated status for {email}: {status}")
                return True
            else:
                print(f"⚠️ Email not found: {email}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating status: {str(e)}")
            return False
    
    def get_all_prospects(self) -> List[Dict]:
        """
        Get all prospects from sheet
        
        Returns:
            List of prospect dictionaries
        """
        if not self.worksheet:
            return []
        
        try:
            all_records = self.worksheet.get_all_records()
            return all_records
            
        except Exception as e:
            print(f"❌ Error getting prospects: {str(e)}")
            return []


def init_tracker() -> Optional[ProspectTracker]:
    """
    Initialize prospect tracker
    
    Returns:
        ProspectTracker instance or None
    """
    if not config.ENABLE_SHEETS_LOGGING:
        return None
    
    tracker = ProspectTracker()
    
    if tracker.authenticate() and tracker.get_or_create_sheet():
        return tracker
    
    return None


def log_prospect_to_sheets(prospect_data: Dict) -> bool:
    """
    Quick function to log a prospect
    
    Args:
        prospect_data: Prospect information
        
    Returns:
        True if successful
    """
    tracker = init_tracker()
    
    if tracker:
        return tracker.log_prospect(prospect_data)
    
    return False
