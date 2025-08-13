from flask import Flask, render_template, request, redirect
import csv

app = Flask(__name__)

# Data for dynamic content
projects = [
    {"name": "AI Chatbot", "description": "Built a chatbot using Python and NLP"},
    {"name": "Data Dashboard", "description": "Created a dashboard with Flask and Chart.js"},
    {"name": "Portfolio Website", "description": "Designed and deployed my personal site"}
]

skills = ["Python", "Flask", "HTML", "CSS", "JavaScript", "SQL"]

@app.route('/')
def home():
    return render_template("index.html", projects=projects, skills=skills)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Save to CSV
        with open('contacts.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, email, message])

        return redirect('/')
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
