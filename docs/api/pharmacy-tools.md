# Pharmacy Tools API

The Pharmacy Tools module provides comprehensive pharmacy management, medication lookup, availability checking, and pricing information.

## PharmacyTool

The `PharmacyTool` class provides comprehensive pharmacy management, medication lookup, availability checking, and pricing information.

```python
# Note: Full API documentation will be auto-generated when the module is available
# ::: rxflow.tools.pharmacy_tools.PharmacyTool
```

## Safety Wrapper Functions

### Pharmacy Lookup

Safe wrapper function for pharmacy search and location services.

```python
# ::: rxflow.tools.pharmacy_tools.safe_pharmacy_lookup
```

### Medication Availability

Safe wrapper for medication availability checking across pharmacies.

```python
# ::: rxflow.tools.pharmacy_tools.safe_medication_availability
```

### Pricing Information

Safe wrapper for medication pricing lookup and comparison.

```python
# ::: rxflow.tools.pharmacy_tools.safe_pricing_lookup
```

## Usage Examples

### Basic Pharmacy Search

```python
from rxflow.tools.pharmacy_tools import PharmacyTool

# Initialize the tool
pharmacy_tool = PharmacyTool()

# Find pharmacies by location
pharmacies = pharmacy_tool.find_nearby_pharmacies("90210")

print(f"Found {pharmacies['count']} pharmacies in area")
for pharmacy in pharmacies['pharmacies']:
    print(f"- {pharmacy['name']}: {pharmacy['distance']} miles")
    print(f"  Address: {pharmacy['address']}")
    print(f"  Hours: {pharmacy['hours']}")
```

### Medication Availability Check

```python
# Check medication availability at specific pharmacy
availability = pharmacy_tool.check_medication_availability({
    "pharmacy_id": "CVS001", 
    "medication": "lisinopril 10mg",
    "quantity": 90
})

if availability['in_stock']:
    print(f"✅ In stock: {availability['available_quantity']} units")
    print(f"Ready for pickup: {availability['pickup_time']}")
else:
    print(f"❌ Out of stock - Expected: {availability['expected_date']}")
```

### Price Comparison

```python
# Compare prices across multiple pharmacies
price_comparison = pharmacy_tool.compare_prices({
    "medication": "omeprazole 20mg",
    "quantity": 30,
    "insurance": "Aetna PPO"
})

print("Price Comparison:")
for price in price_comparison['prices']:
    print(f"{price['pharmacy']}: ${price['copay']} (${price['cash_price']} cash)")
    
# Find lowest cost option
best_option = min(price_comparison['prices'], key=lambda x: x['copay'])
print(f"\nBest Option: {best_option['pharmacy']} - ${best_option['copay']}")
```

### Using Safety Wrappers

```python
from rxflow.tools.pharmacy_tools import (
    safe_pharmacy_lookup,
    safe_medication_availability,
    safe_pricing_lookup
)

# Safe pharmacy search with error handling
result = safe_pharmacy_lookup("90210")
if result.get("success"):
    pharmacies = result["pharmacies"]
else:
    print(f"Error: {result.get('error')}")

# Safe availability check
availability_result = safe_medication_availability({
    "pharmacy_id": "CVS001",
    "medication": "lisinopril",
    "quantity": 90
})

# Safe pricing lookup
pricing_result = safe_pricing_lookup({
    "medication": "omeprazole",
    "pharmacies": ["CVS001", "WAL001", "RIT001"]
})
```

## Pharmacy Management

### Multi-Pharmacy Workflow

