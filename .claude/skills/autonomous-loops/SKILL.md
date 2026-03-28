---
name: autonomous-loops
description: Loop patterns from simple sequential pipelines to RFC-driven DAG orchestration. De-sloppify pattern, decomposition strategies, and loop maintenance. Build reliable agent workflows.
origin: ECC
version: 1.5
---

# Autonomous Loops Skill

Patterns for building reliable, composable agent loops from simple to complex.

## When to Activate

- Building multi-step agent workflows
- Orchestrating complex API interactions
- Implementing long-running tasks
- Decomposing large problems into sub-tasks
- Debugging agent decision patterns
- Improving loop observability

## Loop Hierarchy

### Level 1: Simple Sequential Loop

Single agent makes decision, acts, observes result.

```python
async def process_order(order_id: str):
    while True:
        order = await get_order(order_id)

        if order.status == "pending":
            await process_payment(order)
        elif order.status == "paid":
            await ship_order(order)
        elif order.status == "shipped":
            break
        else:
            raise ValueError(f"Unknown status: {order.status}")
```

Properties:
- Single agent, single loop
- Clear termination condition
- Easy to debug and test
- Limited to simple workflows

### Level 2: Multi-Step Pipeline

Decompose into discrete, reusable steps.

```python
from dataclasses import dataclass
from enum import Enum

class OrderStep(Enum):
    VALIDATE = "validate"
    PROCESS_PAYMENT = "process_payment"
    SHIP = "ship"
    COMPLETE = "complete"

@dataclass
class OrderContext:
    order_id: str
    status: OrderStep
    payment_result: dict = None
    tracking_number: str = None

async def process_order(order_id: str):
    ctx = OrderContext(order_id=order_id, status=OrderStep.VALIDATE)

    while ctx.status != OrderStep.COMPLETE:
        if ctx.status == OrderStep.VALIDATE:
            ctx = await validate_order(ctx)
        elif ctx.status == OrderStep.PROCESS_PAYMENT:
            ctx = await process_payment(ctx)
        elif ctx.status == OrderStep.SHIP:
            ctx = await ship_order(ctx)
        else:
            raise ValueError(f"Unknown step: {ctx.status}")

    return ctx

async def validate_order(ctx: OrderContext) -> OrderContext:
    order = await get_order(ctx.order_id)
    if not order.payment_method:
        raise ValueError("Missing payment method")
    ctx.status = OrderStep.PROCESS_PAYMENT
    return ctx

async def process_payment(ctx: OrderContext) -> OrderContext:
    result = await charge_card(ctx.order_id)
    ctx.payment_result = result
    ctx.status = OrderStep.SHIP
    return ctx

async def ship_order(ctx: OrderContext) -> OrderContext:
    tracking = await create_shipment(ctx.order_id)
    ctx.tracking_number = tracking.number
    ctx.status = OrderStep.COMPLETE
    return ctx
```

Properties:
- Clearer separation of concerns
- Each step is testable independently
- Context carries state through pipeline
- Easy to add/remove steps

### Level 3: Decision Graph (DAG)

Steps branch based on conditions, multiple paths possible.

```python
from enum import Enum

class OrderPath(Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    DIGITAL = "digital"
    REFUND = "refund"

@dataclass
class OrderContext:
    order_id: str
    step: str
    path: OrderPath = None
    order: dict = None
    payment_result: dict = None

async def process_order_dag(order_id: str):
    ctx = OrderContext(order_id=order_id, step="fetch")

    while ctx.step != "complete":
        ctx = await execute_step(ctx)

    return ctx

async def execute_step(ctx: OrderContext) -> OrderContext:
    if ctx.step == "fetch":
        ctx.order = await get_order(ctx.order_id)
        ctx.step = "route"

    elif ctx.step == "route":
        # Branching based on order type
        if ctx.order["type"] == "digital":
            ctx.path = OrderPath.DIGITAL
            ctx.step = "deliver_digital"
        elif ctx.order["type"] == "physical":
            if ctx.order.get("is_express"):
                ctx.path = OrderPath.EXPRESS
                ctx.step = "validate_express"
            else:
                ctx.path = OrderPath.STANDARD
                ctx.step = "validate_standard"

    elif ctx.step == "validate_standard":
        await validate_address(ctx.order)
        ctx.step = "process_payment"

    elif ctx.step == "validate_express":
        if not await can_ship_express(ctx.order):
            ctx.step = "validate_standard"  # fallback
        else:
            ctx.step = "process_payment"

    elif ctx.step == "process_payment":
        ctx.payment_result = await charge_card(ctx.order_id)
        if ctx.path == OrderPath.DIGITAL:
            ctx.step = "deliver_digital"
        else:
            ctx.step = "ship_physical"

    elif ctx.step == "ship_physical":
        await create_shipment(ctx.order_id)
        ctx.step = "complete"

    elif ctx.step == "deliver_digital":
        await send_download_link(ctx.order_id)
        ctx.step = "complete"

    return ctx
```

Properties:
- Multiple execution paths
- Conditional branching
- Recovery paths (fallbacks)
- More complex to trace

### Level 4: RFC-Driven DAG

