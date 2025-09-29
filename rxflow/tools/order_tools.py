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
    
    def submit_refill_order(self, query) -> Dict:
        """
        Submit a refill order to pharmacy - saves to JSON file for demo
        Query can be: string, dict, or JSON string
        """
        try:
            # Handle different input formats
            import json
            
            # If query is already a dict (from LangChain structured input)
            if isinstance(query, dict):
                medication = query.get('medication', '').strip().lower()
                dosage = query.get('dosage', '').strip()
                quantity = int(query.get('quantity', '30'))
                pharmacy_id = query.get('pharmacy_id', '').strip()
                patient_id = query.get('patient_id', '12345').strip()
            # If query is a JSON string
            elif isinstance(query, str) and query.startswith('{') and query.endswith('}'):
                try:
                    data = json.loads(query)
                    medication = data.get('medication', '').strip().lower()
                    dosage = data.get('dosage', '').strip()
                    quantity = int(data.get('quantity', '30'))
                    pharmacy_id = data.get('pharmacy_id', '').strip()
                    patient_id = data.get('patient_id', '12345').strip()
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    return {
                        "success": False,
                        "error": f"Invalid JSON format: {str(e)}",
                        "source": "validation"
                    }
            # If query is colon-separated string
            elif isinstance(query, str):
                parts = query.split(':')
                if len(parts) < 4:
                    return {
                        "success": False,
                        "error": "Invalid order format. Use JSON or 'medication:dosage:quantity:pharmacy_id:patient_id'",
                        "source": "validation"
                    }
                
                medication = parts[0].strip().lower()
                dosage = parts[1].strip()
                quantity = int(parts[2].strip())
                pharmacy_id = parts[3].strip()
                patient_id = parts[4].strip() if len(parts) > 4 else "12345"
            else:
                return {
                    "success": False,
                    "error": f"Invalid input format: {type(query)}. Expected dict, JSON string, or colon-separated string",
                    "source": "validation"
                }
            
            # Map pharmacy display names to internal IDs
            pharmacy_id = self._map_pharmacy_id(pharmacy_id)
            
            logger.info(f"[AI USAGE] Submitting refill order for {medication} {dosage} to {pharmacy_id}")
            
            # Load pharmacy data from JSON file
            import json
            import os
            
            try:
                data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                pharmacy_file = os.path.join(data_dir, 'mock_pharmacies.json')
                
                with open(pharmacy_file, 'r') as f:
                    pharmacy_json_data = json.load(f)
                    
                # Validate pharmacy exists in JSON data
                if pharmacy_id not in pharmacy_json_data:
                    return {
                        "success": False,
                        "error": f"Pharmacy '{pharmacy_id}' not found",
                        "available_pharmacies": list(pharmacy_json_data.keys()),
                        "source": "validation"
                    }
                
                pharmacy = pharmacy_json_data[pharmacy_id]
                inventory = pharmacy.get("inventory", {})
                
                # Check if medication is available in inventory
                medication_found = any(medication in item_key.lower() for item_key in inventory.keys())
                
                if not medication_found:
                    return {
                        "success": False,
                        "error": f"'{medication}' is currently out of stock at {pharmacy.get('name', pharmacy_id)}",
                        "alternative_pharmacies": self._find_alternative_pharmacies(medication),
                        "source": "inventory"
                    }
                    
            except Exception as e:
                logger.error(f"Could not load pharmacy JSON data: {e}")
                return {
                    "success": False,
                    "error": f"Failed to access pharmacy data: {str(e)}",
                    "source": "system_error"
                }
            
            # Generate order confirmation
            order_id = self._generate_order_id()
            
            # Calculate pickup time (base wait time + some variation)
            base_wait = 30  # Default wait time
            pickup_time = datetime.now() + timedelta(minutes=base_wait + random.randint(-5, 15))
            
            # Extract pharmacy address from JSON structure
            address = pharmacy.get("address", {})
            if isinstance(address, dict):
                full_address = f"{address.get('street', '')}, {address.get('city', '')}, {address.get('state', '')} {address.get('zip', '')}"
            else:
                full_address = str(address)
            
            # Create order record
            order_record = {
                "order_id": order_id,
                "patient_id": patient_id,
                "medication": medication,
                "dosage": dosage,
                "quantity": quantity,
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": pharmacy["name"],
                "pharmacy_address": full_address,
                "pharmacy_phone": pharmacy["phone"],
                "status": "received",
                "order_time": datetime.now().isoformat(),
                "estimated_pickup": pickup_time.isoformat(),
                "confirmation_sent": True
            }
            
            # Store order (in production, save to database)
            self.active_orders[order_id] = order_record
            
            # Save order to JSON file for demo
            self._save_order_to_json(order_record)
            
            # Calculate cost from inventory if available
            medication_key = f"{medication}_{dosage}"
            cost = "Contact pharmacy for pricing"
            if medication_key in inventory:
                cost = f"${inventory[medication_key].get('price', 0):.2f}"
            
            logger.info(f"[ORDER SUCCESS] Order {order_id} submitted for {medication} {dosage} at {pharmacy['name']}")
            print(f"🎉 ORDER SUBMITTED SUCCESSFULLY!")
            print(f"📋 Order ID: {order_id}")
            print(f"💊 Medication: {medication} {dosage} (Qty: {quantity})")
            print(f"🏪 Pharmacy: {pharmacy['name']}")
            print(f"📍 Address: {full_address}")
            print(f"📞 Phone: {pharmacy['phone']}")
            print(f"⏰ Estimated Pickup: {pickup_time.strftime('%I:%M %p on %B %d, %Y')}")
            
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
                    "address": full_address,
                    "phone": pharmacy["phone"],
                    "drive_through": False  # Default for now
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
    
    def _save_order_to_json(self, order_record: Dict) -> None:
        """Save order to JSON file for demo purposes"""
        try:
            import json
            import os
            
            # Determine path to data directory
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            orders_file = os.path.join(data_dir, 'submitted_orders.json')
            
            # Load existing orders or create new list
            existing_orders = []
            if os.path.exists(orders_file):
                try:
                    with open(orders_file, 'r') as f:
                        existing_orders = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_orders = []
            
            # Add new order
            existing_orders.append(order_record)
            
            # Save back to file
            with open(orders_file, 'w') as f:
                json.dump(existing_orders, f, indent=2, default=str)
                
            logger.info(f"[ORDER SAVED] Order {order_record['order_id']} saved to {orders_file}")
            
        except Exception as e:
            logger.error(f"Failed to save order to JSON: {str(e)}")
            # Don't fail the order if we can't save to JSON
    
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
    
    def _map_pharmacy_id(self, pharmacy_input: str) -> str:
        """Map pharmacy display names to internal IDs using JSON data"""
        try:
            import json
            import os
            
            # Load pharmacy JSON data to get the mapping
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            pharmacy_file = os.path.join(data_dir, 'mock_pharmacies.json')
            
            with open(pharmacy_file, 'r') as f:
                pharmacy_json_data = json.load(f)
            
            # Check if input is already a valid ID
            if pharmacy_input in pharmacy_json_data:
                return pharmacy_input
                
            # Create reverse mapping from names to IDs
            name_to_id_map = {}
            for pharmacy_id, pharmacy_data in pharmacy_json_data.items():
                pharmacy_name = pharmacy_data.get('name', '').lower().strip()
                name_to_id_map[pharmacy_name] = pharmacy_id
                # Also map shorter versions
                if 'walmart' in pharmacy_name:
                    name_to_id_map['walmart'] = pharmacy_id
                elif 'cvs' in pharmacy_name:
                    name_to_id_map['cvs'] = pharmacy_id
                elif 'walgreens' in pharmacy_name:
                    name_to_id_map['walgreens'] = pharmacy_id
                elif 'h-e-b' in pharmacy_name or 'heb' in pharmacy_name:
                    name_to_id_map['heb'] = pharmacy_id
                    name_to_id_map['h-e-b'] = pharmacy_id
            
            # Try to match input to pharmacy name
            pharmacy_lower = pharmacy_input.lower().strip()
            if pharmacy_lower in name_to_id_map:
                return name_to_id_map[pharmacy_lower]
            
            # Partial matching for cases like "Walmart Pharmacy #98765" -> "WALMART_98765"
            for name, pharmacy_id in name_to_id_map.items():
                if name in pharmacy_lower or pharmacy_lower in name:
                    return pharmacy_id
                    
            return pharmacy_input
            
        except Exception as e:
            logger.warning(f"Could not load pharmacy mapping: {e}")
            # Fallback to static mapping
            pharmacy_mappings = {
                "walmart pharmacy #98765": "WALMART_98765",
                "walmart": "WALMART_98765", 
                "cvs pharmacy #12345": "CVS_12345",
                "cvs": "CVS_12345",
                "walgreens": "WALGREENS_55555",
                "h-e-b pharmacy #77777": "HEB_77777",
                "heb": "HEB_77777"
            }
            
            pharmacy_lower = pharmacy_input.lower().strip()
            return pharmacy_mappings.get(pharmacy_lower, pharmacy_input)

# Create LangChain tools
order_submission_tool = Tool(
    name="submit_refill_order",
    description="Submit a prescription refill order to a pharmacy. Use JSON format: '{\"medication\": \"omeprazole\", \"dosage\": \"20mg\", \"quantity\": \"30\", \"pharmacy_id\": \"WALMART_98765\", \"patient_id\": \"default\"}' OR colon format: 'medication:dosage:quantity:pharmacy_id:patient_id'. Returns confirmation details and pickup information.",
    func=lambda query: OrderSubmissionTool().submit_refill_order(query)
)

# Safe wrappers for robust parameter handling
def safe_order_submission(query):
    """Safe wrapper for order submission"""
    try:
        if query is None or query == {} or query == "":
            return {"success": False, "error": "No order details provided", "source": "validation"}
        
        # Pass the query directly to the tool - it now handles dicts, strings, and JSON
        return OrderSubmissionTool().submit_refill_order(query)
    except Exception as e:
        return {"success": False, "error": f"Order submission failed: {str(e)}", "source": "error"}

def safe_order_tracking(query):
    """Safe wrapper for order tracking"""
    try:
        if query is None or query == {} or query == "":
            return {"success": False, "error": "No order ID provided", "source": "validation"}
        elif isinstance(query, dict):
            query = str(query.get("order_id", query.get("id", "")))
        elif not isinstance(query, str):
            query = str(query)
        return OrderSubmissionTool().track_order(query)
    except Exception as e:
        return {"success": False, "error": f"Order tracking failed: {str(e)}", "source": "error"}

# Create LangChain tools - using StructuredTool for proper argument handling
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

class OrderSubmissionInput(BaseModel):
    """Input for order submission tool."""
    medication: str = Field(description="Name of the medication")
    dosage: str = Field(description="Dosage of the medication (e.g., '20mg')")
    quantity: str = Field(description="Quantity to order (e.g., '30')")
    pharmacy_id: str = Field(description="Pharmacy ID or name")
    patient_id: str = Field(default="12345", description="Patient ID")

def structured_order_submission(medication: str, dosage: str, quantity: str, pharmacy_id: str, patient_id: str = "12345") -> dict:
    """Submit a prescription refill order"""
    try:
        # Create the input dict
        order_input = {
            "medication": medication,
            "dosage": dosage,
            "quantity": quantity,
            "pharmacy_id": pharmacy_id,
            "patient_id": patient_id
        }
        return OrderSubmissionTool().submit_refill_order(order_input)
    except Exception as e:
        return {"success": False, "error": f"Order submission failed: {str(e)}", "source": "error"}

order_submission_tool = StructuredTool.from_function(
    name="submit_refill_order",
    description="Submit a prescription refill order to a pharmacy. Provide medication name, dosage, quantity, pharmacy ID/name, and patient ID. Returns confirmation details and pickup information.",
    func=structured_order_submission,
    args_schema=OrderSubmissionInput
)

order_tracking_tool = Tool(
    name="track_prescription_order",
    description="Track the status of a prescription order using order ID. Returns current status and estimated pickup time.",
    func=safe_order_tracking
)

order_cancellation_tool = Tool(
    name="cancel_prescription_order", 
    description="Cancel a prescription order using order ID. Only works for orders not yet picked up.",
    func=lambda query: OrderSubmissionTool().cancel_order(query)
)