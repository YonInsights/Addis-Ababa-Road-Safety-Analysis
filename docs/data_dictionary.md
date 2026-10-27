# Data Dictionary: Addis Ababa Road Traffic Accidents (RTA)

## 1. Dataset Provenance & Overview

- **Dataset File:** `Data/Addis_Ababa_city_RTA.csv`
- **Total Records (Observations):** 13,063
- **Total Variables (Columns):** 31 (30 features + 1 target variable)
- **Primary Source:** Addis Ababa Sub-City Police Departments (recorded from manual collision dockets, covering approximately 2017–2020).
- **Public Domain / Benchmark Use:** Widely archived across Kaggle, UCI ML repository mirrors, and Figshare for road safety and severity prediction research.
- **Redistribution & Licensing:** Derived from administrative municipal police logs. In line with project safety requirements, raw data remains local to prevent unverified public distribution.

---

## 2. Distinction: Published Facts vs. Analytical Observations

- **Publisher Stated Facts:** The dataset captures collision records prepared by traffic police officers. Variables represent categorical classifications selected during on-scene investigation or hospital follow-up.
- **Our Analytical Observations:** 
  1. The dataset contains severe class imbalance (82.5% Slight Injury, 15.1% Serious Injury, 2.4% Fatal injury).
  2. The data exhibits reporting artifacts: non-applicable or missing values are encoded as literal strings (`'na'`, `'Unknown'`) in addition to empty cells (`NaN`).
  3. No exposure denominators (traffic volumes, vehicle counts per hour, or road segment lengths) are present. Therefore, high accident counts cannot be equated with higher risk without caution.

---

## 3. Variable Definitions by Domain

### Domain 1: Temporal & Incident Overview
| Column Name | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Time` | String (Object) | Time of day collision occurred (HH:MM:SS) | `17:02:00`, `21:30:00` |
| `Day_of_week` | String (Object) | Day of week the incident occurred | `Monday`, `Sunday` |
| `Number_of_vehicles_involved` | Integer (`int64`) | Count of vehicles directly involved in the crash | `1`, `2`, `3` |
| `Number_of_casualties` | Integer (`int64`) | Count of individuals injured or killed | `1`, `2`, `4` |
| `Type_of_collision` | String (Object) | Manner of vehicle impact or object struck | `Collision with roadside-parked vehicles`, `Vehicle with vehicle collision` |
| `Vehicle_movement` | String (Object) | Dynamic action of the vehicle immediately prior | `Going straight`, `Overtaking`, `Turning left` |
| `Cause_of_accident` | String (Object) | Investigating officer's assessed primary cause | `Moving Backward`, `Overtaking`, `No priority to pedestrian` |

### Domain 2: Driver Demographics & Background
| Column Name | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Age_band_of_driver` | String (Object) | Age range of the primary driver | `18-30`, `31-50`, `Under 18`, `Unknown` |
| `Drivers_gender` | String (Object) | Gender of driver | `Male`, `Female`, `Unknown` |
| `Educational_level` | String (Object) | Formal education attainment of driver | `Above high school`, `Junior high school`, `Elementary school` |
| `Vehicle_driver_relation` | String (Object) | Relationship between driver and vehicle | `Employee`, `Owner`, `Other` |
| `Driving_experience` | String (Object) | Total driving experience band | `1-2yr`, `2-5yr`, `5-10yr`, `Above 10yr`, `No Licence` |

### Domain 3: Vehicle Characteristics
| Column Name | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Type_of_vehicle` | String (Object) | Classification of primary vehicle | `Automobile`, `Lorry (41-100Q)`, `Public (> 45 seats)`, `Taxi` |
| `Owner_of_vehicle` | String (Object) | Ownership entity | `Owner`, `Government`, `Organization`, `Other` |
| `Service_year_of_vehicle` | String (Object) | Age band of vehicle in service | `1-2yr`, `2-5yrs`, `5-10yrs`, `Above 10yr`, `Unknown` |
| `Defect_of_vehicle` | String (Object) | Known mechanical defects noted | `No defect`, `7`, `5` (Contains encoding artifacts) |

### Domain 4: Road Infrastructure & Geometry
| Column Name | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Area_accident_occured` | String (Object) | Land-use / locality context | `Residential areas`, `Office areas`, `Hospital areas` |
| `Lanes_or_Medians` | String (Object) | Lane configuration / divider type | `Undivided Two way`, `Two-way (divided with broken lines)` |
| `Road_allignment` | String (Object) | Horizontal/vertical road curvature | `Tangent road with flat terrain`, `Gentle horizontal curve` |
| `Types_of_Junction` | String (Object) | Intersection configuration | `No junction`, `Y Shape`, `T Shape`, `Crossing` |
| `Road_surface_type` | String (Object) | Material / pavement type | `Asphalt roads`, `Gravel roads`, `Earth roads` |
| `Road_surface_conditions` | String (Object) | Surface moisture / friction state | `Dry`, `Wet or damp`, `Snow`, `Flood over 3cm. deep` |

### Domain 5: Environmental Conditions
| Column Name | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Light_conditions` | String (Object) | Ambient lighting at scene | `Daylight`, `Darkness - lights lit`, `Darkness - no lighting` |
| `Weather_conditions` | String (Object) | Atmospheric conditions | `Normal`, `Raining`, `Fog or mist`, `Windy` |

### Domain 6: Casualty & Pedestrian Characteristics
| Column Name | Data Type | Description | Sample Values |
| :--- | :--- | :--- | :--- |
| `Casualty_class` | String (Object) | Role of casualty (Driver/Passenger/Pedestrian) | `Driver or rider`, `Pedestrian`, `Passenger`, `na` |
| `Casualty_gender` | String (Object) | Gender of injured party | `Male`, `Female`, `na` |
| `Age_band_of_casualty` | String (Object) | Age range of casualty | `18-30`, `31-50`, `Under 18`, `na` |
| `Work_of_casuality` | String (Object) | Employment type of casualty | `Employee`, `Self-employed`, `Student`, `Unemployed` |
| `Fitness_of_casuality` | String (Object) | Physical fitness / impairment state | `Normal`, `Deaf`, `Blind` |
| `Pedestrian_movement` | String (Object) | Action of pedestrian if involved | `Not a Pedestrian`, `Crossing from nearside`, `In carriageway` |

### Domain 7: Target Variable (Outcome)
| Column Name | Data Type | Description | Classes & Frequencies |
| :--- | :--- | :--- | :--- |
| **`Accident_severity`** | String (Object) | Maximum casualty outcome severity resulting from the crash | - **`Slight Injury`**: 10,776 (82.5%)<br/>- **`Serious Injury`**: 1,976 (15.1%)<br/>- **`Fatal injury`**: 311 (2.4%) |

