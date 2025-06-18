// Resume Summarizer Application
class ResumeSummarizer {
    constructor() {
        this.predefinedSkills = [
            "Python", "JavaScript", "Java", "C++", "C#", "React", "Node.js", "HTML/CSS", 
            "SQL", "MongoDB", "PostgreSQL", "Git", "Docker", "AWS", "Azure", "Linux",
            "Machine Learning", "Data Science", "Flask", "Django", "Express.js", "Spring Boot",
            "TensorFlow", "PyTorch", "Pandas", "NumPy", "Kubernetes", "Jenkins", "REST APIs",
            "GraphQL", "Redux", "Vue.js", "Angular", "TypeScript", "Golang", "Rust", "Ruby",
            "PHP", "Swift", "Kotlin", "Firebase", "Redis", "Elasticsearch", "Apache Kafka"
        ];

        this.sampleData = {
            personal_info: {
                name: "John Smith",
                email: "john.smith@email.com",
                phone: "+1 (555) 123-4567"
            },
            profiles: {
                github: "https://github.com/johnsmith",
                linkedin: "https://linkedin.com/in/johnsmith",
                leetcode: "https://leetcode.com/johnsmith",
                geeksforgeeks: "https://auth.geeksforgeeks.org/user/johnsmith",
                codechef: "https://codechef.com/users/johnsmith",
                codeforces: "https://codeforces.com/profile/johnsmith"
            },
            skills: ["Python", "JavaScript", "React", "Node.js", "MongoDB", "Git", "Docker", "AWS"],
            experience: [
                {
                    title: "Software Engineer",
                    company: "Tech Solutions Inc.",
                    duration: "June 2022 - Present",
                    description: "Developed and maintained web applications using React and Node.js"
                },
                {
                    title: "Software Development Intern",
                    company: "StartupXYZ",
                    duration: "May 2021 - August 2021",
                    description: "Built REST APIs and implemented database optimizations"
                }
            ],
            achievements: [
                "Winner of University Hackathon 2021",
                "Published research paper on Machine Learning algorithms",
                "Dean's List for 3 consecutive semesters",
                "Led team of 5 developers in capstone project"
            ]
        };

        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.uploadSection = document.getElementById('uploadSection');
        this.uploadArea = document.getElementById('uploadArea');
        this.browseBtn = document.getElementById('browseBtn');
        this.fileInput = document.getElementById('fileInput');
        this.progressSection = document.getElementById('progressSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        this.resultsSection = document.getElementById('resultsSection');
        this.resetBtn = document.getElementById('resetBtn');
        
        // Result containers
        this.personalInfo = document.getElementById('personalInfo');
        this.socialProfiles = document.getElementById('socialProfiles');
        this.skillsContainer = document.getElementById('skillsContainer');
        this.experienceList = document.getElementById('experienceList');
        this.achievementsList = document.getElementById('achievementsList');
    }

    bindEvents() {
        // File input events
        this.browseBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // Reset button
        this.resetBtn.addEventListener('click', () => this.resetApplication());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // Validate file
        if (!this.validateFile(file)) {
            return;
        }

        // Hide upload section and show progress
        this.uploadSection.style.display = 'none';
        this.progressSection.classList.remove('hidden');

        // Simulate processing
        this.simulateProcessing();
    }

    validateFile(file) {
        // Check file type
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file only.');
            return false;
        }

        // Check file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB in bytes
        if (file.size > maxSize) {
            alert('File size must be less than 10MB.');
            return false;
        }

        return true;
    }

