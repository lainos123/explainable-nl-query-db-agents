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

**Date:**  2025-07-31
<!-- Enter the date of the meeting in the format: 2025-03-15 -->

**Week:**  W2 Thursday
<!-- Specify the week number and day of the week, e.g., W2, Thursday -->

**Type (client/internal/mentor):**  Client
<!-- Indicate the type of meeting: client, internal, or mentor -->

**Meeting Name/Purpose:**  Inital Client Meeting (Meet and Greet)
<!-- Briefly state the meeting's name or its main purpose, e.g., Weekly Team Meeting, Update Meeting, Deliverable -->

**Time:**  1530-1550
<!-- Enter the meeting start time (and end time if applicable), e.g., 1400–1500 -->

**Location / Platform:**  Ried Library, In-person
<!-- Specify where the meeting is held, e.g., Room 101, Zoom, Teams, etc. -->

**Attendees:**  
<!-- To indicate attendance, place an 'x' in the box like this: [x] -->

- [X] Sirui Li (Client) 

- [ ] Wei Liu (Unit Coordinator)  
- [ ] Jichunyang Li (Project Facilitator)  

- [X] Franco Meng (Student)  
- [X] RuiZhe Wang (Student)  
- [X] Aswathy Mini Sasikumar (Student)  
- [X] Nirma Rajapaksha Senadherage (Student)  
- [X] Cedrus Dang (Student)  
- [X] Laine Mulvay (Student)  

---

## Agenda
1. Project Overview & Goals
2. Project Priorities & Deliverables
3. Technical Considerations
4. Meeting Schedule & Logistics
5. Immediate Next Steps

---

## Discussion Notes

### 1. Project Overview

- The project aims to build a system that enables users to input natural language queries and receive relevant database records, along with explanations for why those records were selected.
- The focus is on explainable interaction with relational databases using a multi-agent system.
- Instead of returning a single answer, the system will:
    - Identify relevant tables
    - Highlight relevant records
    - Optionally display schema or table relationships to enhance explainability
- This approach is intended to support transparency and trust, especially in scenarios where clarity is important.

### 2. Project Priorities

**First Priority – Build the Core Pipeline**
- Use the SPIDR public dataset (to be provided by Sirui).
- Develop a multi-agent system with the following agents:
    - Agent to interpret the natural language question
    - Agent to identify relevant tables
    - Agent to find relevant records within those tables
- The main focus is on highlighting candidate records, not necessarily returning final answers.
- Schema visualization may be used to help explain table relationships.
- The initial goal is to get the pipeline working; accuracy is not the main concern at this stage.
- Optionally, a graph database structure could be used to model table relationships.

**Second Priority – User Interface & Explainability**
- After the core pipeline is functional, develop a simple dashboard or front-end.
- Users should be able to input queries, see highlighted records, and view explanations.
- Schema visualization can be included for additional clarity (optional).

### 3. Technical Notes

- Any modeling approach is acceptable: small models, rule-based systems, or LLMs.
- Be aware that LLMs may have difficulty with relational databases.
- Assume users have some familiarity with database concepts.

### 4. Meeting Schedule

- Sirui may not be able to attend every meeting in person.
- Meetings with Sirui will be held weekly or fortnightly, depending on availability.
- Sirui will share her availability on Teams.
- Thursdays may be a good option for regular check-ins.

### 5. Immediate Next Steps

**Step 1 – Organise Availability with When2meet**
- Set up a When2meet poll for the team.
- Use the poll to:
    - Identify common times for internal team meetings.
    - Propose suitable slots for meetings with Sirui.
- Once availability is confirmed, schedule recurring meetings.
- The When2meet link will be sent out to the Teams chat, with a reminder sent to WhatsApp.

**Step 2 – Begin Technical Work**
- Wait for Sirui to send the SPIDR dataset.
    - In the meantime, familiarise the team with relational database structures in preparation for the dataset.
- Meanwhile:
    - Read up on multi-agent systems—what they are and how they’re trained.
    - Review academic papers and examples in similar contexts.

---

## Next Steps Needed
- [ ] Send out When2meet link to Teams chat with a reminder on WhatsApp
- [ ] Confirm team and client availability for meetings. Organise reoccuring meetings for both
- [ ] Await SPIDR dataset from Sirui
- [ ] Begin background reading on multi-agent systems: What they are and how they are trained
- [ ] Familiarise team with relational database concepts and structures

---

**Next Meeting Name:**  TBC
- **Date & Time:**  
- **Location / Platform:**  
- **Next Meeting's Minutes to be prepared by:**  

**This Meetings Minutes prepared by:**  Laine Mulvay

