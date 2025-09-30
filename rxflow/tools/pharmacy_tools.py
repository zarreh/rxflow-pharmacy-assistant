"""Pharmacy location and inventory tools for finding nearby pharmacies and checking stock."""

import math
import random
from typing import Any, Dict, List, Optional, cast

from langchain.tools import Tool

from ..services.mock_data import PHARMACY_INVENTORY
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MockPharmacyLocator:
    """Simulates pharmacy location and details lookup service"""

    def __init__(self) -> None:
        # Load pharmacy data from mock service
        self.pharmacy_data = PHARMACY_INVENTORY

        # Extended pharmacy network for demo
        self.extended_pharmacies = {
            "cvs_main": {
                "name": "CVS Pharmacy - Main St",
                "address": "123 Main Street, City, ST 12345",
                "phone": "(555) 123-4567",
                "distance_miles": 0.5,
                "hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth", "Medicare"],
            },
            "walmart_plaza": {
                "name": "Walmart Pharmacy - Plaza",
                "address": "456 Plaza Drive, City, ST 12345",
                "phone": "(555) 234-5678",
                "distance_miles": 3.2,
                "hours": "Mon-Sun: 7AM-11PM",
                "accepts_insurance": [
                    "BlueCross",
                    "Aetna",
                    "UnitedHealth",
                    "Medicare",
                    "Medicaid",
                ],
            },
            "walgreens_downtown": {
                "name": "Walgreens - Downtown",
                "address": "789 Downtown Blvd, City, ST 12345",
                "phone": "(555) 345-6789",
                "distance_miles": 1.8,
                "hours": "24/7",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth"],
            },
            "costco_warehouse": {
                "name": "Costco Pharmacy",
                "address": "321 Warehouse Way, City, ST 12345",
                "phone": "(555) 456-7890",
                "distance_miles": 5.1,
                "hours": "Mon-Fri: 10AM-8:30PM, Sat: 9:30AM-6PM, Sun: 10AM-6PM",
                "accepts_insurance": ["BlueCross", "Aetna", "UnitedHealth", "Medicare"],
                "membership_required": True,
            },
            "rite_aid_north": {
                "name": "Rite Aid - North Side",
                "address": "654 North Avenue, City, ST 12345",
                "phone": "(555) 567-8901",
                "distance_miles": 2.7,
                "hours": "Mon-Sat: 8AM-10PM, Sun: 9AM-8PM",
                "accepts_insurance": ["BlueCross", "Aetna", "Medicare"],
            },
        }

    def find_nearby_pharmacies(self, query: str = "default") -> Dict[str, Any]:
        """
        Find pharmacies near patient location with distance and details.

        Searches the pharmacy network to locate nearby pharmacies based on
        location query, returning sorted results by distance.

        Args:
            query (str): Location query in formats:
                - "default" - Uses demo location (default)
                - "lat,lng" - Geographic coordinates
                - "address" - Full address string
                - "radius:10" - Set custom search radius
                - "insurance:BlueCross" - Filter by insurance

        Returns:
            Dict[str, Any]: Pharmacy search results containing:
                - pharmacies (List[Dict]): List of nearby pharmacy records with:
                    - pharmacy_id (str): Unique pharmacy identifier
                    - name (str): Pharmacy chain and location name
                    - address (str): Full street address
                    - phone (str): Contact phone number
                    - distance_miles (float): Distance from query location
                    - hours (str): Operating hours string
                    - accepts_insurance (List[str]): Accepted insurance plans
                - location (str): Original location query
                - total_found (int): Number of pharmacies located
                - search_radius_miles (float): Search radius used
        """
        try:
            logger.info(f"[AI USAGE] Finding nearby pharmacies with query: {query}")

            # Parse query parameters
            max_radius = 10.0  # Default max radius
            insurance_filter = None

            if query != "default" and ":" in query:
                param_type, value = query.split(":", 1)
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
                if cast(float, pharmacy["distance_miles"]) <= max_radius:
                    # Check insurance if specified
                    if insurance_filter:
                        accepts_insurance = cast(List[str], pharmacy.get("accepts_insurance", []))
                        if insurance_filter not in accepts_insurance:
                            continue

                    # Add inventory and pricing data if available
                    inventory_data = self.pharmacy_data.get(pharm_id, {})

                    pharmacy_info = {
                        "id": pharm_id,
                        **pharmacy,
                        "in_stock_medications": inventory_data.get("in_stock", []),
                        "sample_prices": inventory_data.get("prices", {}),
                        "wait_time_min": inventory_data.get(
                            "wait_time_min", 20 + random.randint(0, 15)
                        ),
                    }

                    filtered_pharmacies.append(pharmacy_info)

            # Sort by distance
            filtered_pharmacies.sort(key=lambda x: cast(float, x["distance_miles"]))

            return {
                "success": True,
                "pharmacies": filtered_pharmacies,
                "count": len(filtered_pharmacies),
                "search_radius_miles": max_radius,
                "insurance_filter": insurance_filter,
                "source": "mock",
            }

        except Exception as e:
            logger.error(f"Error finding nearby pharmacies: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to find nearby pharmacies: {str(e)}",
                "source": "error",
            }

    def get_pharmacy_details(self, pharmacy_id: str) -> Dict[str, Any]:
        """
        Get comprehensive details for a specific pharmacy location.

        Retrieves complete pharmacy information including contact details,
        hours, services, and current inventory status.

        Args:
            pharmacy_id (str): Unique pharmacy identifier
                Examples: "cvs_main", "walgreens_downtown", "walmart_plaza"

        Returns:
            Dict[str, Any]: Complete pharmacy information containing:
                - pharmacy_id (str): Unique pharmacy identifier
                - name (str): Pharmacy name and location
                - address (str): Full street address
                - phone (str): Contact phone number
                - hours (str): Operating hours formatted string
                - accepts_insurance (List[str]): List of accepted insurance plans
                - services (List[str]): Available services (flu shots, consultations)
                - current_wait_time (str): Estimated wait time
                - medications_in_stock (int): Count of medications available
                - success (bool): Whether pharmacy was found successfully
        """
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
                        "wait_time_min": inventory_data.get("wait_time_min", 20),
                    },
                    "source": "mock",
                }

            return {
                "success": False,
                "error": f"Pharmacy '{pharmacy_id}' not found",
                "source": "mock",
            }

        except Exception as e:
            logger.error(f"Error getting pharmacy details: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get pharmacy details: {str(e)}",
                "source": "error",
            }


