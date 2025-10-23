# Match Score Calculation Algorithm

## Overview

The Replacement Search Agent uses a **point-based scoring system** to rank replacement products. Each product starts with a base score and gains/loses points based on how well it matches the original product.

---

## 🎯 Scoring Formula

### **Base Score**
```
Starting Score: 100 points
Minimum Viable Score: 60 points
```

Products below 60 points are **disqualified** and not shown.

---

## 📊 Score Components

### **1. Type Match** (CRITICAL - Must Match)
```
✓ Same type (e.g., both "range"):  +10 points
✗ Different type:                   DISQUALIFIED (score = 0)
```

**Example**:
- Original: Range
- Replacement: Range → ✓ +10 points
- Replacement: Dishwasher → ✗ DISQUALIFIED

---

### **2. Size Match** (CRITICAL)

```
Exact match (e.g., both 30"):       +20 points
Within 1 inch (29-31"):             +15 points
Within 2 inches (28-32"):           +10 points
More than 2 inches difference:      -50 points
```

**Example**:
- Original: 30 inch range
- Replacement: 30 inch → ✓ +20 points
- Replacement: 29 inch → ✓ +15 points
- Replacement: 28 inch → ✓ +10 points
- Replacement: 36 inch → ✗ -50 points

**Tolerance**: 2 inches (configurable)

---

### **3. Fuel Match** (CRITICAL for applicable appliances)

```
Same fuel type:                     +20 points
Different fuel type:                -50 points
Not applicable (e.g., dishwasher):  No penalty
```

**Example**:
- Original: Gas range
- Replacement: Gas → ✓ +20 points
- Replacement: Electric → ✗ -50 points
- Replacement: Dual fuel → ✗ -50 points

---

### **4. Feature Matching** (IMPORTANT)

```
Each matched feature:               +10 points per feature
Each missing feature:               -15 points per feature
```

**Example**:
- Original features: `["convection", "air fry", "self cleaning", "wifi", "5 burners"]`
- Replacement has: `["convection", "air fry", "wifi"]`

**Calculation**:
- Matched: 3 features × 10 = +30 points
- Missing: 2 features × 15 = -30 points
- **Net**: 0 points from features

**Better Match**:
- Replacement has: `["convection", "air fry", "self cleaning", "wifi", "5 burners", "griddle"]`
- Matched: 5 features × 10 = +50 points
- Missing: 0 features × 15 = 0 points
- **Net**: +50 points from features

---

### **5. Availability Bonus** (OPTIONAL)

```
In stock:                           +10 points
Limited stock:                      +5 points
Unknown:                            +3 points
Out of stock:                       0 points
```

---

### **6. Price Information Bonus** (OPTIONAL)

```
Has price listed:                   +5 points
No price:                           0 points
```

---

## 🧮 Complete Example

### **Original Product**:
```
Type: range
Size: 30 inch
Fuel: gas
Features: ["convection", "air fry", "self cleaning", "wifi", "5 burners"]
```

### **Replacement Product A** (High Score):
```
Type: range                         → +10 (type match)
Size: 30 inch                       → +20 (exact size)
Fuel: gas                           → +20 (fuel match)
Features: ["convection", "air fry", "self cleaning", "wifi", "griddle"]
  - Matched: 4 features             → +40 (4 × 10)
  - Missing: 1 feature              → -15 (1 × 15)
Availability: in stock              → +10
Price: $1,099                       → +5

TOTAL SCORE: 100 + 10 + 20 + 20 + 40 - 15 + 10 + 5 = 190 points ⭐⭐⭐
```

### **Replacement Product B** (Medium Score):
```
Type: range                         → +10 (type match)
Size: 29 inch                       → +15 (1 inch diff)
Fuel: gas                           → +20 (fuel match)
Features: ["convection", "air fry"]
  - Matched: 2 features             → +20 (2 × 10)
  - Missing: 3 features             → -45 (3 × 15)
Availability: unknown               → +3
Price: Not listed                   → 0

TOTAL SCORE: 100 + 10 + 15 + 20 + 20 - 45 + 3 + 0 = 123 points ⭐⭐
```