Agent proposes next steps via RFC (Request for Comment), human/system approves.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class RFCStatus(Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"

@dataclass
class RFC:
    id: str
    step: str
    reason: str
    proposed_action: str
    status: RFCStatus = RFCStatus.PROPOSED
    approver: Optional[str] = None
    approved_at: Optional[str] = None

async def process_order_rfc(order_id: str):
    ctx = OrderContext(order_id=order_id, step="start")
    rfc_queue = []

    while ctx.step != "complete":
        # Agent proposes next action
        rfc = await propose_step(ctx)
        rfc_queue.append(rfc)

        # Wait for approval
        approved_rfc = await wait_for_approval(rfc)

        if approved_rfc.status == RFCStatus.APPROVED:
            ctx = await execute_rfc(ctx, approved_rfc)
        elif approved_rfc.status == RFCStatus.REJECTED:
            ctx = await recover_from_rejection(ctx, approved_rfc)

    return ctx, rfc_queue

async def propose_step(ctx: OrderContext) -> RFC:
    if ctx.step == "start":
        return RFC(
            id=f"rfc-{ctx.order_id}-1",
            step="fetch_order",
            reason="Need to retrieve order details",
            proposed_action="Query order database"
        )
    elif ctx.step == "decision_point":
        order = ctx.order
        if order["total"] > 1000:
            return RFC(
                id=f"rfc-{ctx.order_id}-2",
                step="manual_review",
                reason="Order exceeds $1000, requires manual review",
                proposed_action="Send to fraud team for verification"
            )
        else:
            return RFC(
                id=f"rfc-{ctx.order_id}-2",
                step="process_payment",
                reason="Order approved for auto-processing",
                proposed_action="Charge payment method"
            )
```

Properties:
- Agent proposes, human/system approves
- Full decision trail documented (RFCs)
- Recoverable from rejections
- Most transparent and auditable

## De-Sloppify Pattern

Clean up messy, error-prone loops.

### Before (Sloppy)

```python
async def process_user_uploads():
    # No clear state, no recovery
    users = await db.list_users()

    for user in users:
        try:
            files = await s3.list_files(user.id)
            for file in files:
                # Missing validation
                await process_file(file)
                # No tracking of completion
        except Exception as e:
            # Silent failure
            print(f"Error: {e}")
```

### After (De-Sloppified)

```python
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class FileProcessStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class ProcessResult:
    file_id: str
    status: FileProcessStatus
    error: Optional[str] = None
    processed_at: Optional[datetime] = None

async def process_user_uploads():
    users = await db.list_users()
    all_results = []

    for user in users:
        results = await process_user_files(user.id)
        all_results.extend(results)

    # Return results for observability
    return all_results

async def process_user_files(user_id: str) -> list[ProcessResult]:
    results = []

    try:
        files = await s3.list_files(user_id)
    except Exception as e:
        logger.error(f"Failed to list files for user {user_id}: {e}")
        return results

    for file in files:
        result = await process_file_safe(user_id, file)
        results.append(result)

    return results

async def process_file_safe(user_id: str, file) -> ProcessResult:
    result = ProcessResult(
        file_id=file.id,
        status=FileProcessStatus.PENDING
    )

    try:
        # Validate before processing
        if not validate_file(file):
            result.status = FileProcessStatus.FAILED
            result.error = "File validation failed"
            return result

        result.status = FileProcessStatus.PROCESSING
        await process_file(file)
        result.status = FileProcessStatus.SUCCESS
        result.processed_at = datetime.now()

    except Exception as e:
        logger.error(f"Error processing file {file.id}: {e}")
        result.status = FileProcessStatus.FAILED
        result.error = str(e)

    return result
```

Key improvements:
- Explicit state tracking
- All paths handled
- Results returned for observability
- Errors logged, not swallowed
- Recoverable from individual failures

## Loop Observability

Make loops debuggable:

```python
from typing import Callable, TypeVar, Generic

T = TypeVar('T')

class ObservableLoop(Generic[T]):
    def __init__(self, name: str, logger=None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.iterations = []

    async def run(self, initial_state: T, step_fn: Callable) -> T:
        state = initial_state
        iteration = 0

        while True:
            iteration += 1
            self.logger.info(f"{self.name} iteration {iteration}: {state}")

            # Execute step, capture result
            try:
                next_state, should_continue = await step_fn(state)
                self.iterations.append({
                    "iteration": iteration,
                    "input": state,
                    "output": next_state,
                    "status": "success"
                })
            except Exception as e:
                self.logger.error(f"{self.name} iteration {iteration} failed: {e}")
                self.iterations.append({
                    "iteration": iteration,
                    "input": state,
                    "error": str(e),
                    "status": "failed"
                })
                raise

            state = next_state
            if not should_continue:
                break

        return state

    def get_trace(self) -> list[dict]:
        return self.iterations
```

Usage:
```python
loop = ObservableLoop("order_processing")
result = await loop.run(order_ctx, order_step_fn)
print(loop.get_trace())  # Full execution trace
```

## Best Practices

- [x] Explicit state (enum, dataclass)
- [x] Clear termination conditions
- [x] Each step is idempotent or tracked
- [x] Errors logged and handled
- [x] Results observable (no silent failures)
- [x] Easy to test individual steps
- [x] De-sloppify as complexity grows
- [x] Use RFC pattern for critical decisions
- [x] Instrument loops for observability
