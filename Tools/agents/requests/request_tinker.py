def request_tinker(task_id):
    """
    This function is the entry point to the scoring.
    It is called from the courier after the sages approved the task.

    1. Get the task and the history.
    2. Based on the task and the amount of events, calculate a max_potential
    3. Apply the task related max_potenzial to the task
    4. Create for each event in the history an event related max_potencial score, based on the amount of information are applied
    5. Apply the event related max_potencial scores to there respective event
    6. Send the task id to the observer
    """
    pass
