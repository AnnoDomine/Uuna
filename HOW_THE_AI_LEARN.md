# Best practice

One of the most used way to teach an AI is the scoring system. The AI gains points for predictions and learns what the AI did well and what it did poorly.

---

In this AI we do a simular, more complex and way more predictable and scaleable way.

## In deep scoring

> 1 The AI have multiple roles and two of them are "tinker" and "observer".
>
> > 1.1 The Tinker is the scoreboard-creator.
>
> > > 1.1.1 This role gains only the output (without knowledge what was requested).
>
> > > 1.1.2 Based on the quantity of the output the tinker decided how much points this amount could gain.
>
> > > 1.1.3 This information, the role applies to the input, which get continued to the observer.
>
> > 1.2 The Observer is a bad boy.
>
> > > 1.2.1 The observer knows the input, the output, get a percentage confidence from the role, from where the information comes from (architekt, expedition group, etc) and the amount of posible points.
>
> > > 1.2.2 Now the observer gains points based on accuracy, formatting, and logic in a highly judged way.
>
> > > > 1.2.2.1 First he calculate the points this task gains with the max posible points (we call it coopertion-part-points): `Points Received / Max Potential`.
>
> > > > 1.2.2.2 Then he calculate the max possible points with the confidence from the role: `Max Potential * Self-Confidence %`.
>
> > > > 1.2.2.3 The this is the role-personal-score: `Points Received / (Max Potential * Self-Confidence %)`.
>
> > > > 1.2.2.4 The observer now calculated the role personal score to the percental value, and give the role the information, how much percental the role gained for the task. If the percentage would go over 100%, the return is 100%.
>
> 2 The AI does not gain a specific amount of points based on the user interaction. We give multiple points.
>
> > > > 2.1 Role scoring:
>
> > > > 2.1.1 The role by it self gains a percental amount of points based on the task which were done.
>
> > 2.2 Cooperated scoring:
>
> > > 2.2.1 In our KI multiple roles plaing together to presentate the response to the user.
>
> > > 2.2.2 This calculation is based on the sum of all coopertion-part-points from the time, the user makes an input, till the time the user gains an answer.
>
> > > > 2.2.2.1 Beside the sum of the coopertion-part-points, the hole request will gain a spezific point.
>
> > > > > 2.2.2.1.1 To calculate this, the tinker will calculate a scoring based on the quantaty of the request (how much steps, how often the curier needs to apply a pre or a post event,...)
>
> > > > > 2.2.2.1.2 This score is now the base for the task-score.
>
> > > > > 2.2.2.1.3 The task score do not gain a confidence from the roles. It will be the pur score of the task.
>
> > > > 2.2.2.2 Now the sum of the coopertion-part-points and the task-score will be calculated together (cpp: 60%, ts: 40%).
>
> > > > 2.2.2.3 The observer will only tell the percentage reached. If the percentage would go over 100%, the return is 100%.

---

## Request/Research workflow of the agents

> 1 User requests something.
>
> 2 Librarian gains the request and decid:
>
> > 2.1 Do i have knowledge about the request OR
>
> > 2.2 Do i need to research (Even if knowledge is there bout would not totally fit)
>
> 3 If 2.1:
>
> > 3.1 The Librarian response the knowledge to the user
>
> 4 If 2.2:
>
> > 4.1 The Librarian creates a task and sends the task_id to the Courier (If the Librarian have already knowledge which not totaly fit, add it to the task inside the message as field: CONTEXTUAL_INFO)
>
> > 4.2 The Courier gets all information from the task and decided which specialist gains the next step:
>
> > > 4.2.1 The Courier creates an event and send the event to the specilists.
>
> > > > 4.2.1.1 If the choosen specialist is "The Archivist"
>
> > > > > 4.2.1.1.1 The Archivist select the way and the amount of information.
>
> > > > > 4.2.1.1.2 The Archivist combines all information and creates a new event.
>
> > > > > 4.2.1.1.3 The Archivist sends the event_id back to the Courier.
>
> > > > 4.2.2.1 If the choosen specialist is "The Expedition Group"
>
> > > > > 4.2.2.1.1 The Expedition Group select the way and the amount of information.
>
> > > > > 4.2.2.1.2 The Expedition Group combines all information and creates a new event.
>
> > > > > 4.2.2.1.3 The Expedition Group sends the event_id to the Sentinel.
>
> > > > > > 4.2.2.1.3.1 The Sentinel secures the output from the Expedition Group (snitsation, validation,...)
>
> > > > > > 4.2.2.1.3.2 The Sentinel creates a new event with the sanitised information.
>
> > > > > > 4.2.2.1.3.3 The Sentinel sends the event_id back to the Courier.
>
> > > > 4.2.2.1 If the choosen specialist is "The Cartographer"
>
> > > > > 4.2.2.1.1 The Cartographer select the way and the amount of information.
>
> > > > > 4.2.2.1.2 The Cartographer combines all information and creates a new event.
>
> > > > > 4.2.2.1.3 The Cartographer sends the event_id back to the Courier.
>
> > > 4.2.2 After receive an event_id from a specialist, the Courier decides if more information are needed.
>
> > > 4.2.3 If more information needed, repeat from 4.2.1.
>
> > > 4.2.4 If the Courier thinks, the information fits to resolve the request, the Courier creates an new event
>
> > > 4.2.5 The Courier sends the event_id to the Sages.
>
> > > > 4.2.5.1 The Sages decides if the information, which were collected are fit the response and be valid predictions
>
> > > > 4.2.5.2 The Sages creates an event wit the information "APPROVED" or "REJECTED".
>
> > > > 4.2.5.3 The Sages sends the event_id back to the Courier.
>
> > > 4.2.6 If "REJECTED" the courier restarts from 4.2.1.
>
> > > 4.2.7 If "APPROVED" the Courier sends the task_id to the Tinker.
>
> > > > 4.2.7.1 The Tinker creates max_potential in 2 ways:
>
> > > > > 4.2.7.1.1 Based on the hole task incl. ALL events
>
> > > > > > 4.2.7.1.1.1 The quantity of the task
>
> > > > > 4.2.7.1.2 Each event for them self.
>
> > > > > > 4.2.7.1.2.1 The quantity of the event.
>
> > > > > 4.2.7.1.3 Updates the scoring table with each single max_potential
>
> > > > > 4.2.7.1.4 The Tinker sends the task_id to the Observer.
>
> > > > > > 4.2.7.1.4.1 The Observer calculates for each event the scoring.
>
> > > > > > 4.2.7.1.4.2 The Observer calculates for the hole task the scoring.
>
> > > > > > 4.2.7.1.4.3 The Observer sends the task_id to the Courier.
>
> > > 4.2.8 The Courier sends to each involved agent the task_id to inform them, "scoring done"
>
> > > > 4.2.8.1 Each involved agent now can see, which scoring they get.
>
> > > 4.2.8 The Courier sends the task_id to the Librarian
>
> > 4.3 The Librarian creates an output from the information of the task events.
>
> > 4.4 The Librarian sends the output to the user.
>
> 5 Repeat from 1.

---