```python
def find_best_pharmacy_option(medication: str, quantity: int, 
                            patient_location: str, insurance: str) -> dict:
    """Find optimal pharmacy based on availability, price, and convenience"""
    pharmacy_tool = PharmacyTool()
    
    # Step 1: Find nearby pharmacies
    nearby = safe_pharmacy_lookup(patient_location)
    if not nearby.get("success"):
        return {"error": "No pharmacies found in area"}
    
    # Step 2: Check availability and pricing at each pharmacy
    options = []
    
    for pharmacy in nearby["pharmacies"][:5]:  # Check top 5 closest
        # Check availability
        availability = safe_medication_availability({
            "pharmacy_id": pharmacy["id"],
            "medication": medication,
            "quantity": quantity
        })
        
        if not availability.get("in_stock"):
            continue
            
        # Get pricing
        pricing = safe_pricing_lookup({
            "pharmacy_id": pharmacy["id"],
            "medication": medication,
            "quantity": quantity,
            "insurance": insurance
        })
        
        option = {
            "pharmacy": pharmacy,
            "availability": availability,
            "pricing": pricing,
            "score": calculate_pharmacy_score(pharmacy, availability, pricing)
        }
        options.append(option)
    
    # Step 3: Rank options by score
    if not options:
        return {"error": "Medication not available at nearby pharmacies"}
    
    # Sort by score (higher is better)
    options.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "success": True,
        "recommended": options[0],
        "alternatives": options[1:3],
        "total_options": len(options)
    }

def calculate_pharmacy_score(pharmacy: dict, availability: dict, pricing: dict) -> float:
    """Calculate pharmacy option score based on multiple factors"""
    score = 100.0
    
    # Distance factor (closer is better)
    distance_penalty = min(pharmacy["distance"] * 5, 25)  # Max 25 point penalty
    score -= distance_penalty
    
    # Price factor (lower copay is better) 
    copay = pricing.get("copay", 999)
    if copay > 50:
        score -= min((copay - 50) * 0.5, 20)  # Max 20 point penalty
    
    # Availability factor
    if availability.get("pickup_time", "").lower() == "same day":
        score += 10
    elif "next day" in availability.get("pickup_time", "").lower():
        score += 5
        
    # Pharmacy rating bonus
    rating = pharmacy.get("rating", 0)
    score += rating * 2  # Up to 10 points for 5-star rating
    
    # Hours convenience bonus
    if pharmacy.get("24_hour", False):
        score += 5
    elif "8pm" in pharmacy.get("hours", "").lower():
        score += 2
    
    return max(score, 0)  # Ensure non-negative score

# Usage
best_option = find_best_pharmacy_option(
    medication="metformin 1000mg",
    quantity=90,
    patient_location="10001", 
    insurance="Medicare Part D"
)

if best_option.get("success"):
    rec = best_option["recommended"]
    print(f"Recommended: {rec['pharmacy']['name']}")
    print(f"Price: ${rec['pricing']['copay']}")
    print(f"Distance: {rec['pharmacy']['distance']} miles")
```

### Inventory Management

```python
def check_pharmacy_inventory(pharmacy_id: str, medication_list: list) -> dict:
    """Check inventory for multiple medications at once"""
    pharmacy_tool = PharmacyTool()
    
    inventory_report = {
        "pharmacy_id": pharmacy_id,
        "pharmacy_name": "",
        "medications": [],
        "in_stock_count": 0,
        "out_of_stock_count": 0,
        "low_stock_count": 0
    }
    
    # Get pharmacy details
    pharmacy_info = safe_pharmacy_lookup(pharmacy_id)
    if pharmacy_info.get("success"):
        inventory_report["pharmacy_name"] = pharmacy_info["pharmacies"][0]["name"]
    
    for medication in medication_list:
        availability = safe_medication_availability({
            "pharmacy_id": pharmacy_id,
            "medication": medication["name"],
            "quantity": medication["quantity"]
        })
        
        med_status = {
            "medication": medication["name"],
            "requested_quantity": medication["quantity"],
            "available_quantity": availability.get("available_quantity", 0),
            "status": "unknown"
        }
        
        if availability.get("in_stock"):
            available_qty = availability.get("available_quantity", 0)
            if available_qty >= medication["quantity"]:
                med_status["status"] = "in_stock"
                inventory_report["in_stock_count"] += 1
            else:
                med_status["status"] = "low_stock"
                inventory_report["low_stock_count"] += 1
        else:
            med_status["status"] = "out_of_stock"
            med_status["expected_date"] = availability.get("expected_date")
            inventory_report["out_of_stock_count"] += 1
        
        inventory_report["medications"].append(med_status)
    
    return inventory_report

# Usage
medications_needed = [
    {"name": "lisinopril 10mg", "quantity": 90},
    {"name": "metformin 1000mg", "quantity": 180},
    {"name": "omeprazole 20mg", "quantity": 30}
]

inventory = check_pharmacy_inventory("CVS001", medications_needed)
print(f"Inventory Status for {inventory['pharmacy_name']}:")
print(f"✅ In Stock: {inventory['in_stock_count']}")
print(f"⚠️ Low Stock: {inventory['low_stock_count']}")
print(f"❌ Out of Stock: {inventory['out_of_stock_count']}")
```

## Pricing and Insurance

### Insurance Optimization

