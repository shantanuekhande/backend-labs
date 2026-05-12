That is a very observant question. In a standard Django project, you would typically use a **Foreign Key** to the User model: `user = models.ForeignKey(User, ...)`.

However, in **Payment Systems** and **Order Management**, we sometimes use `user_email` (or "denormalized" data) for three specific architectural reasons:

### 1. Guest Checkout Support

If you want to allow users to buy a course without creating a full account first (Guest Checkout), you can't link to a `User` ID because the user doesn't exist in your database yet. Collecting the `user_email` in the `Order` model allows you to:

* Send the payment link/receipt to that email.
* Create the actual `User` account **after** the payment is successful.

### 2. The "Point-in-Time" Record (Audit Trail)

Users change their profiles. A user might change their primary email address next year.

* If you only link to a `User` ID, and the user changes their email, your old 2024 tax/invoice records will show the **new** email.
* By saving the `user_email` directly on the `Order` at the moment of purchase, you have a permanent, unchangeable record of who bought the course and where the receipt was sent.

### 3. Decoupling for "Order Integrity"

In high-level system design, we try to keep the **Order** as a standalone "Contract."
If you accidentally delete a User from your database, a `PROTECT` or `CASCADE` rule on a Foreign Key might interfere with your financial records. Storing the email string ensures that even if the User entity is modified or deleted, the **Financial Record** (The Order) remains intact for your reconciliation jobs.

---