class PharmacyCostTool:
    """Find cheapest pharmacy options for medications"""

    def __init__(self) -> None:
        self.pharmacy_data = PHARMACY_INVENTORY
        self.location_tool = MockPharmacyLocator()

    def find_cheapest_pharmacy(self, query: str) -> Dict[str, Any]:
        """
        STEP 4 WORKFLOW: Find the cheapest pharmacy with promotions and price comparison
        Query format: "medication_name" or JSON string with preferences
        Analyzes prices, promotions, discounts, and provides cost optimization recommendations
        """
        try:
            logger.info(
                f"[AI USAGE] STEP 4 WORKFLOW - Finding cheapest pharmacy with promotions for: {query}"
            )

            # Parse query - could be medication name or JSON with preferences
            medication = None
            customer_age = None
            is_member = False

            if query.startswith("{") and query.endswith("}"):
                try:
                    import json

                    params = json.loads(query)
                    medication = params.get("medication", query).strip().lower()
                    customer_age = params.get("customer_age", 0)
                    is_member = params.get("is_member", False)
                except:
                    medication = query.strip().lower()
            else:
                medication = query.strip().lower()

            # Load pharmacy data directly from JSON files
            import json
            import os

            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
            pharmacy_file = os.path.join(data_dir, "mock_pharmacies.json")

            try:
                with open(pharmacy_file, "r") as f:
                    pharmacy_data = json.load(f)
            except:
                return {"success": False, "error": "Unable to load pharmacy data"}

            # Find pricing for the medication across pharmacies with promotions
            pricing_options = []

            for pharmacy_id, pharmacy_info in pharmacy_data.items():
                inventory = pharmacy_info.get("inventory", {})
                promotions = pharmacy_info.get("promotions", {})

                # Look for medication pricing
                for item_key, item_info in inventory.items():
                    if medication in item_key.lower():
                        base_price = item_info.get("price", 0)
                        is_generic = item_info.get("is_generic", False)
                        manufacturer = item_info.get("manufacturer", "Unknown")

                        # Calculate discounted prices based on promotions
                        best_discount = 0
                        applicable_promotions = []
                        final_price = base_price

                        for promo_id, promo_info in promotions.items():
                            applies = False
                            discount_amount = 0

                            # Check if promotion applies
                            applies_to = promo_info.get("applies_to", [])

                            if "all" in applies_to:
                                applies = True
                            elif "generic" in applies_to and is_generic:
                                applies = True
                            elif "club_member" in applies_to and is_member:
                                applies = True
                            elif (
                                customer_age
                                and customer_age >= 65
                                and "senior"
                                in promo_info.get("description", "").lower()
                            ):
                                applies = True

                            if applies:
                                if promo_info.get("discount_type") == "fixed_price":
                                    # Fixed price program (e.g., Walmart $4 generics)
                                    discount_amount = base_price - promo_info.get(
                                        "fixed_price", base_price
                                    )
                                    if discount_amount > best_discount:
                                        best_discount = discount_amount
                                        final_price = promo_info.get(
                                            "fixed_price", base_price
                                        )
                                elif promo_info.get("discount_percent", 0) > 0:
                                    # Percentage discount
                                    discount_percent = promo_info.get(
                                        "discount_percent", 0
                                    )
                                    discount_amount = base_price * (
                                        discount_percent / 100
                                    )
                                    if discount_amount > best_discount:
                                        best_discount = discount_amount
                                        final_price = base_price - discount_amount

                                if applies:
                                    applicable_promotions.append(
                                        {
                                            "name": promo_id,
                                            "description": promo_info.get(
                                                "description", ""
                                            ),
                                            "discount_amount": discount_amount,
                                            "savings": f"${discount_amount:.2f}",
                                        }
                                    )

                        pricing_options.append(
                            {
                                "pharmacy_name": pharmacy_info.get("name", pharmacy_id),
                                "pharmacy_id": pharmacy_id,
                                "address": pharmacy_info.get("address", {}).get(
                                    "street", "Address not available"
                                ),
                                "phone": pharmacy_info.get(
                                    "phone", "Phone not available"
                                ),
                                "medication_item": item_key,
                                "base_price": base_price,
                                "final_price": final_price,
                                "total_savings": best_discount,
                                "savings_percent": (best_discount / base_price * 100)
                                if base_price > 0
                                else 0,
                                "is_generic": is_generic,
                                "manufacturer": manufacturer,
                                "quantity_available": item_info.get("quantity", 0),
                                "wait_time_hours": item_info.get(
                                    "wait_time_hours", 0.5
                                ),
                                "applicable_promotions": applicable_promotions,
                                "services": pharmacy_info.get("services", []),
                            }
                        )

            # Sort by final price (cheapest first), then by savings
            pricing_options.sort(key=lambda x: (x["final_price"], -x["total_savings"]))

            # Calculate additional insights
            if pricing_options:
                cheapest_price = pricing_options[0]["final_price"]
                most_expensive = max(pricing_options, key=lambda x: x["final_price"])[
                    "final_price"
                ]
                max_savings = (
                    cheapest_price - most_expensive if len(pricing_options) > 1 else 0
                )
            else:
                max_savings = 0

            return {
                "success": True,
                "medication_searched": medication,
                "total_pharmacies_checked": len(pricing_options),
                "cheapest_option": pricing_options[0] if pricing_options else None,
                "top_3_options": pricing_options[:3],  # Top 3 cheapest with promotions
                "max_potential_savings": max_savings,
                "cost_optimization_summary": {
                    "cheapest_price": pricing_options[0]["final_price"]
                    if pricing_options
                    else 0,
                    "average_savings": sum(
                        opt["total_savings"] for opt in pricing_options
                    )
                    / len(pricing_options)
                    if pricing_options
                    else 0,
                    "generic_available": any(
                        opt["is_generic"] for opt in pricing_options
                    ),
                    "promotions_available": any(
                        opt["applicable_promotions"] for opt in pricing_options
                    ),
                },
                "recommendation": f"Cheapest option: {pricing_options[0]['pharmacy_name']} at ${pricing_options[0]['final_price']:.2f}"
                if pricing_options
                else "No options found",
                "source": "enhanced_mock_with_promotions",
            }

        except Exception as e:
            logger.error(f"Error finding cheapest pharmacy: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to find cheapest pharmacy: {str(e)}",
                "source": "error",
            }


