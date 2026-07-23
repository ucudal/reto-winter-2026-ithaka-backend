# 1. Domain Classes (Entities)

> Reflects the SQLAlchemy models implemented in `app/core/models/`.

## Core process

**Cohort** — `id`, `year`, `semester`, `start_date`, `end_date` *(nullable)*, `status` *(default: "Active")*, `notes` *(nullable)*
→ relationships: `groups`, `stages`

**Group** — `id`, `name`, `cohort_id` → Cohort, `current_stage_id` → Stage *(nullable)*, `idea` *(nullable)*, `major` *(nullable)*, `status` *(default: "Active")*, `business_tutor_id` → Tutor *(nullable)*, `technical_tutor_id` → Tutor *(nullable)*
→ relationships: `cohort`, `current_stage`, `students`, `meetings`, `deliverables`, `business_tutor`, `technical_tutor`, `documents`

**Student** — `id`, `user_id` → User *(nullable)*, `name`, `email` *(unique)*, `major` *(nullable)*, `group_id` → Group *(nullable)*
→ relationships: `user`, `group`

**Tutor** — `id`, `user_id` → User *(nullable)*, `name`, `role` *(enum: Business | Technical)*, `specialty` *(nullable)*, `max_capacity` *(default: 0)*, `availability` *(nullable)*, `status` *(default: "Active")*
→ relationships: `user`, `groups_as_business_tutor`, `groups_as_technical_tutor`, `meetings`, `comments`

**Stage** — `id`, `cohort_id` → Cohort, `name`, `order`, `key_dates` *(JSONB, nullable — list of `{description, date}`)*
→ relationships: `cohort`, `groups`, `deliverables`, `support_materials`

**Meeting** — `id`, `group_id` → Group, `tutor_ids` *(JSONB list of tutor ids — una reunión puede tener uno o más tutores)*, `date` *(datetime with tz)*, `participants` *(JSONB list of ids, nullable)*, `notes` *(nullable)*, `next_steps` *(nullable)*, `hours_spent` *(nullable)*, `links` *(JSONB list of `{type, url}`, nullable)*
→ relationships: `group`

**Deliverable** — `id`, `group_id` → Group, `stage_id` → Stage, `expected_date`, `status` *(default: "Pending")*
→ relationships: `group`, `stage`, `documents` *(derivada vía `Document.entity_type='Deliverable'`)*, `comments`

**Comment** — `id`, `tutor_id` → Tutor, `deliverable_id` → Deliverable, `content`
→ relationships: `tutor`

**Document** — `id`, `entity_type` *(enum: Group | Meeting | Deliverable | SupportMaterial)*, `entity_id`, `url`, `platform` *(enum: Drive | SharePoint)*, `order`
→ relationships: *(polimórfica — se resuelve por `entity_type` + `entity_id`, no por FK fija)*

**SupportMaterial** — `id`, `stage_id` → Stage, `title`, `url`
→ relationships: `stage`

## Support / infrastructure

**User** — `id`, `name`, `email` *(unique)*, `role` *(enum: Coordinator | BusinessTutor | TechnicalTutor | Student)*, `password_hash`

## Enums

| Enum | Values |
|------|--------|
| `TutorRole` | `Business`, `Technical` |
| `UserRole` | `Coordinator`, `BusinessTutor`, `TechnicalTutor`, `Student` |
| `DocumentPlatform` | `Drive`, `SharePoint` |
| `EntityType` | `Group`, `Meeting`, `Deliverable`, `SupportMaterial` *(usado por `Document.entity_type`)* |

---

# 2. Tentative Endpoint Structure

