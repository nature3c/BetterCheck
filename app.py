from flask import Flask, render_template_string, request
import datetime
import csv
import os
import re

app = Flask(__name__)
CHECKIN_FILE = "web_checkins.csv"
START_TIME = datetime.time(18, 30)  # 6:30 PM
END_TIME = datetime.time(19, 30)    # 7:30 PM

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Rolling Check-In</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { padding: 2rem; background: #f7f9fc; }
    .container { max-width: 600px; }
    .card { margin-top: 1rem; }
  </style>
</head>
<body>
<div class="container">
  <h1 class="mb-4 text-center">Rolling Check-In (6:30 PM - 7:30 PM)</h1>

  {% if message %}
    <div class="alert alert-info">{{ message }}</div>
  {% elif error %}
    <div class="alert alert-danger">{{ error }}</div>
  {% endif %}

  <form method="POST" class="card p-3 shadow-sm">
    <div class="mb-3">
      <label for="name" class="form-label">Full Name</label>
      <input type="text" class="form-control" name="name" id="name" required>
    </div>
    <div class="mb-3">
      <label for="id" class="form-label">ID Number (6 digits)</label>
      <input type="text" class="form-control" name="id" id="id" pattern="\\d{6}" maxlength="6" required>
    </div>
    <button type="submit" class="btn btn-primary">Check In</button>
  </form>

  <div class="card p-3 mt-4">
    <h5>Check-In Log</h5>
    <table class="table table-striped">
      <thead><tr><th>Name</th><th>ID</th><th>Time</th></tr></thead>
      <tbody>
      {% for name, id, time in checkins %}
        <tr><td>{{ name }}</td><td>{{ id }}</td><td>{{ time }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""

def is_within_checkin_window(current_time):
    return START_TIME <= current_time.time() <= END_TIME

def log_checkin(name, id_number):
    now = datetime.datetime.now()
    with open(CHECKIN_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, id_number, now.strftime("%Y-%m-%d %H:%M:%S")])

def load_checkins():
    if not os.path.exists(CHECKIN_FILE):
        return []
    with open(CHECKIN_FILE, newline='') as file:
        return list(csv.reader(file))

@app.route("/", methods=["GET", "POST"])
def index():
    message, error = "", ""
    if request.method == "POST":
        name = request.form["name"].strip()
        id_number = request.form["id"].strip()

        if not re.fullmatch(r"\d{6}", id_number):
            error = "ID number must be exactly 6 digits."
        elif not name:
            error = "Name cannot be blank."
        elif not is_within_checkin_window(datetime.datetime.now()):
            error = "Check-in is only allowed between 6:30 PM and 7:30 PM."
        else:
            log_checkin(name, id_number)
            message = f"{name}, you are checked in at {datetime.datetime.now().strftime('%H:%M:%S')}."

    checkins = load_checkins()
    return render_template_string(HTML, checkins=checkins, message=message, error=error)

if __name__ == "__main__":
    app.run(debug=True)
