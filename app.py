from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = ""
    if request.method == "POST":
        num1 = request.form.get("num1")
        num2 = request.form.get("num2")
        operator = request.form.get("operator")

        try:
            num1 = float(num1)
            num2 = float(num2)

            if operator == "+":
                result = num1 + num2
            elif operator == "-":
                result = num1 - num2
            elif operator == "*":
                result = num1 * num2
            elif operator == "/":
                result = num1 / num2
        except:
            result = "Error"

    return render_template("cal.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)