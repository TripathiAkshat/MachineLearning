import os
import re
import json
import tempfile
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

POPULAR_SKILLS = [
    # Programming Languages
    'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'TypeScript', 'Swift', 'Kotlin', 'Go',
    'Rust', 'Ruby', 'Scala', 'R', 'MATLAB', 'Dart', 'Perl', 'HTML', 'CSS', 'SQL',
    # Web Development
    'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Spring', 'Express.js', 'Node.js', 'ASP.NET',
    'Ruby on Rails', 'Laravel', 'jQuery', 'Bootstrap', 'Tailwind CSS', 'SASS', 'LESS',
    # Mobile Development
    'React Native', 'Flutter', 'Android', 'iOS', 'Xamarin', 'Ionic',
    # Database
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQL Server', 'SQLite', 'Firebase', 'DynamoDB',
    # Cloud & DevOps
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'CI/CD',
    'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Linux', 'Bash', 'Shell Scripting',
    # Data Science & ML
    'Machine Learning', 'Deep Learning', 'Data Analysis', 'Data Visualization', 'Pandas', 'NumPy', 'TensorFlow',
    'PyTorch', 'Keras', 'scikit-learn', 'OpenCV', 'NLTK', 'spaCy', 'Hadoop', 'Spark', 'Tableau', 'Power BI',
    # Other Technologies
    'Blockchain', 'IoT', 'Cybersecurity', 'REST API', 'GraphQL', 'Microservices', 'Serverless',
    'Computer Vision', 'NLP', 'Big Data', 'Agile', 'Scrum', 'DevOps', 'TDD', 'OOP', 'Functional Programming'
]

def extract_achievements(text):
    """Extract achievements and accomplishments from resume text"""
    achievement_patterns = [
        r'(?:achievements|accomplishments|awards)[\s:]+([\s\S]+?)(?=\n\n|\n\w+:|$)',
        r'(?:awarded|achieved|recognized|won)[\s\w]*\s(?:with|for|as|the)?\s*[^\n,;.]+',
        r'ranked\s*#?\d+',
        r'\d+(?:st|nd|rd|th)\s+place',
        r'(?:first|second|third|top|best|outstanding|excellent|exceptional)[\s\w]*\s(?:award|recognition|achievement)'
    ]
    
    achievements = []
    for pattern in achievement_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            achievement = match.group(0).strip()
            if len(achievement.split()) > 2:  
                achievements.append(achievement)
    
    return list(set(achievements)) 
