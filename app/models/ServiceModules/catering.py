from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, DECIMAL, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    item_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    item_name = Column(String(255), nullable=False)
    item_description = Column(Text)
    category = Column(String(100))
    price = Column(DECIMAL(10,2))
    preparation_time = Column(Integer)
    is_vegetarian = Column(Enum("Y", "N"), default="N")
    is_available = Column(Enum("Y", "N"), default="Y")
    image_url = Column(String(500))
    ingredients = Column(JSON)  # JSON string
    nutritional_info = Column(JSON)  # JSON string
    is_featured = Column(Enum("Y", "N"), default="N")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

class CateringOrder(Base):
    __tablename__ = "catering_orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    order_date = Column(DateTime)
    delivery_date = Column(DateTime)
    delivery_time = Column(DateTime)
    delivery_address = Column(Text)
    guest_count = Column(Integer)
    total_amount = Column(DECIMAL(10,2))
    order_status = Column(Enum("Pending", "Confirmed", "In Progress", "Delivered", "Cancelled", name="catering_order_status_enum"))
    special_instructions = Column(Text)
    delivery_charges = Column(DECIMAL(10,2), default=0.00)
    tax_amount = Column(DECIMAL(10,2), default=0.00)
    discount_amount = Column(DECIMAL(10,2), default=0.00)
    final_amount = Column(DECIMAL(10,2))
    payment_status = Column(Enum("Pending", "Paid", "Partial", name="payment_status_enum"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    business_user = relationship("BusinessUser", back_populates="catering_orders")
    customer = relationship("Customer", back_populates="catering_orders")
    order_items = relationship("OrderItem", back_populates="catering_order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("catering_orders.order_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10,2))
    total_price = Column(DECIMAL(10,2))
    special_instructions = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    catering_order = relationship("CateringOrder", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items") 