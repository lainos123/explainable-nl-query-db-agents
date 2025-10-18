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

**Date:**  2025-09-11
<!-- Enter the date of the meeting in the format: 2025-03-15 -->

**Week:**  W7, Thursday
<!-- Specify the week number and day of the week, e.g., W2, Thursday -->

**Type (client/internal/mentor):**  multipe - internal; client
<!-- Indicate the type of meeting: client, internal, or mentor -->

**Meeting Name/Purpose:**  Weekly Team Meetin; Client Meeting
<!-- Briefly state the meeting's name or its main purpose, e.g., Weekly Team Meeting, Update Meeting, Deliverable -->

**Time:**  0930-0940 client; 1200-1400 team meeting
<!-- Enter the meeting start time (and end time if applicable), e.g., 1400–1500 -->

**Location / Platform:**  Teams; Lab
<!-- Specify where the meeting is held, e.g., Room 101, Zoom, Teams, etc. -->

**Attendees:**  
<!-- To indicate attendance, place an 'x' in the box like this: [x] -->

- [x] Sirui Li (Client) 

- [ ] Wei Liu (Unit Coordinator)  
- [ ] Jichunyang Li (Project Facilitator)  
- [x] Pascal Sun (Project Facilitator)

- [x] Franco Meng (Student)  
- [x] RuiZhe Wang (Student)  
- [x] Aswathy Mini Sasikumar (Student)  
- [x] Nirma Rajapaksha Senadherage (Student)  
- [x] Cedrus Dang (Student)  
- [x] Laine Mulvay (Student)  

---

## Agenda
1. Client Meeting: Discuss progress with Client
2. Internal Meeting: Update on progress within team, decide and delegate tasks
3. Project Progress Update: Show facillitator progress and recieve feedback

---

## Discussion Notes

### Client Chat Notes
- Client: “All look good”
- For Agent C, instead of just testing if the SQL is true/false, compare the similarity of selections.

### Group Meeting
- For Agent C, Use the schema provided with FKs/PKs as the main one (Cedrus’ version is more descriptive).
  - This will make it easier to generate the graph schema.
  - Use `complete_combined_schema.json` as the main schema file.
      - Plan to create a future script to generate this based on Cedrus’ code. At the end maybe , if we don't already have one
  - Develop a script/function to generate the graphDB.
- All scripts and updates to be given to Cedrus and merged by Saturday Night.
    - Ensure scripts accept relevant inputs (e.g., callable with the NL question).

### Notes from Pascal
- Focus on getting the pipeline working well; a running pipeline is the priority.
- For testing Agent C, compare the output of the ground truth SQL to the output of our SQL (compare the results of the queries).

### Next Steps

- Franco: Push updates for Agent C (DONE at time of writing). Afterward, help with UI/UX design (create a canvas and discuss before starting).
- Laine: Update Python files (using Franco's code) for Agents A, B, and C, and provide them to Cedrus.
- Nirma & Ash: Create the testing function for Agent C, execute SQL, and pass results to a comparison function.
- Cedrus: Change repo structure, push updates, and continue working on the application.
    - Write API scripts for each agent.
    - Afterward, connect the API to the front end.
- RuiZhe: Integrated SQL engines into the app and will continue assisting Cedrus with development.

---

**Next Meeting Name:**
- **Date & Time:**  
- **Location / Platform:**  
- **Next Meeting's Minutes to be prepared by:**  Laine Mulvay

**This Meetings Minutes prepared by:**  Laine Mulvay