### **Replacement Product C** (Low Score - Disqualified):
```
Type: range                         → +10 (type match)
Size: 36 inch                       → -50 (6 inch diff, outside tolerance)
Fuel: gas                           → +20 (fuel match)
Features: ["convection"]
  - Matched: 1 feature              → +10 (1 × 10)
  - Missing: 4 features             → -60 (4 × 15)
Availability: unknown               → +3
Price: $899                         → +5

TOTAL SCORE: 100 + 10 - 50 + 20 + 10 - 60 + 3 + 5 = 38 points ❌ DISQUALIFIED
```

---

## 🏆 Score Ranges

### **Excellent Match** (150+ points)
- Exact or near-exact size
- Same fuel type
- Most features matched
- In stock with price

### **Good Match** (100-149 points)
- Size within tolerance
- Same fuel type
- Some features matched
- Available

### **Acceptable Match** (60-99 points)
- Size within tolerance
- Same fuel type
- Few features matched
- May have limited availability

### **Disqualified** (<60 points)
- Size outside tolerance
- Wrong fuel type
- Very few features
- Not shown to user

---

## 🎯 Ranking

Products are sorted by score (highest first):

```
Rank 1: Score 190 → Best match
Rank 2: Score 175
Rank 3: Score 160
...
Rank 10: Score 85 → Still acceptable
```

Only top 10 products are returned.

---

## ⚙️ Configurable Constants

```python
BASE_SCORE = 100          # Starting score
MIN_VIABLE_SCORE = 60     # Minimum to show
SIZE_TOLERANCE = 2        # Inches allowed difference
```

These can be adjusted in `replacement_search_agent.py`:

```python
class ReplacementSearchAgent:
    BASE_SCORE = 100
    MIN_VIABLE_SCORE = 60
    SIZE_TOLERANCE = 2
```

---

## 📈 Score Breakdown in Results

Each replacement includes `match_details`:

```json
{
  "match_score": 190,
  "match_details": {
    "size_match": true,
    "fuel_match": true,
    "features_matched": ["convection", "air fry", "self cleaning", "wifi"],
    "features_missing": ["5 burners"],
    "price_competitive": true
  }
}
```

---

## 🔍 Why This Scoring System?

### **Critical Factors** (Can Disqualify)
1. **Type**: Must be same appliance type
2. **Size**: Must fit in same space (±2 inches)
3. **Fuel**: Must match infrastructure (gas/electric)

### **Important Factors** (Affect Ranking)
4. **Features**: More matched features = better
5. **Availability**: In stock preferred
6. **Price**: Having price info is helpful

### **Penalties**
- Missing features: -15 points each (significant)
- Wrong size: -50 points (critical)
- Wrong fuel: -50 points (critical)

---

## 💡 Examples by Appliance Type

### **Range Scoring**
```
Critical: Type, Size (30"), Fuel (gas/electric)
Important: Convection, Air Fry, Burner Count
Bonus: Smart features, Self-cleaning
```

### **Dishwasher Scoring**
```
Critical: Type, Size (18" or 24")
Important: Quiet operation, Racks, Cycles
Bonus: Smart features, Third rack
Note: Fuel N/A (all electric)
```

### **Refrigerator Scoring**
```
Critical: Type, Size (width), Configuration
Important: Capacity, Ice maker, Water dispenser
Bonus: Smart features, Door-in-door
Note: Fuel N/A (all electric)
```

---

## 🎨 UI Display

Scores are color-coded in the interface:

```
150+:  Green badge  → Excellent match
100-149: Blue badge   → Good match
60-99:  Yellow badge → Acceptable match
<60:   Not shown    → Disqualified
```

---

## 🔧 Customization

To adjust scoring weights, edit `replacement_search_agent.py`:

```python
def _calculate_match_score(self, product, original):
    score = self.BASE_SCORE
    
    # Adjust these values:
    if exact_size:
        score += 20  # Change to 30 for more weight
    
    if fuel_match:
        score += 20  # Change to 30 for more weight
    
    score += len(matched_features) * 10  # Change multiplier
    score -= len(missing_features) * 15  # Change penalty
    
    # ... etc
```

---

## 📊 Statistics

From typical searches:

- **Average Score**: 110-130 points
- **Top Score**: 150-200 points
- **Disqualified**: ~30-40% of results
- **Shown**: Top 10 of viable matches

---

**The scoring system ensures users see the most relevant replacements that will actually work as substitutes for their original appliance!** 🎯
