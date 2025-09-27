"""Order submission and tracking tools for pharmacy refill workflow."""

from langchain.tools import Tool
from typing import Dict, Optional
import random
import string
from datetime import datetime, timedelta
from ..services.mock_data import ORDER_TRACKING, PHARMACY_INVENTORY
from ..utils.logger import get_logger

logger = get_logger(__name__)

class OrderSubmissionTool:
    """Handles prescription refill order submission and tracking"""
    
    # Class-level order storage to persist across instances (for demo purposes)
    _active_orders = {}
    
    def __init__(self):
        self.pharmacy_data = PHARMACY_INVENTORY
        self.order_data = ORDER_TRACKING
        # Use class-level storage to persist orders between tool calls
        self.active_orders = OrderSubmissionTool._active_orders
    
    def submit_refill_order(self, query: str) -> Dict:
        """
        Submit a refill order to pharmacy
        Query format: "medication:dosage:quantity:pharmacy_id:patient_id" or use defaults
        Example: "lisinopril:10mg:30:cvs_main:12345"
        """
        try:
            # Parse the complex query string
            parts = query.split(':')
            if len(parts) < 4:
                return {
                    "success": False,
                    "error": "Invalid order format. Use 'medication:dosage:quantity:pharmacy_id:patient_id'",
                    "source": "validation"
                }
            
            medication = parts[0].strip().lower()
            dosage = parts[1].strip()
            quantity = int(parts[2].strip())
            pharmacy_id = parts[3].strip()
            patient_id = parts[4].strip() if len(parts) > 4 else "12345"
            
            logger.info(f"[AI USAGE] Submitting refill order for {medication} {dosage} to {pharmacy_id}")
            
            # Validate pharmacy exists
            if pharmacy_id not in self.pharmacy_data:
                return {
                    "success": False,
                    "error": f"Pharmacy '{pharmacy_id}' not found",
                    "source": "validation"
                }
            
            pharmacy = self.pharmacy_data[pharmacy_id]
            
            # Check if medication is in stock
            if medication not in pharmacy.get("in_stock", []):
                return {
                    "success": False,
                    "error": f"'{medication}' is currently out of stock at {pharmacy['name']}",
                    "alternative_pharmacies": self._find_alternative_pharmacies(medication),
                    "source": "inventory"
                }
            
            # Generate order confirmation
            order_id = self._generate_order_id()
            
            # Calculate pickup time (base wait time + some variation)
            base_wait = pharmacy.get("wait_time_min", 30)
            pickup_time = datetime.now() + timedelta(minutes=base_wait + random.randint(-5, 15))
            
            # Create order record
            order_record = {
                "order_id": order_id,
                "patient_id": patient_id,
                "medication": medication,
                "dosage": dosage,
                "quantity": quantity,
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": pharmacy["name"],
                "pharmacy_address": pharmacy["address"],
                "pharmacy_phone": pharmacy["phone"],
                "status": "received",
                "order_time": datetime.now().isoformat(),
                "estimated_pickup": pickup_time.isoformat(),
                "confirmation_sent": True
            }
            
            # Store order (in production, save to database)
            self.active_orders[order_id] = order_record
            
            # Calculate cost if available
            price_key = f"{medication}_{dosage}_{quantity}"
            cost = pharmacy.get("prices", {}).get(price_key, "Contact pharmacy for pricing")
            
            return {
                "success": True,
                "order_id": order_id,
                "confirmation_number": order_id,
                "status": "received",
                "medication_details": {
                    "name": medication,
                    "dosage": dosage,
                    "quantity": quantity
                },
                "pharmacy_details": {
                    "name": pharmacy["name"],
                    "address": pharmacy["address"],
                    "phone": pharmacy["phone"],
                    "drive_through": pharmacy.get("drive_through", False)
                },
                "pickup_details": {
                    "estimated_time": pickup_time.strftime("%I:%M %p"),
                    "estimated_date": pickup_time.strftime("%B %d, %Y"),
                    "wait_time_minutes": base_wait
                },
                "cost_info": {
                    "estimated_cost": cost,
                    "payment_due_at_pickup": True
                },
                "next_steps": [
                    "You will receive SMS/email confirmation",
                    "Bring valid ID for pickup",
                    "Call pharmacy if you have questions"
                ],
                "source": "order_system"
            }
            
        except ValueError as e:
            logger.error(f"Error parsing order quantity: {str(e)}")
            return {
                "success": False,
                "error": "Invalid quantity specified. Please provide a valid number.",
                "source": "validation"
            }
        except Exception as e:
            logger.error(f"Error submitting order: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to submit order: {str(e)}",
                "source": "system_error"
            }
    
    def track_order(self, order_id: str) -> Dict:
        """Track an existing order by order ID"""
        try:
            logger.info(f"[AI USAGE] Tracking order {order_id}")
            
            if order_id not in self.active_orders:
                return {
                    "success": False,
                    "error": f"Order '{order_id}' not found. Please check your order ID.",
                    "source": "not_found"
                }
            
            order = self.active_orders[order_id]
            
            # Simulate order status progression
            order_age_minutes = (datetime.now() - datetime.fromisoformat(order["order_time"])).total_seconds() / 60
            
            if order_age_minutes < 5:
                current_status = "received"
                status_description = "Order received and being processed"
            elif order_age_minutes < 20:
                current_status = "processing"
                status_description = "Prescription being prepared"
            else:
                current_status = "ready"
                status_description = "Ready for pickup"
            
            # Update order status
            order["status"] = current_status
            
            return {
                "success": True,
                "order_id": order_id,
                "status": current_status,
                "status_description": status_description,
                "medication": f"{order['medication']} {order['dosage']}",
                "quantity": order["quantity"],
                "pharmacy": order["pharmacy_name"],
                "estimated_pickup": order["estimated_pickup"],
                "order_time": order["order_time"],
                "source": "order_system"
            }
            
        except Exception as e:
            logger.error(f"Error tracking order: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to track order: {str(e)}",
                "source": "system_error"
            }
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an existing order"""
        try:
            logger.info(f"[AI USAGE] Cancelling order {order_id}")
            
            if order_id not in self.active_orders:
                return {
                    "success": False,
                    "error": f"Order '{order_id}' not found",
                    "source": "not_found"
                }
            
            order = self.active_orders[order_id]
            
            # Check if order can be cancelled (not yet picked up)
            if order["status"] == "picked_up":
                return {
                    "success": False,
                    "error": "Cannot cancel order that has already been picked up",
                    "source": "validation"
                }
            
            # Update order status
            order["status"] = "cancelled"
            order["cancelled_time"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "order_id": order_id,
                "status": "cancelled",
                "message": f"Order {order_id} has been successfully cancelled",
                "refund_info": "No charges were applied. Refund processed if payment was made.",
                "source": "order_system"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to cancel order: {str(e)}",
                "source": "system_error"
            }
    
    def _generate_order_id(self) -> str:
        """Generate a unique order confirmation number"""
        # Format: RX + 6 random digits
        return "RX" + ''.join(random.choices(string.digits, k=6))
    
    def _find_alternative_pharmacies(self, medication: str) -> list:
        """Find alternative pharmacies that have the medication in stock"""
        alternatives = []
        for pharm_id, pharmacy in self.pharmacy_data.items():
            if medication in pharmacy.get("in_stock", []):
                alternatives.append({
                    "pharmacy_id": pharm_id,
                    "name": pharmacy["name"],
                    "distance_miles": pharmacy["distance_miles"],
                    "wait_time_min": pharmacy["wait_time_min"]
                })
        
        # Sort by distance
        alternatives.sort(key=lambda x: x["distance_miles"])
        return alternatives[:3]  # Return top 3 closest

# Create LangChain tools
order_submission_tool = Tool(
    name="submit_refill_order",
    description="Submit a prescription refill order to a pharmacy. Use format 'medication:dosage:quantity:pharmacy_id:patient_id'. Returns confirmation details and pickup information.",
    func=lambda query: OrderSubmissionTool().submit_refill_order(query)
)

order_tracking_tool = Tool(
    name="track_prescription_order",
    description="Track the status of a prescription order using order ID. Returns current status and estimated pickup time.",
    func=lambda query: OrderSubmissionTool().track_order(query)
)

order_cancellation_tool = Tool(
    name="cancel_prescription_order", 
    description="Cancel a prescription order using order ID. Only works for orders not yet picked up.",
    func=lambda query: OrderSubmissionTool().cancel_order(query)
)