# Style guide for knowledge base articles on the HMS IT Service Portal

*Extends the HMS IT style guide to address knowledge base articles*

## Table of contents

## Introduction

This document provides a comprehensive **style guide for creating and maintaining knowledge base articles on the HMS IT Service Portal**. It aims to enhance our end-user documentation's findability, clarity, consistency, and professionalism. By following these guidelines, content creators and managers can help our community locate, trust, and understand the information they need more quickly.

This style guide applies to all **public and HMS community knowledge base articles in the HMS IT Service Portal**. It is intended for knowledge creators, editors, and managers responsible for developing and updating user documentation. The guidelines cover various elements, including metadata, article structure, and images, to ensure a standardized approach to documentation.

The guidelines in this document are informed by **best practices from technical writing literature and style guides from established technology companies**. While creating a style guide as comprehensive as these sources is unnecessary, this document distills the most impactful recommendations relevant to the HMS IT knowledge base. The goal is to provide practical and user-centered guidance that helps maintain our documentation's high quality and usability.

## Related governance

- [Style guide for HMS IT](https://hu.sharepoint.com/:w:/r/sites/HMSITAllStaff-Internal/IT%20Internal%20documents/Communications%20governance/General/Style%20guide%20for%20HMS%20IT.docx?d=w8a11c11ff9e54fe699d3666fc45c1361&csf=1&web=1&e=zeeGoP)
- [Workflow for knowledge base articles on the HMS IT Service Portal](https://hu.sharepoint.com/:w:/r/sites/HMSITAllStaff-Internal/IT%20Internal%20documents/Communications%20governance/Knowledge%20base/Workflow%20for%20knowledge%20base%20articles%20on%20the%20HMS%20IT%20Service%20Portal.docx?d=wcc522b8d13ef4ba1ac0b7f137e1f5ad8&csf=1&web=1&e=cc3RSC)

## Summary

Write evergreen content.

Choose the appropriate article type and stick to it:

- **How-to guide** – Solutions for specific, real-world user problems.
- **Tutorial** – Introductions for new users, focusing on teaching.
- **Reference** – Comprehensive lists of options, policies, and details.
- **Background information** – This covers how a service is configured for HMS IT staff.

For article metadata:

- **Article category** – Categorize articles as "Public" or "HMS IT Staff."
- **Short description** – Use sentence case and action-oriented titles that match users' search terms. Avoid vague or redundant titles.

For the body of the article:

- **Introduction** – Provide a brief intro if the title doesn't fully describe the article's scope.
- **Prerequisites** – Include only if unique or unclear; avoid listing obvious prerequisites.
- **Screenshots** – Supplement text with screenshots, focus on relevant portions, and ensure they are easy to see and appropriately sized for different screens.
- **Contact information** – Generally, do not include contact details because users can access help through the HMS IT Service Portal.

## Style guide

### Keep content evergreen

Ensure that documentation remains evergreen by excluding temporary information and updates. If content will become outdated in less than a year, do not include it.

### Consider the article type

Knowledge base articles fall into several primary categories. Before drafting or revising an article, determine which type best fits the content. Stick to that type to ensure clear and focused documentation. When splitting long articles that mix types into separate documents, consider splitting by type. For example, one document can cover step-by-step instructions, while another lists all the available options as part of the process.

#### How-to guide

*How do I do this one thing?*

How-to guides address a single, specific, common problem. They help users fix errors or complete tasks. Unlike tutorials, which aim to familiarize users with a process, how-to guides focus on solving problems. Structure these guides around tasks, not features. Keep the user goal in mind and avoid unnecessary details or unlikely scenarios.

This type of documentation is the most sought-after and should be prioritized in the knowledge base.

#### Reference document

*What are all these things?*

Reference documents list options, fields, attributes, and other details about a service or software exhaustively. Avoid using knowledge base articles for link lists or web content navigation aids.

#### Educational tutorial

*How do I generally use this thing?*

Tutorials guide new users through simple exercises to teach and orient them. The goal is to familiarize the user with the interface or process. These can be called *Getting started* or *Introduction to X*.

Tutorials are often included in in-app onboarding experiences or provided by the app's producer. While duplication of existing documentation is unnecessary, tutorials specific to the HMS community may be needed.

#### Background information

*How does this thing work?*

Background information is most useful for the internal knowledge base for HMS IT staff. It explains why and how a service is set up. This type of documentation is rarely of interest to external users but is valuable for internal understanding and institutional knowledge.

### Article elements

#### Metadata

##### Article category

When setting the article category, use either **Public** or **HMS IT Staff**.

##### Short description guidelines

For the short description, which is the title for the article, use sentence case and follow these guidelines:

|Article type|User need|Short description|Examples|
| --- | --- | --- | --- |
|How-to|Doing a specific task|***VERB*** the ***NOUN*** in ***CONTEXT***|Change your password in Dropbox<br>Install Ivanti Secure Access Client on Windows|
|Reference|Gathering information|***OPTIONS*** in ***CONTEXT***|Privacy settings in Zoom<br>Types of email notifications in STAT|
|Tutorial|Getting oriented|Getting started with ***CONTEXT***|Getting started with VPN<br>Getting started with Canvas|

Use short, descriptive, action-oriented titles.

Don’t start the title with *how to*, simply describe the action that the article will help the user complete.

Match the language in the title to how users search for documentation. Reflecting users' word choices makes it easier for them to find what they need.

- ❌ Setting up Ivanti Secure Access Client (VPN) for secure remote access
- ✅ Establish a VPN connection

Make your title distinctive. Unique titles reduce the number of choices a user makes when searching for documentation.

- ❌ Set up CrashPlan, Using CrashPlan, Configure CrashPlan
- ✅ Download and install CrashPlan, Learn the CrashPlan interface, Recommended CrashPlan settings

#### Body

##### Introduction

Include a brief introduction if the article title doesn't capture the scope of the article. If it's unclear what the article is about from the title, include that information in a sentence or two at the top. Keep it simple, such as "This article will cover X, Y, and Z."

Do not use a heading to label the introduction. Just enter the paragraph text at the top of the article.

##### Prerequisites

Only include prerequisites if they are unique or unclear from the article's context. Many prerequisites, like an internet connection or an HMS account, can be assumed. Readers will also assume some prerequisites based on the article's title, so you don't need to specify that a user needs a Dropbox account in a troubleshooting article about Dropbox, for example.

Only use a heading for prerequisites if they are substantial. Most prerequisites can be covered in the introductory paragraph.

##### Screenshots

Follow these guidelines to use screenshots effectively in your documentation:

- **Supplement with text** – Screenshots support text guidance; they don't replace it. To maintain accessibility, ensure the documentation is understandable even without the screenshots.
- **Orient users** – Use screenshots to help users confirm they are in the correct place within an interface. Place screenshots when there is a significant interface change. Place screenshots directly after the text they illustrate. Put each screenshot on a separate line, creating a break in the text to improve legibility.
- **Focus on relevant portions** – Include only the relevant part of the screen in the screenshot. Avoid capturing unnecessary areas.
- **Make them easy to see** – Do not scale screenshots before uploading. Scaling can distort the image, making it hard to follow. Consider how the image will look on a phone, and size images appropriately. Use a style tag to make images adapt to different screen sizes:
```html
`<img style="max-width: 100%; height: auto;">`
```
- **Add borders** – Add a 1px solid black border to images unless the image already includes a border. You can do this by selecting the image, choosing **Insert/edit image** in the WYSIWYG toolbar, and setting **Border Thickness** to 1. Alternatively, use this HTML styling to add a border and make images adapt to different screen sizes:
```html
`<img style="border: 1px solid black; max-width: 100%; height: auto;">`
```
#### Contact information

Don't include contact information. Users browse these articles in the HMS IT Service Portal, which provides persistent links to "Get help" or "Submit a ticket," so you rarely need to include this. Include contact information only if the article requires a second- or third-tier direct contact.

## Sources

These resources build on the sources used for the main HMS IT style guide. They focus on user documentation.

- Federal Aviation Administration, Human Factors Branch. "User documentation," in "Human Factors Design Standard (HF-STD-001B)," 2016. [https://hf.tc.faa.gov/publications/2016-12-human-factors-design-standard/](https://hf.tc.faa.gov/publications/2016-12-human-factors-design-standard/).
    - This government policy document improves air travel safety by making interfaces, signage, and equipment used by the FAA more straightforward. It includes a section (5.13) on user documentation with precise and valuable recommendations.
- Procida, Daniele. "Documentation System." Divio. Accessed June 30, 2020. [https://documentation.divio.com/](https://documentation.divio.com/).
    - Daniele Procida provides a helpful scheme for categorizing documentation into four general groups: tutorials, how-to guides, explanations, and references. This resource outlines those categories and recommends optimizing each type of documentation.
- Paradis, James G., and Muriel L. Zimmerman. *The MIT Guide to Science and Engineering Communication*. 2nd ed. Cambridge, Mass: MIT Press, 2002.
    - Though this MIT guide is meant for engineers and scientists, a section is dedicated to "Instructions, Procedures, and Computer Documentation." The "Brief Handbook of Style and Usage" in the appendix is practical, as are the sections on collaborative writing and defining your audience and aims.