```python
def optimize_insurance_coverage(patient_insurance: dict, medications: list) -> dict:
    """Optimize medication costs across insurance plans and pharmacies"""
    pharmacy_tool = PharmacyTool()
    
    optimization_report = {
        "patient_insurance": patient_insurance,
        "medications": [],
        "total_savings": 0,
        "recommended_actions": []
    }
    
    for medication in medications:
        med_analysis = {
            "medication": medication["name"],
            "quantity": medication["quantity"],
            "pharmacy_options": [],
            "best_option": None,
            "potential_savings": 0
        }
        
        # Check major pharmacy chains
        pharmacy_chains = ["CVS001", "WAL001", "RIT001", "TAR001"]
        
        for pharmacy_id in pharmacy_chains:
            pricing = safe_pricing_lookup({
                "pharmacy_id": pharmacy_id,
                "medication": medication["name"],
                "quantity": medication["quantity"],
                "insurance": patient_insurance["plan_name"]
            })
            
            if pricing.get("success"):
                option = {
                    "pharmacy_id": pharmacy_id,
                    "pharmacy_name": pricing.get("pharmacy_name", "Unknown"),
                    "copay": pricing.get("copay", 999),
                    "cash_price": pricing.get("cash_price", 999),
                    "insurance_covers": pricing.get("covered", False),
                    "savings_vs_cash": pricing.get("cash_price", 999) - pricing.get("copay", 999)
                }
                med_analysis["pharmacy_options"].append(option)
        
        # Find best option
        if med_analysis["pharmacy_options"]:
            best = min(med_analysis["pharmacy_options"], key=lambda x: x["copay"])
            med_analysis["best_option"] = best
            
            # Calculate savings vs average
            avg_copay = sum(opt["copay"] for opt in med_analysis["pharmacy_options"]) / len(med_analysis["pharmacy_options"])
            med_analysis["potential_savings"] = avg_copay - best["copay"]
            optimization_report["total_savings"] += med_analysis["potential_savings"]
        
        optimization_report["medications"].append(med_analysis)
    
    # Generate recommendations
    if optimization_report["total_savings"] > 50:
        optimization_report["recommended_actions"].append(
            f"Switch pharmacies to save ${optimization_report['total_savings']:.2f} per refill cycle"
        )
    
    # Check for GoodRx alternatives
    high_copay_meds = [med for med in optimization_report["medications"] 
                      if med.get("best_option", {}).get("copay", 0) > 30]
    
    if high_copay_meds:
        optimization_report["recommended_actions"].append(
            "Consider GoodRx or pharmacy discount programs for high-copay medications"
        )
    
    return optimization_report

# Usage
patient_insurance = {
    "plan_name": "Aetna PPO",
    "group_number": "12345",
    "member_id": "ABC123456"
}

patient_medications = [
    {"name": "atorvastatin 40mg", "quantity": 90},
    {"name": "lisinopril 20mg", "quantity": 90}, 
    {"name": "metformin 1000mg", "quantity": 180}
]

optimization = optimize_insurance_coverage(patient_insurance, patient_medications)
print(f"Potential Monthly Savings: ${optimization['total_savings']:.2f}")

for action in optimization['recommended_actions']:
    print(f"💡 {action}")
```

## Data Models

### Pharmacy Record Structure

```python
pharmacy_record = {
    "id": "CVS001",
    "name": "CVS Pharmacy #1234",
    "chain": "CVS",
    "address": "123 Main St, Anytown, CA 90210",
    "phone": "(555) 123-4567",
    "hours": "Mon-Fri 8AM-10PM, Sat-Sun 9AM-8PM",
    "24_hour": False,
    "drive_thru": True,
    "distance": 1.2,
    "rating": 4.5,
    "services": ["immunizations", "medication_therapy", "pill_packing"],
    "accepts_insurance": ["Aetna", "BCBS", "Cigna", "Medicare", "Medicaid"]
}
```

### Availability Response Structure

```python
availability_response = {
    "pharmacy_id": "CVS001",
    "medication": "lisinopril 10mg",
    "requested_quantity": 90,
    "in_stock": True,
    "available_quantity": 120,
    "pickup_time": "Same day",
    "ready_by": "2025-01-15T16:00:00Z",
    "partial_fill_available": True,
    "generic_available": True,
    "brand_available": False
}
```

### Pricing Information Structure

```python
pricing_info = {
    "pharmacy_id": "CVS001",
    "pharmacy_name": "CVS Pharmacy #1234",
    "medication": "omeprazole 20mg",
    "quantity": 30,
    "copay": 15.00,
    "cash_price": 89.99,
    "insurance_price": 15.00,
    "covered": True,
    "tier": 2,
    "prior_auth_required": False,
    "generic_alternative": {
        "available": True,
        "name": "omeprazole",
        "copay": 10.00
    }
}
```

## Integration Patterns

### Real-time Availability Monitoring

