# Project 15 data dictionary

## Dataset summary

- **File:** `carclaims.csv`
- **Records:** 15,420
- **Columns:** 33
- **Target:** `FraudFound`
- **Target values:** `No` = 14,497; `Yes` = 923
- **Raw majority-class baseline:** 14,497 / 15,420 = approximately 94.0%
- **Missing empty cells observed in the initial profile:** 0

The role **explanatory attribute** means information that may be available when an adjuster first triages a claim. The role **must-not-use** means the field is retained for audit or display but excluded from model features. **Nominal** means categories are names with no natural order. **Ordinal** means categories have a meaningful order. **Ratio** means numeric differences and ratios are meaningful and zero has a meaningful interpretation. **Interval** means differences are meaningful but zero is not a natural absence.

## Column dictionary

| # | Exact column name | Measurement type | Observed values or plausible range | Role and use decision |
|---:|---|---|---|---|
| 1 | `Month` | Nominal | `Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec` | Explanatory attribute; month name is a category, not a number. |
| 2 | `WeekOfMonth` | Ordinal | Integers `1`–`5` | Explanatory attribute; later weeks have an order, but the distance is not a measured amount. |
| 3 | `DayOfWeek` | Nominal | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday` | Explanatory attribute; weekdays are categories for this model, not a numeric scale. |
| 4 | `Make` | Nominal | 19 observed categories, including `Accura`, `BMW`, `Chevrolet`, `Dodge`, `Ferrari`, `Ford`, `Honda`, `Jaguar`, `Lexus`, `Mazda`, `Mecedes`, `Mercury`, `Nisson`, `Pontiac`, `Porche`, `Saab`, `Saturn`, `Toyota`, `VW` | Explanatory attribute; spelling such as `Mecedes`, `Nisson`, and `Porche` must be audited rather than silently corrected. |
| 5 | `AccidentArea` | Nominal | `Urban`, `Rural` | Explanatory attribute. |
| 6 | `DayOfWeekClaimed` | Nominal | `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`, and special value `0` | Explanatory attribute if available at triage; `0` is treated as unknown/special, not as a weekday. |
| 7 | `MonthClaimed` | Nominal | Twelve month names and special value `0` | Explanatory attribute if available at triage; `0` is treated as unknown/special, not as a month. |
| 8 | `WeekOfMonthClaimed` | Ordinal | Integers `1`–`5` | Explanatory attribute; ordered week category. |
| 9 | `Sex` | Nominal | `Female`, `Male` | Explanatory attribute; use only as an observed dataset field and document fairness limitations. |
| 10 | `MaritalStatus` | Nominal | `Single`, `Married`, `Divorced`, `Widow` | Explanatory attribute in the supplied dataset; document that sensitive personal attributes can create unfair outcomes and review their use. |
| 11 | `Age` | Ratio | Observed integers `0`–`80`; `0` occurs and is treated as a possible unknown/impossible age requiring audit | Explanatory attribute only after the age-zero quality rule is decided; never use an unexplained `0` as an ordinary age. |
| 12 | `Fault` | Nominal | `Policy Holder`, `Third Party` | Explanatory attribute; claim fault classification available in the supplied record. |
| 13 | `PolicyType` | Nominal | Nine observed combinations such as `Sedan - All Perils`, `Sedan - Collision`, `Sedan - Liability`, `Sport - All Perils`, `Sport - Collision`, `Sport - Liability`, `Utility - All Perils`, `Utility - Collision`, `Utility - Liability` | Explanatory attribute; the text contains vehicle/policy categories but is kept as the supplied field pending preprocessing. |
| 14 | `VehicleCategory` | Nominal | `Sedan`, `Sport`, `Utility` | Explanatory attribute. |
| 15 | `VehiclePrice` | Ordinal | `less than 20,000`; `20,000 to 29,000`; `30,000 to 39,000`; `40,000 to 59,000`; `60,000 to 69,000`; `more than 69,000` | Explanatory attribute; ordered price bands, not exact prices. |
| 16 | `PolicyNumber` | Nominal identifier | Integers `1`–`15,420`, intended to identify a policy/record | **Must-not-use** as a model feature; retain only for case display, traceability, and audit. |
| 17 | `RepNumber` | Nominal identifier-like code | Integers `1`–`16` | **Must-not-use initially** because it identifies a representative/agent code rather than claim evidence; reconsider only if source provenance proves it is legitimate claim-time explanatory information. |
| 18 | `Deductible` | Ratio-like monetary amount | `300`, `400`, `500`, `700` | Explanatory attribute; discrete monetary amount with meaningful differences. |
| 19 | `DriverRating` | Ordinal | Integers `1`–`4` | Explanatory attribute; ordered rating, not a continuous measurement. |
| 20 | `Days:Policy-Accident` | Ordinal | `none`, `1 to 7`, `8 to 15`, `15 to 30`, `more than 30` | Explanatory attribute; ordered time bands. The colon is part of the exact source column name. |
| 21 | `Days:Policy-Claim` | Ordinal | `none`, `8 to 15`, `15 to 30`, `more than 30` | Explanatory attribute; ordered time bands. The colon is part of the exact source column name. |
| 22 | `PastNumberOfClaims` | Ordinal | `none`, `1`, `2 to 4`, `more than 4` | Explanatory attribute; ordered claim-count bands. |
| 23 | `AgeOfVehicle` | Ordinal | `new`, `2 years`, `3 years`, `4 years`, `5 years`, `6 years`, `7 years`, `more than 7` | Explanatory attribute; ordered age bands. |
| 24 | `AgeOfPolicyHolder` | Ordinal | `16 to 17`, `18 to 20`, `21 to 25`, `26 to 30`, `31 to 35`, `36 to 40`, `41 to 50`, `51 to 65`, `over 65` if observed during final audit | Explanatory attribute; ordered age bands. Any value outside the documented set must fail validation. |
| 25 | `PoliceReportFiled` | Nominal binary | `Yes`, `No` | Explanatory attribute; report status must be available before the model recommendation. |
| 26 | `WitnessPresent` | Nominal binary | `Yes`, `No` | Explanatory attribute. |
| 27 | `AgentType` | Nominal binary | `External`, `Internal` | Explanatory attribute; audit for possible process bias before interpreting it. |
| 28 | `NumberOfSuppliments` | Ordinal | `none`, `1 to 2`, `3 to 5`, `more than 5` | Explanatory attribute only if supplements are known when triage occurs; timing must be confirmed because later supplements could be post-initial-claim information. |
| 29 | `AddressChange-Claim` | Ordinal | `no change`, `under 6 months`, `1 year`, `2 to 3 years`, `4 to 8 years` | Explanatory attribute; ordered time-since-change bands. The hyphen is part of the exact source column name. |
| 30 | `NumberOfCars` | Ordinal | `1 vehicle`, `2 vehicles`, `3 to 4`, `5 to 8`, `more than 8` | Explanatory attribute; ordered count bands. |
| 31 | `Year` | Interval calendar field | `1994`, `1995`, `1996` | **Must-not-use** as a model feature; used only to create the chronological split: 1994–1995 training and 1996 test. |
| 32 | `BasePolicy` | Nominal | `Liability`, `Collision`, `All Perils` | Explanatory attribute. |
| 33 | `FraudFound` | Nominal binary target | `No`, `Yes` | **Target, must-not-use as a feature**; this is the historical outcome the model learns to predict. |

## Timing and use notes

1. `FraudFound` is recorded as the historical outcome and must never enter cleaning decisions, feature selection, preprocessing, tuning, model input, or prediction input.
2. `PolicyNumber` is an identifier, not evidence that a claim is fraudulent. It is excluded from features.
3. `Year` is used only for the chronological evaluation split. It is excluded from features so the model cannot learn collection-period effects.
4. `RepNumber` is excluded initially because it is identifier-like. It must not become a proxy for a representative unless provenance proves that use is fair and appropriate.
5. `DayOfWeekClaimed`, `MonthClaimed`, and `Age` contain special-looking values (`0`) that require the Stage B audit. They are not silently treated as ordinary values.
6. `NumberOfSuppliments` requires timing confirmation because a supplement added after the initial claim could be a post-triage field. Until that timing is confirmed, the leakage review must report the uncertainty and the final production feature policy must follow the verified timing.
7. The dataset is anonymised/public for this project. No real identifiable claimant record may be added to the demonstration.
