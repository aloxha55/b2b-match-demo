from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import create_access_token, get_current_user, get_password_hash, require_admin, verify_password
from .config import settings
from .database import Base, engine, get_db
from .models import Assessment, Company, User
from .schemas import (
    AdminAssessmentRecord,
    AdminCompanyRecord,
    AssessmentRead,
    AssessmentSubmission,
    CompanyProfileRead,
    CompanyProfileUpsert,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from .scoring import score_assessment

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Investment Readiness API", version="0.1.0")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/signup", response_model=TokenResponse)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    is_admin = db.query(User).count() == 0
    user = User(email=payload.email, hashed_password=get_password_hash(payload.password), is_admin=is_admin)
    db.add(user)
    db.commit()

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)


@app.get("/users/me")
def me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "is_admin": current_user.is_admin}


@app.put("/company/profile", response_model=CompanyProfileRead)
def upsert_profile(
    payload: CompanyProfileUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if company:
        company.name = payload.name
        company.sector = payload.sector
        company.country = payload.country
        company.size = payload.size
    else:
        company = Company(user_id=current_user.id, **payload.model_dump())
        db.add(company)
    db.commit()
    db.refresh(company)
    return company


@app.get("/company/profile", response_model=CompanyProfileRead)
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    return company


@app.post("/assessments", response_model=AssessmentRead)
def submit_assessment(
    payload: AssessmentSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Create company profile first")

    section_scores, total_score, recommendations = score_assessment(payload.answers)
    assessment = Assessment(
        company_id=company.id,
        answers=payload.answers,
        section_scores=section_scores,
        total_score=total_score,
        recommendations=recommendations,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@app.get("/assessments/latest", response_model=AssessmentRead)
def get_latest_assessment(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    assessment = (
        db.query(Assessment)
        .filter(Assessment.company_id == company.id)
        .order_by(Assessment.created_at.desc())
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No assessment found")
    return assessment


@app.get("/admin/companies", response_model=list[AdminCompanyRecord])
def list_companies(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    companies = db.query(Company, User.email).join(User, Company.user_id == User.id).all()
    return [
        AdminCompanyRecord(
            id=company.id,
            name=company.name,
            sector=company.sector,
            country=company.country,
            size=company.size,
            owner_email=email,
        )
        for company, email in companies
    ]


@app.get("/admin/assessments", response_model=list[AdminAssessmentRecord])
def list_assessments(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    records = (
        db.query(Assessment, Company.name, User.email)
        .join(Company, Assessment.company_id == Company.id)
        .join(User, Company.user_id == User.id)
        .order_by(Assessment.created_at.desc())
        .all()
    )

    return [
        AdminAssessmentRecord(
            company_id=assessment.company_id,
            company_name=company_name,
            owner_email=owner_email,
            total_score=assessment.total_score,
            created_at=assessment.created_at,
        )
        for assessment, company_name, owner_email in records
    ]
