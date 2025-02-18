from app.db.postgres import db

async def create_user(username: str, email: str, hashed_password: str):
    """Insert a new user into the database"""
    query = """
    INSERT INTO users (username, email, hashed_password)
    VALUES ($1, $2, $3) RETURNING id, username, email;
    """
    return await db.fetchrow(query, username, email, hashed_password)

async def get_user_by_username_or_email(identifier: str):
    """Retrieve user by either username or email"""
    query = "SELECT * FROM users WHERE username = $1 OR email = $1"
    return await db.fetchrow(query, identifier)

async def get_user_by_username(username: str):
    """Retrieve user by username"""
    query = "SELECT * FROM users WHERE username = $1"
    return await db.fetchrow(query, username)

async def get_user_by_email(email: str):
    """Retrieve user by email"""
    query = "SELECT * FROM users WHERE email = $1"
    return await db.fetchrow(query, email)

async def mark_user_verified(email: str):
    """Mark a user as verified after email confirmation"""
    query = "UPDATE users SET is_verified = TRUE WHERE email = $1"
    await db.execute(query, email)

async def is_user_verified(email: str):
    """Check if a user is verified"""
    query = "SELECT is_verified FROM users WHERE email = $1"
    result = await db.fetchrow(query, email)
    return result["is_verified"] if result else False
