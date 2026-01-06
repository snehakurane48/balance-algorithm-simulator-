"""Database models for storing simulation data."""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class SimulationRun(Base):
    """Model for simulation runs."""
    __tablename__ = 'simulation_runs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    algorithm = Column(String(50))
    num_clients = Column(Integer)
    num_malicious = Column(Integer)
    attack_type = Column(String(50))
    num_rounds = Column(Integer)
    dataset = Column(String(50), default='aptos')

    # Relationships
    clients = relationship("Client", back_populates="simulation_run")
    metrics = relationship("RoundMetric", back_populates="simulation_run")

class Client(Base):
    """Model for clients in a simulation."""
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    simulation_run_id = Column(Integer, ForeignKey('simulation_runs.id'))
    client_id = Column(Integer)  # 0-based index
    is_malicious = Column(Boolean, default=False)
    attack_type = Column(String(50))

    # Relationships
    simulation_run = relationship("SimulationRun", back_populates="clients")
    round_metrics = relationship("RoundMetric", back_populates="client")

class RoundMetric(Base):
    """Model for metrics per round per client."""
    __tablename__ = 'round_metrics'

    id = Column(Integer, primary_key=True)
    simulation_run_id = Column(Integer, ForeignKey('simulation_runs.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    round_number = Column(Integer)
    train_loss = Column(Float)
    eval_loss = Column(Float)
    eval_accuracy = Column(Float)
    num_examples = Column(Integer)
    asr = Column(Float)  # Attack Success Rate

    # Relationships
    simulation_run = relationship("SimulationRun", back_populates="metrics")
    client = relationship("Client", back_populates="round_metrics")

# Database setup
engine = create_engine('sqlite:///simulation_results.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    """Get a database session."""
    return Session()