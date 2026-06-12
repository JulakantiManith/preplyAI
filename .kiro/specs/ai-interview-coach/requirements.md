# Requirements Document

## Introduction

AI Interview & Presentation Coach is a modern AI-powered platform that helps students, job seekers, and professionals improve their interview and presentation skills. The platform provides multiple practice modes (HR, Technical, Behavioral, Resume-based interviews, and Presentations), real-time speech analysis, confidence scoring, AI-generated feedback, and progress tracking analytics. The system uses Whisper for speech-to-text, Gemini API for AI evaluation, and MediaPipe/OpenCV for visual analysis.

## Glossary

- **Platform**: The AI Interview & Presentation Coach web application comprising a React frontend and FastAPI backend
- **User**: A registered individual (student, job seeker, or professional) who uses the Platform to practice interviews or presentations
- **Interview_Session**: A single practice session where the User answers one or more questions while being recorded
- **Presentation_Session**: A single practice session where the User delivers a presentation while being recorded or uploads presentation materials
- **Speech_Analysis_Engine**: The backend module that processes audio transcriptions to compute speech metrics including WPM, filler word count, pause duration, and communication score
- **Confidence_Analyzer**: The backend module that evaluates hesitation patterns, pause frequency, speech flow, and consistency to produce a confidence score (0-100)
- **AI_Feedback_Engine**: The backend module that uses Gemini API to generate strengths, weaknesses, and recommendations based on session data
- **Question_Generator**: The backend module that uses Gemini API to generate interview questions based on role, type, difficulty, and optionally resume content
- **Transcription_Service**: The backend module that uses Whisper to convert recorded audio into text
- **Resume_Parser**: The backend module that extracts skills, projects, experience, and education from uploaded resume files
- **Analytics_Service**: The backend module that aggregates session data into daily, weekly, and monthly progress reports
- **Auth_Service**: The authentication module powered by Supabase Auth that handles registration, login, logout, and password management
- **Dashboard**: The main interface showing aggregated performance metrics, recent activity, and progress charts
- **Session_History**: The module that stores and retrieves past session transcripts, scores, feedback, and metadata

## Requirements

### Requirement 1: User Registration and Authentication

**User Story:** As a job seeker, I want to create an account and securely log in, so that I can save my practice sessions and track my progress over time.

#### Acceptance Criteria

1. WHEN a visitor submits a registration form with full name, email, and password, THE Auth_Service SHALL create a new user account and send an email verification link
2. WHEN a registered User submits valid login credentials, THE Auth_Service SHALL authenticate the User and return a session token
3. WHEN an authenticated User requests logout, THE Auth_Service SHALL invalidate the current session token
4. WHEN a User submits a forgot-password request with an email address, THE Auth_Service SHALL respond with a generic success message regardless of whether the email is registered, to prevent email enumeration
5. WHEN a User submits a new password via a valid reset link, THE Auth_Service SHALL update the password and invalidate the reset link
6. IF an unauthenticated visitor attempts to access a protected route, THEN THE Platform SHALL redirect the visitor to the login page
7. IF a visitor submits a registration form with invalid data (missing fields, invalid email format, or weak password), THEN THE Auth_Service SHALL reject the registration and display field-specific validation errors
8. IF a registered User submits invalid login credentials, THEN THE Auth_Service SHALL reject the login attempt and display a generic authentication error message
9. IF a User submits a new password via an invalid or expired reset link, THEN THE Auth_Service SHALL reject the request and display an error indicating the link is invalid or expired

### Requirement 2: User Profile Management

**User Story:** As a User, I want to manage my profile information, so that the platform can personalize my practice experience.

#### Acceptance Criteria

1. WHEN an authenticated User submits profile updates (target role, experience level, skills), THE Platform SHALL persist the changes and reflect them immediately in the interface
2. WHEN an authenticated User uploads a resume file (PDF or DOCX), THE Platform SHALL store the file in Supabase Storage and associate it with the User profile
3. THE Platform SHALL validate that uploaded resume files do not exceed 10 MB in size
4. IF a User submits a profile update with invalid data or an oversized file, THEN THE Platform SHALL display field-specific validation errors while preserving all other previously entered profile data