```python
import asyncio
from typing import List, Dict

async def monitor_medication_availability(medications: List[str], 
                                        pharmacies: List[str]) -> Dict:
    """Monitor medication availability across multiple pharmacies in real-time"""
    pharmacy_tool = PharmacyTool()
    monitoring_results = {}
    
    async def check_single_pharmacy(pharmacy_id: str, medication: str):
        """Check availability at a single pharmacy"""
        return await asyncio.to_thread(
            safe_medication_availability,
            {
                "pharmacy_id": pharmacy_id,
                "medication": medication,
                "quantity": 90
            }
        )
    
    # Create tasks for all pharmacy/medication combinations
    tasks = []
    for pharmacy_id in pharmacies:
        for medication in medications:
            task = check_single_pharmacy(pharmacy_id, medication)
            tasks.append((pharmacy_id, medication, task))
    
    # Execute all checks concurrently
    for pharmacy_id, medication, task in tasks:
        try:
            result = await task
            
            if pharmacy_id not in monitoring_results:
                monitoring_results[pharmacy_id] = {}
            
            monitoring_results[pharmacy_id][medication] = {
                "in_stock": result.get("in_stock", False),
                "quantity": result.get("available_quantity", 0),
                "last_checked": "2025-01-15T12:00:00Z"
            }
            
        except Exception as e:
            print(f"Error checking {medication} at {pharmacy_id}: {e}")
    
    return monitoring_results

# Usage
async def main():
    medications = ["lisinopril 10mg", "metformin 1000mg", "omeprazole 20mg"]
    pharmacies = ["CVS001", "WAL001", "RIT001"]
    
    availability_status = await monitor_medication_availability(medications, pharmacies)
    
    for pharmacy_id, medications_status in availability_status.items():
        print(f"\n{pharmacy_id}:")
        for med, status in medications_status.items():
            stock_status = "✅ In Stock" if status["in_stock"] else "❌ Out of Stock"
            print(f"  {med}: {stock_status} ({status['quantity']} units)")

# Run monitoring
# asyncio.run(main())
```

### Pharmacy Network Integration

```python
class PharmacyNetworkManager:
    """Manages integration with multiple pharmacy networks"""
    
    def __init__(self):
        self.pharmacy_tool = PharmacyTool()
        self.network_configs = {
            "cvs": {"api_endpoint": "cvs.api", "auth_required": True},
            "walgreens": {"api_endpoint": "wag.api", "auth_required": True},
            "rite_aid": {"api_endpoint": "riteaid.api", "auth_required": True}
        }
    
    def get_unified_availability(self, medication: str, zip_code: str) -> dict:
        """Get availability across all supported pharmacy networks"""
        all_pharmacies = safe_pharmacy_lookup(zip_code)
        
        if not all_pharmacies.get("success"):
            return {"error": "Unable to find pharmacies in area"}
        
        unified_results = {
            "medication": medication,
            "search_area": zip_code,
            "networks": {},
            "summary": {
                "total_pharmacies": 0,
                "in_stock_count": 0,
                "best_price": None,
                "fastest_pickup": None
            }
        }
        
        for pharmacy in all_pharmacies["pharmacies"]:
            network = self.identify_network(pharmacy["id"])
            
            if network not in unified_results["networks"]:
                unified_results["networks"][network] = {
                    "pharmacies": [],
                    "avg_price": 0,
                    "availability_rate": 0
                }
            
            # Check availability at this pharmacy
            availability = safe_medication_availability({
                "pharmacy_id": pharmacy["id"],
                "medication": medication,
                "quantity": 90
            })
            
            pharmacy_result = {
                "pharmacy": pharmacy,
                "availability": availability,
                "network": network
            }
            
            unified_results["networks"][network]["pharmacies"].append(pharmacy_result)
            unified_results["summary"]["total_pharmacies"] += 1
            
            if availability.get("in_stock"):
                unified_results["summary"]["in_stock_count"] += 1
        
        # Calculate network statistics
        for network, data in unified_results["networks"].items():
            if data["pharmacies"]:
                in_stock = sum(1 for p in data["pharmacies"] 
                              if p["availability"].get("in_stock"))
                data["availability_rate"] = (in_stock / len(data["pharmacies"])) * 100
        
        return unified_results
    
    def identify_network(self, pharmacy_id: str) -> str:
        """Identify which network a pharmacy belongs to"""
        if pharmacy_id.startswith("CVS"):
            return "cvs"
        elif pharmacy_id.startswith("WAL"):
            return "walgreens"  
        elif pharmacy_id.startswith("RIT"):
            return "rite_aid"
        else:
            return "independent"

# Usage
network_manager = PharmacyNetworkManager()
availability = network_manager.get_unified_availability("lisinopril 10mg", "90210")

print(f"Medication: {availability['medication']}")
print(f"Total Pharmacies: {availability['summary']['total_pharmacies']}")
print(f"In Stock: {availability['summary']['in_stock_count']}")

for network, data in availability['networks'].items():
    print(f"\n{network.upper()}:")
    print(f"  Availability Rate: {data['availability_rate']:.1f}%")
    print(f"  Locations: {len(data['pharmacies'])}")
```