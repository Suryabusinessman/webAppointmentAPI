from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.database import Base  # Import your SQLAlchemy Base
# Import all models here to ensure they are included in Base.metadata
from app.models.UserModules.users import User
from app.models.UserModules.usertypes import UserType
from app.models.UserModules.userpermissions import UserPermission
from app.models.UserModules.pages import Page
from app.models.BusinessModules.businesstype import BusinessType
from app.models.BusinessModules.businessmanuser import BusinessUser
from app.models.BusinessModules.businesscategory import BusinessCategory
from app.models.UserModules.authmodules import UserSession
from app.models.LocationModules.locationmaster import LocationMaster
from app.models.LocationModules.locationactivepincode import LocationActivePincode
from app.models.LocationModules.locationuseraddress import LocationUserAddress
from app.models.common import AuditLog, Notification, PaymentTransaction, Staff

# Import Service Modules (correct paths)
from app.models.ServiceModules.hostel import Room, Customer, Booking
from app.models.ServiceModules.hospital import Patient, Appointment
from app.models.ServiceModules.garage import Vehicle, Service, GarageBooking
from app.models.ServiceModules.catering import MenuItem, CateringOrder, OrderItem

# Import Security Modules
from app.models.SecurityModules.security_events import SecurityEvent, SecurityEventType, SecurityEventSeverity
from app.models.SecurityModules.security_sessions import SecuritySession, SessionStatus
from app.models.SecurityModules.security_blocks import SecurityBlock, BlockType, BlockReason, BlockStatus

# this is the Alembic Config object, which provides access to the values within the .ini file.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# This ensures Alembic can detect your models
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()