# Executive Findings Report: Addis Ababa Road Traffic Safety Analysis

**Project Title:** Understanding and Trusting Road Accident Data: An Exploratory Analysis of Addis Ababa  
**Author:** YonInsights (`yo2120018@gmail.com`)  
**Data Source:** Addis Ababa Sub-City Police Departments (2017–2020)  
**Dataset Scale:** 13,063 collision dockets | 31 attributes  

---

## 1. Executive Summary

Road traffic accidents represent one of the leading causes of preventable trauma, premature mortality, and economic disruption in Addis Ababa. Using empirical police crash records collected across sub-city divisions, this study investigates data trustworthiness, temporal crash concentrations, vehicular characteristics, and environmental risk multipliers.

Our analysis uncovers a critical phenomenon: **the volume-severity inversion**. While collision *counts* peak predictably during the late afternoon weekday commute (17:00–18:00 on Fridays), the *lethality rate* (fatal and serious injury share per crash) concentrates during late nighttime and weekend hours—amplified substantially when street lighting infrastructure is missing or dysfunctional.

---

## 2. Key Empirical Findings

### 2.1. The Severity Imbalance
Recorded collision outcomes in Addis Ababa exhibit severe skewness:
- **Slight Injury:** 10,776 collisions (**82.5%**)
- **Serious Injury:** 1,976 collisions (**15.1%**)
- **Fatal Injury:** 311 collisions (**2.4%**)

*Analytical Consideration:* In machine learning classification, this 82.5% majority class requires specialized handling (e.g., class re-weighting, threshold adjustment, or focal loss) to avoid models that achieve high overall accuracy while failing completely to detect fatal crashes.

### 2.2. The Nighttime Lethality Inversion
- **Peak Volume Window:** Collisions peak at **17:00 (1,266 crashes)** and **18:00 (1,114 crashes)**, coinciding with high commuter congestion and pedestrian movement.
- **Peak Fatality Rate Window:** At 17:00, the severe/fatal injury rate is at its daily minimum (**14.4%**). However, between **21:00 and 02:00**, the severe/fatal rate jumps above **21.7%**, with fatal crash counts more than doubling relative to traffic density.
- **Causal Factors:** Nighttime driving features reduced congestion leading to higher travel speeds, reduced driver alertness, potential alcohol impairment, and compromised pedestrian visibility.

### 2.3. The Weekend Disparity
- **Friday** registers the highest collision volume of any day (**2,150 collisions**), driven by peak end-of-week commercial activity.
- **Saturday and Sunday**, despite having lower traffic volumes, record the highest raw fatality counts:
  - **Monday:** 29 fatalities | 15.2% severe/fatal rate
  - **Saturday:** 62 fatalities | 19.1% severe/fatal rate
  - **Sunday:** 55 fatalities | 17.7% severe/fatal rate

### 2.4. Environmental Hazards: The 2.5x Darkness Multiplier
Comparing crash outcomes across ambient lighting conditions reveals the dramatic role of municipal infrastructure:
- **Daylight:** 2.1% fatal | 14.7% serious (Total severe: **16.8%**)
- **Darkness with Lit Streetlights:** 2.8% fatal | 14.7% serious (Total severe: **17.5%**)
- **Darkness with Unlit Streetlights:** 5.6% fatal | 36.1% serious (Total severe: **41.7%**)
- **Darkness with No Lighting:** 5.8% fatal | 29.2% serious (Total severe: **35.0%**)

When municipal streetlights are dark or broken, the probability of a crash resulting in severe or fatal trauma surges by **nearly 2.5 times** compared to daylight or properly illuminated corridors.

### 2.5. Vehicle Classification & Casualty Dispersion
- Private passenger automobiles account for the largest volume of incidents, but their casualty distribution is tightly concentrated at 1 casualty per incident.
- Public transit buses (>45 seats) and heavy freight lorries exhibit broader casualty distributions, with upper whiskers reaching **6 to 8 casualties per crash** due to occupant occupancy density and vehicle mass differentials.

---

## 3. Data Trustworthiness & Methodological Limitations

A core requirement of ethical data science is communicating what data *cannot* establish:

1. **The Exposure Denominator Trap:** We cannot calculate individual trip fatality risk because traffic volume (vehicle-kilometres travelled or pedestrian counts) is not recorded. A high crash count at 17:00 reflects vehicle exposure, not necessarily higher individual driver risk.
2. **Reporting Bias:** Minor property damage or non-injury collisions are frequently resolved informally without police docketing, whereas serious and fatal collisions almost always mandate police records.
3. **The "Pseudo-Missing" Gap:** While standard null checks show 0% missingness in casualty demographics, **36.2% of records (4,727 rows)** contain the text marker `'na'` where demographic data was unrecorded.
4. **Data Entry Artifacts:** Features such as `Defect_of_vehicle` contain numeric codes (`'7'`, `'5'`) reflecting untranslated manual docket forms.

---

## 4. Policy Recommendations for Addis Ababa City Administration

Based strictly on the verified empirical evidence, municipal authorities should prioritize:

1. **Targeted Street Lighting Maintenance:** Prioritize rapid-response repairs for streetlights along high-speed corridors. Functional lighting is associated with reducing severe outcomes from 41.7% down to 17.5%.
2. **Nighttime & Weekend Speed Enforcement:** Shift automated radar speed enforcement and traffic police patrols to Friday, Saturday, and Sunday nights (21:00–03:00) when fatality rates peak.
3. **Digital Collision Reporting Standardization:** Replace paper docketing with standardized digital reporting that eliminates text `'na'` placeholders and validates category codes at the point of entry.
