<!-- 
  File Naming Convention: 2025-MM-DD-WX-type-name.md

  - MM: Month (e.g., 01 for January)
  - DD: Day (e.g., 09)
  - WX: Week number (e.g., W2 for Week 2)
  - type: Meeting type (e.g., client, internal, mentor)
  - name: Meeting name or purpose (e.g., sync, update, deliverable, etc.)

  Example:
    2025-03-15-W2-client-update.md
    (This file would be for a client meeting held on March 15, 2025, during Week 2.)
-->

# CITS5553 Meeting Minutes

**Date:**  2025-08-14
<!-- Enter the date of the meeting in the format: 2025-03-15 -->

**Week:**  W4, Thursday
<!-- Specify the week number and day of the week, e.g., W2, Thursday -->

**Type (client/internal/mentor):**  client
<!-- Indicate the type of meeting: client, internal, or mentor -->

**Meeting Name/Purpose:**  Update Meeting
<!-- Briefly state the meeting's name or its main purpose, e.g., Weekly Team Meeting, Update Meeting, Deliverable -->

**Time:**  0930-0940
<!-- Enter the meeting start time (and end time if applicable), e.g., 1400–1500 -->

**Location / Platform:**  Teams
<!-- Specify where the meeting is held, e.g., Room 101, Zoom, Teams, etc. -->

**Attendees:**  
<!-- To indicate attendance, place an 'x' in the box like this: [x] -->

- [x] Sirui Li (Client) 

- [ ] Wei Liu (Unit Coordinator)  
- [ ] Jichunyang Li (Project Facilitator)  

- [x] Franco Meng (Student)  
- [x] RuiZhe Wang (Student)  
- [x] Aswathy Mini Sasikumar (Student)  
- [x] Nirma Rajapaksha Senadherage (Student)  
- [x] Cedrus Dang (Student)  
- [x] Laine Mulvay (Student)  

---

## Agenda
1. Discuss draft proposal

---

## Discussion Notes
turn Explainability conten, data display and aggrigation, timeline, next steps


### 1. Rethink Agent Design

#### Record Retrieval & UI
- Records will be retrieved directly, and the UI will handle the explanation and display.
- SQL queries can be executed directly via a program (e.g., Python) connected to the database; a separate agent for query execution is not required.

#### Explainability Component
- Outputs from the database selector (Agent A) and schema summariser (Agent B) will be provided to the UI’s explainability section.
- After records are returned, the UI will handle explainability for the user.

- **Agent Flow:**
  - **A:** Selects Database
  - **B:** Reads the selected database and summarises the schema
  - **C:** Uses the schema description and user natural language query to generate SQL query


### 2. Data Display & Aggregations
- For queries involving aggregations (e.g., averages), the system will return relevant records rather than calculated results.
- Large result sets will be truncated initially; alternative display methods can be considered in the future.


### 3. Timeline
- The current Gantt chart and timeline are acceptable but should remain flexible to accommodate potential development delays (e.g., bugs).

---

## Next Steps Needed
1. Finalise proposal and submit
  a. update Agents used and flow diagram
2. Submit Individaul Proposals
3. Get API keys from Sirui
4. Next week: begin developing the framework and agents if team members are available.

---

**Next Meeting Name:**
- **Date & Time:**  Saturday 1600
- **Location / Platform:**  Teams
- **Next Meeting's Minutes to be prepared by:**  Laine Mulvay

**This Meetings Minutes prepared by:**  Laine Mulvay

