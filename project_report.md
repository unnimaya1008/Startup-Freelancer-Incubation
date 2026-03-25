# Project Report
## Startup–Freelancer–Incubation Platform

### 1. Overview
The **Startup–Freelancer–Incubation Platform** is a Django‑based web application that connects startups with freelancers and mentors, supports project posting and proposal workflows, and enables mentorship sessions. The system also includes AI‑assisted verification for freelancers/mentors and AI‑assisted proposal ranking to help startups make informed hiring decisions. The platform provides multi‑role access (Startup, Freelancer, Mentor, Investor, Admin) with role‑specific dashboards and workflows.

### 2. Software Requirement Specification (SRS)

#### 2.1 Functional Requirements
**2.1.1 User Authentication & Role Management**
- **Requirement ID:** FR-AUTH-001
- **Description:** The system shall provide secure login/logout and user registration with role assignment (Startup, Freelancer, Mentor, Investor, Admin).
- **Inputs:** Username, Email, Password, Role
- **Outputs:** Authentication status, user session
- **Priority:** High
- **Dependencies:** None

**2.1.2 Startup Profile Management**
- **Requirement ID:** FR-STARTUP-001
- **Description:** Startups shall be able to create and manage their profile, including company details and branding.
- **Inputs:** Startup name, description, website, industry, logo
- **Outputs:** Updated profile
- **Priority:** High
- **Dependencies:** Authentication

**2.1.3 Freelancer Profile Management**
- **Requirement ID:** FR-FREELANCER-001
- **Description:** Freelancers shall be able to create and manage their profile, availability, domain, portfolio, and verification artifacts.
- **Inputs:** Full name, domain, availability, resume/certificates
- **Outputs:** Updated profile
- **Priority:** High
- **Dependencies:** Authentication

**2.1.4 Mentor Profile Management**
- **Requirement ID:** FR-MENTOR-001
- **Description:** Mentors shall be able to create and manage their profile and verification artifacts.
- **Inputs:** Expertise area, experience, certificates
- **Outputs:** Updated profile
- **Priority:** High
- **Dependencies:** Authentication

**2.1.5 Project Management**
- **Requirement ID:** FR-PROJECT-001
- **Description:** Startups shall be able to create, update, and manage projects including requirements and timelines.
- **Inputs:** Project title, domain, requirements file, dates
- **Outputs:** Project created/updated
- **Priority:** High
- **Dependencies:** Startup profile

**2.1.6 Proposal Submission & Review**
- **Requirement ID:** FR-PROPOSAL-001
- **Description:** Freelancers shall be able to submit proposals; startups shall be able to review, approve, or reject proposals.
- **Inputs:** Proposal text, attachments, expected timeline/payment
- **Outputs:** Proposal status
- **Priority:** High
- **Dependencies:** Project management

**2.1.7 Project Assignment**
- **Requirement ID:** FR-ASSIGN-001
- **Description:** Startups shall be able to assign projects to freelancers or internal employees.
- **Inputs:** Project ID, freelancer/employee info
- **Outputs:** Assignment record
- **Priority:** High
- **Dependencies:** Proposal review

**2.1.8 Milestone Tracking**
- **Requirement ID:** FR-MILESTONE-001
- **Description:** Assigned freelancers shall manage milestones and track progress.
- **Inputs:** Milestone title, due date, progress
- **Outputs:** Updated milestones
- **Priority:** Medium
- **Dependencies:** Project assignment

**2.1.9 Ratings & Feedback**
- **Requirement ID:** FR-RATING-001
- **Description:** Startups shall rate freelancers and employees; startups shall rate mentors post‑session.
- **Inputs:** Rating values, feedback
- **Outputs:** Stored ratings and averages
- **Priority:** Medium
- **Dependencies:** Completion of work/session

**2.1.10 Mentorship Sessions**
- **Requirement ID:** FR-SESSION-001
- **Description:** Startups shall request mentorship sessions; mentors approve and schedule sessions.
- **Inputs:** Topic, date, notes, approval status
- **Outputs:** Session schedule
- **Priority:** Medium
- **Dependencies:** Mentor availability

