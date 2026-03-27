import json
import os

#from Demos.BackupRead_BackupWrite import sid
#from spacy.symbols import agent

FILE_NAME = "student.json"
#------------Class---------------------
class Student:
    def __init__(self,sid,name,age,course):
        self.sid= sid
        self.name= name
        self.age = age
        self.course = course 
    def to_dict(self):
        return {"sid":self.sid,
                "name":self.name,
                "age":self.age,
                "course":self.course
        }
#--------------File Handeling-----------------
def load_data():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r") as file:
        return json.load(file)
def save_data(data):
    with open(FILE_NAME,"w") as file:
        json.dump(data,file,indent=4)
#-------------Functions----------------
def add_student():
    try:
        sid = int(input("enter student id:"))
        name = input("enter student name:")
        age = int(input("enter student age:"))
        course = input("enter student course:")
        student = Student(sid,name,age,course)
        data = load_data()
        data.append(student.to_dict())
        save_data(data)
        print("student added successfully")
    except ValueError:
        print("Data is inappropriate")
def view_student():
    data = load_data()
    if not  data:
        print("No student data found")
        return
    else:
        for student in data:
            print(f"\nID: {student['sid']}")
            print(f"Name: {student['name']}")
            print(f"Age: {student['age']}")
            print(f"Course: {student['course']}")
def update_student():
    sid = int(input("enter student id:"))
    data = load_data()
    for student in data:
        if student['sid'] == sid:
            student['name'] = input("enter student new name:")
            student['age'] = int(input("enter student new age:"))
            student['course'] = input("enter student new course:")
            save_data(data)
            print("student updated successfully")
            return
    print("student not found")
           
def search_student():
    sid = int(input("enter student id:"))
    data = load_data()
    for student in data:
        if student['sid'] == sid:
            print("Student found")
            print(student)
            return
    print("student not found")
 
def delete_student():
    
        sid = int(input("enter student id:"))
        data = load_data()
        new_data = [s for s in data if s['sid'] != sid ]
        if len(data) == len(new_data):
            print("Student not found!")
        else:
            save_data(new_data)
            print("student record deleted successfully")
def menu():
    while True:
        print("\n ================ Student Management System ==============")
        print("1. add student")
        print("2. View student")
        print("3. Search student")
        print("4. Update student")
        print("5. Delete student")
        print("6. Exit")
        
        choice = int(input("Enter your choice:"))
        
        if choice == 1:
            add_student()
        elif choice == 2:
            view_student()
        elif choice == 3:
            search_student()
        elif choice == 4:
            update_student()
        elif choice == 5:
            delete_student()
        elif choice == 6:
            print("Thank you for using this program")
            break
        else:
            print("Invalid choice")
            
if __name__ == "__main__":
    menu()