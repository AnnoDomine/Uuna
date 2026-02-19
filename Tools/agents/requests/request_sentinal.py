def request_sentinel(task_id: int, event_id: int):
    """
    This function handles the sentinel flow.

    1. Get the event
    2. Loop till event is finished (max 5 times):
    2.1 Decide based on the request which tool is used
    2.2 Use the tool
    2.3 Check if the event is finished
    3. Create new event with output of all tools
    4. Send new event id to courier

    """
    pass
