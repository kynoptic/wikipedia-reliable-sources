# Content guidelines for Project pages on the HMS IT website

*These guidelines define the information architecture and content model for the “Project detail page” content type on the HMS IT website. This model maps directly to the site’s CMS components to ensure all project communications are clear, consistent, and actionable.*

## Introduction

This document provides a standardized framework for creating project detail pages by mapping strategic communication goals to specific CMS fields. It aims to **ensure all project communications are clear, comprehensive, and consistent**. The primary audience is content creators, project managers, and communications staff.

These guidelines apply to all project pages. They govern the structure and content for communicating **active and upcoming IT projects**.

This governance is necessary to streamline project communication and drive desired user actions. By standardizing the page structure within the CMS, we help users **quickly understand a project’s purpose, impact, and required actions**, which supports project success and manages user expectations.

### Related governance

- **Parent governance** – `[Link to overall website content style guide]`
- **Related governance** – `[Link to news & announcements guidelines]`

## Summary

- The main **Title** must be a benefit-oriented headline. The **Introduction body** explains the project’s “why” (problem and benefits).
- Project details are built using the **Accordion component**, with five mandatory sections – **Who is affected, What to expect, Actions to take, Timeline,** and **Support**.
- **Accordion subtitles** and **Labels** must be populated with specific keywords and summaries relevant to the project’s content, not generic placeholders.
- Additional accordion sections may be added *only* if they contain critical information the user needs that doesn’t fit within the standard five sections.

## Content brief

- **Objective** – To inform the HMS community about a specific IT project, clearly communicating its purpose and benefits, while driving particular user actions (for example, deleting data, registering for training).
- **User needs** – Users must understand what a project is, why it’s happening, if they are affected, what to expect, and what they are required to do.
- **Business goals** – To support project success through clear communication, manage user expectations, increase adoption of new services, and foster a culture of responsible stewardship.
- **Audience**:
    - **Primary** – Specific user groups directly affected by the project (for example, PIs, lab data managers).
    - **Secondary** – The broader HMS community, leadership, and partner departments.
- **Tone** – Authoritative, supportive, and direct. The content must articulate the problem and solution, focusing on the user and using “we” and “our” to create a sense of shared responsibility, while providing unambiguous calls to action.

## Content structure and components

This section details the CMS fields and content guidance.

### **Page title**

- **CMS field** – `Title`
- **HTML tag** – `<h1>`
- **Purpose** – Plainly describe the project with a transparent, benefit-oriented description.
- **Guidance** – Frame the title as a solution and focus on the positive outcome instead of the problem it addresses.
- **Examples**:
    - ✅ *Safeguarding HMS research storage*
    - ⛔ *Research Data Storage Lifecycle Project*

### **Introductory content**

#### **Introductory title (Subtitle)**

- **CMS field** – `Intro title`
- **HTML tag** – `<p>` (styled)
- **Purpose** – To provide a concise, one-sentence description of the project.
- **Guidance** – Write a clear, factual statement explaining what the project is.
- **Example**:

> HMS IT is expanding data cleanup activities and introducing sustainable data lifecycle practices to strengthen the sustainability, accessibility, and security of HMS research storage.

#### **Introduction body**

- **CMS field** – `Body`
- **HTML tag** – `<p>`, `<ul>`
- **Purpose** – To establish the strategic context by explaining the “why” and outlining the value proposition.
- **Guidance** – This rich-text field must contain:
    1. **The problem** – A paragraph explaining the issue that necessitates the project.
    1. **The solution and benefits** – A bulleted list highlighting the positive outcomes.
- **Example**:

> Our primary research storage systems are nearing capacity as ever-larger datasets accumulate…  This effort will help us:

    - Safeguard research storage capacity…
    - Simplify day-to-day research data management…

### **Accordion components**

This component houses the tactical details. It must begin with the five standard “Accordion items” in the order below. The `Accordion section title` field should be left blank.

