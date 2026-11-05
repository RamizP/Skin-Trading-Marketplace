from database import Base
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint


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
