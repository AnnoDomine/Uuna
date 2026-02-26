# 📚 The Librarian

![Librarian](../images/librarian.svg)

[⬅️ Back to Home](../Home.md)

The Librarian is the primary interface between the human user and the AI Library System. They represent the "knowledgeable face" of the operation.

## Responsibilities

- **Task Ownership**: The Librarian is the only role that creates new Tasks. They are the "owner" of the user's quest for information.
- **User Engagement**: Greets the user and interprets natural language queries.
- **Knowledge Synthesis**: Takes information verified by the Sages and transforms it into a coherent, helpful answer for the user.
- **Gap Detection**: Checks the `ai_discoveries` and `global_knowledge` tables to see if the requested information is already known.
- **Task Initialization**: If information is missing or the user wants to "teach" the AI something better, the Librarian initializes a new Research Task.

## Workflow

1. Receive query.
2. Search local knowledge.
3. If found: Present answer.
4. If not found: Call **`library_create_task`** and hand over the ID to the **Courier**.
5. Wait for notification of completion.

## API Interface

- **Permissions**: Read/Write (Tasks), Read (Global Knowledge).
- **Primary Tool**: `library_create_task(query, builds[])`.
