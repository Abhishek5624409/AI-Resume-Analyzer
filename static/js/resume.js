// Name
document.getElementById("name").addEventListener("input", function () {
    document.getElementById("preview-name").innerText = this.value || "Your Name";
});

// Job Title
document.getElementById("title").addEventListener("input", function () {
    document.getElementById("preview-title").innerText = this.value || "Java Full Stack Developer";
});

// Email
document.getElementById("email").addEventListener("input", function () {
    document.getElementById("preview-email").innerText = this.value || "your@email.com";
});

// Phone
document.getElementById("phone").addEventListener("input", function () {
    document.getElementById("preview-phone").innerText = this.value || "1234567891";
});

// Summary
document.getElementById("summary").addEventListener("input", function () {
    document.getElementById("preview-summary").innerText = this.value || "Professional Summary";
});

document.getElementById("skills").addEventListener("input", function () {
    document.getElementById("preview-skills").innerText =
        this.value || "Java, Spring Boot";
});

// Education
document.getElementById("education").addEventListener("input", function () {
    document.getElementById("preview-education").innerText = this.value || "Education";
});

// Experience
document.getElementById("experience").addEventListener("input", function () {
    document.getElementById("preview-experience").innerText = this.value || "Experience";
});

// Projects
document.getElementById("projects").addEventListener("input", function () {
    document.getElementById("preview-projects").innerText = this.value || "Projects";
});

// Certificates
document.getElementById("certificates").addEventListener("input", function () {
    document.getElementById("preview-certificates").innerText = this.value || "Certificates";
});

// Photo Preview






document.getElementById("skills").addEventListener("input", function () {

    const skills = this.value.split(",");

    let html = "";

    skills.forEach(skill => {

        html += `
        <div class="skill">
            <span>${skill.trim()}</span>

            <div class="progress">
                <div class="progress-bar bg-primary"
                     style="width:${70 + Math.random()*30}%">
                </div>
            </div>
        </div>
        `;

    });

    document.getElementById("preview-skills").innerHTML = html;

});

document.getElementById("skills").addEventListener("input", function () {

    const skills = this.value.split(",");

    let html = "";

    skills.forEach(skill => {

        html += `
        <div class="mb-3">
            <strong>${skill.trim()}</strong>
            <div class="progress">
                <div class="progress-bar bg-primary"
                     style="width:90%">
                </div>
            </div>
        </div>`;
    });

    document.getElementById("preview-skills").innerHTML = html;

});

const photo = document.getElementById("photo");

photo.addEventListener("change", function () {
    const file = this.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            document.getElementById("preview-photo").src = e.target.result;
        };

        reader.readAsDataURL(file);
    }
});


document.querySelector('form[action="/download-resume"]').addEventListener("submit", function () {

    document.getElementById("pdf-name").value =
        document.getElementById("name").value;

    document.getElementById("pdf-email").value =
        document.getElementById("email").value;

    document.getElementById("pdf-phone").value =
        document.getElementById("phone").value;

    document.getElementById("pdf-summary").value =
        document.getElementById("summary").value;

    document.getElementById("pdf-skills").value =
        document.getElementById("skills").value;

    document.getElementById("pdf-education").value =
        document.getElementById("education").value;

    document.getElementById("pdf-experience").value =
        document.getElementById("experience").value;

    document.getElementById("pdf-projects").value =
        document.getElementById("projects").value;

    document.getElementById("pdf-certificates").value =
        document.getElementById("certificates").value;

});