#### Who is affected

- **CMS fields and guidance**:
    - **Accordion title** – *Who is affected*
    - **Accordion subtitle** – Write a specific summary of the affected groups for *this* project.
    - **Accordion label 1 / Label 2** – Use specific keywords that categorize the affected users and the project’s scope.
    - **Accordion content** – Detail the specific roles, departments, or user groups.
- **Example**:
    - **Accordion title** – Who is affected
    - **Accordion subtitle** – PIs, lab managers, and research staff
    - **Accordion label 1** – PIs
    - **Accordion label 2** – Research data
    - **Accordion content** – All users of HMS centralized storage are affected, including…

#### What to expect

- **CMS fields and guidance**:
    - **Accordion title** – *What to expect*
    - **Accordion subtitle** – Summarize the user experience for *this* project.
    - **Accordion label 1 / Label 2** – Use keywords for the project methodology.
    - **Accordion content** – Describe the project’s rollout process from the user’s perspective.
- **Example**:
    - **Accordion title** – What to expect
    - **Accordion subtitle** – Phased engagement with tailored communications
    - **Accordion label 1** – Phases
    - **Accordion label 2** – Dashboards
    - **Accordion content** – You can expect a **phased engagement** starting with the deletion of obsolete or unused data…

#### Actions to take

- **CMS fields and guidance**:
    - **Accordion title** – *Actions to take*
    - **Accordion subtitle** – Summarize the primary required actions for *this* project.
    - **Accordion label 1 / Label 2** – Use action-oriented keywords for the main tasks.
    - **Accordion content** – Use a list of direct, verb-first instructions. **Bold** the most critical action.
- **Example**:
    - **Accordion title** – Actions to take
    - **Accordion subtitle** – Review reports, delete old data, and tag datasets
    - **Accordion label 1** – Delete
    - **Accordion label 2** – Tag
    - **Accordion content**:
    - Review the data usage reports…
    - **Delete obsolete or redundant data…**

#### Timeline

- **CMS fields and guidance**:
    - **Accordion title** – *Timeline*
    - **Accordion subtitle** – State the overall start and end dates for *this* project.
    - **Accordion label 1 / Label 2** – Use keywords for key project phases or milestones.
    - **Accordion content** – Detail the schedule, including phases and their date ranges.
- **Example**:
    - **Accordion title** – Timeline
    - **Accordion subtitle** – June 2025 - June 2026
    - **Accordion label 1** – Data deletion
    - **Accordion label 2** – Lifecycle improvements
    - **Accordion content** – The estimated project duration is **June 16, 2025, to June 30, 2026**…

#### Support

- **CMS fields and guidance**:
    - **Accordion title** – *Support*
    - **Accordion subtitle** – Summarize the primary support channels for *this* project.
    - **Accordion label 1 / Label 2** – Use keywords for the types of support offered.
    - **Accordion content** – Provide clear, direct contact information and support resources.
- **Example**:
    - **Accordion title** – Support
    - **Accordion subtitle** – Contact the RDM team for questions and training
    - **Accordion label 1** – Training
    - **Accordion label 2** – Office hours
    - **Accordion content** – Support, training, and office hours will be offered… For questions, contact the **HMS IT Research Data Management team**.

#### **Optional accordion items**

- **Purpose** – To provide a structured way to include important information that does not fit into the five standard sections.
- **Guidance**:
    - Only add a new accordion if the information is **critical for the user to know** and represents a **distinct topic**.
    - The accordion title must be clear and descriptive.
    - The subtitle and labels must follow the same rule as the standard sections – be specific to the content within.
    - **Do not** create accordions for minor details or information that could be included in one of the standard sections.
- **Potential use cases**:
    - **Related policies** – For projects that introduce or rely on specific institutional policies.
    - **Technical specifications** – For projects where users need to know detailed technical requirements (for example, software versions, hardware compatibility).
