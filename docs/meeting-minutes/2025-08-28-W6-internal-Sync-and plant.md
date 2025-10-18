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

**Date:**  20025-08-28
<!-- Enter the date of the meeting in the format: 2025-03-15 -->

**Week:**  W6, Thursdya
<!-- Specify the week number and day of the week, e.g., W2, Thursday -->

**Type (client/internal/mentor):**  internal (client in morning - no minutes)
<!-- Indicate the type of meeting: client, internal, or mentor -->

**Meeting Name/Purpose:**  Sync + Plan
<!-- Briefly state the meeting's name or its main purpose, e.g., Weekly Team Meeting, Update Meeting, Deliverable -->

**Time:**  1200-1320
<!-- Enter the meeting start time (and end time if applicable), e.g., 1400–1500 -->

**Location / Platform:**  Lab
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
- [ ] Cedrus Dang (Student)  
- [x] Laine Mulvay (Student)  

---

## Agenda
1. Debreif Client meeting from the morning
2. Update on Progress
3. Plan tasks

---

## Discussion Notes

### Cedrus + RuiZhe
- They created a custom schema format to help LLMs understand the database structure more easily. This is so that we can pull from any database, but it differs from our current 'tables.json' structure.
    - The new schema still includes PK (Primary Key) or FK (Foreign Key) information.
    - These have even been changed from flags to complete JSON Keys
    - The format is intended to be more LLM-friendly.
- Cedrus and RuiZhe will continue working on setting up the backend and database linking to frontend so that agents can query it. 

### Agent C
- The main difference between Agent C and Agent B is that Agent C also receives FK/PK information.
- Each agent is given progressively more schema information as we drill down what database, and tables we want.
- Plan to experiment with Agent C by providing both the tables selected by Agent B and the full schema to see which approach works best.

### Agent B testing
- Working on pulling a list of table names for testing purposes and saving them to confirm that Agent B is correctly selecting tables.

### Work for Later (if we ahve time)
- For Agent A: Remove simple/stop words from the natural language query to improve cosine similarity search.
- For Agent A: If the output is incorrect, print the schemas from the sqlite file and check if the selected table could actually answer the question.
- Ash's idea: Use the list of possible questions from `train_spider.json` to feed into Agent B if the NL query isn't one of the actual questions for that database. This would be similar to a company using their past queries to help Agents A/B generate better answers.

### Other Notes
- **No client meeting next week (study break)**.
- **Next meeting** will be on **Thursday** (online/on campus).

## Next Steps Needed

1. Cedrus and RuiZhe: Continue working on backend and database setup, and refining the new schema format.
    - push any work that is complete
2. Nirma and Laine: Build on top of Agent A/B from Franco and Ash, and start work on Agent C.
3. Franco and Ash:
    - Push work on Agent A/B
    - Set up testing for Agent B's table selection.
    - Finalise Agent A.
    - (Optional) Explore switching Agent A/B to use Cedrus' new schema format.

---

**Next Meeting Name:** Internal
- **Date & Time:**  Thursday 4th 
- **Location / Platform:**  Online or In person
- **Next Meeting's Minutes to be prepared by:**  Laine Mulvay

**This Meetings Minutes prepared by:**  Laine Mulvay

