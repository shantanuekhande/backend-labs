# Why Payment Systems Use “Order First → Payment Later”

This is not an unnecessary extra step.
It is the **standard architecture used in real payment systems** because it provides:

* security
* consistency
* auditability
* retry safety
* payment tracking

The backend must create an **Order** before the actual payment starts.

---

# The Core Idea

The browser/mobile app should NEVER directly control:

* final amount
* transaction identity
* payment state

Those must be controlled by the backend.

So the flow becomes:

```text id="1t6im6"
Frontend
   ↓
Create Order (Backend)
   ↓
Backend verifies everything
   ↓
Razorpay Order Created
   ↓
Frontend gets razorpay_order_id
   ↓
User Pays
```

This is called the:

# Order → Payment Handshake

---

# 1. Server Becomes the Source of Truth

Without creating an order first, the frontend could manipulate payment data.

---

## Problem

Suppose frontend sends:

```json id="t8a52f"
{
   "course_id": 10,
   "amount": 1
}
```

A malicious user can modify this using:

* browser devtools
* intercepted API calls
* Postman
* custom scripts

Now your ₹10,000 course becomes ₹1.

---

## Solution

Backend ignores frontend pricing completely.

Instead:

```python id="0q1l8u"
course = Course.objects.get(id=course_id)
amount = course.price
```

The backend fetches the real amount from DB and creates a Razorpay order for exactly that amount.

Now the client cannot tamper with pricing.

---

# 2. Preventing “Ghost Payments”

A payment gateway may successfully collect money even if your frontend crashes.

---

## Scenario

Imagine this sequence:

```text id="4o10p3"
User pays successfully
        ↓
Internet disconnects
        ↓
Frontend never receives success response
```

Now:

* Razorpay has the money
* your backend has no tracking record
* user says: “Money deducted but course not unlocked”

This becomes a support nightmare.

---

## Solution

Create internal order BEFORE payment begins:

```python id="pbbjlwm"
Order.objects.create(
    status="PENDING"
)
```

Now the backend already has a record:

```text id="xuqut8"
"We are expecting a payment attempt for Order #101"
```

Even if frontend crashes, webhook callbacks can still update the order later.

---

# 3. Preventing Duplicate Charges (Idempotency)

Networks fail frequently.

Users refresh pages.
Users double-click buttons.

Without order tracking, duplicate payments become possible.

---

## Problem

User clicks:

```text id="9fpp4t"
Pay
```

Network hangs.

User clicks again.

Gateway may create:

```text id="1wvsux"
2 separate payment transactions
```

Result:

```text id="9iwt9x"
User charged twice
```

---

## Solution

The `razorpay_order_id` acts as a stable transaction identity.

Every retry references the SAME order:

```text id="5hjlwm"
Order #101
```

instead of creating new uncontrolled transactions.

This concept is called:

# Idempotency

Meaning:

```text id="c0z0uu"
Repeating the same request should not create duplicate effects.
```

Extremely important in payment systems.

---

# 4. Pre-payment Validation

Before accepting money, backend must verify business rules.

Examples:

* Is the course active?
* Is the user authenticated?
* Does the user already own the course?
* Is the course discontinued?
* Is coupon still valid?

These checks belong on the server.

Not in frontend JavaScript.

---

# 5. Auditability and Payment Tracking

Real systems must track the FULL lifecycle of a payment.

Not just successful payments.

---

# Typical Lifecycle

```text id="f2m4jv"
PENDING
   ↓
SUCCESS
```

or:

```text id="dchbvf"
PENDING
   ↓
FAILED
```

or:

```text id="cqjlwm"
PENDING
   ↓
ABANDONED
```

Companies analyze:

* failed payments
* retry rates
* abandoned checkouts
* fraud patterns
* refund history

This requires a persistent Order/Payment record from the beginning.

---

# Why Two Separate Entities Exist

Usually systems maintain BOTH:

| Entity                | Purpose                      |
| --------------------- | ---------------------------- |
| Internal Order        | Your business transaction    |
| Payment Gateway Order | External payment transaction |

Your backend must map them together.

Example:

| Internal Order | Razorpay Order |
| -------------- | -------------- |
| 101            | order_abcd123  |

This mapping is critical during:

* webhook handling
* payment verification
* refunds
* reconciliation

---

# Real Mental Model

Think of it like signing a contract before transferring money.

---

# Step 1 — Agreement

Backend and Razorpay agree:

```text id="j2nls4"
"We are attempting payment
for Order #101 worth ₹10,000."
```

Razorpay generates:

```text id="74b04y"
razorpay_order_id
```

---

# Step 2 — Execution

User uses that order ID to complete payment.

---

# Why This Architecture Exists

Those extra milliseconds provide:

* security
* fraud prevention
* retry safety
* consistency
* recoverability
* audit logs
* backend control

Without this architecture, payment systems become unreliable very quickly.

---

# Final Core Principle

```text id="5sm2yn"
Never trust the frontend
for financial transactions.
```

Frontend is only the UI.

Backend must control:

* pricing
* transaction creation
* payment verification
* state management

That is why professional payment systems always follow:

# Order First → Payment Second
