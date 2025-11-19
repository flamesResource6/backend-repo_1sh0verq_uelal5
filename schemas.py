"""
Database Schemas for Dark Whale SaaS

Each Pydantic model below maps to a MongoDB collection using the lowercased
class name as collection name (e.g., Client -> "client").

These schemas are read by the database tools and used for validation.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, EmailStr

# Core entities
class Client(BaseModel):
    name: str = Field(..., description="Company or client name")
    email: EmailStr = Field(..., description="Primary contact email")
    contact_person: Optional[str] = Field(None, description="Key contact")
    phone: Optional[str] = Field(None, description="Phone number")
    status: Literal["lead", "active", "paused", "churned"] = Field("lead")
    industry: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    mrr: float = Field(0, ge=0, description="Monthly recurring revenue")

class Content(BaseModel):
    title: str
    channel: Literal["blog", "linkedin", "twitter", "instagram", "youtube", "newsletter"]
    owner: Optional[str] = None
    status: Literal["idea", "draft", "review", "scheduled", "published", "archived"] = "idea"
    scheduled_date: Optional[str] = Field(
        None, description="ISO date (YYYY-MM-DD) when content is planned"
    )
    client_id: Optional[str] = Field(None, description="Related client _id as string")
    notes: Optional[str] = None

class Task(BaseModel):
    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    state: Literal["backlog", "in_progress", "review", "done"] = "backlog"
    client_id: Optional[str] = None
    due_date: Optional[str] = Field(None, description="ISO date YYYY-MM-DD")

class InvoiceItem(BaseModel):
    name: str
    quantity: float = Field(1, ge=0)
    unit_price: float = Field(0, ge=0)

class Invoice(BaseModel):
    client_id: str
    number: str = Field(..., description="Invoice number")
    issue_date: str = Field(..., description="ISO date YYYY-MM-DD")
    due_date: str = Field(..., description="ISO date YYYY-MM-DD")
    currency: str = Field("EUR")
    status: Literal["draft", "sent", "paid", "overdue", "void"] = "draft"
    items: List[InvoiceItem] = Field(default_factory=list)
    notes: Optional[str] = None

# Backwards-compatible examples remain (optional for reference)
class User(BaseModel):
    name: str
    email: EmailStr
    address: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    in_stock: bool = True
