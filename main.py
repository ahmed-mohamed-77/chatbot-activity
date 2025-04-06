from database import Base, engine, SeedTable
from datetime import time, datetime
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import uvicorn

Base.metadata.create_all(engine)

local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()
        
app = FastAPI()
@app.get("/")
def hello_world():
    return {"message" : "hello world"}

@app.get("/seed")
def seed_db(db=Depends(get_db)):

    # Define the shifts for each day
    shifts = [
        # Monday to Thursday
        {"day_no": 0, "day": "Monday", "start_shift": time(9, 0), "end_shift": time(18, 0), 
            "start_break": time(13, 30), "end_break": time(14, 30)},
        {"day_no": 1, "day": "Tuesday", "start_shift": time(9, 0), "end_shift": time(18, 0), 
            "start_break": time(13, 30), "end_break": time(14, 30)},
        {"day_no": 2, "day": "Wednesday", "start_shift": time(9, 0), "end_shift": time(18, 0), 
            "start_break": time(13, 30), "end_break": time(14, 30)},
        {"day_no": 3, "day": "Thursday", "start_shift": time(9, 0), "end_shift": time(18, 0), 
            "start_break": time(13, 30), "end_break": time(14, 30)},
        
        # Friday
        {"day_no": 4, "day": "Friday", "start_shift": time(9, 0), "end_shift": time(18, 0), 
            "start_break": time(12, 30), "end_break": time(14, 30)},
        
        # Saturday
        {"day_no": 5, "day": "Saturday", "start_shift": time(9, 0), "end_shift": time(17, 0), 
            "start_break": time(12, 30), "end_break": time(13, 0)},
    ]

    for shift in shifts:
        shift["start_shift"] = shift["start_shift"].strftime('%H:%M')
        shift["end_shift"] = shift["end_shift"].strftime('%H:%M')
        shift["start_break"] = shift["start_break"].strftime('%H:%M')
        shift["end_break"] = shift["end_break"].strftime('%H:%M')
        
        seed_table = SeedTable(
            day_no = shift["day_no"],
            day = shift["day"],
            start_shift = shift["start_shift"],
            end_shift = shift["end_shift"],
            start_break = shift["start_break"],
            end_break = shift["end_break"]
        )
        
        try:
            db.add(seed_table)
            db.commit()
            db.refresh(seed_table)
            
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    return {"message": "Table has been inserted successfully", "shift": seed_table}


@app.get("/chatbot")
def chatbot_activity(db = Depends(get_db)):
    
    # Get current date and time
    current_datetime = datetime.now()

    # Extract the current day (full weekday name like "Monday")
    current_day = current_datetime.strftime("%A")

    current_time = current_datetime.time()  # ✅ get current time as datetime.time

    # Get the index of the day of the week (0 = Monday, 6 = Sunday)
    day_index = current_datetime.weekday()

    today_shift = db.query(SeedTable).filter(SeedTable.day == current_day).first()


    if today_shift:
        start_shift = today_shift.start_shift
        end_shift = today_shift.end_shift
        start_break = today_shift.start_break
        end_break = today_shift.end_break

        if start_shift <= current_time < end_shift:
            if start_break <= current_time <= end_break:
                return {
                    "available": True,
                    "message": "Chatbot is available during break time."
                }
            else:
                return {
                    "available": False,
                    "message": "Chatbot is not available during working hours."
                }
        else:
            return {
                "available": True,
                "message": "Chatbot is available outside shift hours."
            }
    else:
        return {
            "available": True,
            "message": "Chatbot is available today (no shift/holiday)."
        }

if __name__ == "__main__":
    uvicorn.run(app=app, port=8000, host="0.0.0.0")