### Requirement 3: Dashboard Overview

**User Story:** As a User, I want to see a summary of my practice activity and performance, so that I can quickly understand my progress.

#### Acceptance Criteria

1. WHEN an authenticated User navigates to the Dashboard, THE Platform SHALL display total interview sessions completed, total presentation sessions completed, average score, confidence score, and communication score
2. WHEN an authenticated User views the Dashboard, THE Platform SHALL display a weekly progress chart showing score trends for the current week
3. WHEN an authenticated User views the Dashboard, THE Platform SHALL display a list of the 5 most recent sessions with type, date, and score
4. THE Dashboard SHALL update displayed metrics within 5 seconds of a new session being completed
5. WHEN an authenticated User with zero completed sessions navigates to the Dashboard, THE Platform SHALL display an onboarding state with a welcome message and call-to-action to start their first session instead of showing zero metrics

### Requirement 4: Interview Practice Sessions

**User Story:** As a job seeker, I want to practice different types of interviews with AI-generated questions, so that I can prepare effectively for real interviews.

#### Acceptance Criteria

1. WHEN a User selects an interview type (HR, Technical, Behavioral, or Custom) and a target role, THE Question_Generator SHALL produce a set of relevant interview questions
2. WHEN a User starts an Interview_Session, THE Platform SHALL activate audio recording and display the current question
3. WHEN a User completes answering a question, THE Transcription_Service SHALL convert the recorded audio to text within 30 seconds
4. WHEN transcription is complete, THE Speech_Analysis_Engine SHALL analyze the transcript and produce speech metrics
5. WHEN speech analysis is complete, THE AI_Feedback_Engine SHALL generate feedback including strengths, weaknesses, and recommendations
6. WHEN all questions in an Interview_Session are answered, THE Platform SHALL display a score report summarizing performance across all answers
7. IF audio recording fails due to microphone access denial, THEN THE Platform SHALL display a clear error message explaining how to grant microphone permissions

### Requirement 5: Technical Interview Mode

**User Story:** As a software professional, I want to practice technical interviews on specific computer science topics at varying difficulty levels, so that I can prepare for technical screenings.

#### Acceptance Criteria

1. WHEN a User selects a technical topic (Data Structures, Algorithms, OS, DBMS, CN, OOP, Java, Python, JavaScript, React, Node.js, or Cloud Computing) and difficulty level (Beginner, Intermediate, or Advanced), THE Question_Generator SHALL produce topic-specific technical questions at the selected difficulty
2. WHEN a User answers a technical question, THE AI_Feedback_Engine SHALL evaluate technical accuracy, completeness, and communication clarity
3. WHEN the AI_Feedback_Engine identifies an incomplete or incorrect answer, THE Question_Generator SHALL generate a follow-up question probing the weak area
4. THE Platform SHALL display the evaluation score breakdown showing separate scores for technical accuracy, completeness, and communication

### Requirement 6: Resume-Based Interviews

**User Story:** As a job seeker, I want to practice interviews based on my actual resume, so that I can prepare for questions likely to come up about my experience.

#### Acceptance Criteria

1. WHEN a User uploads a resume (PDF or DOCX), THE Resume_Parser SHALL extract skills, projects, experience, and education sections within 60 seconds
2. WHEN extraction is complete, THE Platform SHALL display the extracted information for User confirmation before generating questions
3. WHEN a User confirms extracted resume data, THE Question_Generator SHALL generate personalized interview questions targeting the extracted skills and experiences
4. IF the Resume_Parser fails to extract meaningful data from an uploaded file, THEN THE Platform SHALL display an error message and suggest re-uploading a properly formatted resume

### Requirement 7: Presentation Coach

**User Story:** As a professional, I want to practice presentations and receive feedback on my delivery, so that I can improve my public speaking skills.

#### Acceptance Criteria

