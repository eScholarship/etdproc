
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

<summary><strong>📁 Python Files Grouped by Subsystem</strong></summary>

### Core ETD Processing Pipeline
| File | Description |
|------|-------------|
| `controller.py` | Coordinates high‑level workflow steps for ETD processing. |
| `computeValues.py` | Computes derived metadata values used during ETD processing. |
| `maps.py` | Contains mapping tables or transformation logic for metadata. |
| `consts.py` | Defines shared constants used across the codebase. |

### Database & Configuration
| File | Description |
|------|-------------|
| `configDb.py` | Manages configuration stored in the local database. |
| `dbIntf.py` | Database interface layer for reading/writing ETD processing related info. |
| `populateConfig.py` | Populates initial configuration values into the database. |


### OAI‑PMH Harvesting & Processing
| File | Description |
|------|-------------|
| `processOai.py` | Processes OAI‑PMH harvests and saves incoming records. |
| `oaiupdate.py` | Performs diff and normalization for oaioverride state. |
| `parseXml.py` | Parses ProQuest XML metadata files used in ETD workflows. |
| `parseGateway.py` | Parses gateway‑submitted ETD metadata or payloads. |


### ProQuest & External Package Intake
| File | Description |
|------|-------------|
| `getPQpackage.py` | Downloads or extracts ProQuest ETD submission packages. |
| `parseGateway.py` | Parses gateway‑submitted ETD metadata or payloads. |

### MARC & Library Systems (OCLC / Alma / SILS)
| File | Description |
|------|-------------|
| `generateMarc.py` | Generates MARC records from ETD metadata. |
| `harvestMarc.py` | Harvests MARC records from external sources. |
| `oclctoAlma.py` | Converts OCLC data into Alma‑compatible formats. |
| `sendToSILS.py` | Sends records or updates to the SILS (Alma) system. |

### Merritt Repository Integration
| File | Description |
|------|-------------|
| `sendToMerritt.py` | Sends ETD packages or metadata to the Merritt repository. |
| `getFromMerritt.py` | Retrieves files or metadata from the Merritt repository. |
| `fillMerrittArk.py` | Fills Merritt ARK identifiers for ETD items if MC callback was not captured. |
| `reprocessMCLog.py` | Reprocesses Merritt copy logs for troubleshooting or recovery. |

### eScholarship Integration
| File | Description |
|------|-------------|
| `depositToEschol.py` | Handles deposit of processed ETDs into eScholarship. |
| `escholClient.py` | Client wrapper for interacting with eScholarship APIs. |

### Queue Processing & Workflow Automation
| File | Description |
|------|-------------|
| `processQueues.py` | Processes internal job queues for ETD workflows. |







