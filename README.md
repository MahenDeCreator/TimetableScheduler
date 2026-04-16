# Academic Timetable Scheduler

#### Run on your local machine by:
* `python manage.py runserver`
* then go to port `http://127.0.0.1:8000/` to run the local server


| Hard Constraints                                  | Soft Constraints                                     |
| --------------------------------------------------|:----------------------------------------------------:|
| Unique session timing                             | sessions are assigned according to group requirements|
| Subject capacity <= classroom capacity            | All subjects are according to their faculty          |
| No overlapping classroom usage                    | Balanced subject distribution per group weekly       |
| Teacher schedules are non-overlapping             | Instructors are matched to their assigned subjects  |

This project implements an evolutionary algorithm to generate optimized university timetables, ensuring efficient resource allocation and minimal scheduling conflicts.

