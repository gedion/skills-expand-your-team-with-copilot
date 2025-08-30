"""
In-memory database configuration and setup for Mergington High School API
"""

from argon2 import PasswordHasher

# In-memory storage for development
activities_data = {}
teachers_data = {}

# Simple in-memory collection class to mimic MongoDB API
class InMemoryCollection:
    def __init__(self, data_store):
        self.data = data_store
    
    def find(self, query=None):
        if query is None:
            return [{"_id": k, **v} for k, v in self.data.items()]
        # Simplified query support for basic operations
        result = []
        for key, value in self.data.items():
            match = True
            for q_key, q_value in query.items():
                if q_key == "_id":
                    if key != q_value:
                        match = False
                        break
                elif "." in q_key:  # Handle nested queries like "schedule_details.days"
                    nested_keys = q_key.split(".")
                    nested_value = value
                    for nkey in nested_keys:
                        if isinstance(nested_value, dict) and nkey in nested_value:
                            nested_value = nested_value[nkey]
                        else:
                            match = False
                            break
                    if match and isinstance(q_value, dict) and "$in" in q_value:
                        if not any(item in nested_value for item in q_value["$in"]):
                            match = False
                elif q_key not in value or value[q_key] != q_value:
                    match = False
                    break
            if match:
                result.append({"_id": key, **value})
        return result
    
    def find_one(self, query):
        results = self.find(query)
        return results[0] if results else None
    
    def insert_one(self, doc):
        doc_id = doc.pop("_id")
        self.data[doc_id] = doc
        return type('Result', (), {'inserted_id': doc_id})()
    
    def update_one(self, query, update):
        doc = self.find_one(query)
        if doc:
            doc_id = doc["_id"]
            if "$push" in update:
                for key, value in update["$push"].items():
                    if key in self.data[doc_id]:
                        self.data[doc_id][key].append(value)
                    else:
                        self.data[doc_id][key] = [value]
            if "$pull" in update:
                for key, value in update["$pull"].items():
                    if key in self.data[doc_id] and value in self.data[doc_id][key]:
                        self.data[doc_id][key].remove(value)
            return type('Result', (), {'modified_count': 1})()
        return type('Result', (), {'modified_count': 0})()
    
    def count_documents(self, query=None):
        return len(self.find(query or {}))
    
    def aggregate(self, pipeline):
        # Simplified aggregation for getting unique days
        if len(pipeline) == 3 and "$unwind" in pipeline[0] and "$group" in pipeline[1]:
            days = set()
            for value in self.data.values():
                if "schedule_details" in value and "days" in value["schedule_details"]:
                    for day in value["schedule_details"]["days"]:
                        days.add(day)
            return [{"_id": day} for day in sorted(days)]
        return []

activities_collection = InMemoryCollection(activities_data)
teachers_collection = InMemoryCollection(teachers_data)

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""

    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    },
    "Study AI once a day": {
        "description": "Daily AI learning sessions for aspiring AI-first entrepreneurs. Study machine learning, artificial intelligence concepts, and emerging technologies",
        "schedule": "Monday to Friday, 8:00 AM - 8:30 AM",
        "schedule_details": {
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "start_time": "08:00",
            "end_time": "08:30"
        },
        "max_participants": 25,
        "participants": ["barki@mergington.edu"]
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]

