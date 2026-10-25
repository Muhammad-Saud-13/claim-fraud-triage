<!-- Page 1: DSC306 Data Mining — Semester project briefs (Lectures 1–14) -->

# COMSATS University Islamabad — Department of Computer Science

# DSC306 Data Mining — Semester Projects

Sixteen end-user products, one per group — built on Lectures 1 to 14

| | |
|---|---|
| **Groups** | 16 groups of 3 students |
| **Marks** | 100, carried into the project component of the sessional assessment |
| **CLO** | CLO-5 — develop a project based on data science concepts in a team environment (Bloom: Creating) |
| **Techniques** | Everything from Lectures 1–14: the KDD process, attribute types and data quality, pre-processing, proximity measures, decision trees, rule-based classifiers, nearest neighbour, naïve Bayes, neural networks, and honest evaluation |
| **Deliverable** | A working application with a user interface that someone outside this class could open and use — not a notebook, not a set of plots |
| **Duration** | Three days. Issued Saturday 24 October; submission and viva Tuesday 27 October. The day plan on the last page is a requirement, not advice. |

## What you are building

Every project in this document is a product with a named user who has a real problem. Not a model, not an analysis — a thing that person opens, puts their own case into, and gets an answer they can act on. The test the instructor will apply at the demo is simple: can someone who has never taken this course sit down at your screen and get something useful out of it without you talking?

The sixteen projects differ in domain. They do not differ in difficulty. Every one requires the same pipeline, the same number of models, the same evaluation discipline and the same six screens, and each carries exactly one domain-specific technical challenge of comparable weight. Choosing project 3 over project 11 changes what you build it for, not how hard it is.

> **Read this before you choose**
>
> A model that is 94% accurate and sits in a notebook scores lower here than a model that is 71% accurate inside an application a ward sister, a loan officer or a farmer can actually use. The marks follow the product, the honesty of the evaluation, and the quality of the explanation — not the accuracy figure.

---

<!-- Page 2: DSC306 Data Mining — Semester project briefs (Lectures 1–14) -->

## The common specification — identical for all sixteen projects

This is what equalises the difficulty. Every group delivers all seven stages below, whatever the domain. Marks are allocated against these stages, not against the subject matter.

### A — Data and documentation

- A dataset of at least 2,000 records and 10 attributes, with at least three of the four measurement types from Lecture 2 present among them.
- A data dictionary you wrote: every column, its measurement type, its plausible range, and whether it is an identifier, an explanatory attribute, the target, or something that must not be used.
- A written statement of which columns would not be known at the moment the user asks the question, and are therefore excluded. Every project below has at least one.

### B — Data quality audit and repair (Lectures 2–3)

- At least six distinct fault categories found, using the vocabulary of Lecture 2, each with the expression that detects it and the count of affected records.
- Repairs carried out with a provenance column per repaired field, and a before-and-after table showing the effect of each repair as a number.
- A validate() function of at least ten assertions that passes on your cleaned data and fails on the raw data.

### C — Pre-processing (Lectures 3–4)

- A stated and justified decision on whether attributes need rescaling, separately for each model family you use.
- Either dimensionality reduction or feature subset selection, with the two compared on the same model.
- Discretization or binarization wherever a model you use requires it, with the binning choice justified.

### D — Models (Lectures 5–14)

- At least three classifiers from three different families — chosen from decision tree, rule-based, nearest neighbour, naïve Bayes, and neural network — trained on the same prepared data and compared on the same test set.
- One of the three must be a decision tree or a rule set, because the product has to explain itself.
- Hyper-parameters chosen by a stated procedure, not by trying numbers until one looks good.

### E — Evaluation (Lectures 9–10)

- A train/test split that reflects how the product will actually be used. If your data carries a date, the split is by time, and you must say so.
- The majority-class baseline reported beside every accuracy figure. An accuracy quoted alone earns no marks.
- At least two metrics beyond accuracy, with a written reason for why those two suit this user.
- A ROC curve with AUC, and a cost matrix with the operating threshold chosen from it rather than left at 0.5.
- k-fold cross-validation on the training portion, with the spread reported — not just the mean.

### F — Explanation

- Every prediction the product shows must come with its reason. A decision path, a rule, the nearest training cases, or the attributes that moved the posterior — whichever your model supports.
- The reason must be written in the user's language, not in the model's. "Prior admissions > 2 and severity III" is acceptable; "node 14, gini 0.31" is not.

### G — The application

A web application — Streamlit, Gradio, Flask or Django, your choice — with six screens. Five are the same for every group; the sixth is named in your project brief.

| # | Screen | What it must do |
|---|--------|-----------------|
| 1 | Data & quality | Load the data, show the audit report, let the user download the cleaned file |
| 2 | Model performance | Comparison table across your three models, ROC curve, confusion matrix, the baseline beside every figure |
| 3 | Single prediction | A form for one case → the prediction, a confidence, and the explanation |
| 4 | Batch scoring | Upload a CSV of many cases → a ranked, filterable table → download the result |
| 5 | Settings | Choose the model, move the decision threshold, edit the cost matrix, and see the consequences update live |
| 6 | Domain screen | Named in your project brief below — this is the screen that makes it your product |

---

<!-- Page 3: DSC306 Data Mining — Semester project briefs (Lectures 1–14) -->

The application must start from a clean machine with one documented command and must not require the marker to edit a path, install something not in your requirements file, or hold a dataset you did not ship. A product that only runs on the laptop of the student who wrote it is not a product.


