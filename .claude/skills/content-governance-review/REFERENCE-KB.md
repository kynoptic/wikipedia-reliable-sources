# Knowledge base content governance

Knowledge base-specific guidelines for HMS IT Service Portal articles to ensure findability, clarity, and consistency.

## Summary

**Write evergreen content** - Exclude temporary information that will be outdated in less than a year.

**Choose the appropriate article type:**
- **How-to guide** – Solutions for specific, real-world user problems
- **Tutorial** – Introductions for new users, focusing on teaching
- **Reference** – Comprehensive lists of options, policies, and details
- **Background information** – How a service is configured (HMS IT staff only)

**Article metadata:**
- **Article category** – "Public" or "HMS IT Staff"
- **Short description** – Sentence case, action-oriented titles matching user search terms

**Article body:**
- **Introduction** – Brief intro if title doesn't fully describe scope
- **Prerequisites** – Include only if unique or unclear
- **Screenshots** – Supplement text, focus on relevant portions, and ensure visibility
- **Contact information** – Generally omit (portal provides "Get help" links)

---

## Evergreen content requirement

**Critical rule:** Content must remain accurate and relevant for at least one year.

**What to exclude:**
- Temporary information
- Time-specific updates ("next month" and "recently")
- References to current events or versions that will change
- Announcements or news items

**Examples of violations:**
- ❌ "The new interface was released last month"
- ✅ "The current interface includes..."
- ❌ "We will be upgrading the system in January"
- ✅ "Contact HMS IT if you need assistance with system upgrades"

---

## Article types

### How-to guide

**User question:** "How do I do this one thing?"

**Purpose:** Address a single, specific, common problem

**Characteristics:**
- Help users fix errors or complete tasks
- Structured around tasks, not features
- Keep user goal in mind
- Avoid unnecessary details or unlikely scenarios
- Focus on solving problems, not teaching

**Priority:** This is the most sought-after type; prioritize in knowledge base

**Title format:** VERB the NOUN in CONTEXT
- Examples:
  - "Change your password in Dropbox"
  - "Install Ivanti Secure Access Client on Windows"

### Tutorial

**User question:** "How do I generally use this thing?"

**Purpose:** Guide new users through simple exercises to teach and orient

**Characteristics:**
- Familiarize user with interface or process
- Can be titled "Getting started" or "Introduction to X"
- May duplicate vendor documentation if HMS-specific context needed

**Title format:** Getting started with CONTEXT
- Examples:
  - "Getting started with VPN"
  - "Getting started with Canvas"

### Reference document

**User question:** "What are all these things?"

**Purpose:** Exhaustively list options, fields, attributes, and details

**Characteristics:**
- Comprehensive lists
- Not for link lists or navigation aids
- Focuses on completeness

**Title format:** OPTIONS in CONTEXT
- Examples:
  - "Privacy settings in Zoom"
  - "Types of email notifications in STAT"

### Background information

**User question:** "How does this thing work?"

**Purpose:** Explain why and how a service is set up

**Characteristics:**
- Most useful for internal knowledge base (HMS IT staff)
- Valuable for institutional knowledge
- Rarely of interest to external users

---

## Article metadata

### Article category

**Required values:**
- **Public** – Accessible to all users
- **HMS IT Staff** – Internal documentation only

### Short description (title) guidelines

**Formatting:**
- Use sentence case
- Action-oriented
- Match user search terms
- Keep short and distinctive

**Title patterns by type:**

| Article type | Title pattern | Examples |
| --- | --- | --- |
| How-to | VERB the NOUN in CONTEXT | Change your password in Dropbox<br>Install Ivanti Secure Access Client on Windows |
| Reference | OPTIONS in CONTEXT | Privacy settings in Zoom<br>Types of email notifications in STAT |
| Tutorial | Getting started with CONTEXT | Getting started with VPN<br>Getting started with Canvas |

**Best practices:**

Don't start with "how to":
- ❌ "How to set up Ivanti Secure Access Client (VPN) for secure remote access"
- ✅ "Establish a VPN connection"