**2.1.11 Notifications & Messaging**
- **Requirement ID:** FR-NOTIF-001
- **Description:** The system shall provide notifications and internal messaging between users.
- **Inputs:** Title, message content
- **Outputs:** Notification/message entries
- **Priority:** Medium
- **Dependencies:** Authentication

**2.1.12 AI‑Assisted Verification**
- **Requirement ID:** FR-AI-001
- **Description:** The system shall perform AI‑assisted verification on freelancer/mentor profiles using provided evidence (GitHub, certificates).
- **Inputs:** GitHub URL, certificate file
- **Outputs:** Verification status, fraud score, AI report
- **Priority:** Medium
- **Dependencies:** AI configuration key

**2.1.13 AI‑Assisted Proposal Ranking**
- **Requirement ID:** FR-AI-002
- **Description:** The system shall generate AI‑assisted proposal scores to help rank proposals.
- **Inputs:** Proposal data
- **Outputs:** AI score and report
- **Priority:** Medium
- **Dependencies:** AI configuration key

#### 2.2 Non‑Functional Requirements
**2.2.1 Performance**
- **Requirement ID:** NFR-PERF-001
- **Description:** Common user actions (login, view project, submit proposal) should complete within 2–3 seconds under normal load.
- **Priority:** High

**2.2.2 Scalability**
- **Requirement ID:** NFR-PERF-002
- **Description:** The system should support growth in users and projects with modular app separation.
- **Priority:** High

**2.2.3 Security**
- **Requirement ID:** NFR-SEC-001
- **Description:** User passwords must be securely hashed and protected using Django’s authentication framework.
- **Priority:** High

**2.2.4 Reliability**
- **Requirement ID:** NFR-REL-001
- **Description:** The system should gracefully handle errors and provide informative feedback to the user.
- **Priority:** Medium

**2.2.5 Usability**
- **Requirement ID:** NFR-USAB-001
- **Description:** UI should be consistent and role‑specific with clear navigation for startup, freelancer, and mentor users.
- **Priority:** Medium

**2.2.6 Compliance & Privacy**
- **Requirement ID:** NFR-COMP-001
- **Description:** The system should support privacy‑safe handling of personal data and secure file storage.
- **Priority:** Medium

### 3. Software Design Document (SDD)

#### 3.1 System Features (Modules)
**3.1.1 Authentication & User Roles**
- **Functionality:** Custom user model with role‑based access for Startup, Freelancer, Mentor, Investor, Admin.
- **Inputs:** Registration/login credentials
- **Outputs:** User session

**3.1.2 Startup Management**
- **Functionality:** Startup profile, employee directory, project posting, proposal review, notifications.

**3.1.3 Freelancer Management**
- **Functionality:** Freelancer profile, availability, domain filtering, proposal submission, milestones, ratings.

**3.1.4 Mentor Management**
- **Functionality:** Mentor profile, session scheduling and approval, mentor ratings.

**3.1.5 Project & Proposal Management**
- **Functionality:** Project creation, proposal submission, AI ranking, and assignment workflows.

**3.1.6 AI‑Assisted Verification**
- **Functionality:** Verification of freelancer/mentor evidence (GitHub, certificates) and scoring.

#### 3.2 System Architecture Design
**System Components**
1. **Frontend:** Django templates with role‑based dashboards and forms
2. **Backend:** Python Django framework (multiple apps)
3. **Database:** SQLite (dev) with models for users, projects, proposals, ratings, and sessions
4. **File Storage:** Django media storage; optional Supabase storage integration
5. **AI Services:** Gemini API for verification and proposal scoring

**System Interaction**
- Users interact with Django views and templates.
- Backend persists and retrieves data from the database.
- AI services are called for verification and proposal ranking.

**Scalability & Security Measures**
- Modular Django apps allow scaling by domain.
- Django authentication and CSRF protection for security.
- Secure file handling with optional external storage.

