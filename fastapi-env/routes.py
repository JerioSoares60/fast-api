from models import UserModel

@app.post("/register")
def register_user(user: UserModel):
    # Hash the password before storing
    hashed_password = utils.hash_password(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password

    # Insert the user into the database
    db["users"].insert_one(user_data)

    return {"message": "User registered successfully"}