def extract_resume_info(pdf_path):
    try:
        pdf = PdfReader(pdf_path)
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
        
        result = {
            "phone": None,
            "email": None,
            "education": [],
            "skills": [],
            "achievements": [],
            "percentage": None,
            "github": None,
            "linkedin": None,
            "leetcode": None,
            "geeksforgeeks": None,
            "codechef": None,
            "codeforces": None,
            "hackerrank": None
        }
        
        # Define patterns for different data extraction
        patterns = {
            "phone": r'(?:\+91[-\s]?)?[0-9]{5}[-\s]?[0-9]{5}',
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "education": r'(?:Education|EDUCATION)\s+([^\n]+?)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*–\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            "skills": r'(?:Skills|SKILLS|Technical Skills)[\s:]+([\s\S]+?)(?=\n\n|\n\w+:|$)',
            "percentage": r'(\d{1,3}%|\d{1,3}\.\d{1,2}%)',
            # LeetCode pattern - matches various formats including just usernames
            "leetcode": re.compile(
                r'(?i)(?:leetcode\.com/|leet\s*code[\s:]*|lc[\s:]*|^|\s)'  # Prefix
                r'(?:https?:\/\/)?(?:www\.)?'  # Optional http/https and www
                r'(?:leetcode\.com/)?'  # Optional domain
                r'([a-zA-Z0-9_\-.]{3,})'  # Username
            ),
            # GeeksforGeeks pattern
            "geeksforgeeks": re.compile(
                r'(?i)(?:geeksforgeeks\.org/|gfg[\s:]*|^|\s)'  # Prefix
                r'(?:https?:\/\/)?(?:www\.)?'  # Optional http/https and www
                r'(?:geeksforgeeks\.org/)?'  # Optional domain
                r'(?:profile/|user/)?'  # Optional profile/user path
                r'([a-zA-Z0-9_\-.]{3,})'  # Username
            ),
            # CodeChef pattern
            "codechef": re.compile(
                r'(?i)(?:codechef\.com/|cc[\s:]*|^|\s)'  # Prefix
                r'(?:https?:\/\/)?(?:www\.)?'  # Optional http/https and www
                r'(?:codechef\.com/)?'  # Optional domain
                r'(?:users/)?'  # Optional users path
                r'([a-zA-Z0-9_\-.]{3,})'  # Username
            ),
            "codeforces": re.compile(
                r'(?i)(?:codeforces|cf)[\s:]*[\\-\\/]?\\s*'
                r'(?:https?:\/\/)?(?:www\.)?'
                r'codeforces\.com\/profile\/([a-zA-Z0-9_\-\.]+)'
            ),
    
            "hackerrank": re.compile(
                r'(?i)(?:hackerrank|hr)[\s:]*[\\-\\/]?\\s*'
                r'(?:https?:\/\/)?(?:www\.)?'
                r'hackerrank\.com\/(?:profile\/)?([a-zA-Z0-9_\-\.]+)'
            )
        }
    
        # Normalize text by removing special characters that might break the patterns
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Email
        email_match = re.search(patterns["email"], text.replace('\n', ''))
        if email_match:
            result["email"] = email_match.group(0).strip()
        
        # Phone number
        phone_match = re.search(patterns["phone"], text)
        if phone_match:
            result["phone"] = phone_match.group(0).strip()
        
        # Education
        education_matches = re.finditer(patterns["education"], text, re.IGNORECASE)
        for match in education_matches:
            result["education"].append(match.group(1).strip())
        
        # Extract achievements
        result["achievements"] = extract_achievements(text)
        
        # Extract skills
        found_skills = set()
        
        # 1. Extract from skills section
        skills_match = re.search(patterns["skills"], text, re.IGNORECASE)
        if skills_match:
            skills_text = re.sub(r'\s+', ' ', skills_match.group(1)).strip()
            skills = [s.strip() for s in re.split(r'[,•\n]', skills_text) if s.strip()]
            found_skills.update(skills)
        
        # 2. Match against popular skills in the entire text
        for skill in POPULAR_SKILLS:
            # Case-insensitive match with word boundaries
            if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
                found_skills.add(skill)
        
        tech_keywords = {
            'languages': r'\b(?:Python|Java|JavaScript|C\+\+|C#|Ruby|Go|Rust|Swift|Kotlin|PHP|TypeScript|SQL|HTML|CSS)\b',
            'frameworks': r'\b(?:Django|Flask|React|Angular|Vue|Node\.js|Express|Spring|Laravel|Ruby on Rails|ASP\.NET)\b',
            'databases': r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQL Server|SQLite|DynamoDB|Firebase)\b',
            'tools': r'\b(?:Docker|Kubernetes|AWS|Azure|Google Cloud|Git|Jenkins|Ansible|Terraform|Tableau|Power BI)\b',
            'ml_ai': r'\b(?:Machine Learning|Deep Learning|TensorFlow|PyTorch|Keras|scikit-learn|NLP|Computer Vision|OpenCV|NLTK|spaCy)\b'
        }
        
        for category, pattern in tech_keywords.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                found_skills.add(match.group(0))
        
        result["skills"] = sorted(list(found_skills), key=lambda x: x.lower())
        
        percentage_match = re.search(patterns["percentage"], text)
        if percentage_match:
            context = text[max(0, percentage_match.start()-50):percentage_match.end()+50]
            result["percentage"] = {
                'value': percentage_match.group(1).strip(),
                'context': context.strip() if context else None
            }
        
        # Define coding profile patterns and their URL formats
        coding_profiles = [
            {
                'name': 'github',
                'patterns': [
                    r'github\.com/([a-zA-Z0-9-]+)(?:/|$)',
                    r'github[\\s:]*([a-zA-Z0-9-]+)'
                ],
                'url': 'https://github.com/{}',
                'min_length': 3
            },
            {
                'name': 'linkedin',
                'patterns': [
                    r'linkedin\.com/in/([a-zA-Z0-9-]+)(?:/|$)',
                    r'linkedin[\\s:]*in[\\s:]*([a-zA-Z0-9-]+)'
                ],
                'url': 'https://www.linkedin.com/in/{}',
                'min_length': 3
            },
            {
                'name': 'leetcode',
                'patterns': [
                    r'leetcode\.com/([a-zA-Z0-9-]+)(?:/|$)',
                    r'leet[\\s:]*code[\\s:]*([a-zA-Z0-9-]+)',
                    r'lc[\\s:]*([a-zA-Z0-9-]+)'
                ],
                'url': 'https://leetcode.com/{}',
                'min_length': 3
            },
            {
                'name': 'geeksforgeeks',
                'patterns': [
                    r'geeksforgeeks\.org/(?:profile/|user/)?([a-zA-Z0-9-]+)(?:/|$)',
                    r'gfg[\\s:]*([a-zA-Z0-9-]+)'
                ],
                'url': 'https://www.geeksforgeeks.org/user/{}',
                'min_length': 3
            },
            {
                'name': 'codechef',
                'patterns': [
                    r'codechef\.com/(?:users/)?([a-zA-Z0-9-]+)(?:/|$)',
                    r'cc[\\s:]*([a-zA-Z0-9-]+)'
                ],
                'url': 'https://www.codechef.com/users/{}',
                'min_length': 3
            },
            {
                'name': 'codeforces',
                'patterns': [
                    r'codeforces\.com/profile/([a-zA-Z0-9-]+)(?:/|$)',
                    r'cf[\\s:]*([a-zA-Z0-9-]+)'
                ],
                'url': 'https://codeforces.com/profile/{}',
                'min_length': 3
            },
            {
                'name': 'hackerrank',
                'patterns': [
                    r'hackerrank\.com/([a-zA-Z0-9_]+)(?:/|$)',
                    r'hr[\\s:]*([a-zA-Z0-9_]+)'
                ],
                'url': 'https://www.hackerrank.com/profile/{}',
                'min_length': 3
            }
        ]

        # Process each coding profile
        for profile in coding_profiles:
            username = None
            
            # Try each pattern for this profile
            for pattern in profile['patterns']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Get the first matching group if it exists, otherwise use the whole match
                    username = match.group(1) if len(match.groups()) > 0 else match.group(0)
                    # Clean up the username
                    username = re.sub(r'[^\\w\\-_.]', '', username)
                    if username and len(username) >= profile['min_length']:
                        result[profile['name']] = profile['url'].format(username)
                        break
        return result 
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            result = extract_resume_info(filepath)
            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "Could not extract information from the resume"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            try:
                os.remove(filepath)
            except:
                pass
    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF file."}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
