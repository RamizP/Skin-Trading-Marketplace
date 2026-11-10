from database import Base
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint, DateTime, func


class CaseDrop(Base):
    __tablename__ = "case_drop"
    __table_args__ = (
        UniqueConstraint(
            "case_entity_id",
            "reward_entity_id",
            name="uq_case_drop_reward",
        ),
    )

    id = Column(Integer, primary_key=True)

    case_entity_id = Column(
        Integer,
        ForeignKey("entity.id"),
        nullable=False,
    )

    reward_entity_id = Column(
        Integer,
        ForeignKey("entity.id"),
        nullable=False,
    )

    weight = Column(Integer, nullable=False)

class FreeCaseCooldown(Base):
    __tablename__ = "free_case_cooldown"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)

    last_claimed_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )