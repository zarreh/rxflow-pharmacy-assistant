"""Pharmacy location and inventory tools for finding nearby pharmacies and checking stock."""

from langchain.tools import Tool
from typing import Dict, List, Optional
import math
import random
from ..services.mock_data import PHARMACY_INVENTORY
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PharmacyLocationTool:
    """Find nearby pharmacies based on location"""
    
    def __init__(self):
        self.pharmacy_data = PHARMACY_INVENTORY
        
        # Extended pharmacy network for demo
        self.extended_pharmacies = {
            "cvs_main": {
                "name": "CVS Pharmacy - Main St",
                "address": "123 Main Street, City, ST 12345",
                "phone": "(555) 123-4567",
                "distance_miles": 0.5,
                "hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth", "Medicare"]
            },
            "walmart_plaza": {
                "name": "Walmart Pharmacy - Plaza",
                "address": "456 Plaza Drive, City, ST 12345", 
                "phone": "(555) 234-5678",
                "distance_miles": 3.2,
                "hours": "Mon-Sun: 7AM-11PM",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth", "Medicare", "Medicaid"]
            },
            "walgreens_downtown": {
                "name": "Walgreens - Downtown",
                "address": "789 Downtown Blvd, City, ST 12345",
                "phone": "(555) 345-6789", 
                "distance_miles": 1.8,
                "hours": "24/7",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth"]
            },
            "costco_warehouse": {
                "name": "Costco Pharmacy",
                "address": "321 Warehouse Way, City, ST 12345",
                "phone": "(555) 456-7890",
                "distance_miles": 5.1,
                "hours": "Mon-Fri: 10AM-8:30PM, Sat: 9:30AM-6PM, Sun: 10AM-6PM",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth", "Medicare"],
                "membership_required": True
            },
            "rite_aid_north": {
                "name": "Rite Aid - North Side",
                "address": "654 North Avenue, City, ST 12345",
                "phone": "(555) 567-8901",
                "distance_miles": 2.7,
                "hours": "Mon-Sat: 8AM-10PM, Sun: 9AM-8PM",
                "accepts_insurance": ["BlueCross", "Aetna", "Medicare"]
            }
        }
    
    def find_nearby_pharmacies(self, query: str = "default") -> Dict:
        """
        Find nearby pharmacies
        Query can be: "default", "radius:miles", or "insurance:plan_name"
        """
        try:
            logger.info(f"[AI USAGE] Finding nearby pharmacies with query: {query}")
            
            # Parse query parameters
            max_radius = 10.0  # Default max radius
            insurance_filter = None
            
            if query != "default" and ':' in query:
                param_type, value = query.split(':', 1)
                if param_type.lower() == "radius":
                    try:
                        max_radius = float(value)
                    except ValueError:
                        max_radius = 10.0
                elif param_type.lower() == "insurance":
                    insurance_filter = value.strip()
            
            # Filter pharmacies by radius and insurance
            filtered_pharmacies = []
            for pharm_id, pharmacy in self.extended_pharmacies.items():
                # Check radius
                if pharmacy["distance_miles"] <= max_radius:
                    # Check insurance if specified
                    if insurance_filter:
                        if insurance_filter not in pharmacy.get("accepts_insurance", []):
                            continue
                    
                    # Add inventory and pricing data if available
                    inventory_data = self.pharmacy_data.get(pharm_id, {})
                    
                    pharmacy_info = {
                        "id": pharm_id,
                        **pharmacy,
                        "in_stock_medications": inventory_data.get("in_stock", []),
                        "sample_prices": inventory_data.get("prices", {}),
                        "wait_time_min": inventory_data.get("wait_time_min", 20 + random.randint(0, 15))
                    }
                    
                    filtered_pharmacies.append(pharmacy_info)
            
            # Sort by distance
            filtered_pharmacies.sort(key=lambda x: x["distance_miles"])
            
            return {
                "success": True,
                "pharmacies": filtered_pharmacies,
                "count": len(filtered_pharmacies),
                "search_radius_miles": max_radius,
                "insurance_filter": insurance_filter,
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error finding nearby pharmacies: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to find nearby pharmacies: {str(e)}",
                "source": "error"
            }
    
    def get_pharmacy_details(self, pharmacy_id: str) -> Dict:
        """Get detailed information for a specific pharmacy"""
        try:
            logger.info(f"[AI USAGE] Getting details for pharmacy: {pharmacy_id}")
            
            if pharmacy_id in self.extended_pharmacies:
                pharmacy = self.extended_pharmacies[pharmacy_id]
                inventory_data = self.pharmacy_data.get(pharmacy_id, {})
                
                return {
                    "success": True,
                    "pharmacy": {
                        "id": pharmacy_id,
                        **pharmacy,
                        "in_stock_medications": inventory_data.get("in_stock", []),
                        "prices": inventory_data.get("prices", {}),
                        "wait_time_min": inventory_data.get("wait_time_min", 20)
                    },
                    "source": "mock"
                }
            
            return {
                "success": False,
                "error": f"Pharmacy '{pharmacy_id}' not found",
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error getting pharmacy details: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get pharmacy details: {str(e)}",
                "source": "error"
            }

