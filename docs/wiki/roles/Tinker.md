# ⚙️ The Tinker (Quantity Evaluator)
![Tinker](../images/tinker.svg)

[⬅️ Back to Home](../Home.md)

The Tinker is the "Blind Judge" of effort. They assess the workload based purely on the volume of the produced result.

## The Blind Assessment
*   **Input**: The Tinker receives **only the Output** of an agent. They have NO knowledge of the original request or the input context.
*   **Logic**: Based on the quantity (e.g., number of rows, length of text, complexity of the structure), the Tinker determines the **Max Potential Points** for the task.

## Responsibilities
*   **Potential Assignment**: Setting the scoring ceiling for individual agent tasks.
*   **Global Task-Score**: Evaluating the entire request cycle (number of steps, courier decisions, event density) to provide the 40% component of the Global Score.

## Purpose
This prevents "context bias." The Tinker doesn't care if the answer is right; they only care how much effort the work represents.