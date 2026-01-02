
# ETD processor

ETD processor ingests incoming ETD packages from **ProQuest** and deposits them into **Merritt**, **eScholarship**, and the **Systemwide ILS**.


## 🚀 Run Instructions

```bash
python controller.py
```
## Data Flow
ProQuest → Merritt

ProQuest Gateway + Zip package → eScholarship, OCLC

ETD Proc → OCLC → OclcToALMA → ALMA

ALMA OAI → ETD Proc → Merritt, eScholarship

## 📂 Source Files



