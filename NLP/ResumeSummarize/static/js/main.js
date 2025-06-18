// Handle file selection from file input
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

// Handle file drop
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    
    const uploadContainer = event.currentTarget;
    uploadContainer.classList.remove('border-blue-500', 'bg-blue-50');
    
    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
        uploadFile(file);
    } else {
        alert('Please upload a PDF file');
    }
}

// Upload file to server
async function uploadFile(file) {
    const loading = document.getElementById('loading');
    const uploadContainer = document.getElementById('upload-container');
    
    try {
        loading.classList.remove('hidden');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error processing resume. Please try again.');
    } finally {
        loading.classList.add('hidden');
    }
}

// Display the extracted information
function displayResults(data) {
    // Hide upload container and show results
    document.getElementById('upload-container').classList.add('hidden');
    document.getElementById('results').classList.remove('hidden');
    
    // Display personal information
    const personalInfo = document.getElementById('personal-info');
    personalInfo.innerHTML = '';
    
    if (data.name) {
        personalInfo.innerHTML += `
            <div class="flex items-start">
                <span class="text-gray-600 font-medium w-24">Name:</span>
                <span class="flex-1">${data.name}</span>
            </div>`;
    }
    
    if (data.email) {
        personalInfo.innerHTML += `
            <div class="flex items-start">
                <span class="text-gray-600 font-medium w-24">Email:</span>
                <span class="flex-1">${data.email}</span>
            </div>`;
    }
    
    if (data.phone) {
        personalInfo.innerHTML += `
            <div class="flex items-start">
                <span class="text-gray-600 font-medium w-24">Phone:</span>
                <span class="flex-1">${data.phone}</span>
            </div>`;
    }
    
    // Display education
    const educationInfo = document.getElementById('education-info');
    educationInfo.innerHTML = '';
    
    if (data.education && data.education.length > 0) {
        data.education.forEach(edu => {
            let eduHtml = `
                <div class="mb-4 pb-4 border-b border-gray-100 last:border-0 last:pb-0 last:mb-0">
                    <h4 class="font-semibold text-gray-800">${edu.degree || 'Degree'}</h4>
                    <p class="text-gray-600">${edu.institution || ''} ${edu.year ? `• ${edu.year}` : ''}</p>`;
            
            if (edu.description) {
                eduHtml += `<p class="text-gray-700 mt-1 text-sm">${edu.description}</p>`;
            }
            
            eduHtml += '</div>';
            educationInfo.innerHTML += eduHtml;
        });
    } else {
        educationInfo.innerHTML = '<p class="text-gray-500">No education information found</p>';
    }
    
    // Display skills
    const skillsInfo = document.getElementById('skills-info');
    skillsInfo.innerHTML = '';
    
    if (data.skills && data.skills.length > 0) {
        data.skills.forEach(skill => {
            skillsInfo.innerHTML += `
                <span class="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                    ${skill}
                </span>`;
        });
    } else {
        skillsInfo.innerHTML = '<p class="text-gray-500">No skills found</p>';
    }
    
    // Display social and coding profiles
    const socialLinks = document.getElementById('social-links');
    socialLinks.innerHTML = '';
    
    const profiles = [
        { key: 'github', icon: 'github', name: 'GitHub' },
        { key: 'linkedin', icon: 'linkedin', name: 'LinkedIn' },
        { key: 'leetcode', icon: 'code', name: 'LeetCode' },
        { key: 'hackerrank', icon: 'laptop-code', name: 'HackerRank' },
        { key: 'codechef', icon: 'utensils', name: 'CodeChef' },
        { key: 'codeforces', icon: 'code-branch', name: 'CodeForces' },
        { key: 'geeksforgeeks', icon: 'laptop', name: 'GeeksforGeeks' }
    ];
    
    profiles.forEach(profile => {
        if (data[profile.key]) {
            let url = data[profile.key];
            if (!url.startsWith('http')) {
                // Add https:// if not present
                url = `https://${url}`;
            }
            
            socialLinks.innerHTML += `
                <a href="${url}" target="_blank" class="flex items-center px-4 py-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
                    <i class="fab fa-${profile.icon} text-gray-700 mr-2"></i>
                    <span>${profile.name}</span>
                </a>`;
        }
    });
    
    if (socialLinks.innerHTML === '') {
        socialLinks.innerHTML = '<p class="text-gray-500">No social or coding profiles found</p>';
    }
}

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    document.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Scroll to results after loading
function scrollToResults() {
    const results = document.getElementById('results');
    if (results && !results.classList.contains('hidden')) {
        results.scrollIntoView({ behavior: 'smooth' });
    }
}

// Call scrollToResults after the page loads
window.addEventListener('load', scrollToResults);
