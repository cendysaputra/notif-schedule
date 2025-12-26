import smtplib
import json
from datetime import datetime, timedelta
import os
import re

class EmailNotifier:
    def __init__(self, config_file='email_config.json'):
        self.config = self.load_config(config_file)
        
    def load_config(self, config_file):
        # Github Action
        if os.getenv('GITHUB_ACTIONS'):
            return {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': os.getenv('SENDER_EMAIL'),
                'sender_password': os.getenv('SENDER_PASSWORD'),
                'recipient_emails': [os.getenv('RECIPIENT_EMAIL')]
            }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Config file {config_file} not found and no environment variables set")
    
    def read_schedule_file(self, file_path):
        projects = []
        current_project = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Gak ada format tanggal > nama perusahaan
            date_pattern = r'^[A-Za-z]+,\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*-'
            if not re.match(date_pattern, line):
                if current_project:
                    projects.append(current_project)
                current_project = {
                    'company': line,
                    'schedules': []
                }
            else:
                # Jadwal
                if current_project:
                    current_project['schedules'].append(line)
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def parse_date_from_schedule(self, schedule_line):
        """Parse tanggal dari format: Day, DD MMM YYYY - Deskripsi"""
        try:
            date_pattern = r'^[A-Za-z]+,\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})'
            match = re.match(date_pattern, schedule_line)
            
            if match:
                day = int(match.group(1))
                month_name = match.group(2)
                year = int(match.group(3))
                
                month_map = {
                    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
                    'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
                    'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
                }
                
                month = month_map.get(month_name)
                if month:
                    return datetime(year, month, day).date()
            
            return None
        except Exception as e:
            print(f"Error parsing date from: {schedule_line} - {str(e)}")
            return None
    
    def check_notifications_needed(self, projects):
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        notifications = []
        
        for project in projects:
            company = project['company']
            for schedule in project['schedules']:
                event_date = self.parse_date_from_schedule(schedule)
                
                if event_date:
                    description = schedule.split(' - ', 1)[1] if ' - ' in schedule else schedule
                    
                    # Notif showing besok
                    if event_date == tomorrow:
                        notifications.append({
                            'company': company,
                            'date': event_date.strftime('%d %b %Y'),
                            'description': description,
                            'type': 'tomorrow',
                            'message': f"{company} : {description} (besok, {event_date.strftime('%d %b %Y')})"
                        })
                    
                    # Notifshowing hari ini
                    elif event_date == today:
                        notifications.append({
                            'company': company,
                            'date': event_date.strftime('%d %b %Y'),
                            'description': description,
                            'type': 'today',
                            'message': f"Hari ini: {company} : {description} (hari ini, {event_date.strftime('%d %b %Y')})"
                        })
        
        return notifications
    
    def send_email(self, notifications):
        if not notifications:
            print("Tidak ada notifikasi untuk dikirim hari ini.")
            return
        
        # Setup email
        smtp_server = self.config['smtp_server']
        smtp_port = self.config['smtp_port']
        sender_email = self.config['sender_email']
        sender_password = self.config['sender_password']
        recipient_emails = self.config['recipient_emails']
        
        # Validasi config
        if not sender_email or not sender_password or not recipient_emails:
            print("Error: Email configuration incomplete!")
            return
        
        # Pisah notifikasi berdasarkan type
        today_notifications = [n for n in notifications if n['type'] == 'today']
        tomorrow_notifications = [n for n in notifications if n['type'] == 'tomorrow']

        # Body email
        body = "Halo Cendy,\nBerikut daftar proyek yang akan showing.\n\n"

        # Section hari ini
        if today_notifications:
            body += "HARI INI\n"
            for i, notification in enumerate(today_notifications, start=1):
                body += f"{i}. {notification['company']} : {notification['description']} ({notification['date']})\n"
            body += "\n"

        # Section besok
        if tomorrow_notifications:
            body += "BESOK\n"
            for i, notification in enumerate(tomorrow_notifications, start=1):
                body += f"{i}. {notification['company']} : {notification['description']} ({notification['date']})\n"
            body += "\n"

        body += f"\nNotifikasi ini dikirim otomatis pada {datetime.now().strftime('%d/%m/%Y %H:%M')} WIB.\n"
        
        # Header email
        subject = f"Showing Project Imajiner - {datetime.now().strftime('%d/%m/%Y')}"
        message = f"Subject: {subject}\nFrom: {sender_email}\nTo: {', '.join(recipient_emails)}\n\n{body}".encode('utf-8')
        
        try:
            # Kirim email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_emails, message)
            server.quit()
            
            print(f"Email berhasil dikirim ke {len(recipient_emails)} penerima.")
            print(f"Total notifikasi: {len(notifications)}")
            
        except Exception as e:
            print(f"Gagal mengirim email: {str(e)}")
    
    def run_daily_check(self):
        try:
            projects = self.read_schedule_file('jadwal_proyek.txt')
            notifications = self.check_notifications_needed(projects)
            self.send_email(notifications)
            
        except FileNotFoundError:
            print("File jadwal_proyek.txt tidak ditemukan!")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.run_daily_check()
