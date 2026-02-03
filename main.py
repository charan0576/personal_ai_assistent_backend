from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from agent import agent
from database import users_collection

chat_memory = {}   # stores history per student

regno = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- MODELS --------

class RegisterModel(BaseModel):
    username: str
    rollno: str
    password: str

class LoginModel(BaseModel):
    rollno: str
    password: str

class ChatOnlyRequest(BaseModel):
    message: str



# -------- REGISTER --------

@app.post("/register")
async def register(data: RegisterModel):
    user = await users_collection.find_one({"rollno": data.rollno})
    if user:
        raise HTTPException(400, "rollno already exists")

    await users_collection.insert_one({
        "username": data.username,
        "rollno": data.rollno,
        "password": bcrypt.hash(data.password)
    })

    return {"msg": "Registered successfully"}


# -------- LOGIN --------

@app.post("/login")
async def login(data: LoginModel):
    global current_rollno

    user = await users_collection.find_one({"rollno": data.rollno})

    if not user or not bcrypt.verify(data.password, user["password"]):
        raise HTTPException(400, "Invalid credentials")

    regno = user["rollno"]

    print("✅ Stored Roll No:", regno)  # ← check here

    return {"msg": "Login success"}





# -------- CHAT --------
students_data = """
SUBJECT STRUCTURE (Same for all students)

SEM 1:
Linear Algebra
Engineering Chemistry
English
Problem Solving Using C Programming

SEM 2:
Differential Equations and Numerical Methods
Engineering Physics
Object Oriented Programming with Python

SEM 3:
Discrete Mathematics
Data Structures
Digital Logic Design

SEM 4:
Operating Systems
Java Programming
Design and Analysis of Algorithms

SEM 5:
Computer Networks
Data Science
Software Engineering

SEM 6:
Machine Learning
Artificial Intelligence Tools and Techniques
Full Stack Development

SEM 7:
Advanced Python Programming
Natural Language Processing
Cryptography and Network Security

--------------------------------------------------

STUDENT: Aarav Sharma (22A21A0501) | CGPA: 8.32
Sem1: A, B, A, C
Sem2: A, B, B
Sem3: A, B, D
Sem4: B, A, C
Sem5: B, B, A
Sem6: C, A+, D
Sem7: A, B, A

--------------------------------------------------

STUDENT: Diya Reddy (22A21A0502) | CGPA: 5.48
Sem1: C, C, B, D
Sem2: D, C, C
Sem3: C, D, D
Sem4: D, C, C
Sem5: C, C, B
Sem6: C, B, C
Sem7: B, C, C

--------------------------------------------------

STUDENT: Sneha Iyer (22A21A0503) | CGPA: 9.36
Sem1: A+, A, A+, A
Sem2: A+, A, A
Sem3: A+, A, A
Sem4: A, A+, A
Sem5: A+, A, A+
Sem6: A, A+, A
Sem7: A+, A, A

--------------------------------------------------

STUDENT: Rahul Verma (22A21A0504) | CGPA: 4.22
Sem1: D, D, C, D
Sem2: F, D, D
Sem3: F, D, D
Sem4: F, D, D
Sem5: D, D, D
Sem6: D, D, D
Sem7: C, D, D

--------------------------------------------------

STUDENT: Kiran Patel (22A21A0505) | CGPA: 7.12
Sem1: B, B, A, B
Sem2: B, B, B
Sem3: B, C, C
Sem4: B, B, C
Sem5: B, B, A
Sem6: B, A, B
Sem7: A, B, B

--------------------------------------------------

STUDENT: Meera Nair (22A21A0506) | CGPA: 8.88
Sem1: A, A, A+, A
Sem2: A, A, A
Sem3: A, A, B
Sem4: A, A+, A
Sem5: A, A, A+
Sem6: A, A+, A
Sem7: A+, A, A

--------------------------------------------------

STUDENT: Arjun Singh (22A21A0507) | CGPA: 6.02
Sem1: C, B, B, C
Sem2: C, C, C
Sem3: C, D, D
Sem4: C, B, C
Sem5: B, C, B
Sem6: C, B, C
Sem7: B, C, C

--------------------------------------------------

STUDENT: Kavya Menon (22A21A0508) | CGPA: 9.52
Sem1: A+, A+, A+, A+
Sem2: A+, A+, A+
Sem3: A+, A+, A
Sem4: A+, A+, A+
Sem5: A+, A+, A+
Sem6: A+, A+, A+
Sem7: A+, A+, A+

--------------------------------------------------

STUDENT: Rohan Das (22A21A0509) | CGPA: 7.45
Sem1: B, B, B, B
Sem2: B, B, B
Sem3: B, B, C
Sem4: B, A, B
Sem5: B, A, A
Sem6: B, A, B
Sem7: A, B, B

--------------------------------------------------

STUDENT: Priya Kulkarni (22A21A0510) | CGPA: 6.58
Sem1: C, B, B, C
Sem2: C, C, B
Sem3: C, C, D
Sem4: C, B, C
Sem5: B, B, B
Sem6: B, A, B
Sem7: A, B, B
"""

