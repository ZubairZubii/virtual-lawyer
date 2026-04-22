from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Citizen(Base):
    __tablename__ = "citizens"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    join_date: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(64))
    cases_involved: Mapped[int] = mapped_column(Integer, default=0)


class Lawyer(Base):
    __tablename__ = "lawyers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    specialization: Mapped[str] = mapped_column(String(255), default="General Practice")
    verification_status: Mapped[str] = mapped_column(String(64), default="Pending")
    cases_solved: Mapped[int] = mapped_column(Integer, default=0)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    join_date: Mapped[str] = mapped_column(String(32))
    location: Mapped[str] = mapped_column(String(255), default="Not specified")
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    specializations_json: Mapped[str] = mapped_column(Text, default="[]")
    years_exp: Mapped[int] = mapped_column(Integer, default=0)
    cases: Mapped[int] = mapped_column(Integer, default=0)
    phone: Mapped[str] = mapped_column(String(64), default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    profile_image: Mapped[str] = mapped_column(String(512), default="")


class StoredCase(Base):
    __tablename__ = "stored_cases"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    scope: Mapped[str] = mapped_column(String(16), index=True)
    payload_json: Mapped[str] = mapped_column(Text)


class LawyerClientRow(Base):
    __tablename__ = "lawyer_client_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lawyer_id: Mapped[str] = mapped_column(String(64), index=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[str] = mapped_column(Text)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))


class AppSetting(Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text)