<!-- Page 8: DSC306 Data Mining — Semester project briefs (Lectures 1–14) -->
# Our Project

### PROJECT 15 — Insurance Claim Fraud Triage

**Who uses it:** A claims adjuster deciding which claims to investigate.

**The problem:** Investigating every claim is impossible and investigating none is expensive. Adjusters pick by instinct, so straightforward claims get delayed while organised fraud passes through.

**What the product does:** The adjuster sees the day's claims ranked by fraud indicators, each with the specific patterns that triggered it and a recommendation to pay, review or investigate. Genuine claimants are paid faster because fewer of them are held up.

**Mining task:** Binary classification — does this claim warrant investigation?

**Starting data:** Public vehicle-insurance fraud datasets (around 15,000 claims), or a synthetic register you build with a documented fraud mechanism.

**Your assigned technical challenge:** Leakage under extreme imbalance. Fraud is a small minority, and these datasets usually contain at least one attribute recorded only after an investigation concluded. You must find it, prove it is leaking by showing the accuracy with and without it, and build the honest model that does not use it.

**Sixth screen (domain-specific):** A case-file screen — one claim with its indicators, comparable past claims the model found similar, and the adjuster's decision recorded against the recommendation.

---


---

<!-- Page 9: DSC306 Data Mining — Semester project briefs (Lectures 1–14) -->

## The three-day plan

You have three days, not a semester. The specification above does not shrink, so the only thing that saves you is sequencing: get a rough version of every stage working early, then improve the weakest one. A group that spends Sunday perfecting the data cleaning will have no application on Tuesday.

| When | Target | You must be able to say |
|------|--------|-------------------------|
| Saturday evening | Project chosen, data on screen | "We have loaded the file, we know its shape, and we have listed the columns we will not use and why." Divide the work now: one member on data, one on models, one starting the application from an empty screen. |
| Sunday morning | Cleaned data | "Six fault categories found and repaired with provenance, and validate() passes." Stop cleaning at midday whether or not it is perfect. |
| Sunday afternoon | One model, end to end | "One model trains, predicts, and we have an accuracy beside its baseline." It does not matter yet that the model is weak — it matters that the path from raw file to prediction runs without a human in the middle. |
| Sunday evening | Application skeleton running | "All six screens exist and open, even if four of them are empty." Whoever is building the application must not wait for the final model; wire it to the first one and swap the model later. |
| Monday morning | Three models compared | "Three families trained on identical data and compared on the same test set, with the split justified." |
| Monday afternoon | Evaluation complete | "Baseline beside every accuracy, two further metrics justified, ROC with AUC, cost matrix driving the threshold, cross-validation spread reported." This stage carries the most marks of any — do not let it be the one you rush. |
| Monday evening | Explanation, then the sixth screen | "Every prediction the product shows carries its reason, in the user's language." Build your domain screen only once that is true. |
| Tuesday morning | Freeze and rehearse | No new features. Write the README, test the one-command start on a machine that is not the one you built it on, and question each other for the viva. |
| Tuesday | Submission and viva | Twelve-minute demonstration, eight minutes of questions, all three members present and each answering on the part they built. |

### Triage, if Monday night arrives and you are not ready

If you fall behind, cut in this order. Drop the sixth domain screen first, then the third model, then reduce the fault categories from six to the three you can evidence properly. Never cut the baseline, the cost matrix or the explanation. Those three carry more marks than everything you would be protecting by cutting them, and a product without them fails the demonstration however good it looks.

## Marking — 100 marks

| Component | Marks | What earns them |
|-----------|-------|-----------------|
| Data quality work (Stages A–B) | 15 | Six genuine fault categories with evidence; repairs traceable; validator passes on clean and fails on raw |
| Pre-processing (Stage C) | 10 | Rescaling decision correct per model family; reduction and selection genuinely compared, not just both run |
| Models (Stage D) | 15 | Three families, properly tuned, fairly compared on identical data |
| Evaluation honesty (Stage E) | 20 | The largest single component. Correct split, baseline everywhere, metrics justified, threshold from a cost matrix, cross-validation spread reported |
| Explanation quality (Stage F) | 10 | Every prediction explained, in the user's language |
| The application (Stage G) | 20 | Six screens working; starts with one command on a clean machine; a stranger can use it unaided |
| Your assigned challenge | 10 | The domain-specific difficulty named in your brief, addressed and evidenced |
| Demo and viva | 10 | Marked individually. Each member answers on the part they built. |

---

<!-- Page 10: DSC306 Data Mining — Semester project briefs (Lectures 1–14) -->

## Where the marks actually are

Evaluation honesty carries more marks than the application itself, and far more than accuracy. A group reporting 68% accuracy against a 61% baseline, with a threshold chosen from a cost matrix and a frank account of what the model cannot do, scores above a group reporting 97% that turns out to rest on a leaked column. Every dataset in this list has at least one attribute that will do that to you.

## Ethics requirement

**On data about people.** Several of these products touch health, money, employment or safety. Use anonymised or public data only; never put a real person's identifiable record into a demonstration. Every product must state on screen that it is a student project and is not fit for clinical, financial or legal use. Projects 1, 3, 5, 9 and 15 must each include a short written statement of who could be harmed if the product were wrong, and what the interface does to reduce that risk.

## Proposing your own

Any of the sixteen may be swapped for a project of your own design, provided it meets the full common specification, has a named user with a real problem, and is agreed with the instructor on Saturday night. With three days available, a project proposed on Sunday will not be approved.