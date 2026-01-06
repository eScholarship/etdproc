
# ETD processor

ETD processor ingests incoming ETD packages from **ProQuest** and deposits them into **Merritt**, **eScholarship**, and the **Systemwide ILS**. 

The ETD Processing (etdproc) system is a modular pipeline designed to ingest, normalize, enrich, and distribute Electronic Theses and Dissertations (ETDs) across multiple downstream systems, including Merritt, eScholarship, and the UC Libraries’ Systemwide ILS/Alma environment. The architecture emphasizes clear separation of concerns, with each subsystem handling a distinct phase of the workflow while sharing common utilities for configuration, database access, and metadata transformation.

At a high level, the system operates as a data‑processing conveyor belt: ETD packages arrive from sources such as ProQuest or campus gateways, move through a series of validation and enrichment steps, and are ultimately deposited into preservation and discovery platforms.


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

## 📊 Architectural Diagram (Text‑Based)

```
                          +-----------------------------+
                          |     ETD Processing System   |
                          |           (etdproc)         |
                          +--------------+--------------+
                                         |
                                         v
                         +---------------+----------------+
                         |     Core Pipeline Orchestration|
                         |  (controller.py, processQueue.py)   |
                         +---------------+----------------+
                                         |
      -----------------------------------------------------------------------------------
      |                 |                         |                         |           |
      v                 v                         v                         v           v

+-----------+   +------------------+    +--------------------+    +----------------+   +----------------+
|  Ingest   |   |  Metadata Parsing|    |  Metadata Enrichment|    |  Queue Engine |   | Configuration  |
|  Sources  |   |  & Normalization |    |  & Mapping          |    | processQueues |   |  & Database    |
+-----------+   +------------------+    +--------------------+    +----------------+   +----------------+
| - ProQuest|   | - parseXml.py    |    | - computeValues.py |    |  Automated job |   | - configDb.py |
|   getPQ   |   | - parseGateway   |    | - maps.py          |    |  routing       |   | - dbIntf.py   |
| - Gateway |   | - processOai     |    | - consts.py        |    |                |   |               |
| - OAI-PMH |   | - oaiupdate      |    |                    |    |                |   |               |
+-----------+   +------------------+    +--------------------+    +----------------+   +----------------+

      |                 |                         |                         |           |
      -----------------------------------------------------------------------------------
                                         |
                                         v
                         +---------------+----------------+
                         |     Output & Distribution      |
                         +---------------+----------------+
                                         |
      -----------------------------------------------------------------------------------
      |                 |                         |                         |           
      v                 v                         v                         v           

+----------------+  +------------------+   +---------------------+   +----------------------+
|  Merritt Repo  |  |  eScholarship    |   |  Library Systems    |   |  MARC / Cataloging   |
| Preservation   |  |  Deposit         |   |  (SILS / Alma)      |   |       |
+----------------+  +------------------+   +---------------------+   +----------------------+
| - sendToMerritt|  | - depositToEschol|   | - sendToSILS.py     |   | - generateMarc.py     |
| - getFromMerritt| | - escholClient   |   | - oclctoAlma.py     |   |                      |
| - fillMerrittArk| |                  |   |                     |   |                      |
| - reprocessMCLog| |                  |   |                     |   |                      |
+----------------+  +------------------+   +---------------------+   +----------------------+

```

---

### 📘 How to Read This Diagram

- **Top layer**: The orchestrator that drives the entire ETD workflow.  
- **Middle layer**: Ingest, parsing, enrichment, configuration, and queue automation.  
- **Bottom layer**: Final distribution to preservation, discovery, and library systems.  
- Arrows show the general direction of data flow from ingest → processing → distribution.









