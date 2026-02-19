def request_observer(task_id):
    """
    This function handles the flow for the observer.

    1. Get the task
    2. Take the history and decide for every single event in the history how much points this event gain.
        - ADDITIONAL: Because of amount of events, which could be relative huge, we split the events into blocks by role
        - CONTEXT: As we block by role, we can role specified add the information how this role is to evaluate the points
        - QUEUE: We can already create all related information into an queue first, befor we serve the information
        - LENGTH: Beside split into role based tasks, we split the amount of information, so the event block should not be more than 1000 characters length.
            1. To prevent the context, we calculate the length of the context dynamicly while filling the queue
            2. If the have the case, one single event would already over the 1000 character size, it will be applied as a single event
        - STORE: After every request, the scores will be stored
        - NEXT: Now the next item in the queue will be scored.
    3. As the observer now scored the events and knows the overview, the observer gain the hole task to evaluate the task points
    4. If everything is done, the observer stores the task points.
    5. The observer sends the task id to every involved agent. (Calls a function, which sends the information about the scoring to the agents)
    """
    pass
