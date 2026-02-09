# Content guidelines for the HMS IT Quarterly Newsletter

*A comprehensive guide to the information architecture, content model, and editorial standards for the HMS IT Quarterly Newsletter.*

## Introduction

The introduction provides the “why” behind the document. In clear, paragraph prose, cover the following three sections:

- **Purpose of the document**: This document serves as the official playbook for creating the **HMS IT Quarterly Newsletter**. It provides a complete editorial framework, from high-level strategy to modular templates, to ensure every edition is consistent, effective, and flexible. Its primary audience is the content creators, editors, and managers responsible for producing the newsletter.
- **Scope and applicability**: These guidelines apply exclusively to the **HMS IT Quarterly Newsletter**, distributed to all **HMS faculty, staff, and students**. The modular system defined here is the mandatory structure for all quarterly editions to ensure brand alignment and a predictable reader experience.
- **Background and justification**: This governance is necessary to streamline the newsletter production process, making it **faster and more efficient** to assemble each issue. By establishing a clear, modular system with predefined rules for tone, length, and structure, we can consistently deliver high-quality, scannable, and action-oriented content that informs readers of key IT updates and reinforces the value of IT services.

### Related governance

- **Parent governance**: *[Link to broader, more general governance, for example, “HMS Digital Content Strategy”]*
- **Child governance**: *[Guidance to be determined]*
- **Related governance**: *[Link to documents on the same hierarchical level, for example, “HMS Brand and Voice Guidelines”]*

## Summary

This modular newsletter system is designed for scannability and clear calls to action. Every newsletter must be built from the approved content modules and adhere to the following core rules.

- **Modular structure**: Assemble each issue using the required modules: Welcome, “In This Edition,” 2-3 Flexible Content Modules, and a concluding Contact & Footer.
- **Action-oriented**: Every key message must have one clear, verb-driven call to action (CTA), preferably as a button.
- **Scannability is key**: Assume readers will skim. Use **bold keywords**, short paragraphs (1–3 sentences), bullet points, and clear, descriptive headlines.
- **Brevity and clarity**: Aim for a total word count of 600–800 words and a Grade 8–9 reading level. Link out to more detailed documentation rather than explaining everything in the newsletter.
- **Consistent tone**: Write in a professional, friendly, and helpful tone, as a knowledgeable peer sharing useful updates.

## Content guidelines

This is the core of the document. It must be structured to move from high-level strategy to specific, tactical instructions.

### Content brief

This section establishes the strategic foundation for the content type.

- **Objective**: To inform readers of key IT updates, drive specific actions (especially regarding security and compliance), and reinforce the value of IT services.
- **User needs**: Users need a clear, quick, and reliable way to learn about IT changes that affect them, understand required actions, and discover resources that can help them.
- **Business goals**: This content supports HMS IT’s objectives by increasing community engagement, ensuring compliance with security policies, promoting the use of strategic tools, and demonstrating IT’s value to the organization.
- **Audience**:
    - **Primary**: HMS faculty, staff, and students.
    - **Secondary**: HMS-affiliated researchers and administrators.
- **Tone**: Professional, friendly, and action-oriented. Write as a helpful and knowledgeable peer sharing useful updates, not as a corporate announcement.

### Content structure and components

Break the content type down into its core components in the order they appear. For each element, provide the following details:

#### Welcome Module

- **CMS field and HTML tag**: `[Welcome_Headline]` / `<h2>`, `[Welcome_Body]` / `<p>`, `[Welcome_CTA_Button]` / `<a class="button">`
- **Purpose**: To greet the reader warmly, set the context for the current issue, and invite engagement. This module is always the first in the newsletter.
- **Guidance**:
    - **Word count**: 50–80 words.
    - **Content**: Write 1–2 short, conversational paragraphs. Personalize the message to the time of year or academic calendar (e.g., “As the semester begins…”).
    - **Call to Action (CTA)**: Include one clear, low-effort CTA to encourage reader engagement, such as a link to a one-question survey.
- **Examples**:
    - ✅ Correct: *As the campus community welcomes the Class of 2029, we’re excited to share what’s been happening in IT with this new quarterly newsletter. We want this to be as helpful as possible, so we’d love to hear from you. Fill out our one-question reader survey to let us know what you want to see in future newsletters.*
    - ⛔ Incorrect: *This communication serves as the third-quarterly information dispatch from the Information Technology department. The purpose of this document is to disseminate information regarding recent departmental activities and strategic initiatives. It is our hope that the contents herein will prove to be of significant value to all stakeholders across the institution.*

#### “In This Edition” Module

- **CMS field and HTML tag**: `[Module_Title]` / `<h3>`, `[Bulleted_List]` / `<ul><li>`
- **Purpose**: To provide a scannable table of contents so readers can quickly find what is relevant to them.
- **Guidance**:
    - **Word count**: 40–60 words.
    - **Structure**: Use a bulleted list with 3–4 items.
    - **Content**: Each bullet should be a concise summary (~10-12 words) of a major section in the newsletter.
    - **Formatting**: Start each bullet point with a **bolded keyword** that matches the corresponding section’s headline.
- **Examples**:
    - ✅ Correct:

> **In this edition**

        - **Stay secure** by setting up Okta Verify for 2FA and using VPN on public Wi-Fi networks.
        - **Key projects** focus on modernizing spaces and streamlining administrative processes.
        - **Account access** has been updated to make eligibility more efficient and easier to understand.
    - ⛔ Incorrect:

> **What’s Inside This Newsletter**

        - This issue contains a detailed overview of the various security protocols that have been recently implemented, including but not limited to two-factor authentication and virtual private network usage guidelines for community members.
        - You will also find a comprehensive list of ongoing strategic projects.
        - Finally, we discuss updates to the account provisioning system.

#### Flexible Content Module

- **CMS field and HTML tag**: `[Module_Title]` / `<h2>`, `[Body_Text]` / `<p>`, `[CTA_Button]` / `<a class="button">`
- **Purpose**: To deliver the core messages of the newsletter, such as service updates, project highlights, or resource announcements. Each newsletter should contain 2-3 of these modules.
- **Guidance**:
    - **Word count**: 90–130 words per module.
    - **Headline**: Use a clear, benefit-driven headline of 7 words or less.
    - **Body**: Write 2–3 short paragraphs explaining the “what” and the “why.” Emphasize the value to the reader (e.g., improved security, efficiency, or access). Link to detailed documentation where appropriate, but limit hyperlinks to 1-2 per module.
    - **Call to Action (CTA)**: Include a single, clear CTA button with an action-oriented label (≤ 4 words).
- **Examples**:
    - ✅ Correct

> 👤 **Account Access Updates**

> A secure campus starts with secure personal accounts. With that in mind, the Identity and Access Management (IAM) team continually improves how accounts are provisioned. After more than two years of effort, IAM has made several key changes to streamline the process.

> These enhancements will make account management more efficient and easier for everyone to understand.

> **[BUTTON: Read the Guides]**

    - ⛔ Incorrect

> **Information Regarding Recent Modifications to the Identity and Access Management (IAM) System and Associated Protocols**

> Per the multi-year strategic plan outlined by the Identity and Access Management division, a series of system-wide enhancements have been successfully deployed. These changes are part of a long-term effort to optimize the procedural framework governing the provisioning and de-provisioning of user accounts across the institutional ecosystem, leveraging HUIT-supported software and processes to achieve greater operational synergy. For more information, click here.

> **[BUTTON: More Details]**

#### Urgent Campaign Block

- **CMS field and HTML tag**: `[Campaign_Headline]` / `<h2>`, `[Campaign_Body]` / `<p>`, `[Campaign_CTA_Button]` / `<a class="button">`
- **Purpose**: To drive one single, high-priority action, often related to security or compliance. Use this module for mandatory or time-sensitive tasks.
- **Guidance**:
    - **Word count**: 50–70 words.
    - **Headline**: Lead with a strong, action-oriented headline that functions as a command.
    - **Body**: Use a single, direct paragraph. Explain what the user needs to do, why it is critical, and how easy it is. Reinforce the benefit and urgency.
    - **Call to Action (CTA)**: The button text must be a clear command that mirrors the headline’s action.
- **Examples**:
    - ✅ Correct

> 🛡️ **Claim your computer to boost security**

> We’re asking all community members to take a moment to officially claim the primary computer you use for your University work. This quick, one-time process helps us protect institutional data, verify devices on our network, and ensure you’re eligible for IT support. It is crucial for complying with Harvard’s Information Security Policy.

> **[BUTTON: Claim Your Computer]**

    - ⛔ Incorrect

> **A Note on Device Attestation for Security Compliance**

> It has come to our attention that many users have not yet completed the necessary process of claiming their primary computer. This is an important step for a variety of reasons, including security and support eligibility. It would be beneficial for all personnel to complete this process at their earliest convenience to ensure they are in compliance with university policy.

> **[BUTTON: Click Here to Proceed]**

#### Contact & Footer Module

- **CMS field and HTML tag**: `[Static_Footer_Block]` / `<div>`
- **Purpose**: To provide standardized contact information and legal boilerplate. This module is always the last in the newsletter.
- **Guidance**:
    - **Consistency is mandatory**. This module must be uniform across all issues to ensure brand recognition and provide a reliable resource for users seeking help.
    - **Do not alter** the structure, contact methods, or legal text without approval from IT leadership and Communications.
- **Examples**:
    - ✅ Correct

> **Contact HMS IT**

> We’re here to help with all your technology questions, requests, and issues:

        - [HMS IT Service Portal](link)
        - [Email: itservicedesk@hms.harvard.edu](mailto:itservicedesk@hms.harvard.edu)
        - [**Phone:** 617-432-2000] (Mon–Fri, 8:00 AM–5:00 PM)
        - [**In-person support:** TMEC Room 225] (Mon–Fri, 9:00 AM–4:00 PM)

> **Harvard Medical School — Information Technology**

> © [Year] The President and Fellows of Harvard College

> [View in browser](link) | [Unsubscribe](link)

    - ⛔ Incorrect

> **Get in touch!**

> Got a problem? Email the service desk. Or you can call us. We also have a walk-up desk.

> © [Year] Harvard. All rights reserved.