### 4. Constraints
1. **Technology Constraints**: Python/Django ecosystem, server must support Python and database.
2. **Browser Compatibility**: Modern browsers (Chrome/Firefox/Edge).
3. **Infrastructure**: Requires file storage for resumes/certificates and images.
4. **Regulatory**: Handle personal data carefully (GDPR‑style best practices).

### 5. Application Architecture
1. **Frontend**: Django templates (HTML/CSS/JS)
2. **Backend**: Django (Python) with app modules
3. **Database**: SQLite (development) – can migrate to PostgreSQL/MySQL for production
4. **Authentication**: Django auth + custom user model
5. **External Integrations**: Gemini API, optional Supabase storage
6. **Deployment**: Can be hosted on any Python‑capable server or cloud (AWS/GCP/Azure)

### 6. API / Route Design (Representative)
Although primarily server‑rendered, key routes include:
1. **Authentication**
- `POST /login/` – user login
- `POST /accounts/signup/` – user registration

2. **Startup**
- `GET /startup/profile/`
- `POST /startup/projects/create/`
- `GET /startup/projects/<project_id>/`
- `GET /startup/proposals/<project_id>/`

3. **Freelancer**
- `GET /freelancer/profile/`
- `GET /freelancer/projects/available/`
- `POST /freelancer/projects/<project_id>/proposal/`

4. **Mentor**
- `GET /mentor/dashboard/`
- `POST /startup/sessions/create/`

### 7. Database Design (High‑Level)
**Primary Entities**
1. `CustomUser` (role, username, email, password)
2. `StartupProfile`
3. `FreelancerProfile`
4. `MentorProfile`
5. `Project`
6. `ProjectProposal`
7. `ProjectAssignment`
8. `Milestone`
9. `Notification`
10. `Message`
11. `MentorshipSession`

### 8. Technology Stack
- **Backend:** Python 3, Django 5.2
- **Frontend:** Django templates + HTML/CSS/JS
- **Database:** SQLite (dev)
- **Libraries:** pillow, python‑dotenv, requests, supabase
- **AI Integration:** Gemini API
- **Version Control:** Git

### 9. Use Cases
**9.1 Use Case: Startup Creates a Project**
- **Actors:** Startup user
- **Preconditions:** Startup profile exists
- **Main Flow:** Startup enters project details → system validates → project created
- **Postconditions:** Project available for freelancer proposals

**9.2 Use Case: Freelancer Submits Proposal**
- **Actors:** Freelancer user
- **Preconditions:** Freelancer profile exists; project is available
- **Main Flow:** Freelancer fills proposal form → submit → proposal stored
- **Postconditions:** Startup can review proposal

**9.3 Use Case: Mentor Session Request**
- **Actors:** Startup, Mentor
- **Preconditions:** Mentor profile exists
- **Main Flow:** Startup requests session → mentor approves → session scheduled
- **Postconditions:** Session appears in both dashboards

### 10. Implementation Notes
- Follows Django app‑based modular structure.
- Uses forms for validation and templates for rendering.
- AI verification and proposal ranking are triggered asynchronously by views.

### 11. Environment Setup (Development)
1. Install Python 3.12+
2. Create and activate virtual environment
3. Install requirements: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

### 12. Test Plan (Overview)
**Objectives:** Validate authentication, project workflows, proposal handling, and mentoring flows.

**Test Scope:**
- Backend (Django models, forms, views)
- Frontend (templates, navigation, form validation)

**Test Types:**
- Unit testing for models and utilities
- Integration testing for workflow flows
- Functional testing for end‑to‑end flows
- Performance testing for login and project listing

### 13. Sample Test Scenarios
1. Login with valid/invalid credentials
2. Startup creates project
3. Freelancer submits proposal
4. Startup approves/rejects proposal
5. Mentor approves session request

### 14. Conclusion
The Startup–Freelancer–Incubation Platform provides a unified ecosystem for collaboration between startups, freelancers, mentors, and investors. With role‑based workflows, project and proposal management, mentoring, and AI‑assisted verification, the platform is positioned to support startup growth and efficient talent engagement.