1. WHEN a User starts a Presentation_Session with live recording, THE Platform SHALL activate audio and video recording simultaneously
2. WHEN a User uploads presentation materials (PPT or PDF), THE Platform SHALL associate the materials with the Presentation_Session
3. WHEN a Presentation_Session recording is complete, THE Speech_Analysis_Engine SHALL analyze speaking speed, clarity, structure, communication, and engagement
4. WHEN presentation analysis is complete, THE AI_Feedback_Engine SHALL generate a presentation-specific score and improvement suggestions
5. WHEN presentation analysis is complete, THE Platform SHALL display presentation scores broken down by speaking speed, clarity, structure, communication, and engagement categories

### Requirement 8: Speech Analysis

**User Story:** As a User, I want detailed analysis of my speaking patterns, so that I can identify and correct specific speech habits.

#### Acceptance Criteria

1. WHEN a transcript is available, THE Speech_Analysis_Engine SHALL calculate words per minute (WPM) for the entire response
2. WHEN a transcript is available, THE Speech_Analysis_Engine SHALL detect and count filler words (um, uh, like, actually, basically, you know) in the transcript
3. THE Speech_Analysis_Engine SHALL compute a Communication Score (0-100) based on WPM proximity to the ideal range (120-160 WPM), filler word frequency, and pause patterns
4. THE Speech_Analysis_Engine SHALL report total word count, total filler word count, speaking duration, and average pause duration for each analyzed response
5. WHEN WPM falls outside the ideal range (120-160), THE Speech_Analysis_Engine SHALL flag the deviation in the feedback report

### Requirement 9: Confidence Analysis

**User Story:** As a User, I want to understand how confident I sound during practice, so that I can work on projecting confidence in real situations.

#### Acceptance Criteria

1. WHEN a session recording is analyzed, THE Confidence_Analyzer SHALL produce a confidence score between 0 and 100
2. THE Confidence_Analyzer SHALL compute the confidence score based on hesitation count, pause frequency, speech flow consistency, and response completeness
3. WHEN the confidence score is between 1 and 49 (inclusive), THE AI_Feedback_Engine SHALL include specific recommendations for improving confidence in the feedback report
4. THE Platform SHALL display the confidence score with a visual indicator (color-coded or gauge) showing the performance level

### Requirement 10: AI Feedback Generation

**User Story:** As a User, I want actionable AI-generated feedback after each session, so that I know exactly what to improve.

#### Acceptance Criteria

1. WHEN speech analysis and confidence analysis are complete for a session, THE AI_Feedback_Engine SHALL generate a feedback report containing strengths, weaknesses, and recommendations sections
2. THE AI_Feedback_Engine SHALL generate a minimum of 2 strengths, 2 weaknesses, and 3 recommendations per session
3. WHEN generating feedback for a technical interview, THE AI_Feedback_Engine SHALL include evaluation of technical content accuracy in addition to delivery feedback
4. THE AI_Feedback_Engine SHALL produce the complete feedback report within 45 seconds of receiving analysis data
5. WHEN generating feedback for any non-technical interview, THE AI_Feedback_Engine SHALL include evaluation of communication structure and logical flow in addition to delivery feedback

### Requirement 11: Analytics and Progress Tracking

**User Story:** As a User, I want to visualize my improvement over time, so that I can stay motivated and identify long-term trends.

#### Acceptance Criteria

1. WHEN a User navigates to the Analytics page, THE Analytics_Service SHALL display daily, weekly, and monthly progress views
2. THE Analytics_Service SHALL render line charts showing score trends and bar charts showing session frequency over the selected time period
3. WHEN a User selects a specific time range, THE Analytics_Service SHALL filter all displayed metrics to that range
4. THE Analytics_Service SHALL compute and display trends for overall score, confidence score, and communication score separately
5. WHEN a User has fewer than 3 sessions, THE Platform SHALL display available analytics alongside a message encouraging more practice to enable full trend analysis

### Requirement 12: Session History

**User Story:** As a User, I want to review my past practice sessions, so that I can revisit feedback and track specific improvements.

#### Acceptance Criteria

1. WHEN a User navigates to Session History, THE Platform SHALL display a paginated list of all past sessions sorted by date (most recent first)
2. THE Platform SHALL display session type, date, duration, and overall score for each entry in the history list
3. WHEN a User selects a past session, THE Platform SHALL display the full transcript, all scores, AI feedback, and session metadata
4. WHEN a User has more than 20 sessions, THE Platform SHALL paginate results with 20 sessions per page
5. THE Platform SHALL allow filtering session history by session type (Interview or Presentation) and date range

