"""
End-to-end tests for code review flow.

Tests complete code review process including review submission,
feedback handling, approval workflows, and iteration cycles.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import asyncio


class ReviewStatus(Enum):
    """Code review status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"


class CommentType(Enum):
    """Type of review comment."""
    GENERAL = "general"
    INLINE = "inline"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    NITPICK = "nitpick"
    BLOCKING = "blocking"


class ReviewDecision(Enum):
    """Reviewer decision."""
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    COMMENT = "comment"


class Severity(Enum):
    """Finding severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CodeChange:
    """Represents a code change in the review."""
    file_path: str
    old_content: str
    new_content: str
    line_start: int = 1
    line_end: int = 1


@dataclass
class ReviewComment:
    """A comment in a code review."""
    id: str
    author: str
    content: str
    comment_type: CommentType = CommentType.GENERAL
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    severity: Severity = Severity.INFO
    resolved: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    suggestion: Optional[str] = None

    def resolve(self) -> None:
        """Mark comment as resolved."""
        self.resolved = True


@dataclass
class ReviewRequest:
    """A code review request."""
    id: str
    title: str
    description: str
    author: str
    changes: list[CodeChange] = field(default_factory=list)
    reviewers: list[str] = field(default_factory=list)
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReviewIteration:
    """An iteration of the review process."""
    iteration_number: int
    comments: list[ReviewComment] = field(default_factory=list)
    decision: Optional[ReviewDecision] = None
    reviewer: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


class MockCodeAnalyzer:
    """Mock code analyzer for automated review."""

    def __init__(self):
        self.rules: dict[str, Severity] = {
            "unused_import": Severity.WARNING,
            "missing_docstring": Severity.INFO,
            "type_error": Severity.ERROR,
            "security_issue": Severity.CRITICAL
        }
        self._findings: dict[str, list[dict]] = {}

    def add_finding(self, file_path: str, finding: dict) -> None:
        """Add a finding for a file."""
        if file_path not in self._findings:
            self._findings[file_path] = []
        self._findings[file_path].append(finding)

    async def analyze(self, changes: list[CodeChange]) -> list[ReviewComment]:
        """Analyze code changes and return comments."""
        comments = []
        for i, change in enumerate(changes):
            file_findings = self._findings.get(change.file_path, [])
            for finding in file_findings:
                comment = ReviewComment(
                    id=f"auto-{i}-{len(comments)}",
                    author="automated-reviewer",
                    content=finding.get("message", "Issue found"),
                    comment_type=CommentType.INLINE,
                    file_path=change.file_path,
                    line_number=finding.get("line", 1),
                    severity=finding.get("severity", Severity.INFO)
                )
                comments.append(comment)
        return comments


class MockReviewer:
    """Mock human reviewer."""

    def __init__(self, name: str):
        self.name = name
        self._responses: dict[str, tuple[ReviewDecision, list[ReviewComment]]] = {}

    def set_response(
        self,
        review_id: str,
        decision: ReviewDecision,
        comments: list[ReviewComment]
    ) -> None:
        """Set response for a review."""
        self._responses[review_id] = (decision, comments)

    async def review(self, request: ReviewRequest) -> ReviewIteration:
        """Perform review."""
        decision, comments = self._responses.get(
            request.id,
            (ReviewDecision.COMMENT, [])
        )

        # Update comment authors
        for comment in comments:
            comment.author = self.name

        return ReviewIteration(
            iteration_number=1,
            comments=comments,
            decision=decision,
            reviewer=self.name
        )


class MockReviewWorkflow:
    """Complete review workflow manager."""

    def __init__(self):
        self.reviews: dict[str, ReviewRequest] = {}
        self.iterations: dict[str, list[ReviewIteration]] = {}
        self.analyzer = MockCodeAnalyzer()
        self.reviewers: dict[str, MockReviewer] = {}
        self._approval_rules: dict[str, int] = {"min_approvals": 1}

    def register_reviewer(self, reviewer: MockReviewer) -> None:
        """Register a reviewer."""
        self.reviewers[reviewer.name] = reviewer

    def set_approval_rules(self, min_approvals: int = 1) -> None:
        """Set approval rules."""
        self._approval_rules["min_approvals"] = min_approvals

    async def submit_review(self, request: ReviewRequest) -> ReviewRequest:
        """Submit a review request."""
        self.reviews[request.id] = request
        self.iterations[request.id] = []
        request.status = ReviewStatus.PENDING

        # Run automated analysis
        auto_comments = await self.analyzer.analyze(request.changes)
        if auto_comments:
            auto_iteration = ReviewIteration(
                iteration_number=0,
                comments=auto_comments,
                decision=None,
                reviewer="automated"
            )
            self.iterations[request.id].append(auto_iteration)

        return request

    async def request_review(
        self,
        review_id: str,
        reviewer_name: str
    ) -> Optional[ReviewIteration]:
        """Request review from a specific reviewer."""
        request = self.reviews.get(review_id)
        reviewer = self.reviewers.get(reviewer_name)

        if not request or not reviewer:
            return None

        request.status = ReviewStatus.IN_PROGRESS
        iteration = await reviewer.review(request)
        iteration.iteration_number = len(self.iterations[review_id]) + 1
        self.iterations[review_id].append(iteration)

        # Update status based on decision
        if iteration.decision == ReviewDecision.APPROVE:
            approvals = sum(
                1 for it in self.iterations[review_id]
                if it.decision == ReviewDecision.APPROVE
            )
            if approvals >= self._approval_rules["min_approvals"]:
                request.status = ReviewStatus.APPROVED
        elif iteration.decision == ReviewDecision.REQUEST_CHANGES:
            request.status = ReviewStatus.CHANGES_REQUESTED

        request.updated_at = datetime.now()
        return iteration

    async def add_comment(
        self,
        review_id: str,
        comment: ReviewComment
    ) -> bool:
        """Add a comment to a review."""
        if review_id not in self.reviews:
            return False

        # Add to latest iteration or create new one
        iterations = self.iterations[review_id]
        if iterations:
            iterations[-1].comments.append(comment)
        else:
            new_iteration = ReviewIteration(
                iteration_number=1,
                comments=[comment]
            )
            iterations.append(new_iteration)

        return True

    def resolve_comment(self, review_id: str, comment_id: str) -> bool:
        """Resolve a comment."""
        iterations = self.iterations.get(review_id, [])
        for iteration in iterations:
            for comment in iteration.comments:
                if comment.id == comment_id:
                    comment.resolve()
                    return True
        return False

    def get_blocking_comments(self, review_id: str) -> list[ReviewComment]:
        """Get all unresolved blocking comments."""
        blocking = []
        for iteration in self.iterations.get(review_id, []):
            for comment in iteration.comments:
                if (comment.comment_type == CommentType.BLOCKING and
                    not comment.resolved):
                    blocking.append(comment)
        return blocking

    async def merge(self, review_id: str) -> bool:
        """Attempt to merge a review."""
        request = self.reviews.get(review_id)
        if not request:
            return False

        if request.status != ReviewStatus.APPROVED:
            return False

        blocking = self.get_blocking_comments(review_id)
        if blocking:
            return False

        request.status = ReviewStatus.MERGED
        return True


# ============================================================================
# Test Classes
# ============================================================================

class TestReviewSubmission:
    """Tests for review submission."""

    @pytest.fixture
    def workflow(self) -> MockReviewWorkflow:
        """Create workflow."""
        return MockReviewWorkflow()

    @pytest.mark.asyncio
    async def test_submit_review(self, workflow: MockReviewWorkflow):
        """Test submitting a review request."""
        request = ReviewRequest(
            id="pr-1",
            title="Add feature",
            description="Adds new feature",
            author="developer"
        )

        result = await workflow.submit_review(request)

        assert result.status == ReviewStatus.PENDING
        assert "pr-1" in workflow.reviews

    @pytest.mark.asyncio
    async def test_submit_with_changes(self, workflow: MockReviewWorkflow):
        """Test submitting review with code changes."""
        changes = [
            CodeChange(
                file_path="src/main.py",
                old_content="",
                new_content="def hello(): pass"
            )
        ]
        request = ReviewRequest(
            id="pr-2",
            title="Add hello",
            description="Add hello function",
            author="dev",
            changes=changes
        )

        await workflow.submit_review(request)

        assert len(workflow.reviews["pr-2"].changes) == 1


class TestAutomatedAnalysis:
    """Tests for automated code analysis."""

    @pytest.fixture
    def workflow(self) -> MockReviewWorkflow:
        """Create workflow with findings."""
        wf = MockReviewWorkflow()
        wf.analyzer.add_finding("src/main.py", {
            "message": "Missing docstring",
            "line": 1,
            "severity": Severity.INFO
        })
        return wf

    @pytest.mark.asyncio
    async def test_automated_comments(self, workflow: MockReviewWorkflow):
        """Test automated analysis creates comments."""
        request = ReviewRequest(
            id="pr-auto",
            title="Test",
            description="Test auto review",
            author="dev",
            changes=[
                CodeChange("src/main.py", "", "def foo(): pass")
            ]
        )

        await workflow.submit_review(request)

        iterations = workflow.iterations["pr-auto"]
        assert len(iterations) > 0
        assert any(
            c.author == "automated-reviewer"
            for c in iterations[0].comments
        )


class TestReviewerWorkflow:
    """Tests for reviewer workflow."""

    @pytest.fixture
    def workflow(self) -> MockReviewWorkflow:
        """Create workflow with reviewer."""
        wf = MockReviewWorkflow()
        reviewer = MockReviewer("alice")
        reviewer.set_response("pr-rev", ReviewDecision.APPROVE, [])
        wf.register_reviewer(reviewer)
        return wf

    @pytest.mark.asyncio
    async def test_request_review(self, workflow: MockReviewWorkflow):
        """Test requesting a review."""
        request = ReviewRequest(
            id="pr-rev",
            title="Review Me",
            description="Need review",
            author="dev"
        )
        await workflow.submit_review(request)

        iteration = await workflow.request_review("pr-rev", "alice")

        assert iteration is not None
        assert iteration.reviewer == "alice"
        assert iteration.decision == ReviewDecision.APPROVE

    @pytest.mark.asyncio
    async def test_approval_updates_status(self, workflow: MockReviewWorkflow):
        """Test approval updates review status."""
        request = ReviewRequest(
            id="pr-rev",
            title="Approve Me",
            description="Ready for approval",
            author="dev"
        )
        await workflow.submit_review(request)

        await workflow.request_review("pr-rev", "alice")

        assert workflow.reviews["pr-rev"].status == ReviewStatus.APPROVED


class TestChangesRequested:
    """Tests for changes requested workflow."""

    @pytest.fixture
    def workflow(self) -> MockReviewWorkflow:
        """Create workflow with critical reviewer."""
        wf = MockReviewWorkflow()
        reviewer = MockReviewer("bob")
        comments = [
            ReviewComment(
                id="c1",
                author="bob",
                content="Fix this",
                comment_type=CommentType.BLOCKING,
                severity=Severity.ERROR
            )
        ]
        reviewer.set_response("pr-fix", ReviewDecision.REQUEST_CHANGES, comments)
        wf.register_reviewer(reviewer)
        return wf

    @pytest.mark.asyncio
    async def test_changes_requested_status(self, workflow: MockReviewWorkflow):
        """Test changes requested updates status."""
        request = ReviewRequest(
            id="pr-fix",
            title="Needs Work",
            description="Incomplete",
            author="dev"
        )
        await workflow.submit_review(request)
        await workflow.request_review("pr-fix", "bob")

        assert workflow.reviews["pr-fix"].status == ReviewStatus.CHANGES_REQUESTED


class TestCommentManagement:
    """Tests for comment management."""

    @pytest.fixture
    def workflow(self) -> MockReviewWorkflow:
        """Create workflow."""
        return MockReviewWorkflow()

    @pytest.mark.asyncio
    async def test_add_comment(self, workflow: MockReviewWorkflow):
        """Test adding a comment."""
        request = ReviewRequest(
            id="pr-comment",
            title="Comment Test",
            description="Test",
            author="dev"
        )
        await workflow.submit_review(request)

        comment = ReviewComment(
            id="c1",
            author="reviewer",
            content="Nice work!"
        )
        result = await workflow.add_comment("pr-comment", comment)

        assert result is True

    @pytest.mark.asyncio
    async def test_resolve_comment(self, workflow: MockReviewWorkflow):
        """Test resolving a comment."""
        request = ReviewRequest(id="pr-res", title="Resolve", description="", author="dev")
        await workflow.submit_review(request)

        comment = ReviewComment(id="c-res", author="reviewer", content="Fix this")
        await workflow.add_comment("pr-res", comment)

        result = workflow.resolve_comment("pr-res", "c-res")
        assert result is True


class TestMergeWorkflow:
    """Tests for merge workflow."""

    @pytest.fixture
    def approved_workflow(self) -> MockReviewWorkflow:
        """Create workflow with approved PR."""
        wf = MockReviewWorkflow()
        reviewer = MockReviewer("approver")
        reviewer.set_response("pr-merge", ReviewDecision.APPROVE, [])
        wf.register_reviewer(reviewer)
        return wf

    @pytest.mark.asyncio
    async def test_merge_approved_pr(self, approved_workflow: MockReviewWorkflow):
        """Test merging an approved PR."""
        request = ReviewRequest(
            id="pr-merge",
            title="Ready to Merge",
            description="All good",
            author="dev"
        )
        await approved_workflow.submit_review(request)
        await approved_workflow.request_review("pr-merge", "approver")

        result = await approved_workflow.merge("pr-merge")

        assert result is True
        assert approved_workflow.reviews["pr-merge"].status == ReviewStatus.MERGED

    @pytest.mark.asyncio
    async def test_cannot_merge_pending(self, approved_workflow: MockReviewWorkflow):
        """Test cannot merge pending PR."""
        request = ReviewRequest(
            id="pr-pending",
            title="Not Ready",
            description="Still pending",
            author="dev"
        )
        await approved_workflow.submit_review(request)

        result = await approved_workflow.merge("pr-pending")

        assert result is False


class TestBlockingComments:
    """Tests for blocking comment handling."""

    @pytest.fixture
    def workflow(self) -> MockReviewWorkflow:
        """Create workflow."""
        wf = MockReviewWorkflow()
        reviewer = MockReviewer("blocker")
        comments = [
            ReviewComment(
                id="block-1",
                author="blocker",
                content="Security issue",
                comment_type=CommentType.BLOCKING,
                severity=Severity.CRITICAL
            )
        ]
        reviewer.set_response("pr-block", ReviewDecision.REQUEST_CHANGES, comments)
        wf.register_reviewer(reviewer)
        return wf

    @pytest.mark.asyncio
    async def test_get_blocking_comments(self, workflow: MockReviewWorkflow):
        """Test getting blocking comments."""
        request = ReviewRequest(
            id="pr-block",
            title="Has Blockers",
            description="",
            author="dev"
        )
        await workflow.submit_review(request)
        await workflow.request_review("pr-block", "blocker")

        blocking = workflow.get_blocking_comments("pr-block")

        assert len(blocking) == 1
        assert blocking[0].severity == Severity.CRITICAL

    @pytest.mark.asyncio
    async def test_cannot_merge_with_blockers(self, workflow: MockReviewWorkflow):
        """Test cannot merge with unresolved blockers."""
        request = ReviewRequest(id="pr-block", title="Blocked", description="", author="dev")
        await workflow.submit_review(request)
        # Manually set to approved to test blocker check
        workflow.reviews["pr-block"].status = ReviewStatus.APPROVED

        result = await workflow.merge("pr-block")

        assert result is False


class TestMultipleReviewers:
    """Tests for multiple reviewer workflow."""

    @pytest.fixture
    def multi_reviewer_workflow(self) -> MockReviewWorkflow:
        """Create workflow requiring multiple approvals."""
        wf = MockReviewWorkflow()
        wf.set_approval_rules(min_approvals=2)

        alice = MockReviewer("alice")
        alice.set_response("pr-multi", ReviewDecision.APPROVE, [])
        wf.register_reviewer(alice)

        bob = MockReviewer("bob")
        bob.set_response("pr-multi", ReviewDecision.APPROVE, [])
        wf.register_reviewer(bob)

        return wf

    @pytest.mark.asyncio
    async def test_requires_multiple_approvals(
        self,
        multi_reviewer_workflow: MockReviewWorkflow
    ):
        """Test PR requires multiple approvals."""
        request = ReviewRequest(
            id="pr-multi",
            title="Multi Review",
            description="Needs 2 approvals",
            author="dev"
        )
        await multi_reviewer_workflow.submit_review(request)

        # First approval
        await multi_reviewer_workflow.request_review("pr-multi", "alice")
        assert multi_reviewer_workflow.reviews["pr-multi"].status != ReviewStatus.APPROVED

        # Second approval
        await multi_reviewer_workflow.request_review("pr-multi", "bob")
        assert multi_reviewer_workflow.reviews["pr-multi"].status == ReviewStatus.APPROVED