class PharmacyInventoryTool:
    """Check pharmacy inventory and availability"""

    def __init__(self) -> None:
        self.inventory_data = PHARMACY_INVENTORY

    def check_inventory(self, query: str) -> Dict[str, Any]:
        """
        Check medication availability and stock levels at pharmacies.

        Queries pharmacy inventory systems to determine medication availability,
        supporting both specific pharmacy checks and network-wide searches.

        Args:
            query (str): Inventory query in formats:
                - "pharmacy_id:medication" - Check specific pharmacy
                - "medication" - Check all pharmacies in network
                Examples: "cvs_main:omeprazole", "lisinopril"

        Returns:
            Dict[str, Any]: Inventory results containing:
                - medication (str): Standardized medication name searched
                - results (List[Dict]): List of pharmacy inventory records with:
                    - pharmacy_id (str): Pharmacy identifier
                    - pharmacy_name (str): Human-readable pharmacy name
                    - in_stock (bool): Whether medication is available
                    - quantity (int): Units in stock (0 if unavailable)
                    - price (float): Cost per unit if available
                    - last_updated (str): Timestamp of inventory check
                - total_pharmacies_checked (int): Number of locations queried
                - pharmacies_with_stock (int): Count with medication available
        """
        try:
            # Parse query
            if ":" in query:
                pharmacy_id, medication = query.split(":", 1)
                pharmacy_id = pharmacy_id.strip()
                medication = medication.strip().lower()

                logger.info(
                    f"[AI USAGE] Checking inventory for {medication} at {pharmacy_id}"
                )

                # Check specific pharmacy
                if pharmacy_id in self.inventory_data:
                    pharmacy = self.inventory_data[pharmacy_id]
                    in_stock = medication in cast(List[str], pharmacy.get("in_stock", []))

                    return {
                        "success": True,
                        "pharmacy_id": pharmacy_id,
                        "pharmacy_name": pharmacy["name"],
                        "medication": medication,
                        "in_stock": in_stock,
                        "wait_time_min": pharmacy.get("wait_time_min", 30),
                        "source": "mock",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Pharmacy '{pharmacy_id}' not found",
                        "source": "mock",
                    }
            else:
                # Check all pharmacies for medication
                medication = query.strip().lower()
                logger.info(
                    f"[AI USAGE] Checking inventory for {medication} at all pharmacies"
                )

                availability = []
                for pharm_id, pharmacy in self.inventory_data.items():
                    in_stock_list = cast(List[str], pharmacy.get("in_stock", []))
                    in_stock = medication in in_stock_list
                    availability.append(
                        {
                            "pharmacy_id": pharm_id,
                            "pharmacy_name": pharmacy["name"],
                            "in_stock": in_stock,
                            "wait_time_min": pharmacy.get("wait_time_min", 30),
                            "distance_miles": pharmacy.get("distance_miles", 0),
                        }
                    )

                # Sort by availability (in stock first), then by distance
                availability.sort(
                    key=lambda x: (not x["in_stock"], x["distance_miles"])
                )

                return {
                    "success": True,
                    "medication": medication,
                    "availability": availability,
                    "pharmacies_with_stock": len(
                        [p for p in availability if p["in_stock"]]
                    ),
                    "source": "mock",
                }

        except Exception as e:
            logger.error(f"Error checking inventory: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to check inventory: {str(e)}",
                "source": "error",
            }

    def get_wait_times(self, pharmacy_ids: str = "all") -> Dict[str, Any]:
        """
        Get current wait times and service capacity for pharmacies.

        Retrieves real-time wait time estimates for specified pharmacies
        to help patients plan their visits and minimize waiting time.

        Args:
            pharmacy_ids (str): Pharmacy selection in formats:
                - "all" - Get wait times for all pharmacies (default)
                - "cvs_main,walgreens_downtown" - Comma-separated list
                - "cvs_main" - Single pharmacy identifier

        Returns:
            Dict[str, Any]: Wait time information containing:
                - wait_times (List[Dict]): List of pharmacy wait data with:
                    - pharmacy_id (str): Pharmacy identifier
                    - pharmacy_name (str): Human-readable name
                    - current_wait_minutes (int): Estimated wait in minutes
                    - queue_length (int): Number of customers waiting
                    - busy_level (str): "Low", "Moderate", "High"
                    - last_updated (str): Timestamp of wait time data
                - pharmacies_checked (int): Number of locations queried
                - average_wait_time (float): Average wait across all pharmacies
        """
        try:
            logger.info(f"[AI USAGE] Getting wait times for pharmacies: {pharmacy_ids}")

            if pharmacy_ids == "all":
                pharm_list = list(self.inventory_data.keys())
            else:
                pharm_list = [pid.strip() for pid in pharmacy_ids.split(",")]

            wait_times = []
            for pharm_id in pharm_list:
                if pharm_id in self.inventory_data:
                    pharmacy = self.inventory_data[pharm_id]
                    # Add some realistic variation to wait times
                    base_wait = cast(int, pharmacy.get("wait_time_min", 30))
                    current_wait = base_wait + random.randint(-10, 20)
                    current_wait = max(5, current_wait)  # Minimum 5 minutes

                    wait_times.append(
                        {
                            "pharmacy_id": pharm_id,
                            "pharmacy_name": pharmacy["name"],
                            "wait_time_min": current_wait,
                            "distance_miles": pharmacy.get("distance_miles", 0),
                            "status": "normal"
                            if current_wait <= 30
                            else "busy"
                            if current_wait <= 60
                            else "very_busy",
                        }
                    )

            # Sort by wait time
            wait_times.sort(key=lambda x: cast(int, x["wait_time_min"]))

            return {
                "success": True,
                "wait_times": wait_times,
                "fastest_pharmacy": wait_times[0] if wait_times else None,
                "source": "mock",
            }

        except Exception as e:
            logger.error(f"Error getting wait times: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get wait times: {str(e)}",
                "source": "error",
            }


