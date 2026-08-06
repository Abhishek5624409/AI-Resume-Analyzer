print("Hello")
import re
from flask import session
import bcrypt
import random
from flask_mail import Mail,Message
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from flask import make_response
from xhtml2pdf import pisa
from io import BytesIO


import os
import matplotlib.pyplot as plt
import os
import pdfplumber
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
     password="abhishek56242002@#*",   
    database="resume_db",
    port=3306
)
import bcrypt



from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3.6-flash")


app = Flask(__name__)
app.secret_key="yadav@1234resumebuilder"



cursor = conn.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS resumes(
id INT PRIMARY KEY AUTO_INCREMENT,
name TEXT,
email TEXT,
phone TEXT,
score INT,
ats_score INT)
""")
conn.commit()
   


@app.route("/")
def home():
    if "user_id" not in session:
       return redirect("/register")

    cursor.execute("SELECT COUNT(*) FROM resumes WHERE user_id=%s",
                   (session["user_id"],))
    total_resumes = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM resumes")
    avg_score = cursor.fetchone()[0]

    if avg_score is None:
        avg_score = 0

    cursor.execute("SELECT AVG(ats_score) FROM resumes")
    avg_ats = cursor.fetchone()[0]

    if avg_ats is None:
        avg_ats = 0

    return render_template(
        "dashboard.html",
        total_resumes=total_resumes,
        avg_score=round(avg_score, 2),
        avg_ats=round(avg_ats, 2)
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        
        username = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute(
        "INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
        (username, email, hashed_password)
    )
        conn.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user:
            if bcrypt.checkpw(password.encode(), user[3].encode()):
                session["user_id"] = user[0]
                session["user_name"] = user[1]
                return redirect(url_for("home"))
            else:
                return "Wrong Password"
        else:
            return "User Not Found"

    return render_template("login.html")




  







@app.route("/upload", methods=["POST"])
def upload():
         file = request.files["resume"]

         job_description = request.form["job_description"]

         if file:
                 path = os.path.join("uploads", file.filename)
                 file.save(path)

         text = ""

         with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

                # Email
                email = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)

                prompt = f"""
                Analyze this resume and giv:
                1.Resume Score out of 100
                2.ATS Score out of 100
                3.Strengths
                4.Weaknesses
                5.Skill Missing
                6.Imorovement Suggestions

                Resume:
                {text}

                Job Description
                { job_description}"""

                try:
                  response = model.generate_content(prompt)
                  ai_feedback = response.text
                except Exception:
                  ai_feedback = """
                  AI Feedback is temporarily unavailable.

                Possible reasons:
                - Gemini API daily quota exceeded
                  - Internet connection issue
                   - API key problem

                     Please try again later.
                         """

# Phone
                phone = re.findall(r'\b\d{10}\b', text)

# Name
                lines = text.split("\n")
                name = lines[0].strip() if lines else "Not Found"


                # Projects
            project_keywords = ["Project", "Projects", "Academic Project"]
            projects = "Not Found"
            for line in text.split("\n"):
             if any(keyword.lower() in line.lower() for keyword in project_keywords):
              projects = line
             break

# Experience
         experience_keywords = ["Experience", "Work Experience", "Internship"]
         experience = "Fresher"

         for line in text.split("\n"):
          if any(keyword.lower() in line.lower() for keyword in experience_keywords):
           experience = line
          break

        
         skills = [
            "Python", "Java", "Flask", "HTML",
            "CSS", "JavaScript", "SQL", "React",
            "Docker", "Git"
        ]

         

         found_skills = []

         for skill in skills:
            if skill.lower() in text.lower():
                found_skills.append(skill)

            score = int((len(found_skills) / len(skills)) * 100)

         missing_skills = []
         for skill in skills:
            if skill not in found_skills:
                missing_skills.append(skill)

                

                matched = 0

                for skill in found_skills:
                 if skill.lower() in job_description.lower():
                  matched += 1

            ats_score = int((matched / len(skills)) * 100)
            cursor.execute(
             """INSERT INTO resumes
            ( user_id,name, email, phone, score, ats_score)
              VALUES (%s, %s, %s, %s, %s,%s)
              """,
           (
             session["user_id"],        
             name,
             email[0] if email else "Not Found",       
             phone[0] if phone else "Not Found",
             score,
            ats_score
             )
             )
            conn.commit()
            return render_template(
     "result.html",
     projects=projects,
     experience=experience,
    name=name,
    email=email[0] if email else "Not Found",
    phone=phone[0] if phone else "Not Found",
    skills=found_skills,
    score=score,
    ats_score=ats_score,
     missing=missing_skills,
     ai_feedback=ai_feedback
)

@app.route("/history")
def history():
    cursor.execute("SELECT * FROM resumes WHERE user_id=%s",
                   (session["user_id"],))
    data = cursor.fetchall()

    total_resumes=len(data)

    if total_resumes > 0:
        average_score = sum(row[4]for row in
        data) / total_resumes
    else:
        average_score=0

    scores = [row[4] for row in data]
    names=[row[1]for row in data]
    ats_scores = [row[5] for row in data]

    plt.figure(figsize=(8,4))
    plt.bar(names, scores,color="skyblue")
    plt.ylim(0,100)
    plt.title("Resume Scores")
    plt.xlabel("Candidates")
    plt.ylabel("Score(%)")
    plt.xticks(rotation=0)
    plt.tight_layout()

    os.makedirs("static", exist_ok=True)
    plt.savefig("static/chart.png")
    labels= names
    sizes= scores

    plt.figure(figsize=(6,6))
    plt.pie(sizes,labels=labels,autopct="%1.1f%%")
    plt.title("Resume Score Distribution")

    plt.savefig("static/piechart.png")
    plt.close()

    return render_template("history.html", data=data,
         total_resumes=total_resumes,
                           average_score=round(average_score,2))
   
      


    

         

       
print(__name__)
from flask import redirect
@app.route("/delete/<int:id>")
def detete(id):
  cursor.execute("DELETE FROM resumes WHERE id=%s",(id,))
  conn.commit()
  return redirect("/history")




@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        return f"Reset link sent to {email}"

    return render_template("forgot_password.html")




@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]

        cursor.execute(
            "UPDATE users SET username=%s, email=%s ,WHERE id=%s",
            (username, email,session["user_id"])
        )

        conn.commit()

    cursor.execute("SELECT username, email FROM users WHERE id=1")
    user = cursor.fetchone()

    return render_template(
        "profile.html",
        username=user[0],
        email=user[1]
    )

@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        return "Password Changed Successfully"
    return render_template("change_password.html")


@app.route("/resume-tips")
def resume_tips():
    tips = [
        "Keep your resume to 1-2 pages.",
        "Use action verbs like Developed, Designed, Created.",
        "Add measurable achievements.",
        "Include relevant technical skills.",
        "Customize your resume for each job.",
        "Keep ATS-friendly formatting.",
        "Avoid spelling and grammar mistakes.",
        "Add GitHub and LinkedIn profile links."
    ]
    return render_template("resume_tips.html", tips=tips)




@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/download-report/<int:id>")
def download_report(id):
    print("ID=",id)

    cursor.execute("""
    SELECT name, email, phone, score, ats_score
    FROM resumes
    WHERE id=%s
    """, (id,))

    resume = cursor.fetchone()

    if not resume:
     return "Resume Not Found"

    name, email, phone, score, ats_score = resume

    
    cursor.execute("SELECT*FROM resumes")
    print(cursor.fetchall())
    



    pdf_file = f"Resume_Report_{id}.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>AI Resume Analyzer Report</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Name:</b> {name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Email:</b> {email}", styles["Normal"]))
    story.append(Paragraph(f"<b>Phone:</b> {phone}", styles["Normal"]))
    story.append(Paragraph(f"<b>Resume Score:</b> {score}%", styles["Normal"]))
    story.append(Paragraph(f"<b>ATS Score:</b> {ats_score}%", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph("<b>Generated by AI Resume Analyzer</b>", styles["Heading2"]))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)

@app.route("/resume-builder")
def resume_builder():
    return render_template(
    "resume_builder.html")

@app.route("/generate-resume", methods=["POST"])
def generate_resume():
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    skills = request.form["skills"]

    return f"""
    <h1>Resume Generated Successfully</h1>
    <h2>{name}</h2>
    <p>Email: {email}</p>
    <p>Phone: {phone}</p>
    <p>Skills: {skills}</p>
    """ 
    return render_template(
    "resume_preview.html",
    name=name,
    email=email,
    phone=phone,
    skills=skills,
    experience=experience,
    projects=projects,
    photo_path=photo_path
)
   

@app.route("/edit-resume", methods=["POST"])
def edit_resume():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    skills = request.form["skills"]
    experience = request.form["experience"]
    projects = request.form["projects"]

    return render_template(
        "edit_resume.html",
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        experience=experience,
        projects=projects
    )

@app.route("/download-resume", methods=["POST"])
def download_resume():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    skills = request.form["skills"]
    experience = request.form["experience"]
    projects = request.form["projects"]

    pdf_file = "Professional_Resume.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Professional Resume</b>", styles["Title"]))
    story.append(Paragraph(f"<b>Name:</b> {name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Email:</b> {email}", styles["Normal"]))
    story.append(Paragraph(f"<b>Phone:</b> {phone}", styles["Normal"]))
    story.append(Paragraph(f"<b>Skills:</b> {skills}", styles["Normal"]))
    story.append(Paragraph(f"<b>Experience:</b> {experience}", styles["Normal"]))
    story.append(Paragraph(f"<b>Projects:</b> {projects}", styles["Normal"]))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)



@app.route("/download-resume", methods=["POST"])
def download_resume_pdf():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    summary = request.form["summary"]
    skills = request.form["skills"]
    education = request.form["education"]
    experience = request.form["experience"]
    projects = request.form["projects"]
    certificates = request.form["certificates"]

    pdf_file = "Professional_Resume.pdf"

    doc = SimpleDocTemplate(pdf_file)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>Professional Resume</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Name:</b> {name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Email:</b> {email}", styles["Normal"]))
    story.append(Paragraph(f"<b>Phone:</b> {phone}", styles["Normal"]))
    story.append(Paragraph(f"<b>Summary:</b> {summary}", styles["Normal"]))
    story.append(Paragraph(f"<b>Skills:</b> {skills}", styles["Normal"]))
    story.append(Paragraph(f"<b>Education:</b> {education}", styles["Normal"]))
    story.append(Paragraph(f"<b>Experience:</b> {experience}", styles["Normal"]))
    story.append(Paragraph(f"<b>Projects:</b> {projects}", styles["Normal"]))
    story.append(Paragraph(f"<b>Certificates:</b> {certificates}", styles["Normal"]))

    doc.build(story)

    return send_file(pdf_file, as_attachment=True)



@app.route("/download-resume", methods=["POST"])
def download_resume_pdf_():

    html = render_template(
        "resume_preview.html",
        name=request.form.get("name"),
        email=request.form.get("email"),
        phone=request.form.get("phone"),
        summary=request.form.get("summary"),
        skills=request.form.get("skills"),
        education=request.form.get("education"),
        experience=request.form.get("experience"),
        projects=request.form.get("projects"),
        certificates=request.form.get("certificates")
    )

    pdf = BytesIO()
    pisa.CreatePDF(html, dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=Resume.pdf"

    return response




if __name__ == "__main__":
    print("Starting Flask...")
    app.run(debug=True)

@app.route("/test")
def test():
    return "Working"    