```
# Cohorts
GET    /api/cohorts
GET    /api/cohorts/{id}
PUT    /api/cohorts/{id}
GET    /api/cohorts/{id}/groups
GET    /api/cohorts/{id}/stages

# Groups
GET    /api/groups
GET    /api/groups/{id}
PUT    /api/groups/{id}
DELETE /api/groups/{id}
GET    /api/groups/{id}/students
GET    /api/groups/{id}/meetings
GET    /api/groups/{id}/deliverables
GET    /api/groups/{id}/documents
PUT   /api/groups/{id}/documents

# Students
GET    /api/students
GET    /api/students/{id}
PUT    /api/students/{id}
DELETE /api/students/{id}

# Tutors
GET    /api/tutors
GET    /api/tutors/{id}
PUT    /api/tutors/{id}
GET    /api/tutors/{id}/groups
GET    /api/tutors/{id}/capacity
GET    /api/tutors/overloaded

# Stages
GET    /api/cohorts/{cohortId}/stages
PUT   /api/cohorts/{cohortId}/stages
GET    /api/stages/{id}
GET    /api/stages/{id}/deliverables
GET    /api/stages/{id}/materials

# Meetings
GET    /api/meetings
GET    /api/meetings/{id}
PUT    /api/meetings/{id}
DELETE /api/meetings/{id}
GET    /api/groups/{groupId}/meetings/total-hours

# Deliverables
GET    /api/deliverables
GET    /api/deliverables/{id}
PUT    /api/deliverables/{id}
GET    /api/deliverables/pending
GET    /api/deliverables/overdue

# Documents (polimórfico: hoy soporta Group y Deliverable como entity_type)
GET    /api/deliverables/{deliverableId}/documents
PUT   /api/deliverables/{deliverableId}/documents
GET    /api/groups/{id}/documents
PUT   /api/groups/{id}/documents
DELETE /api/documents/{id}

# Comments
GET    /api/deliverables/{deliverableId}/comments
POST   /api/deliverables/{deliverableId}/comments
DELETE /api/comments/{id}

# Support Materials
GET    /api/materials
GET    /api/materials/{id}
PUT    /api/materials/{id}
DELETE /api/materials/{id}

# Dashboard
GET    /api/dashboard/summary

# Auth / Users
POST   /api/auth/login
GET    /api/users/me
GET    /api/users          (coordinator only)
POST   /api/users
```

---

# 3. Sample Payloads

### Cohort
```json
// GET /api/cohorts/{id}
{
  "id": 1,
  "year": 2026,
  "semester": 1,
  "start_date": "2026-03-01",
  "end_date": "2026-07-15",
  "status": "Active",
  "notes": "First cohort of the year",
  "group_count": 12
}

// PUT /api/cohorts/{id} (request)
{
  "year": 2026,
  "semester": 1,
  "start_date": "2026-03-01",
  "end_date": "2026-07-15",
  "notes": "First cohort of the year"
}
```

### Group
```json
// GET /api/groups/{id}
{
  "id": 45,
  "name": "EcoRoute",
  "cohort_id": 1,
  "idea": "Recycling route platform for companies",
  "current_stage": {
    "id": 2,
    "name": "Preliminary Project"
  },
  "business_tutor": {
    "id": 8,
    "name": "María Pérez"
  },
  "technical_tutor": {
    "id": 14,
    "name": "Diego Ramírez"
  },
  "students": [
    { "id": 101, "name": "Ana Fernández" },
    { "id": 102, "name": "Luca Rossi" }
  ]
}

// PUT /api/groups/{id} (request)
{
  "name": "EcoRoute",
  "cohort_id": 1,
  "idea": "Recycling route platform for companies",
  "student_ids": [101, 102],
  "current_stage_id": 2,
  "business_tutor_id": 8,
  "technical_tutor_id": 14
}
```

### Student
```json
// GET /api/students/{id}
{
  "id": 101,
  "name": "Ana Fernández",
  "email": "ana.fernandez@ucu.edu.uy",
  "major": "Systems Engineering",
  "group_id": 45
}

// PUT /api/students/{id} (request)
{
  "name": "Ana Fernández",
  "email": "ana.fernandez@ucu.edu.uy",
  "major": "Systems Engineering",
  "group_id": 45
}
```

### Tutor
```json
// GET /api/tutors/{id}
{
  "id": 8,
  "name": "María Pérez",
  "role": "Business",
  "specialty": "Strategy and market validation",
  "availability": "Monday and Wednesday afternoon",
  "max_capacity": 88,
  "status": "Active"
}

// GET /api/tutors/{id}/capacity
// "groups" y "hours_consumed" se calculan a partir de los grupos donde este
// tutor es business_tutor o technical_tutor, sumando las horas de sus meetings.
{
  "tutor_id": 8,
  "max_capacity": 88,
  "assigned_hours": 66,
  "available_hours": 22,
  "usage_percentage": 75,
  "overloaded": false,
  "groups": [
    { "group_id": 45, "name": "EcoRoute", "hours_consumed": 18 },
    { "group_id": 52, "name": "AgroSmart", "hours_consumed": 22 }
  ]
}
```

### Stage
```json
// GET /api/stages/{id}
{
  "id": 2,
  "cohort_id": 1,
  "name": "Preliminary Project",
  "order": 2,
  "key_dates": [
    { "description": "Partial submission", "date": "2026-04-20" }
  ]
}

// GET /api/stages/{id}/deliverables
[
  { "id": 5, "group_id": 45, "expected_date": "2026-04-20", "status": "Pending" }
]
```

