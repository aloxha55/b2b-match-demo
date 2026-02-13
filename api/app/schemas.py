from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CompanyProfileUpsert(BaseModel):
    name: str
    sector: str
    country: str
    size: str


class CompanyProfileRead(CompanyProfileUpsert):
    id: int

    class Config:
        from_attributes = True


class AssessmentSubmission(BaseModel):
    answers: dict[str, int]


class AssessmentRead(BaseModel):
    id: int
    section_scores: dict[str, int]
    total_score: int
    recommendations: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminAssessmentRecord(BaseModel):
    company_id: int
    company_name: str
    owner_email: EmailStr
    total_score: int
    created_at: datetime


class AdminCompanyRecord(BaseModel):
    id: int
    name: str
    sector: str
    country: str
    size: str
    owner_email: EmailStr