Make titles distinctive:
- ❌ "Set up CrashPlan", "Using CrashPlan", "Configure CrashPlan" (too similar)
- ✅ "Download and install CrashPlan", "Learn the CrashPlan interface", "Recommended CrashPlan settings" (distinctive)

Match user language:
- Use terms users search for
- Reflect users' word choices
- Avoid internal jargon

Avoid redundancy:
- Don't repeat information from category or other metadata
- Keep focused on unique identifiers

---

## Article body elements

### Introduction

**When to include:**
- Title doesn't fully capture the article's scope
- Additional context would be helpful

**Format:**
- Brief (1-2 sentences)
- Simple language: "This article covers X, Y, and Z"
- No heading label (just start with paragraph text)

**When to omit:**
- Title is self-explanatory
- Scope is clear from metadata

### Prerequisites

**When to include:**
- Prerequisites are unique or unclear
- Not obvious from context

**When to omit:**
- Obvious prerequisites (internet connection, HMS account)
- Assumable from article title (e.g., don't mention needing Dropbox account in Dropbox troubleshooting article)

**Formatting:**
- Include in introductory paragraph if brief
- Use separate heading only if substantial

### Screenshots

**Purpose:**
- Supplement text guidance (don't replace it)
- Help users confirm correct location in interface
- Maintain accessibility (documentation must work without screenshots)

**When to use:**
- Significant interface changes
- Complex UI navigation
- Confirming user location in workflow

**Technical requirements:**
- Place directly after text they illustrate
- Each screenshot on separate line (creates text break)
- Include only relevant portion of screen
- Don't scale before uploading (causes distortion)
- Consider mobile viewing

**Image sizing:**
```html
<img style="max-width: 100%; height: auto;">
```

**Borders:**
- Add 1px solid black border unless image has one
- Use WYSIWYG: Insert/edit image → Border Thickness = 1
- Or use HTML:
```html
<img style="border: 1px solid black; max-width: 100%; height: auto;">
```

**Best practices:**
- Focus on relevant portions only
- Ensure legibility on all screen sizes
- Place images to break up text for readability

### Contact information

**Default:** Do not include

**Why:** HMS IT Service Portal provides persistent "Get help" and "Submit a ticket" links

**Exception:** Include only when article requires second- or third-tier direct contact

---

## Article type selection guide

**Decision tree:**

1. **Is the user trying to solve a specific problem or complete a task?**
   - Yes → How-to guide

2. **Is the user new and needs general orientation?**
   - Yes → Tutorial

3. **Does the user need a comprehensive list or reference?**
   - Yes → Reference document

4. **Is this explaining internal HMS IT configuration?**
   - Yes → Background information (mark as "HMS IT Staff")

**Avoid mixing types:**
- If an article covers multiple types, split into separate documents
- Example: One doc for step-by-step instructions (how-to), another for all available options (reference)

---

## Common governance violations and recommended fixes

### Evergreen violations
| Violation | Fix |
| --- | --- |
| "We upgraded the system last month" | "The system includes..." |
| "This feature will be available in Q2" | "Contact HMS IT for information about upcoming features" |
| "The new version was released recently" | "The current version is..." |

### Title violations
| Violation | Fix |
| --- | --- |
| "How to install VPN" | "Install Ivanti Secure Access Client on Windows" |
| "VPN setup guide" | "Establish a VPN connection" |
| "Information about Zoom settings" | "Privacy settings in Zoom" |

### Content type violations
| Violation | Issue | Fix |
| --- | --- | --- |
| How-to guide with exhaustive option list | Mixing how-to and reference | Split into two articles: "Configure Zoom for privacy" (how-to) and "Privacy settings in Zoom" (reference) |
| Tutorial solving specific problem | Mixing tutorial and how-to | Make it a tutorial (general orientation) or how-to (specific problem) |

---

## Complete source files

For detailed KB governance including workflows and organization:

- `governance/Knowledge base/Style guide for knowledge base articles on the HMS IT Service Portal.md`
- `governance/Knowledge base/Organization of knowledge base articles on the HMS IT Service Portal.md`
- `governance/Knowledge base/Workflow for knowledge base articles on the HMS IT Service Portal.md`
