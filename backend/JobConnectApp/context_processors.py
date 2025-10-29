def user_context(request):
    user = None
    role = None

    if request.session.get("admin"):
        user = request.session["admin"]
        role = "Admin"
        email = user.get("email", "")
    elif request.session.get("applicant"):
        user = request.session["applicant"]
        role = "Applicant"
        email = user.get("email", "")
    elif request.session.get("employer"):
        user = request.session["employer"]
        role = "Employer"
        email = user.get("email", "")

    return {"user": user, "role": role, "email": email if user else None}
