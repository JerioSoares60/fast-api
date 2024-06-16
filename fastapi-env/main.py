from fastapi import FastAPI
from pymongo import MongoClient
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the User Authentication API"}
# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["user_auth"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db["users"].find_one({"email": form_data.username})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not utils.verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Return a token or generate a session
    return {"message": "Login successful"}

@app.post("/link_id")
def link_id(user_id: str, linked_id: str):
    # Find the user by user_id
    user = db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update the user's document with the linked ID
    db["users"].update_one({"_id": user["_id"]}, {"$set": {"linked_id": linked_id}})

    return {"message": "ID linked successfully"}

@app.get("/join_data")
def join_data():
    # Join data from users and another collection
    joined_data = list(db["users"].aggregate([
        {
            "$lookup": {
                "from": "another_collection",
                "localField": "linked_id",
                "foreignField": "id",
                "as": "joined_data"
            }
        }
    ]))

    return joined_data


@app.delete("/delete_user/{user_id}")
def delete_user(user_id: str):
    # Find the user by user_id
    user = db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Delete the user from the users collection
    db["users"].delete_one({"_id": user["_id"]})

    # Delete associated data from other collections
    db["another_collection"].delete_many({"linked_id": user["linked_id"]})

    return {"message": "User and associated data deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)