# Create LangChain tools
pharmacy_location_tool = Tool(
    name="find_nearby_pharmacies",
    description="Find nearby pharmacies. Use 'default' for all nearby, 'radius:5' for specific radius in miles, or 'insurance:BlueCross' to filter by accepted insurance.",
    func=lambda query: MockPharmacyLocator().find_nearby_pharmacies(query),
)

pharmacy_inventory_tool = Tool(
    name="check_pharmacy_inventory",
    description="Check if a medication is in stock. Use 'medication_name' to check all pharmacies or 'pharmacy_id:medication_name' for specific pharmacy.",
    func=lambda query: PharmacyInventoryTool().check_inventory(query),
)

pharmacy_wait_times_tool = Tool(
    name="get_pharmacy_wait_times",
    description="Get current wait times for prescription filling. Use 'all' for all pharmacies or comma-separated pharmacy IDs.",
    func=lambda query: PharmacyInventoryTool().get_wait_times(query),
)

pharmacy_details_tool = Tool(
    name="get_pharmacy_details",
    description="Get detailed information for a specific pharmacy including hours, contact info, and services. Use pharmacy_id as input.",
    func=lambda query: MockPharmacyLocator().get_pharmacy_details(query),
)

find_cheapest_pharmacy_tool = Tool(
    name="find_cheapest_pharmacy",
    description="STEP 4 WORKFLOW: Find the cheapest pharmacy option for a medication with current promotions and pricing. ALWAYS use after cost optimization to compare pharmacy prices. Returns ranked options by price with specific dollar amounts and promotions. Use medication name as input.",
    func=lambda query: PharmacyCostTool().find_cheapest_pharmacy(query),
)