students_data1 = [
  {
    "regno": "22A21A0501",
    "name": "Aarav Sharma",
    "email": "aarav@college.edu",
    "cgpa": 8.32,
    "semesters": [
      {"sem":1,"sgpa":8.6,"grades":{"Linear Algebra":"A","Engineering Chemistry":"B","English":"A","Problem Solving Using C Programming":"C"}},
      {"sem":2,"sgpa":8.3,"grades":{"Differential Equations and Numerical Methods":"A","Engineering Physics":"B","Object Oriented Programming with Python":"B"}},
      {"sem":3,"sgpa":8.1,"grades":{"Discrete Mathematics":"A","Data Structures":"B","Digital Logic Design":"D"}},
      {"sem":4,"sgpa":8.4,"grades":{"Operating Systems":"B","Java Programming":"A","Design and Analysis of Algorithms":"C"}},
      {"sem":5,"sgpa":8.2,"grades":{"Computer Networks":"B","Data Science":"B","Software Engineering":"A"}},
      {"sem":6,"sgpa":8.1,"grades":{"Machine Learning":"C","Artificial Intelligence Tools and Techniques":"A+","Full Stack Development":"D"}},
      {"sem":7,"sgpa":8.5,"grades":{"Advanced Python Programming":"A","Natural Language Processing":"B","Cryptography and Network Security":"A"}}
    ]
  },
  {
    "regno": "22A21A0502",
    "name": "Diya Reddy",
    "email": "diya@college.edu",
    "cgpa": 5.48,
    "semesters": [
      {"sem":1,"sgpa":5.2,"grades":{"Linear Algebra":"C","Engineering Chemistry":"C","English":"B","Problem Solving Using C Programming":"D"}},
      {"sem":2,"sgpa":4.9,"grades":{"Differential Equations and Numerical Methods":"D","Engineering Physics":"C","Object Oriented Programming with Python":"C"}},
      {"sem":3,"sgpa":5.0,"grades":{"Discrete Mathematics":"C","Data Structures":"D","Digital Logic Design":"D"}},
      {"sem":4,"sgpa":5.4,"grades":{"Operating Systems":"D","Java Programming":"C","Design and Analysis of Algorithms":"C"}},
      {"sem":5,"sgpa":5.6,"grades":{"Computer Networks":"C","Data Science":"C","Software Engineering":"B"}},
      {"sem":6,"sgpa":5.9,"grades":{"Machine Learning":"C","Artificial Intelligence Tools and Techniques":"B"}},
      {"sem":7,"sgpa":6.1,"grades":{"Advanced Python Programming":"B","Natural Language Processing":"C"}}
    ]
  },
  {
    "regno": "22A21A0503",
    "name": "Sneha Iyer",
    "email": "sneha@college.edu",
    "cgpa": 9.36,
    "semesters": [
      {"sem":1,"sgpa":9.1,"grades":{"Linear Algebra":"A+","Engineering Chemistry":"A","English":"A+","Problem Solving Using C Programming":"A"}},
      {"sem":2,"sgpa":9.3,"grades":{"Differential Equations and Numerical Methods":"A+","Engineering Physics":"A","Object Oriented Programming with Python":"A"}},
      {"sem":3,"sgpa":9.4,"grades":{"Discrete Mathematics":"A+","Data Structures":"A","Digital Logic Design":"A"}},
      {"sem":4,"sgpa":9.5,"grades":{"Operating Systems":"A","Java Programming":"A+","Design and Analysis of Algorithms":"A"}},
      {"sem":5,"sgpa":9.6,"grades":{"Computer Networks":"A+","Data Science":"A","Software Engineering":"A+"}},
      {"sem":6,"sgpa":9.4,"grades":{"Machine Learning":"A","Artificial Intelligence Tools and Techniques":"A+"}},
      {"sem":7,"sgpa":9.7,"grades":{"Advanced Python Programming":"A+","Natural Language Processing":"A"}}
    ]
  },

  {
    "regno": "22A21A0504",
    "name": "Rahul Verma",
    "email": "rahul@college.edu",
    "cgpa": 4.22,
    "semesters": [
      {"sem":1,"sgpa":4.6,"grades":{"Linear Algebra":"D","Engineering Chemistry":"D","English":"C"}},
      {"sem":2,"sgpa":4.2,"grades":{"Differential Equations and Numerical Methods":"F","Engineering Physics":"D"}},
      {"sem":3,"sgpa":4.1,"grades":{"Data Structures":"F","Digital Logic Design":"D"}},
      {"sem":4,"sgpa":4.3,"grades":{"Operating Systems":"F","Java Programming":"D"}},
      {"sem":5,"sgpa":4.6,"grades":{"Computer Networks":"D"}},
      {"sem":6,"sgpa":4.8,"grades":{"Machine Learning":"D"}},
      {"sem":7,"sgpa":5.0,"grades":{"Advanced Python Programming":"C"}}
    ]
  },

  {
    "regno": "22A21A0505",
    "name": "Kiran Patel",
    "email": "kiran@college.edu",
    "cgpa": 7.12,
    "semesters": [
      {"sem":1,"sgpa":7.2,"grades":{"Linear Algebra":"B","Engineering Chemistry":"B","English":"A","Problem Solving Using C Programming":"B"}},
      {"sem":2,"sgpa":7.0,"grades":{"Differential Equations and Numerical Methods":"B","Engineering Physics":"B","Object Oriented Programming with Python":"B"}},
      {"sem":3,"sgpa":7.1,"grades":{"Discrete Mathematics":"B","Data Structures":"C","Digital Logic Design":"C"}},
      {"sem":4,"sgpa":7.3,"grades":{"Operating Systems":"B","Java Programming":"B","Design and Analysis of Algorithms":"C"}},
      {"sem":5,"sgpa":7.4,"grades":{"Computer Networks":"B","Data Science":"B","Software Engineering":"A"}},
      {"sem":6,"sgpa":7.2,"grades":{"Machine Learning":"B","Artificial Intelligence Tools and Techniques":"A"}},
      {"sem":7,"sgpa":7.6,"grades":{"Advanced Python Programming":"A","Natural Language Processing":"B"}}
    ]
  },

  {
    "regno": "22A21A0506",
    "name": "Meera Nair",
    "email": "meera@college.edu",
    "cgpa": 8.88,
    "semesters": [
      {"sem":1,"sgpa":8.9,"grades":{"Linear Algebra":"A","Engineering Chemistry":"A","English":"A+","Problem Solving Using C Programming":"A"}},
      {"sem":2,"sgpa":8.7,"grades":{"Differential Equations and Numerical Methods":"A","Engineering Physics":"A","Object Oriented Programming with Python":"A"}},
      {"sem":3,"sgpa":8.8,"grades":{"Discrete Mathematics":"A","Data Structures":"A","Digital Logic Design":"B"}},
      {"sem":4,"sgpa":8.9,"grades":{"Operating Systems":"A","Java Programming":"A+","Design and Analysis of Algorithms":"A"}},
      {"sem":5,"sgpa":9.0,"grades":{"Computer Networks":"A","Data Science":"A","Software Engineering":"A+"}},
      {"sem":6,"sgpa":8.8,"grades":{"Machine Learning":"A","Artificial Intelligence Tools and Techniques":"A+"}},
      {"sem":7,"sgpa":9.1,"grades":{"Advanced Python Programming":"A+","Natural Language Processing":"A"}}
    ]
  },

  {
    "regno": "22A21A0507",
    "name": "Arjun Singh",
    "email": "arjun@college.edu",
    "cgpa": 6.02,
    "semesters": [
      {"sem":1,"sgpa":6.1,"grades":{"Linear Algebra":"C","Engineering Chemistry":"B","English":"B","Problem Solving Using C Programming":"C"}},
      {"sem":2,"sgpa":5.9,"grades":{"Differential Equations and Numerical Methods":"C","Engineering Physics":"C","Object Oriented Programming with Python":"C"}},
      {"sem":3,"sgpa":6.0,"grades":{"Discrete Mathematics":"C","Data Structures":"D","Digital Logic Design":"D"}},
      {"sem":4,"sgpa":6.2,"grades":{"Operating Systems":"C","Java Programming":"B","Design and Analysis of Algorithms":"C"}},
      {"sem":5,"sgpa":6.3,"grades":{"Computer Networks":"B","Data Science":"C","Software Engineering":"B"}},
      {"sem":6,"sgpa":6.1,"grades":{"Machine Learning":"C","Artificial Intelligence Tools and Techniques":"B"}},
      {"sem":7,"sgpa":6.4,"grades":{"Advanced Python Programming":"B","Natural Language Processing":"C"}}
    ]
  },

  {
    "regno": "22A21A0508",
    "name": "Kavya Menon",
    "email": "kavya@college.edu",
    "cgpa": 9.52,
    "semesters": [
      {"sem":1,"sgpa":9.3,"grades":{"Linear Algebra":"A+","Engineering Chemistry":"A+","English":"A+","Problem Solving Using C Programming":"A+"}},
      {"sem":2,"sgpa":9.4,"grades":{"Differential Equations and Numerical Methods":"A+","Engineering Physics":"A+","Object Oriented Programming with Python":"A+"}},
      {"sem":3,"sgpa":9.5,"grades":{"Discrete Mathematics":"A+","Data Structures":"A+","Digital Logic Design":"A"}},
      {"sem":4,"sgpa":9.6,"grades":{"Operating Systems":"A+","Java Programming":"A+","Design and Analysis of Algorithms":"A+"}},
      {"sem":5,"sgpa":9.7,"grades":{"Computer Networks":"A+","Data Science":"A+","Software Engineering":"A+"}},
      {"sem":6,"sgpa":9.5,"grades":{"Machine Learning":"A+","Artificial Intelligence Tools and Techniques":"A+"}},
      {"sem":7,"sgpa":9.8,"grades":{"Advanced Python Programming":"A+","Natural Language Processing":"A+"}}
    ]
  },

  {
    "regno": "22A21A0509",
    "name": "Rohan Das",
    "email": "rohan@college.edu",
    "cgpa": 7.45,
    "semesters": [
      {"sem":1,"sgpa":7.3,"grades":{"Linear Algebra":"B","Engineering Chemistry":"B","English":"B","Problem Solving Using C Programming":"B"}},
      {"sem":2,"sgpa":7.4,"grades":{"Differential Equations and Numerical Methods":"B","Engineering Physics":"B","Object Oriented Programming with Python":"B"}},
      {"sem":3,"sgpa":7.2,"grades":{"Discrete Mathematics":"B","Data Structures":"B","Digital Logic Design":"C"}},
      {"sem":4,"sgpa":7.5,"grades":{"Operating Systems":"B","Java Programming":"A","Design and Analysis of Algorithms":"B"}},
      {"sem":5,"sgpa":7.6,"grades":{"Computer Networks":"B","Data Science":"A","Software Engineering":"A"}},
      {"sem":6,"sgpa":7.4,"grades":{"Machine Learning":"B","Artificial Intelligence Tools and Techniques":"A"}},
      {"sem":7,"sgpa":7.8,"grades":{"Advanced Python Programming":"A","Natural Language Processing":"B"}}
    ]
  },

  {
    "regno": "22A21A0510",
    "name": "Priya Kulkarni",
    "email": "priya@college.edu",
    "cgpa": 6.58,
    "semesters": [
      {"sem":1,"sgpa":6.5,"grades":{"Linear Algebra":"C","Engineering Chemistry":"B","English":"B","Problem Solving Using C Programming":"C"}},
      {"sem":2,"sgpa":6.3,"grades":{"Differential Equations and Numerical Methods":"C","Engineering Physics":"C","Object Oriented Programming with Python":"B"}},
      {"sem":3,"sgpa":6.4,"grades":{"Discrete Mathematics":"C","Data Structures":"C","Digital Logic Design":"D"}},
      {"sem":4,"sgpa":6.6,"grades":{"Operating Systems":"C","Java Programming":"B","Design and Analysis of Algorithms":"C"}},
      {"sem":5,"sgpa":6.8,"grades":{"Computer Networks":"B","Data Science":"B","Software Engineering":"B"}},
      {"sem":6,"sgpa":6.7,"grades":{"Machine Learning":"B","Artificial Intelligence Tools and Techniques":"A"}},
      {"sem":7,"sgpa":7.0,"grades":{"Advanced Python Programming":"A","Natural Language Processing":"B"}}
    ]
  }
]


