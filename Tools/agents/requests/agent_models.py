from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from Tools.agents.get_agent_skill_set import Agents

# --- Courier Models ---
class SpecialistSelection(BaseModel):
    specialist: Agents = Field(..., description="The name of the next specialist to handle the task.")

# --- Librarian Models ---
class LibrarianSummary(BaseModel):
    summary: str = Field(..., description="The comprehensive summary of all researched information.")

class LibrarianResponse(BaseModel):
    knowledge: str = Field(..., description="The summarized knowledge found in the internal base, or 'None' if nothing relevant exists.")
    confidence: int = Field(..., description="Confidence score from 0 to 100 regarding the quality of the information.", ge=0, le=100)
    needs_more_research: bool = Field(..., description="True if the internal knowledge is insufficient and a deep archive search is required.")

# --- Sages Models ---
class ApprovalStatus(str, Enum):
    APPROVED = "approved"
    REVOKED = "revoked"

class SageVerdict(BaseModel):
    approval: ApprovalStatus = Field(..., description="Verdict on the task logic.")
    context: str = Field(..., description="The rationale or instructions for the next steps.")

# --- Observer Models ---
class EventEvaluation(BaseModel):
    event_id: str = Field(..., description="The UUID of the event.")
    quality_score: int = Field(..., description="The awarded quality points (0 to Max Potential).", ge=0)
    honesty_rating: str = Field(..., description="Rating of the agent's honesty regarding their confidence (e.g., 'Excellent', 'Fair', 'Poor').")
    feedback: str = Field(..., description="Qualitative feedback for the agent.")

class ObserverVerdict(BaseModel):
    evaluations: List[EventEvaluation] = Field(..., description="Detailed evaluation for each event in the task history.")
    audit_status: str = Field(..., description="Overall quality audit result (e.g., 'EXCELLENT', 'GOOD', 'FAIR', 'POOR').")
    overall_summary: str = Field(..., description="A comprehensive summary of the research quality and findings.")

class AgentLesson(BaseModel):
    role: Agents = Field(..., description="The role of the agent who learned the lesson.")
    lesson: str = Field(..., description="A concise, factual statement of what was learned or improved (e.g., 'Table X column Y refers to Z').")
    quality_score: int = Field(..., description="The quality score associated with this lesson (0-100).", ge=0, le=100)

class ResearchLearning(BaseModel):
    lessons: List[AgentLesson] = Field(..., description="List of lessons learned by the agents during this task.")

# --- Tinker Models ---
class EventPotential(BaseModel):
    event_id: str = Field(..., description="The UUID of the event.")
    potential_score: int = Field(..., description="The calculated potential score (difficulty) for this event.", ge=0, le=1000)
    reasoning: str = Field(..., description="A brief explanation why this score was assigned.")

class TinkerAssessment(BaseModel):
    assessments: List[EventPotential] = Field(..., description="List of potential scores for each task event.")

# --- Expedition Group Models ---
class LoreResearchStatus(BaseModel):
    is_finished: bool = Field(..., description="True if the lore context has been fully established.")
    reason: str = Field(..., description="Explanation of what was found and why it's sufficient or what's missing.")

# --- Sentinel Models ---
class SecurityAuditStatus(BaseModel):
    is_finished: bool = Field(..., description="True if the data has been fully audited and sanitized.")
    security_verdict: str = Field(..., description="The final security assessment (e.g., 'CLEAN', 'SENSITIVE_DATA_REDACTED', 'FLAGGED').")
    reason: str = Field(..., description="Explanation of the findings and actions taken.")