    simulateProcessing() {
        let progress = 0;
        const steps = [
            { progress: 20, text: 'Reading PDF file...' },
            { progress: 40, text: 'Extracting text content...' },
            { progress: 60, text: 'Analyzing personal information...' },
            { progress: 80, text: 'Identifying skills and experience...' },
            { progress: 100, text: 'Processing complete!' }
        ];

        let currentStep = 0;

        const updateProgress = () => {
            if (currentStep < steps.length) {
                const step = steps[currentStep];
                this.progressFill.style.width = `${step.progress}%`;
                this.progressText.textContent = step.text;
                currentStep++;

                setTimeout(updateProgress, 800);
            } else {
                setTimeout(() => {
                    this.showResults();
                }, 500);
            }
        };

        updateProgress();
    }

    showResults() {
        // Hide progress section
        this.progressSection.classList.add('hidden');
        
        // Show results section with animation
        this.resultsSection.classList.remove('hidden');
        this.resultsSection.classList.add('fade-in');

        // Populate results
        this.populatePersonalInfo();
        this.populateSocialProfiles();
        this.populateSkills();
        this.populateExperience();
        this.populateAchievements();
    }

    populatePersonalInfo() {
        const { personal_info } = this.sampleData;
        this.personalInfo.innerHTML = `
            <div class="info-item">
                <span class="info-item__label">Name</span>
                <span class="info-item__value">${personal_info.name}</span>
            </div>
            <div class="info-item">
                <span class="info-item__label">Email</span>
                <span class="info-item__value">${personal_info.email}</span>
            </div>
            <div class="info-item">
                <span class="info-item__label">Phone</span>
                <span class="info-item__value">${personal_info.phone}</span>
            </div>
        `;
    }

    populateSocialProfiles() {
        const { profiles } = this.sampleData;
        const profileIcons = {
            github: '🐙',
            linkedin: '💼',
            leetcode: '🔢',
            geeksforgeeks: '🧑‍💻',
            codechef: '👨‍🍳',
            codeforces: '⚔️'
        };

        const profileNames = {
            github: 'GitHub',
            linkedin: 'LinkedIn',
            leetcode: 'LeetCode',
            geeksforgeeks: 'GeeksforGeeks',
            codechef: 'CodeChef',
            codeforces: 'Codeforces'
        };

        this.socialProfiles.innerHTML = Object.entries(profiles)
            .map(([platform, url]) => `
                <div class="profile-item">
                    <span class="profile-item__icon">${profileIcons[platform]}</span>
                    <a href="${url}" target="_blank" class="profile-item__link">
                        ${profileNames[platform]}
                    </a>
                </div>
            `).join('');
    }

    populateSkills() {
        const { skills } = this.sampleData;
        this.skillsContainer.innerHTML = skills
            .map(skill => `<span class="skill-tag">${skill}</span>`)
            .join('');
    }

    populateExperience() {
        const { experience } = this.sampleData;
        this.experienceList.innerHTML = experience
            .map(exp => `
                <div class="experience-item">
                    <div class="experience-item__header">
                        <h4 class="experience-item__title">${exp.title}</h4>
                        <div class="experience-item__company">${exp.company}</div>
                        <div class="experience-item__duration">${exp.duration}</div>
                    </div>
                    <p class="experience-item__description">${exp.description}</p>
                </div>
            `).join('');
    }

    populateAchievements() {
        const { achievements } = this.sampleData;
        this.achievementsList.innerHTML = achievements
            .map(achievement => `
                <div class="achievement-item">
                    <span class="achievement-item__icon">🏆</span>
                    <p class="achievement-item__text">${achievement}</p>
                </div>
            `).join('');
    }

    resetApplication() {
        // Reset file input
        this.fileInput.value = '';
        
        // Hide results and progress
        this.resultsSection.classList.add('hidden');
        this.progressSection.classList.add('hidden');
        
        // Show upload section
        this.uploadSection.style.display = 'block';
        
        // Reset progress
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Processing your resume...';
        
        // Clear results
        this.personalInfo.innerHTML = '';
        this.socialProfiles.innerHTML = '';
        this.skillsContainer.innerHTML = '';
        this.experienceList.innerHTML = '';
        this.achievementsList.innerHTML = '';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResumeSummarizer();
});