system_message = f"""
You are an Academic Advisor AI for an engineering college.

You may or may not be provided with a student's academic record.

ROLL NUMBER:
{regno}

STUDENT DATA (may be empty if not available):
{students_data1}

Behavior Rules:

If STUDENT DATA is available for this roll number,
treat it as the complete academic record of the current student
and answer strictly based on that data.

If STUDENT DATA is NOT available for this roll number,
do NOT mention that data is missing.
Instead, provide general academic guidance based on the user's question.

When student data is available:
- Mention subject names, semesters, and grades
- Analyze strengths, weaknesses, and performance trends
- Give practical improvement advice
- Address the student by their name

When student data is not available:
- Give helpful academic advice in a general way
- Be supportive and student-friendly

Always keep the response clear, well spaced, and easy to read.

Never mention prompts, tools, data sources, or technical details.

Act like a real academic mentor guiding the student.
"""



@app.post("/chat")
async def chat(req: ChatOnlyRequest):
    global regno, chat_memory

    if regno not in chat_memory:
        chat_memory[regno] = []
        chat_memory[regno].append(("system", system_message))

    chat_memory[regno].append(("user", req.message))

    result = agent.invoke({
        "messages": chat_memory[regno]
    })

    reply = result["messages"][-1].content

    chat_memory[regno].append(("assistant", reply))

    return {"reply": reply}