### Meeting
```json
// PUT /api/meetings/{id} (request)
{
  "group_id": 45,
  "tutor_ids": [8, 14],
  "date": "2026-04-10T15:00:00Z",
  "participants": [101, 102],
  "notes": "Value proposition discussed. Business model adjusted for next deliverable.",
  "next_steps": "Interview 5 potential customers",
  "hours_spent": 1.5,
  "links": [
    { "type": "Drive", "url": "https://drive.google.com/minutes-04-10" }
  ]
}

// GET /api/groups/{groupId}/meetings/total-hours
{
  "group_id": 45,
  "total_hours": 18,
  "max_capacity": 22,
  "remaining_hours": 4
}
```

### Deliverable
```json
// GET /api/deliverables/{id}
{
  "id": 5,
  "group_id": 45,
  "stage_id": 2,
  "expected_date": "2026-04-20",
  "status": "Pending",
  "documents": [
    { "id": 30, "url": "https://drive.google.com/deliverable-1", "platform": "Drive", "order": 1 }
  ],
  "comments": [
    { "id": 7, "tutor_id": 8, "content": "Needs deeper competitive analysis" }
  ]
}

// PUT /api/deliverables/{id} (request)
{
  "group_id": 45,
  "stage_id": 2,
  "expected_date": "2026-04-20",
  "status": "Under review"
}
```

### Document
```json
// PUT /api/deliverables/{deliverableId}/documents (request)
// El endpoint sigue siendo específico por entidad (más simple de usar desde el
// frontend), pero internamente guarda entity_type="Deliverable" y entity_id={deliverableId}.
{
  "url": "https://drive.google.com/ecoroute-doc",
  "platform": "Drive",
  "order": 1
}

// GET /api/deliverables/{deliverableId}/documents
[
  { "id": 30, "entity_type": "Deliverable", "entity_id": 5, "url": "https://drive.google.com/ecoroute-doc", "platform": "Drive", "order": 1 }
]

// PUT /api/groups/{id}/documents (request) — mismo patrón, ahora disponible también para Group
{
  "url": "https://drive.google.com/ecoroute-repo",
  "platform": "Drive",
  "order": 1
}
```

### Comment
```json
// POST /api/deliverables/{deliverableId}/comments (request)
{
  "tutor_id": 8,
  "content": "Review the target market section"
}

// GET /api/deliverables/{deliverableId}/comments
[
  { "id": 7, "tutor_id": 8, "deliverable_id": 5, "content": "Review the target market section" }
]
```

### Support Material
```json
// GET /api/materials
[
  { "id": 12, "stage_id": 2, "title": "Business Model Canvas Template", "url": "https://drive.google.com/bmc-template" }
]

// PUT /api/materials/{id} (request)
{
  "stage_id": 2,
  "title": "Business Model Canvas Template",
  "url": "https://drive.google.com/bmc-template"
}
```

### Dashboard
```json
// GET /api/dashboard/summary
// "GroupWithoutTutor" = business_tutor_id o technical_tutor_id es NULL.
// "OverloadedTutor" = suma de horas de meetings > max_capacity del tutor.
{
  "active_groups": 42,
  "active_tutors": 18,
  "groups_by_stage": [
    { "stage": "Ideation", "count": 15 },
    { "stage": "Preliminary Project", "count": 18 },
    { "stage": "Final Project", "count": 9 }
  ],
  "capacity": {
    "total_available_hours": 440,
    "total_used_hours": 310,
    "usage_percentage": 70.5
  },
  "pending_deliverables": 23,
  "alerts": [
    { "type": "GroupWithoutTutor", "group_id": 60, "description": "Missing technical tutor" },
    { "type": "OverloadedTutor", "tutor_id": 8, "description": "104% of capacity" }
  ]
}
```

### Auth
```json
// POST /api/auth/login (request)
{
  "email": "maria.perez@ucu.edu.uy",
  "password": "********"
}

// response
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 8,
    "name": "María Pérez",
    "role": "BusinessTutor"
  }
}
```

---

### Note
For list responses (`GET /api/groups`, `GET /api/tutors`, etc.), it's best to wrap them in a paginated object from the MVP stage on, to avoid breaking the API contract later:

```json
{
  "items": [ /* ... */ ],
  "total_items": 42,
  "page": 1,
  "page_size": 20
}
```