class PharmacyInventoryTool:
    """Check pharmacy inventory and availability"""
    
    def __init__(self):
        self.inventory_data = PHARMACY_INVENTORY
    
    def check_inventory(self, query: str) -> Dict:
        """
        Check if medication is in stock at pharmacy
        Query format: "pharmacy_id:medication" or just "medication" (checks all pharmacies)
        """
        try:
            # Parse query
            if ':' in query:
                pharmacy_id, medication = query.split(':', 1)
                pharmacy_id = pharmacy_id.strip()
                medication = medication.strip().lower()
                
                logger.info(f"[AI USAGE] Checking inventory for {medication} at {pharmacy_id}")
                
                # Check specific pharmacy
                if pharmacy_id in self.inventory_data:
                    pharmacy = self.inventory_data[pharmacy_id]
                    in_stock = medication in pharmacy.get("in_stock", [])
                    
                    return {
                        "success": True,
                        "pharmacy_id": pharmacy_id,
                        "pharmacy_name": pharmacy["name"],
                        "medication": medication,
                        "in_stock": in_stock,
                        "wait_time_min": pharmacy.get("wait_time_min", 30),
                        "source": "mock"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Pharmacy '{pharmacy_id}' not found",
                        "source": "mock"
                    }
            else:
                # Check all pharmacies for medication
                medication = query.strip().lower()
                logger.info(f"[AI USAGE] Checking inventory for {medication} at all pharmacies")
                
                availability = []
                for pharm_id, pharmacy in self.inventory_data.items():
                    in_stock = medication in pharmacy.get("in_stock", [])
                    availability.append({
                        "pharmacy_id": pharm_id,
                        "pharmacy_name": pharmacy["name"],
                        "in_stock": in_stock,
                        "wait_time_min": pharmacy.get("wait_time_min", 30),
                        "distance_miles": pharmacy.get("distance_miles", 0)
                    })
                
                # Sort by availability (in stock first), then by distance
                availability.sort(key=lambda x: (not x["in_stock"], x["distance_miles"]))
                
                return {
                    "success": True,
                    "medication": medication,
                    "availability": availability,
                    "pharmacies_with_stock": len([p for p in availability if p["in_stock"]]),
                    "source": "mock"
                }
                
        except Exception as e:
            logger.error(f"Error checking inventory: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to check inventory: {str(e)}",
                "source": "error"
            }
    
    def get_wait_times(self, pharmacy_ids: str = "all") -> Dict:
        """
        Get current wait times for pharmacies
        pharmacy_ids: comma-separated list or "all"
        """
        try:
            logger.info(f"[AI USAGE] Getting wait times for pharmacies: {pharmacy_ids}")
            
            if pharmacy_ids == "all":
                pharm_list = list(self.inventory_data.keys())
            else:
                pharm_list = [pid.strip() for pid in pharmacy_ids.split(',')]
            
            wait_times = []
            for pharm_id in pharm_list:
                if pharm_id in self.inventory_data:
                    pharmacy = self.inventory_data[pharm_id]
                    # Add some realistic variation to wait times
                    base_wait = pharmacy.get("wait_time_min", 30)
                    current_wait = base_wait + random.randint(-10, 20)
                    current_wait = max(5, current_wait)  # Minimum 5 minutes
                    
                    wait_times.append({
                        "pharmacy_id": pharm_id,
                        "pharmacy_name": pharmacy["name"],
                        "wait_time_min": current_wait,
                        "distance_miles": pharmacy.get("distance_miles", 0),
                        "status": "normal" if current_wait <= 30 else "busy" if current_wait <= 60 else "very_busy"
                    })
            
            # Sort by wait time
            wait_times.sort(key=lambda x: x["wait_time_min"])
            
            return {
                "success": True,
                "wait_times": wait_times,
                "fastest_pharmacy": wait_times[0] if wait_times else None,
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error getting wait times: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get wait times: {str(e)}",
                "source": "error"
            }

# Create LangChain tools
pharmacy_location_tool = Tool(
    name="find_nearby_pharmacies",
    description="Find nearby pharmacies. Use 'default' for all nearby, 'radius:5' for specific radius in miles, or 'insurance:BlueCross' to filter by accepted insurance.",
    func=lambda query: PharmacyLocationTool().find_nearby_pharmacies(query)
)

pharmacy_inventory_tool = Tool(
    name="check_pharmacy_inventory", 
    description="Check if a medication is in stock. Use 'medication_name' to check all pharmacies or 'pharmacy_id:medication_name' for specific pharmacy.",
    func=lambda query: PharmacyInventoryTool().check_inventory(query)
)

pharmacy_wait_times_tool = Tool(
    name="get_pharmacy_wait_times",
    description="Get current wait times for prescription filling. Use 'all' for all pharmacies or comma-separated pharmacy IDs.",
    func=lambda query: PharmacyInventoryTool().get_wait_times(query)
)

pharmacy_details_tool = Tool(
    name="get_pharmacy_details",
    description="Get detailed information for a specific pharmacy including hours, contact info, and services. Use pharmacy_id as input.",
    func=lambda query: PharmacyLocationTool().get_pharmacy_details(query)
)