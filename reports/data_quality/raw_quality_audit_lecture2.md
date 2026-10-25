RAW PROFILE AND LECTURE 2 AUDIT

Profile table: reports/data_quality/raw_profile.csv
Similarity table: reports/data_quality/label_similarity_variants.csv
Audit table: reports/data_quality/raw_quality_audit_lecture2.csv

Genuine Lecture 2 fault count:
- 3 genuine Lecture 2 fault categories remain: sentinel value, inconsistent encoding, and outlier.
- PolicyType/VehicleCategory has 4,987 rows in one systematic source-defined combination and is not counted as a fault; PolicyType is redundant for modelling.
- Duplicate, missing value, and invalid value checks found zero records and are not counted.
- Age and timing cross-column comparisons are reported as checks passed for fault classification because the source definitions do not prove that the fields describe the same event or person.

Example rows for sentinel Age=0:

PolicyNumber Age AgeOfPolicyHolder Year
------------ --- ----------------- ----
8            0   16 to 17          1994
14           0   16 to 17          1994
29           0   16 to 17          1994
32           0   16 to 17          1994
59           0   16 to 17          1994



Example rows for PolicyType/VehicleCategory mismatch:

PolicyNumber PolicyType        VehicleCategory BasePolicy
------------ ----------        --------------- ----------
4            Sedan - Liability Sport           Liability 
12           Sedan - Liability Sport           Liability 
13           Sedan - Liability Sport           Liability 
15           Sedan - Liability Sport           Liability 
16           Sedan - Liability Sport           Liability 



Age=0 distribution across AgeOfPolicyHolder bands: 16 to 17=320
Example rows for Days:Policy-Accident/Days:Policy-Claim check:

PolicyNumber DaysPolicyAccident DaysPolicyClaim
------------ ------------------ ---------------
205          none               more than 30   
732          none               more than 30   
1074         none               more than 30   
1211         none               more than 30   
1309         none               more than 30   



Example rows for Month/MonthClaimed same-year check:

PolicyNumber Month MonthClaimed Year
------------ ----- ------------ ----
1            Dec   Jan          1994
3            Oct   Nov          1994
4            Jun   Jul          1994
5            Jan   Feb          1994
6            Oct   Nov          1994




Modelling notes (not counted as faults):
- FraudFound is the target and is highly imbalanced: No=14,497; Yes=923.
- PolicyNumber is a unique identifier and is excluded from model features.

Checks passed (not counted as faults):
- No blank source cells.
- Duplicate checks excluding PolicyNumber affected 0 records; excluding PolicyNumber and RepNumber affected 0 records.
- No -1 or 999-style codes were observed.
- No invalid values were found in the checked numeric-like ranges.

Quality notes:
- Timeliness: Year ranges from 1994 to 1996; the later model task will use a chronological split.
- Relevance: The file does not contain an obvious claim amount field, so financial loss size cannot be modelled directly.
- Source data dictionary: no separate source data dictionary was included in the workspace; measurement roles are documented in reports/data_quality/data_dictionary.md.
