from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base all AgentFleet models inherit from.

    Domain tables (agent, fleet, run, step, ...) land in Phase 1 —
    see docs/06-ARCHITECTURE-SCALABILITY.md for the data model.
    """
