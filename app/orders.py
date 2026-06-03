from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from . import models, schemas

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Validate customer exists
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    # Validate products & check inventory before any changes
    resolved_items = []
    for item in order.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item.product_id} not found"
            )
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Insufficient stock for '{product.name}': "
                       f"requested {item.quantity}, available {product.quantity}"
            )
        resolved_items.append((product, item.quantity))

    # All checks passed — create order
    total = sum(product.price * qty for product, qty in resolved_items)

    db_order = models.Order(customer_id=order.customer_id, total_amount=round(total, 2))
    db.add(db_order)
    db.flush()  # get db_order.id before committing

    for product, qty in resolved_items:
        order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=product.id,
            quantity=qty,
            unit_price=product.price
        )
        db.add(order_item)
        product.quantity -= qty  # reduce stock

    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[schemas.OrderOut])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Order).offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Restore inventory on cancellation
    for item in order.items:
        item.product.quantity += item.quantity

    db.delete(order)
    db.commit()
