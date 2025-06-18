
import os
import re
import json
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import fitz  # PyMuPDF
import spacy
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Predefined skills list
PREDEFINED_SKILLS = [
    "Python", "JavaScript", "Java", "C++", "C#", "React", "Node.js", "HTML/CSS", 
    "SQL", "MongoDB", "PostgreSQL", "Git", "Docker", "AWS", "Azure", "Linux",
    "Machine Learning", "Data Science", "Flask", "Django", "Express.js", "Spring Boot",
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Kubernetes", "Jenkins", "REST APIs",
    "GraphQL", "Redux", "Vue.js", "Angular", "TypeScript", "Golang", "Rust", "Ruby",
    "PHP", "Swift", "Kotlin", "Firebase", "Redis", "Elasticsearch", "Apache Kafka",
    "Selenium", "Pytest", "Jest", "Bootstrap", "Sass", "LESS", "Webpack", "Babel",
    "Apache", "Nginx", "Microservices", "CI/CD", "DevOps", "Agile", "Scrum", "JIRA"
]

# Social media and coding platform patterns
SOCIAL_PATTERNS = {
    'github': r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38})\b',
    'linkedin': r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9\-_.]+)\/?',
    'leetcode': r'(?:https?:\/\/)?(?:www\.)?leetcode\.com\/([a-zA-Z0-9\-_]+)\/?',
    'geeksforgeeks': r'(?:https?:\/\/)?(?:www\.)?geeksforgeeks\.org\/user\/([a-zA-Z0-9\-_]+)\/?',
    'codechef': r'(?:https?:\/\/)?(?:www\.)?codechef\.com\/users\/([a-zA-Z0-9\-_]+)\/?',
    'codeforces': r'(?:codeforces\.com\/profile\/)([a-zA-Z0-9\-_]+)',
    'hackerrank': r'(?:hackerrank\.com\/profile\/)([a-zA-Z0-9\-_]+)',
    'stackoverflow': r'(?:stackoverflow\.com\/users\/\d+\/)([a-zA-Z0-9\-_]+)'
}

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # Education patterns
        self.degree_patterns = [
            r'\bB\.?Tech\b', r'\bM\.?Tech\b', r'\bB\.?E\.?\b', r'\bM\.?E\.?\b',
            r'\bB\.?Sc\b', r'\bM\.?Sc\b', r'\bB\.?A\b', r'\bM\.?A\b',
            r'\bB\.?Com\b', r'\bM\.?Com\b', r'\bMBA\b', r'\bPhD\b',
            r'\bBachelor\b', r'\bMaster\b', r'\bDoctorate\b'
        ]
        self.cgpa_pattern = r'\b(CGPA|GPA)\s*[:]?\s*(\d\.\d{1,2})\b'

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
            
    def extract_hyperlinks(self, file_path):
        """Extract clickable hyperlinks from PDF"""
        hyperlinks = {}
        try:
            doc = fitz.open(file_path)
            for page in doc:
                links = page.get_links()
                for link in links:
                    if link.get('uri'):
                        url = link['uri'].strip()
                        # Clean up URL by removing any trailing slashes or unwanted characters
                        url = re.sub(r'[\s\"]+$', '', url)
                        # Get link text from the rectangle area
                        rect = link['from']
                        expanded_rect = rect + (-2, -2, 2, 2)  # Expand rect slightly
                        link_text = page.get_textbox(expanded_rect).strip()
                        
                        # Normalize URL for better matching
                        normalized_url = url.lower()
                        if not normalized_url.startswith(('http://', 'https://')):
                            normalized_url = 'https://' + normalized_url
                        
                        # Match social platforms
                        for platform, pattern in SOCIAL_PATTERNS.items():
                            # Skip if we already have this platform
                            if platform in hyperlinks:
                                continue
                                
                            match = re.search(pattern, normalized_url, re.IGNORECASE)
                            if match:
                                # For GitHub, ensure we have the full URL
                                if platform == 'github' and 'github.com' not in normalized_url:
                                    url = f'https://github.com/{match.group(1)}'
                                
                                hyperlinks[platform] = {
                                    'url': url,
                                    'text': link_text or url
                                }
                                break
            doc.close()
            
            # Also try to extract URLs from text as a fallback
            text = self.extract_text_from_pdf(file_path)
            if text:
                self._extract_urls_from_text(text, hyperlinks)
                
        except Exception as e:
            logger.error(f"Error extracting hyperlinks: {str(e)}")
        return hyperlinks
        
    def _extract_urls_from_text(self, text, hyperlinks):
        """Helper method to extract and add URLs from text content"""
        # This regex matches URLs in text
        url_pattern = r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            # Skip if we already have this URL
            if any(url in link_data['url'] for link_data in hyperlinks.values()):
                continue
                
            normalized_url = url.lower()
            if not normalized_url.startswith(('http://', 'https://')):
                normalized_url = 'https://' + normalized_url
                
            for platform, pattern in SOCIAL_PATTERNS.items():
                if platform in hyperlinks:
                    continue
                    
                if re.search(pattern, normalized_url, re.IGNORECASE):
                    hyperlinks[platform] = {
                        'url': url,
                        'text': url  # No link text available from text extraction
                    }
                    break
        
    def extract_education(self, text):
        """Extract education details including degrees, CGPA, college, and year"""
        education = {'degrees': [], 'cgpa': None, 'college': None, 'year': None}
        
        try:
            # Extract degrees using regex
            for pattern in self.degree_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                education['degrees'].extend(matches)
            
            # Remove duplicates while preserving order
            seen = set()
            education['degrees'] = [x for x in education['degrees'] 
                                 if not (x in seen or seen.add(x))]
            
            # Extract CGPA
            cgpa_match = re.search(self.cgpa_pattern, text, re.IGNORECASE)
            if cgpa_match:
                education['cgpa'] = cgpa_match.group(2)
            
            # Extract college using NER if available
            if self.nlp:
                doc = self.nlp(text)
                for ent in doc.ents:
                    if ent.label_ == "ORG" and any(word in ent.text.lower() 
                                                 for word in ['university', 'college', 'institute']):
                        education['college'] = ent.text
                        break
            
            # Extract year (format: YYYY or YYYY-YYYY or YYYY - YYYY or YYYY to YYYY)
            year_patterns = [
                r'(?:20\d{2}[-–—]\s*(?:20)?\d{2})',  # 2018-2022 or 2018 - 2022 or 2018–2022
                r'\b(?:20|19)\d{2}\b(?:\s*[-–—]\s*(?:20|19)?\d{2})?',  # 2018 or 2018-2022 or 2018–2022
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,.-]*(?:20|19)\d{2}[\s-]*(?:to|[-–—])[\s-]*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,.-]*)?(?:20|19)?\d{2}'  # Jan 2018 - Dec 2022
            ]
            
            for pattern in year_patterns:
                year_match = re.search(pattern, text, re.IGNORECASE)
                if year_match:
                    education['year'] = year_match.group(0).strip()
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}")
            
        return education

    def extract_contact_info(self, text):
        """Extract contact information using regex patterns"""
        contact_info = {}

        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['email'] = emails[0] if emails else None

        # Phone pattern (multiple formats)
        phone_patterns = [
            r'\+?1?\s*\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4}',  # US format
            r'\+?\d{1,3}[\s.-]*\(?\d{3,4}\)?[\s.-]*\d{3,4}[\s.-]*\d{3,4}',  # International
            r'\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4}'  # Basic format
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0].strip()
                break

        return contact_info

    def extract_name(self, text):
        """Extract name using spaCy NER if available, otherwise use heuristics"""
        if self.nlp:
            doc = self.nlp(text[:1000])  # Process first 1000 chars for performance
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text

        # Fallback: Look for name patterns at the beginning of the resume
        lines = text.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            line = line.strip()
            # Skip empty lines and lines with common resume headers
            if not line or any(keyword in line.lower() for keyword in 
                             ['resume', 'cv', 'curriculum', 'contact', 'email', 'phone']):
                continue

            # Check if line looks like a name (2-4 words, starts with capital)
            words = line.split()
            if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word.isalpha()):
                return line

        return None

    def extract_social_profiles(self, text):
        """Extract social media and coding platform URLs"""
        profiles = {}

        for platform, pattern in SOCIAL_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                username = matches[0]
                if platform == 'github':
                    profiles[platform] = f"https://github.com/{username}"
                elif platform == 'linkedin':
                    profiles[platform] = f"https://linkedin.com/in/{username}"
                elif platform == 'leetcode':
                    profiles[platform] = f"https://leetcode.com/{username}"
                elif platform == 'geeksforgeeks':
                    profiles[platform] = f"https://auth.geeksforgeeks.org/user/{username}"
                elif platform == 'codechef':
                    profiles[platform] = f"https://codechef.com/users/{username}"
                elif platform == 'codeforces':
                    profiles[platform] = f"https://codeforces.com/profile/{username}"
                elif platform == 'hackerrank':
                    profiles[platform] = f"https://hackerrank.com/profile/{username}"
                elif platform == 'stackoverflow':
                    profiles[platform] = f"https://stackoverflow.com/users/{username}"

        return profiles

    def extract_skills(self, text):
        """Extract skills from predefined list using fuzzy matching"""
        found_skills = []
        text_lower = text.lower()

        for skill in PREDEFINED_SKILLS:
            # Check for exact match or common variations
            skill_variations = [
                skill.lower(),
                skill.lower().replace('.', ''),
                skill.lower().replace(' ', ''),
                skill.lower().replace('/', ' '),
            ]

            for variation in skill_variations:
                if variation in text_lower:
                    if skill not in found_skills:
                        found_skills.append(skill)
                    break

        return found_skills

    def extract_experience(self, text):
        """Extract work experience using pattern matching"""
        experiences = []

        # Split text into sections
        sections = re.split(r'\n\s*(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)\s*\n', 
                          text, flags=re.IGNORECASE)

        if len(sections) > 1:
            experience_text = sections[1]
        else:
            # Look for experience keywords
            exp_keywords = ['intern', 'engineer', 'developer', 'analyst', 'manager', 'consultant']
            lines = text.split('\n')
            experience_lines = []

            for i, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in exp_keywords):
                    # Include context lines
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    experience_lines.extend(lines[start:end])

            experience_text = '\n'.join(experience_lines)

        # Extract individual experiences using patterns
        # Pattern for: Title at Company (Date range)
        exp_pattern = r'([A-Za-z\s,]+?)\s+(?:at|@)\s+([A-Za-z\s&.,]+?)\s*(?:\n|\s)*([A-Za-z0-9\s,-]+\d{4})'
        matches = re.findall(exp_pattern, experience_text, re.MULTILINE)

        for match in matches[:5]:  # Limit to 5 experiences
            title, company, duration = match
            experiences.append({
                'title': title.strip(),
                'company': company.strip(),
                'duration': duration.strip(),
                'description': 'Experience details extracted from resume'
            })

        return experiences

    def extract_achievements(self, text):
        """Extract achievements and accomplishments"""
        achievements = []

        # Look for achievement sections
        achievement_keywords = ['achievements', 'accomplishments', 'awards', 'honors', 'recognition']
        lines = text.split('\n')

        in_achievement_section = False

        for line in lines:
            line = line.strip()

            # Check if we're entering an achievement section
            if any(keyword in line.lower() for keyword in achievement_keywords):
                in_achievement_section = True
                continue

            # Check if we're leaving the section (new major section)
            if in_achievement_section and line.isupper() and len(line) > 5:
                if not any(keyword in line.lower() for keyword in achievement_keywords):
                    in_achievement_section = False

            # Extract achievements
            if in_achievement_section and line and not line.isupper():
                # Clean up bullet points and special characters
                achievement = re.sub(r'^[•\-\*]\s*', '', line)
                if len(achievement) > 10:  # Filter out very short entries
                    achievements.append(achievement)

        # Also look for award patterns throughout the text
        award_patterns = [
            r'(winner|awarded|received|earned)\s+([^\n]{10,80})',
            r'(\d+(?:st|nd|rd|th)\s+place)\s+([^\n]{10,80})',
            r'(dean\'s list|honor roll|magna cum laude|summa cum laude)',
        ]

        for pattern in award_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    achievement = ' '.join(match).strip()
                else:
                    achievement = match.strip()
                if achievement not in achievements:
                    achievements.append(achievement)

        return achievements[:10]  # Limit to 10 achievements

    def parse_resume(self, file_path):
        """Main method to parse resume and extract all information"""
        try:
            text = self.extract_text_from_pdf(file_path)
            if not text:
                return {"error": "Could not extract text from PDF"}
                
            result = {
                "personal_info": {
                    "name": self.extract_name(text),
                    **self.extract_contact_info(text)
                },
                "profiles": self.extract_social_profiles(text),
                "skills": self.extract_skills(text),
                "experience": self.extract_experience(text),
                "achievements": self.extract_achievements(text),
                "education": self.extract_education(text),
                "hyperlinks": self.extract_hyperlinks(file_path),
                "extraction_timestamp": datetime.now().isoformat()
            }
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return {"error": f"Error parsing resume: {str(e)}"}

# Initialize parser
parser = ResumeParser()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index_1.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and resume parsing"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file type
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        unique_filename = timestamp + filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        file.save(file_path)

        # Parse the resume
        result = parser.parse_resume(file_path)

        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'success': True,
            'data': result,
            'message': 'Resume parsed successfully'
        })

    except RequestEntityTooLarge:
        return jsonify({'error': 'File is too large. Maximum size is 16MB'}), 413
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File is too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
