from flask import Flask, render_template,request  

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"]) 
def calculator(): 
    result = "" 
    if request.method == "POST": 
      num1 = float(request.form["num1"]) 
      num2 = float(request.form["num2"]) 
      operation = request.form["operation"] 
      if operation == "add": 
        result = num1 + num2 
      elif operation == "sub": 
        result = num1 - num2 
      elif operation == "mul": 
        result = num1 * num2 
      elif operation == "div": 
        if num2 != 0: 
          result = num1 / num2
      else: result = "Cannot divide by zero"

    return render_template("templates/calculator.html", result=result) 
if __name__ == "__main__": 
  app.run(debug=True)