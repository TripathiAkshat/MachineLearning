import re
import os
import json
import PyPDF2
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.secret_key = 'your-secret-key-here'  # Change this in production

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class ResumeParser:
    def __init__(self):
        """Initialize the resume parser with patterns for data extraction."""
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+91[-\s]?)?[0-9]{5}[-\s]?[0-9]{5}',
            'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?',
            'github': r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+/?',
            'leetcode': r'(?:https?://)?(?:www\.)?leetcode\.com/[A-Za-z0-9_-]+/?',
            'hackerrank': r'(?:https?://)?(?:www\.)?hackerrank\.com/[A-Za-z0-9_-]+/?',
            'codechef': r'(?:https?://)?(?:www\.)?codechef\.com/users/[A-Za-z0-9_-]+/?',
            'codeforces': r'(?:https?://)?(?:www\.)?codeforces\.com/profile/[A-Za-z0-9_-]+/?',
            'gfg': r'(?:https?://)?(?:www\.)?geeksforgeeks\.org/[A-Za-z0-9_-]+/?'
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return ""

    def extract_name(self, text: str) -> str:
        """Extract name from resume text (assumes name is at the beginning)."""
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and not re.search(r'[@+]', line) and len(line.split()) <= 4:
                if not any(keyword in line.lower() for keyword in ['phone', 'email', 'address', 'linkedin', 'github']):
                    return line
        return "Not Found"

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text."""
        contact_info = {key: '' for key in self.patterns.keys()}
        
        # Look at the first 20 lines for contact info
        header_text = ' '.join(text.split('\n')[:20])
        
        # Extract email
        email_matches = re.findall(self.patterns['email'], header_text, re.IGNORECASE)
        if email_matches:
            contact_info['email'] = email_matches[0]
        
        # Extract phone (Indian format)
        phone_matches = re.findall(self.patterns['phone'], header_text)
        if phone_matches:
            contact_info['phone'] = phone_matches[0]
        
        # Extract social and coding profiles
        for platform in ['linkedin', 'github', 'leetcode', 'hackerrank', 'codechef', 'codeforces', 'gfg']:
            matches = re.findall(self.patterns[platform], header_text, re.IGNORECASE)
            if matches:
                contact_info[platform] = matches[0]
        
        return contact_info

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced education extraction that handles various formats."""
        education = []
        
        # Common education patterns
        patterns = [
            # B.Tech/B.E./B.Sc
            (r'(?i)((?:B\.?[Tt]ech|B\.?E\.?|B\.?S\.?c?|Bachelor(?:\'?s)?(?:\s+of)?\s+(?:Science|Engineering|Technology|Computer Science|Computer Engineering|Information Technology|Computer Applications))(?:\.|\s+in)?\s*([\w\s&,]+?)\s*(?:,|at|from|\(|$)(?:.*?)(?:(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|\b(?:20\d{2})\b))?', 'bachelors'),
            
            # M.Tech/M.E./M.Sc
            (r'(?i)((?:M\.?[Tt]ech|M\.?E\.?|M\.?S\.?c?|Master(?:\'?s)?(?:\s+of)?\s+(?:Science|Engineering|Technology|Computer Science|Computer Engineering|Information Technology))(?:\.|\s+in)?\s*([\w\s&,]+?)\s*(?:,|at|from|\(|$)(?:.*?)(?:(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|\b(?:20\d{2})\b))?', 'masters'),
            
            # MBA/PGDM
            (r'(?i)((?:MBA|PGDM|PGDBM|M\.?B\.?A\.?)(?:\s+in)?\s*([\w\s&,]+?)\s*(?:,|at|from|\(|$)(?:.*?)(?:(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|\b(?:20\d{2})\b))?)', 'mba'),
            
            # PhD
            (r'(?i)((?:Ph\.?D\.?|Doctor of Philosophy)(?:\s+in)?\s*([\w\s&,]+?)\s*(?:,|at|from|\(|$)(?:.*?)(?:(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|\b(?:20\d{2})\b))?)', 'phd'),
            
            # 12th/High School
            (r'(?i)((?:Class\s+XII|12th|12\s*(?:th)?\s*Grade?|Senior\s+Secondary)\b(?:\s*[:\-]?\s*([\w\s&,]+?)\s*(?:,|at|from|\(|$))?(?:.*?)(?:(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|\b(?:20\d{2})\b))?)', '12th'),
            
            # 10th/Secondary
            (r'(?i)((?:Class\s+X|10th|10\s*(?:th)?\s*Grade?|High\s+School|Secondary)\b(?:\s*[:\-]?\s*([\w\s&,]+?)\s*(?:,|at|from|\(|$))?(?:.*?)(?:(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|\b(?:20\d{2})\b))?)', '10th'),
        ]

        for pattern, edu_type in patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                degree = match.group(1).strip()
                institution = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else 'Not specified'
                
                # Extract year
                year_match = re.search(r'(?:20\d{2}[-–—]\s*(?:20\d{2}|Present|Current|Now)|20\d{2})', 
                                     text[match.end():match.end()+100])
                year = year_match.group(0) if year_match else None
                
                # Extract CGPA/Percentage
                cgpa_match = re.search(r'(?:CGPA|GPA|Percentage|%)\s*[:]?\s*([0-9]+\.[0-9]+|[\d.]+(?:\s*%|/10|/100|/4\.0|/4)?)', 
                                     text[match.end():match.end()+200], re.IGNORECASE)
                cgpa = cgpa_match.group(1) if cgpa_match else None

                # Clean up institution name
                if institution and institution != 'Not specified':
                    institution = re.sub(r'[,\-–—]\s*$', '', institution).strip()
                    for edu in ['B.Tech', 'B.E.', 'B.E', 'B.S.', 'B.S', 'M.Tech', 'M.E.', 'M.E', 'M.S.', 'M.S', 
                               'Bachelor', 'Master', 'Bachelors', 'Masters', 'MBA', 'PhD', 'Ph.D']:
                        institution = re.sub(rf'(?i)\b{re.escape(edu)}\b\s*', '', institution).strip()
                    institution = re.sub(r'\s+', ' ', institution).strip()

                education.append({
                    'degree': degree,
                    'type': edu_type,
                    'institution': institution,
                    'year': year,
                    'cgpa': cgpa
                })

        # Sort by education level (PhD > Masters > MBA > Bachelors > 12th > 10th)
        type_priority = {
            'phd': 0, 'masters': 1, 'mba': 2, 'bachelors': 3, 
            '12th': 4, '10th': 5
        }
        education.sort(key=lambda x: type_priority.get(x['type'], 10))

        return education

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text."""
        skills = []
        
        # Common technical skills patterns
        skill_patterns = [
            r'(?i)(?:skills|technical skills|programming languages|technologies?)[:\s]*(.*?)(?:\n\n|\n\s*\n|$)',
            r'(?i)proficient in (.*?)(?:\.|,|\n|$)',
            r'(?i)experience with (.*?)(?:\.|,|\n|$)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                skills.extend([s.strip() for s in re.split(r'[,;]', match) if s.strip()])
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in skills if not (x in seen or seen.add(x))]

    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text."""
        experiences = []
        
        # Look for experience section
        exp_section = self._extract_section(text, 'experience')
        if not exp_section:
            return experiences
            
        # Split into individual experiences
        exp_items = re.split(r'\n\s*\n', exp_section)
        
        for item in exp_items:
            lines = [line.strip() for line in item.split('\n') if line.strip()]
            if not lines:
                continue
                
            # First line typically contains role and company
            first_line = lines[0]
            role_company = re.split(r'[•\-–—]', first_line, 1)
            
            if len(role_company) >= 2:
                role = role_company[0].strip()
                company = role_company[1].strip()
            else:
                role = first_line
                company = "Not specified"
                
            # Extract duration (if present)
            duration = None
            for line in lines:
                duration_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4})\s*[\u2013\u2014-]?\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4}|Present|Current)', line, re.IGNORECASE)
                if duration_match:
                    duration = f"{duration_match.group(1)} - {duration_match.group(2)}"
                    break
                    
            # Extract location (if present)
            location = None
            for line in lines:
                if re.search(r'[A-Z][a-z]+,\s*[A-Z]{2}\b', line):  # Matches "City, ST" format
                    location = line.strip()
                    break
                    
            # Extract bullet points
            bullet_points = []
            for line in lines[1:]:
                if line.startswith(('•', '-', '–', '—')):
                    bullet_points.append(line[1:].strip())
                elif bullet_points and not line.startswith(('•', '-', '–', '—')):
                    bullet_points[-1] += ' ' + line.strip()
            
            experiences.append({
                'role': role,
                'company': company,
                'duration': duration,
                'location': location,
                'description': bullet_points
            })
            
        return experiences

    def _extract_section(self, text: str, section_name: str) -> str:
        """Helper to extract a specific section from the resume."""
        section_headers = {
            'experience': ['experience', 'work experience', 'professional experience', 'employment history'],
            'education': ['education', 'academic background', 'academic qualifications'],
            'skills': ['skills', 'technical skills', 'key skills', 'core competencies'],
            'projects': ['projects', 'personal projects', 'academic projects'],
            'achievements': ['achievements', 'awards', 'honors', 'certifications']
        }
        
        # Find section start
        start_idx = -1
        for header in section_headers.get(section_name, [section_name]):
            match = re.search(rf'(?:^|\n)\s*{re.escape(header)}\s*:?\s*(?:\n|$)', text, re.IGNORECASE)
            if match:
                start_idx = match.end()
                break
                
        if start_idx == -1:
            return ""
            
        # Find section end (next section or end of text)
        end_idx = len(text)
        for section in section_headers.values():
            for header in section:
                if header == section_name:
                    continue
                match = re.search(rf'(?:^|\n)\s*{re.escape(header)}\s*:?\s*(?:\n|$)', 
                                text[start_idx:], re.IGNORECASE)
                if match and match.start() < (end_idx - start_idx):
                    end_idx = start_idx + match.start()
                    
        return text[start_idx:end_idx].strip()

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Parse resume and extract all relevant information."""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(file_path)
            if not text:
                return {"error": "Could not extract text from PDF"}

            # Extract information
            result = {
                "name": self.extract_name(text),
                "contact_info": self.extract_contact_info(text),
                "education": self.extract_education(text),
                "skills": self.extract_skills(text),
                "experience": self.extract_experience(text),
                "raw_text": text[:1000] + "..." if len(text) > 1000 else text  # Include first 1000 chars of raw text
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Error processing resume: {str(e)}"}

# Initialize the parser
resume_parser = ResumeParser()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
        
    try:
        # Save the uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Parse the resume
        result = resume_parser.parse_resume(filepath)
        
        # Clean up the temporary file
        try:
            os.remove(filepath)
        except:
            pass
            
        return jsonify(result)
        
    except Exception as e:
        # Clean up in case of error
        if 'filepath' in locals() and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)