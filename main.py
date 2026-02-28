from fastapi import FastAPI, HTTPException, Request
from database import supabase
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum

app = FastAPI(title="University Welfare System")

# Data model for Idea Submission
class IdeaCreate(BaseModel):
    student_id: str
    title: str
    description: str

class PriceUpdate(BaseModel):
    vendor_id: str
    item_id: str
    new_price: float

class ApprovalStatus(str, Enum):
    PENDING_TEACHER = "PENDING_TEACHER"
    PENDING_DSO = "PENDING_DSO"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@app.get("/")
def read_root():
    return {"status": "University Welfare API is Online"}

@app.post("/ideas/submit")
async def submit_idea(idea: IdeaCreate):
    try:
        # Inserting data into the 'student_ideas' table we created
        response = supabase.table("student_ideas").insert({
            "student_id": idea.student_id,
            "title": idea.title,
            "description": idea.description,
            "status": "UNDER_REVIEW"
        }).execute()
        
        return {"message": "Idea submitted successfully", "data": response.data}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/vendors/update-price")
async def propose_price_change(update: PriceUpdate):
    # We don't change 'current_price' yet. 
    # We only update 'proposed_price' and set 'is_approved' to False.
    try:
        response = supabase.table("vendor_price_list").update({
            "proposed_price": update.new_price,
            "is_approved": False
        }).eq("id", update.item_id).execute()
        
        return {"status": "Pending Management Approval", "details": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/admin/approve-price/{item_id}")
async def approve_price(item_id: str):
    # 1. Fetch the proposed price
    # 2. Move it to current_price
    # 3. Set is_approved to True
    item = supabase.table("vendor_price_list").select("*").eq("id", item_id).single().execute()
    
    proposed = item.data['proposed_price']
    
    supabase.table("vendor_price_list").update({
        "current_price": proposed,
        "is_approved": True,
        "proposed_price": None
    }).eq("id", item_id).execute()
    
    return {"status": "Price is now Live"}

@app.post("/approvals/move-to-next/{request_id}")
async def process_approval(request_id: str, current_user_role: str, action: str):
    """
    Logic: 
    - If Teacher approves -> Move to PENDING_DSO
    - If DSO approves -> Move to APPROVED
    """
    # 1. Get current status from Supabase
    request = supabase.table("approval_logs").select("*").eq("id", request_id).single().execute()
    current_status = request.data['status']

    if action == "REJECT":
        supabase.table("approval_logs").update({"status": ApprovalStatus.REJECTED}).eq("id", request_id).execute()
        return {"message": "Request Rejected"}

    # 2. Role-based movement
    new_status = current_status
    if current_user_role == "TEACHER" and current_status == ApprovalStatus.PENDING_TEACHER:
        new_status = ApprovalStatus.PENDING_DSO
    elif current_user_role == "DSO_ADMIN" and current_status == ApprovalStatus.PENDING_DSO:
        new_status = ApprovalStatus.APPROVED

    # 3. Update Database
    supabase.table("approval_logs").update({"status": new_status}).eq("id", request_id).execute()
    
    return {"message": f"Moved to {new_status}"}

@app.get("/search/vendors")
async def search_vendors(category: str = None, query: str = None):
    # Start building the query
    db_query = supabase.table("vendors").select("*")
    
    if category:
        db_query = db_query.eq("category", category)
    if query:
        db_query = db_query.ilike("business_name", f"%{query}%")
        
    response = db_query.execute()
    return response.data

@app.get("/search/jobs")
async def get_jobs(type: str = None):
    # Filter for Technical vs Non-Technical
    db_query = supabase.table("internal_jobs").select("*").eq("status", "OPEN")
    if type:
        db_query = db_query.eq("job_type", type)
        
    response = db_query.execute()
    return response.data


@app.post("/recruitment/webhook")
async def recruitment_webhook(request: Request):
    # 1. Capture the automatic background data from Supabase
    payload = await request.json()
    
    # 2. Extract the new row data (the 'record')
    new_drive = payload.get("record")
    if not new_drive:
        return {"status": "ignored", "message": "No record found"}

    tag = new_drive.get("interest_tag")
    title = new_drive.get("title", "New Drive")

    # 3. Find students matching the interest
    # 'cs' stands for 'contains' - perfect for Postgres arrays
    matched_students = supabase.table("students") \
        .select("email, full_name") \
        .contains("interests", [tag]) \
        .execute()

    # 4. Practical Logging
    print(f"NOTIFICATION: {len(matched_students.data)} students matched for '{title}' ({tag})")
    
    return {"status": "success", "sent_to": len(matched_students.data)}

@app.get("/security/verify")
async def verify_permission(user_id: str, location: str):
    """
    Checks if a user has an active, approved permission for a specific area.
    """
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        # Query for an active permission matching user, location, and current time
        response = supabase.table("security_permissions") \
            .select("*") \
            .eq("entity_reference_id", user_id) \
            .eq("target_area", location) \
            .eq("status", "ACTIVE") \
            .gte("valid_to", now) \
            .lte("valid_from", now) \
            .execute()

        if not response.data:
            return {
                "access": "DENIED",
                "reason": "No active permission found for this location/time."
            }

        permission = response.data[0]
        return {
            "access": "GRANTED",
            "details": {
                "scope": permission["scope"],
                "authorized_by": permission["authorized_by"],
                "expires_at": permission["valid_to"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/security/verify-vendor-staff")
async def verify_vendor(staff_id: str):
    # Check if the staff belongs to an active vendor
    response = supabase.table("vendor_staff") \
        .select("*, vendors(business_name, category)") \
        .eq("id", staff_id) \
        .execute()
    
    if not response.data:
        return {"access": "DENIED", "message": "Staff not registered."}
        
    return {"access": "GRANTED", "vendor": response.data[0]["vendors"]["business_name"]}

@app.get("/admin/registration-report")
async def get_registration_report():
    """
    Generates a summary report for the University Management.
    """
    try:
        # 1. Get Club Statistics
        clubs_data = supabase.table("clubs").select("status").execute()
        total_clubs = len(clubs_data.data)
        approved_clubs = len([c for c in clubs_data.data if c['status'] == 'APPROVED'])

        # 2. Get Student Engagement (Top Interests)
        # This helps management see what skills students actually want
        students = supabase.table("students").select("interests").execute()
        all_interests = []
        for s in students.data:
            if s['interests']:
                all_interests.extend(s['interests'])
        
        # Simple frequency count
        interest_summary = {tag: all_interests.count(tag) for tag in set(all_interests)}

        # 3. Get Pending Approvals Count
        pending = supabase.table("approval_logs").select("id").eq("status", "PENDING_TEACHER").execute()

        return {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "club_stats": {
                "total": total_clubs,
                "approved": approved_clubs,
                "pending_approval": total_clubs - approved_clubs
            },
            "engagement": {
                "top_interests": dict(sorted(interest_summary.items(), key=lambda x: x[1], reverse=True)[:5])
            },
            "system_health": {
                "pending_tasks_for_faculty": len(pending.data)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

MAX_WEEKLY_HOURS = 20

@app.post("/jobs/apply")
async def apply_for_job(student_id: str, job_id: str):
    try:
        # 1. Get the hours for the job the student is applying for
        job = supabase.table("internal_jobs").select("hours_per_week").eq("id", job_id).single().execute()
        new_job_hours = job.data['hours_per_week']

        # 2. Calculate current hours from already 'SELECTED' jobs
        # We join job_applications with internal_jobs
        current_jobs = supabase.table("job_applications") \
            .select("internal_jobs(hours_per_week)") \
            .eq("student_id", student_id) \
            .eq("status", "SELECTED") \
            .execute()

        current_hours = sum(item['internal_jobs']['hours_per_week'] for item in current_jobs.data)

        # 3. Practical Check: Prevent Overcommitment
        if (current_hours + new_job_hours) > MAX_WEEKLY_HOURS:
            return {
                "status": "REJECTED",
                "reason": f"Time Management Limit: This job would put you at {current_hours + new_job_hours} hours/week. Max allowed is {MAX_WEEKLY_HOURS}."
            }

        # 4. If okay, record the application
        supabase.table("job_applications").insert({
            "student_id": student_id,
            "job_id": job_id,
            "status": "APPLIED"
        }).execute()

        return {"status": "SUCCESS", "message": "Application submitted."}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/courses/enroll")
async def enroll_in_course(student_id: str, course_id: str):
    # Practical Check: Is the student already in this department's course?
    # This prevents double-loading a student.
    existing = supabase.table("course_enrollments") \
        .select("*") \
        .eq("student_id", student_id) \
        .eq("course_id", course_id) \
        .execute()
    
    if existing.data:
        return {"status": "FAILED", "message": "Already enrolled in this course."}

    supabase.table("course_enrollments").insert({
        "student_id": student_id,
        "course_id": course_id,
        "status": "PENDING_DEPT_APPROVAL" # Welfare rule: Dept must approve
    }).execute()
    
    return {"status": "SUCCESS", "message": "Enrollment request sent to Department."}

@app.put("/students/interests")
async def update_student_interests(student_id: str, interests: list):
    """Update interests so the notification webhook finds this student."""
    supabase.table("students").update({"interests": interests}).eq("id", student_id).execute()
    return {"message": "Interests updated", "current_tags": interests}

@app.post("/courses/approve")
async def approve_course_enrollment(enrollment_id: str, action: str):
    """Department Head approves or rejects a student's course request."""
    status = "APPROVED" if action == "APPROVE" else "REJECTED"
    supabase.table("course_enrollments").update({"status": status}).eq("id", enrollment_id).execute()
    return {"status": status, "id": enrollment_id}

# --- CLUBS & EVENTS LOGIC ---

@app.post("/clubs/register")
async def register_club(name: str, lead_id: str, category: str):
    """Creates a new club request (Starts as PENDING)."""
    data = {"name": name, "lead_student_id": lead_id, "category": category, "status": "PENDING_TEACHER"}
    return supabase.table("clubs").insert(data).execute()

@app.post("/events/create")
async def create_event(title: str, club_id: str, date: str, venue: str):
    """Club leads use this to post events."""
    data = {"title": title, "club_id": club_id, "event_date": date, "venue": venue}
    return supabase.table("events").insert(data).execute()

@app.get("/events/all")
async def get_all_events():
    """Public feed for all students."""
    # We join with the clubs table to show which club is hosting
    return supabase.table("events").select("*, clubs(name)").execute()

# --- JOB POSTING LOGIC ---

@app.post("/jobs/post")
async def post_internal_job(title: str, dept: str, hours: int, pay: float):
    """Admins or Dept heads post student jobs."""
    data = {"job_title": title, "department": dept, "hours_per_week": hours, "pay_rate": pay, "status": "OPEN"}
    return supabase.table("internal_jobs").insert(data).execute()

# --- APPROVAL & INBOX ENDPOINTS ---

@app.get("/approvals/pending/teacher")
async def get_teacher_pending():
    """Clubs waiting for initial Faculty recommendation."""
    return supabase.table("clubs").select("*, students(full_name)").eq("status", "PENDING_TEACHER").execute()

@app.get("/approvals/pending/admin")
async def get_admin_pending():
    """Clubs recommended by Faculty, waiting for DSO Final Sign-off."""
    return supabase.table("clubs").select("*, students(full_name)").eq("status", "PENDING_DSO").execute()

@app.get("/approvals/pending/prices")
async def get_pending_prices():
    """Vendor price changes waiting for DSO approval."""
    return supabase.table("vendor_price_list").select("*").not_.is_("proposed_price", "null").execute()

@app.get("/approvals/all-clubs")
async def get_all_clubs():
    """Retrieves all clubs and their current workflow stage for the DSO view."""
    return supabase.table("clubs").select("*, students(full_name)").execute()

@app.post("/approvals/move-to-next/{club_id}")
async def move_club_status(club_id: str, current_user_role: str, action: str):
    """The 'State Machine' logic for moving approvals forward."""
    if action == "REJECT":
        return supabase.table("clubs").update({"status": "REJECTED"}).eq("id", club_id).execute()

    new_status = "PENDING_TEACHER"
    if current_user_role == "TEACHER":
        new_status = "PENDING_DSO"
    elif current_user_role == "DSO_ADMIN":
        new_status = "APPROVED"

    return supabase.table("clubs").update({"status": new_status}).eq("id", club_id).execute()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)