### Requirement 13: Eye Contact and Head Pose Analysis (Phase 3)

**User Story:** As a User, I want feedback on my non-verbal communication, so that I can improve my body language during interviews and presentations.

#### Acceptance Criteria

1. WHEN video recording is active during a session, THE Platform SHALL use MediaPipe to track the User's eye gaze direction in real-time
2. WHEN a video session is complete, THE Platform SHALL calculate an eye contact percentage representing time spent looking at the camera
3. WHEN video recording is active, THE Platform SHALL use MediaPipe to estimate head pose (pitch, yaw, roll) throughout the session
4. WHEN head pose analysis is complete, THE Platform SHALL report head movement stability when movement is within acceptable thresholds, and flag excessive movement only when thresholds are exceeded
5. IF the User's camera feed is too dark or the face is not detected, THEN THE Platform SHALL display a warning and suggest improving lighting or camera positioning

### Requirement 14: Landing Page

**User Story:** As a visitor, I want to understand what the platform offers, so that I can decide whether to sign up.

#### Acceptance Criteria

1. THE Platform SHALL display a landing page containing hero section, features section, how-it-works section, benefits section, testimonials section, pricing section, FAQ section, and footer
2. WHEN a visitor clicks a call-to-action button on the landing page, THE Platform SHALL navigate the visitor to the registration page
3. IF navigation to the registration page fails due to a network or server error, THEN THE Platform SHALL display a user-friendly error message and offer a retry option
4. THE Platform SHALL render the landing page in under 3 seconds on a standard broadband connection
5. THE Platform SHALL display the landing page responsively across desktop (1024px+), tablet (768px-1023px), and mobile (below 768px) viewports

### Requirement 15: Responsive Design and Dark Mode

**User Story:** As a User, I want to use the platform comfortably on any device and in any lighting condition, so that I can practice anytime.

#### Acceptance Criteria

1. THE Platform SHALL render all pages responsively across desktop, tablet, and mobile viewports without horizontal scrolling
2. WHEN a User toggles dark mode, THE Platform SHALL immediately switch all UI components to a dark color scheme and attempt to persist the preference; IF persistence fails, THE Platform SHALL maintain the visual change for the current session
3. WHEN a User revisits the Platform, THE Platform SHALL apply the previously selected color scheme preference
4. THE Platform SHALL default to the operating system's preferred color scheme for first-time visitors

### Requirement 16: Data Persistence and Storage

**User Story:** As a User, I want all my practice data securely stored, so that I never lose my progress.

#### Acceptance Criteria

1. WHEN an Interview_Session or Presentation_Session is completed, THE Platform SHALL persist the transcript, scores, feedback, duration, and date to the database
2. THE Platform SHALL store uploaded files (resumes, presentations) in Supabase Storage with access restricted to the owning User
3. IF a database write operation fails, THEN THE Platform SHALL retry the operation once and display an error message to the User if the retry also fails
4. THE Platform SHALL associate all stored data (sessions, analytics, files) with the authenticated User's account

### Requirement 17: API Performance and Error Handling

**User Story:** As a User, I want the platform to respond quickly and handle errors gracefully, so that my practice sessions are not disrupted.

#### Acceptance Criteria

1. THE Platform SHALL return API responses for non-AI endpoints within 500 milliseconds under normal load
2. IF an API request fails due to a network error, THEN THE Platform SHALL display a user-friendly error message and offer a retry option
3. IF the Gemini API returns an error or timeout, THEN THE AI_Feedback_Engine SHALL retry the request once before reporting a failure to the User
4. THE Platform SHALL validate all user inputs on both client and server sides using Zod schemas before processing
5. IF server-side validation fails, THEN THE Platform SHALL return structured error responses with field-specific error messages


### Requirement 18: Code Organization and Maintainability

**User Story:** As a development team, I want the codebase to follow strict organization standards, so that the platform remains scalable, maintainable, and easy to extend.

#### Acceptance Criteria

