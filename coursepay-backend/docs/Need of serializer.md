Because Django models and Python objects are **not directly understandable by APIs or frontend apps**.

A **Serializer** acts like a **translator + validator** between:

* Python/Django objects
  ⬇
* JSON data sent over HTTP

Think of it this way:

```text
Frontend / Mobile App  <--JSON-->  Serializer  <--Python Objects--> Django Models
```

Without serializers, Django REST APIs would be messy very quickly.

---

# First Problem: Django Objects Cannot Be Sent as JSON

Suppose you have a model:

```python
class Course(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
```

And inside a view:

```python
course = Course.objects.first()

return Response(course)
```

This fails because:

```python
<Course object (1)>
```

is a Python object, not JSON.

But APIs communicate using JSON:

```json
{
    "title": "Django",
    "price": 999
}
```

Serializer converts model → JSON.

---

# What Serializer Actually Does

A serializer mainly does 4 jobs:

---

# 1. Convert Model → JSON (Serialization)

```python
serializer = CourseSerializer(course)

serializer.data
```

Output:

```json
{
    "id": 1,
    "title": "Django",
    "price": 999
}
```

This is called:

# Serialization

Python object → JSON-compatible data

---

# 2. Convert JSON → Model Data (Deserialization)

Suppose frontend sends:

```json
{
    "title": "Python",
    "price": 500
}
```

Serializer converts this JSON into validated Python data.

```python
serializer = CourseSerializer(data=request.data)

if serializer.is_valid():
    serializer.save()
```

This becomes a real database object.

---

# 3. Validation

Serializer is also a validator.

Example:

```python
class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Price cannot be negative"
            )
        return value
```

Now bad input is rejected BEFORE database save.

---

# 4. Security / Field Control

Suppose model has:

```python
class Course(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
    admin_notes = models.TextField()
```

You may NOT want frontend users to see:

```python
admin_notes
```

Serializer controls exposure:

```python
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["title", "price"]
```

This is VERY important in real APIs.

---

# Why Not Just Use `model_to_dict()`?

Good question.

Django already has:

```python
from django.forms.models import model_to_dict
```

But serializers are much more powerful.

| Feature                 | model_to_dict | Serializer |
| ----------------------- | ------------- | ---------- |
| Convert model to dict   | ✅             | ✅          |
| JSON support            | ❌             | ✅          |
| Validation              | ❌             | ✅          |
| Nested objects          | ❌             | ✅          |
| API request parsing     | ❌             | ✅          |
| Field permissions       | ❌             | ✅          |
| Custom logic            | ❌             | ✅          |
| Works with DRF Response | ❌             | ✅          |

---

# Real Industry Perspective

In real backend systems:

Serializer becomes the:

* API contract
* validation layer
* transformation layer
* security boundary

Senior engineers rely heavily on serializers.

---

# Simple Mental Model

Think:

```text
Model = Database Structure

Serializer = API Structure
```

Very important distinction.

Your DB structure and API structure are often different.

Example:

Database:

```text
first_name
last_name
```

API may want:

```json
{
   "full_name": "Shantanu Kumar"
}
```

Serializer handles this transformation.

---

# Full Example

## Model

```python
class Course(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField()
```

---

## Serializer

```python
from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"
```

---

## View

```python
@api_view(["GET"])
def get_courses(request):

    courses = Course.objects.all()

    serializer = CourseSerializer(courses, many=True)

    return Response(serializer.data)
```

---

# Flow Internally

```text
DB Rows
   ↓
Django Model Objects
   ↓
Serializer
   ↓
Python Dict
   ↓
JSON Response
   ↓
Frontend
```

And reverse for POST requests.

---

# Why Serializer Is a Big Deal in DRF

Without serializer:

* manual validation
* manual JSON conversion
* manual field filtering
* manual nested handling
* repetitive code everywhere

Serializer centralizes all of this cleanly.

That’s why Django REST Framework is built around serializers.
