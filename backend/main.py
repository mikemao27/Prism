from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import engine, get_db, Base
import models
import auth
from dotenv import load_dotenv
from router import route
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from summarizer import summarize_conversation, should_summarize, generate_title

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prism")
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/app.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas 
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class ConversationCreate(BaseModel):
    title: str = "New Conversation"

class MessageSend(BaseModel):
    content: str

class APIKeyAdd(BaseModel):
    provider: str
    api_key: str

class ConversationRename(BaseModel):
    title: str

class ConversationArchive(BaseModel):
    archived: bool

class MessageEdit(BaseModel):
    content: str

# Auth Routes
@app.post("/auth/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email Already Registered"
        )

    new_user = models.User(
        email=user_data.email,
        hashed_password=auth.hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = auth.create_access_token({"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/auth/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Email or Password"
        )

    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

# Conversation Routes
@app.post("/conversations")
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = models.Conversation(
        user_id=current_user.id,
        title=data.title
    )
    db.add(convo)
    db.commit()
    db.refresh(convo)
    return {"id": convo.id, "title": convo.title, "model_locked": convo.model_locked}

@app.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convos = db.query(models.Conversation).filter(
        models.Conversation.user_id == current_user.id
    ).order_by(models.Conversation.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "model_locked": c.model_locked,
            "archived": c.archived,
            "updated_at": str(c.updated_at)
        }
        for c in convos
    ]

@app.get("/conversations/{convo_id}/messages")
def get_messages(
    convo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == convo_id
    ).order_by(models.Message.created_at.asc()).all()

    return [
        {"id": m.id, "role": m.role, "content": m.content, "model_used": m.model_used, "tokens_used": m.tokens_used}
        for m in messages
    ]

@app.post("/conversations/{convo_id}/messages")
def send_message(
    convo_id: int,
    data: MessageSend,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    
    user_msg = models.Message(
        conversation_id=convo_id,
        role="user",
        content=data.content
    )

    db.add(user_msg)
    db.commit()

    all_messages = db.query(models.Message).filter(
        models.Message.conversation_id == convo_id
    ).order_by(models.Message.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in all_messages]

    user_keys = db.query(models.APIKey).filter(
        models.APIKey.user_id == current_user.id
    ).all()
    available_models = [
        {
            "provider": k.provider,
            "model": k.provider,
            "api_key": k.api_key,
            "credit_balance": k.credit_balance
        }
        for k in user_keys
    ]

    if convo.model_locked:
        from router import get_llm
        model_name = convo.model_locked
        llm = get_llm(model_name)
    else:
        model_name, llm = route(data.content, available_models)
        convo.model_locked = model_name
        convo.title = generate_title(data.content)
        db.commit()
    
    response = llm.chat(history)

    assistant_msg = models.Message(
        conversation_id=convo_id,
        role="assistant",
        content=response["content"],
        model_used=response["model"],
        tokens_used=response["tokens_used"]
    )
    db.add(assistant_msg)
    db.commit()

    message_count = db.query(models.Message).filter(
        models.Message.conversation_id == convo_id
    ).count()

    if should_summarize(message_count):
        history_for_summary = [{"role": m.role, "content": m.content} for m in
                               db.query(models.Message).filter(
                                   models.Message.conversation_id == convo_id
                               ).order_by(models.Message.created_at.asc()).all()]
        summary_text = summarize_conversation(history_for_summary)
        summary = models.Summary(
            conversation_id=convo_id,
            summary_text=summary_text
        )
        db.add(summary)
        db.commit()

    return {
        "content": response["content"],
        "model_used": response["model"],
        "tokens_used": response["tokens_used"],
        "message_id": assistant_msg.id
    }

# API Key Routes
@app.post("/keys")
def add_api_key(
    data: APIKeyAdd,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    key = models.APIKey(
        user_id=current_user.id,
        provider=data.provider,
        api_key=data.api_key,
        credit_balance=data.credit_balance
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return {"id": key.id, "provider": key.provider, "credit_balance": key.credit_balance}

@app.get("/keys")
def get_api_keys(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    keys = db.query(models.APIKey).filter(
        models.APIKey.user_id == current_user.id
    ).all()

    return [
        {"id": k.id, "provider": k.provider, "credit_balance": k.credit_balance}
        for k in keys
    ]

# Conversation Management
@app.patch("/conversations/{convo_id}/rename")
def rename_conversation(
    convo_id: int,
    data: ConversationRename,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    convo.title = data.title
    db.commit()
    return {"id": convo.id, "title": convo.title}

@app.patch("/conversations/{convo_id}/archive")
def archive_conversation(
    convo_id: int,
    data: ConversationArchive,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    convo.archived = data.archived
    db.commit()
    return {"id": convo.id, "archived": convo.archived}

@app.delete("/conversations/{convo_id}")
def delete_conversation(
    convo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo.id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    db.query(models.Message).filter(
        models.Message.conversation_id == convo_id
    ).delete()
    db.query(models.Summary).filter(
        models.Summary.conversation_id == convo_id
    ).delete()
    db.delete(convo)
    db.commit()
    return {"deleted": True}

# Message Management
@app.delete("/conversations/{convo_id}/messages/{message_id}")
def delete_message(
    convo_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.conversation_id == convo_id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message Not Found")
    db.delete(message)
    db.commit()
    return {"deleted": True}

@app.patch("/conversations/{convo_id}/messages/{message_id}/edit")
def edit_message(
    convo_id: int,
    message_id: int,
    data: MessageEdit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    
    message = db.query(models.Message).filter(
        models.Message.id == message_id,
        models.Message.conversation_id == convo_id,
        models.Message.role == "user"
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message Not Found")
    
    db.query(models.Message).filter(
        models.Message.conversation_id == convo_id,
        models.Message.id > message_id
    ).delete()

    message.content = data.content
    db.commit()

    history = db.query(models.Message).filter(
        models.Message.conversation_id == convo_id
    ).order_by(models.Message.created_at.asc()).all()
    history_payload = [{"role": m.role, "content": m.content} for m in history]

    from router import get_llm
    llm = get_llm(convo.model_locked)
    response = llm.chat(history_payload)

    assistant_msg = models.Message(
        conversation_id=convo_id,
        role="assistant",
        content=response["content"],
        model_used=response["model"],
        tokens_used=response["tokens_used"]
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return {
        "content": response["content"],
        "moddel_used": response["model"],
        "tokens_used": response["tokens_used"],
        "message_id": assistant_msg.id
    }

@app.post("/conversations/{convo_id}/summarize")
def summarize(
    convo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()

    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")
    
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == convo_id
    ).order_by(models.Message.created_at.asc()).all()

    if not messages:
        raise HTTPException(status_code=400, detail="No Messages to Summarize")
    
    history = [{"role": m.role, "content": m.content} for m in messages]
    summary_text = summarize_conversation(history)

    summary = models.Summary(
        conversation_id=convo_id,
        summary_text=summary_text
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)

    return {"summary": summary_text, "id": summary.id}

@app.get("/conversations/{convo_id}/summaries")
def get_summaries(
    convo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    convo = db.query(models.Conversation).filter(
        models.Conversation.id == convo_id,
        models.Conversation.user_id == current_user.id
    ).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation Not Found")

    summaries = db.query(models.Summary).filter(
        models.Summary.conversation_id == convo_id
    ).order_by(models.Summary.created_at.desc()).all()

    return [{"id": s.id, "summary_text": s.summary_text, "created_at": str(s.created_at)} for s in summaries]

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@app.patch("/auth/password")
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not auth.verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current Password is Incorrect"
        )
    
    current_user.hashed_password = auth.hash_password(data.new_password)
    db.commit()
    return {"success": True}

@app.delete("/keys/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    key = db.query(models.APIKey).filter(
        models.APIKey.id == key_id,
        models.APIKey.user_id == current_user.id
    ).first()

    if not key:
        raise HTTPException(status_code=404, detail="API Key Not Found")
    
    db.delete(key)
    db.commit()
    return {"deleted": True}

@app.patch("/keys/{key_id}/balance")
def update_balance(
    key_id: int,
    data: APIKeyAdd,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    key = db.query(models.APIKey).filter(
        models.APIKey.id == key_id,
        models.APIKey.user_id == current_user.id
    ).first()

    if not key:
        raise HTTPException(status_code=404, detail="API Key Not Found")
    
    key.credit_balance = data.credit_balance
    db.commit()
    return {"id": key.id, "provider": key.provider, "credit_balance": key.credit_balance}

@app.get("/settings")
def serve_settings():
    return FileResponse("../frontend/settings.html")

@app.get("/landing")
def serve_landing():
    return FileResponse("../frontend/landing.html")