1. THE Platform SHALL enforce that no frontend or backend source file exceeds 600 lines of code
2. IF a source file approaches 600 lines, THEN THE Platform SHALL split the file into smaller modules, components, hooks, services, utilities, or feature files
3. THE Platform SHALL implement business logic in dedicated service or utility modules separate from UI components
4. THE Platform SHALL isolate all API communication in dedicated service files separate from UI and business logic modules
5. THE Platform SHALL follow a feature-based architecture where related components, hooks, services, and utilities are co-located within feature directories
6. THE Platform SHALL place shared UI components in reusable component directories accessible to all feature modules
7. THE Platform SHALL maintain a codebase structure that remains scalable, maintainable, and production-ready as features are added


### Requirement 19: Development Phasing

**User Story:** As a development team, I want a clear phased delivery plan, so that core functionality is stable before advanced features are built on top of it.

#### Acceptance Criteria

1. THE Platform SHALL complete all MVP phase features before any Phase 2 features are implemented
2. THE Platform SHALL complete all Phase 2 features before any Phase 3 features are implemented
3. WHEN a task is completed, THE Platform SHALL produce a testable deliverable that can be independently verified
4. IF a task contains only placeholder implementations, THEN THE Platform SHALL mark the task as incomplete until functional implementation replaces the placeholder


### Requirement 20: Creator Attribution and Professional Footer

**User Story:** As a visitor, I want to see information about the creator of the platform, so that I can learn more about the developer and connect professionally.

#### Acceptance Criteria

1. THE Platform SHALL display a footer on all public pages
2. THE footer SHALL display the creator name, GitHub profile link, and LinkedIn profile link
3. WHEN a visitor clicks the GitHub link, THE Platform SHALL open the creator's GitHub profile in a new browser tab
4. WHEN a visitor clicks the LinkedIn link, THE Platform SHALL open the creator's LinkedIn profile in a new browser tab
5. THE footer SHALL remain responsive across desktop, tablet, and mobile devices
6. THE footer SHALL include the current year and platform copyright information
7. THE creator information SHALL be configurable through environment variables or application configuration rather than hardcoded values

### Requirement 21: Authentication Navigation and Route Protection

**User Story:** As a User, I want the navigation to reflect my authentication state and prevent access to inappropriate pages, so that my experience is seamless and secure.

#### Acceptance Criteria

1. WHEN a User is authenticated, THE Platform SHALL display the user's name and a Logout action in the navbar, replacing the Sign In/Register actions
2. WHEN a User is unauthenticated, THE Platform SHALL display Sign In and Register actions in the navbar
3. WHEN an authenticated User clicks Logout, THE Platform SHALL display a confirmation dialog before terminating the session
4. WHEN a User confirms logout in the dialog, THE Auth_Service SHALL invalidate the session and redirect the User to the login page
5. WHEN a User with an unverified email attempts to log in, THE Platform SHALL display "Please verify your email address before signing in" instead of the generic invalid credentials message
6. IF an authenticated User attempts to navigate to /login, /register, /forgot-password, or /reset-password, THEN THE Platform SHALL redirect the User to /dashboard
7. WHEN a User authenticates successfully and uses the browser Back button, THE Platform SHALL NOT expose the login or registration pages; route guards SHALL enforce correct redirects regardless of navigation method

### Requirement 22: Theme Flash Prevention (FOUC)

**User Story:** As a User with dark mode enabled, I want the platform to render in my saved theme immediately on page load, so that I never see a white flash that disrupts my visual experience.

#### Acceptance Criteria

1. WHEN a User with a saved dark mode preference loads or refreshes any page, THE Platform SHALL apply the dark theme class to the document before the first paint, preventing any visible flash of the light theme
2. WHEN a first-time visitor loads the Platform, THE Platform SHALL detect the operating system color scheme preference and apply the corresponding theme class before the first paint
3. THE Platform SHALL execute theme initialization synchronously via an inline blocking script in `index.html`, before React or any module scripts execute
4. WHEN a User navigates between routes within the application, THE Platform SHALL preserve the active theme without any visual transition or flicker between pages
5. WHEN a User refreshes the browser on any page, THE Platform SHALL render the page directly in the previously saved theme without momentarily displaying the opposite theme
