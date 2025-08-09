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

**Date:**  2025-08-09
<!-- Enter the date of the meeting in the format: 2025-03-15 -->

**Week:**  W3, Saturday
<!-- Specify the week number and day of the week, e.g., W2, Thursday -->

**Type (client/internal/mentor):**  Internal
<!-- Indicate the type of meeting: client, internal, or mentor -->

**Meeting Name/Purpose:**  Weekend Checkin
<!-- Briefly state the meeting's name or its main purpose, e.g., Weekly Team Meeting, Update Meeting, Deliverable -->

**Time:**  1600-1635
<!-- Enter the meeting start time (and end time if applicable), e.g., 1400–1500 -->

**Location / Platform:**  Teams
<!-- Specify where the meeting is held, e.g., Room 101, Zoom, Teams, etc. -->

**Attendees:**  
<!-- To indicate attendance, place an 'x' in the box like this: [x] -->

- [ ] Sirui Li (Client) 

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
1. Discuss Draft Project Poposal Progress and Sirui's message
2. Decide on Tasks for Draft Project Proposal
3. Decide on internal deadline for those tasks
---

## Discussion Notes
### 1. Discuss Draft Project Proposal Progress and Sirui's message
1. The team confirmed that several sections of the draft project proposal (scoping document) still need to be completed.
2. Franco confirmed that he is happy for Aswathy and Cedrus to focus on the **methodology section** of the project proposal.
3. Aswathy outlined a plan based on research into similar multi-agent systems.
4. The team discussed the initial plan of using **four distinct agents** to handle the project's workflow, noting that this structure aligns with the client's recent suggestions:
    - The **first agent (Agent A)** would be a **database selector**. It would take the user's query and the pre-existing **database schema embeddings** to identify the most relevant databases from a dataset of 200.
        - The team discussed using **OpenAI embeddings** and **BERT** to create these database embeddings.
        - Aswathy and Cedrus agreed that a simple similarity search would not be sufficient, and a **semantic search approach** is required.
        - Cedrus raised a point about whether similarity searches should be based on the **full database context** or just the **schema**. He suggested that schema-based similarity might be more effective for a smaller-scale project, as it provides a more flexible search than a key-based approach without being overwhelmed by the full database content.
        - The team agreed that both approaches should be tested to determine which method yields the best results.
    - The **second agent (Agent B)** would be responsible for selecting the relevant tables and columns within the chosen database.
    - The **third agent (Agent C)** would be a **SQL generator** that uses the query, tables, and columns to generate the final SQL code.
    - The **fourth agent (Agent D)** would then fetch the records from the database using the generated SQL query.
    - Franco noted that Agent B would also need to understand the **database schema** to correctly perform joins and other database operations.
5. The team agreed that this structure is a solid starting point and should be documented in the methodology section, with the understanding that it may be revised as they test different approaches.


### 2. Decide on Tasks for Draft Project Proposal
1. The team will push their completed work to the Git repository and send a message in the Teams channel to let the others know it is ready to be reviewed.
2. Franco will act as the **Client Manager**, handling all client communications and meeting scheduling.
3. Laine will be responsible for **taking and posting meeting minutes** and confirming tasks after each meeting.
4. The following tasks were assigned for the project proposal:
    - **Aim, Background and Deliverables**: Franco has already completed these sections.
    - **Timeline**: Nirma and Laine will work on this section.
    - **Methodology**: Aswathy and Cedrus will focus on this section.
    - **General Support**: RuiZhe will provide assistance with any other sections Franco needs help with.

---

## Next Steps Needed
1. Complete tasks for Draft Project Proposal by **Sunday Night**
    - Cedrus + Aswathy doing the Method
    - Laine + Nirma doing the Timeline
    - RuiZhe helping where possible (consult Franco)
    - Franco refining what he has already written
2. Franco (and anyone else who wants to help) to Compile work and finalise before sending to Client by **Tuesday**
3. Franco to confirm meeting location (Teams or in person?) on Thursday

---

**Next Meeting Name:** Client Meeting
- **Date & Time:**  Thursday 13th August 9:30am
- **Location / Platform:**  TBC
- **Next Meeting's Minutes to be prepared by:**  Laine Mulvay

**This Meetings Minutes prepared by:**  Laine Mulvay

