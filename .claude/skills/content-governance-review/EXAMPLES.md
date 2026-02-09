# Content Governance Review - Usage Examples

Detailed examples demonstrating how the content governance review skill works in different scenarios.

## Example 1: Quick Email Review

### User Request
```
Quick check on this email draft before I send it
```

### Skill Response
```
[Performs Quick Scan of email content]

## Content Governance Review: Quick Scan

**Content Type**: Broadcast Email
**Critical Issues Found**: 4
**Auto-fixable**: 4

### Critical Issues

#### 1. Formatting - Title case in subject line (Line 1)
**Current**: "Network Interruptions On June 27"
**Fix**: "Network interruptions on June 27"
**Severity**: Critical - Subject lines must use sentence case
**Auto-fixable**: Yes

#### 2. Word Usage - Non-descriptive link (Line 12)
**Current**: "Click here for more information"
**Fix**: "Read more about network maintenance on the HMS IT website"
**Severity**: Critical - Violates phishing prevention guidelines
**Auto-fixable**: Yes

#### 3. Word Usage - Use of "PC" (Line 15)
**Current**: "Restart your PC after the upgrade"
**Fix**: "Restart your computer after the upgrade"
**Severity**: Critical - Word list violation
**Auto-fixable**: Yes

#### 4. Platform-Specific - Missing time zone (Line 8)
**Current**: "from 6:00 AM to 1:00 PM"
**Fix**: "from 6:00 AM to 1:00 PM EDT (UTC-4)"
**Severity**: Critical - Time zones required in outage notifications
**Auto-fixable**: Yes

---

All 4 issues are auto-fixable. Shall I apply these corrections?
```

### User Approval
```
Yes, fix them
```

### Skill Completion
```
[Applies all fixes using Edit tool]

✅ Fixed 4 critical issues:
- Changed subject line to sentence case
- Updated link text to be descriptive
- Replaced "PC" with "computer"
- Added time zone "EDT (UTC-4)"

Your email is now ready to send!
```

---

## Example 2: Comprehensive KB Article Review

### User Request
```
Full governance review of KB0012345
```

### Skill Response
```
[Reads KB article, performs Comprehensive Review]

## Content Governance Review: Comprehensive

**Content Type**: Knowledge Base Article
**Total Issues Found**: 38
**Critical**: 2 | **Important**: 12 | **Minor**: 24
**Auto-fixable**: 28

### Critical Issues (2)

#### 1. Content Type - Non-evergreen content (Line 23)
**Issue**: Temporal reference "next month"
**Current**: "The new interface will be available next month"
**Fix**: "The new interface will be available soon" or "Contact HMS IT for availability"
**Severity**: Critical - KB articles must be evergreen (remain accurate for 1+ year)
**Auto-fixable**: No - Context-dependent rewrite needed

#### 2. Metadata - Article type mismatch (Line 1-5)
**Issue**: Content is tutorial but marked as how-to guide
**Current**: Article category marked as "How-to guide"
**Analysis**: Content teaches general interface usage (tutorial) rather than solving specific problem (how-to)
**Fix**: Change article type to "Tutorial" and retitle as "Getting started with VPN"
**Severity**: Critical - Affects discoverability and user expectations
**Auto-fixable**: No - Requires metadata change and potential retitle

### Important Issues (12)

#### Voice/Tone (3 issues)
- Line 45: Passive voice "The settings can be changed" → "Change the settings"
- Line 67: Rhetorical question "Need help?" → "Contact support"
- Line 89: Future tense "You will see" → "You see"

#### Word Usage (7 issues)
- Lines 12, 34, and 56: "click" → "select" (3 occurrences)
- Line 78: "application" → "app" (mobile context)
- Line 92: "i.e." → "that is"
- Line 103: "PC" → "computer"
- Line 145: "please" → omit (unnecessary)

#### Formatting (2 issues)
- Line 28: Curly quotes "..." → Straight quotes "..."
- Line 112: Missing monospace for file path

### Minor Issues (24)

[Brief listing of 24 minor issues including Oxford commas, spacing, paragraph length]

---

**Batch Fix Available**: 28 issues can be automatically corrected.

The 2 critical issues and some important issues require manual attention:
- Rewrite non-evergreen content (Line 23)
- Correct article type classification
- Manual voice/tone improvements

Would you like me to:
1. Apply the 28 auto-fixes first?
2. See detailed breakdown of all issues by category?
3. Focus on just critical and important issues?
```

### User Choice
```
Apply the auto-fixes first
```

### Skill Completion
```
[Applies 28 auto-fixes]

✅ Fixed 28 issues:
- **Word usage** (10): Replaced "click" with "select", "PC" with "computer", removed "please", etc.
- **Formatting** (12): Fixed quotes, added monospace to paths, and corrected spacing
- **Structure** (6): Added Oxford commas and fixed list formatting

Remaining issues require manual review:
- **Line 23**: Rewrite "next month" for evergreen content
- **Article type**: Change from how-to to tutorial
- **Voice/tone**: 3 passive voice instances need context-aware rewrites

Would you like guidance on addressing these manual fixes?
```

---

## Example 3: Targeted Word List Check

### User Request
```
Check this document against the word list
```

### Skill Response
```
[Performs Targeted Review - Word Usage only]

## Content Governance Review: Targeted (Word Usage)

**Content Type**: General Documentation
**Word List Violations Found**: 15
**All violations are auto-fixable**

### Violations by Category

#### Non-inclusive language (2 violations)
- Line 67: "blacklist" → "blocklist"
- Line 134: "master/slave" → "primary/secondary"

#### Device-specific verbs (6 violations)
- Lines 12, 23, 45, 67, 89, and 102: "click" → "select"

#### Platform references (3 violations)
- Lines 34, 56, and 78: "PC" → "computer"

#### Software terminology (2 violations)
- Lines 41 and 93: "application" → "app" (mobile/web context)

#### Unnecessary politeness (1 violation)
- Line 89: "please restart" → "restart" (implies optional action)

#### Non-descriptive links (1 violation)
- Line 102: "click here" → use descriptive link text

#### Latin abbreviations (1 violation)
- Line 134: "i.e." → "that is"

---

**Summary by line**:
- Line 12: "click" → "select"
- Line 23: "click" → "select"
- Line 34: "PC" → "computer"
- Line 41: "application" → "app"
- Line 45: "click" → "select"
- Line 56: "PC" → "computer"
- Line 67: "blacklist" → "blocklist" and "click" → "select"
- Line 78: "PC" → "computer"
- Line 89: "please restart" → "restart" and "click" → "select"
- Line 93: "application" → "app"
- Line 102: "click here" → descriptive link and "click" → "select"
- Line 134: "master/slave" → "primary/secondary" and "i.e." → "that is"

All 15 violations are auto-fixable. Apply batch fix?
```

### User Approval
```
Yes
```

### Skill Completion
```
✅ Fixed 15 word list violations:
- 6 device-specific verbs
- 3 platform references
- 2 non-inclusive terms
- 2 software terminology
- 1 unnecessary politeness
- 1 non-descriptive link

Your document now complies with the HMS IT word list!
```

---

## Example 4: Ambiguous Fix Requiring Clarification

### User Request
```
Review this document and fix issues
```

### Skill Response
```
[Reviews content, identifies issues including ambiguous case]

Found 12 issues total, 11 are straightforward auto-fixes.

However, I found an ambiguous situation on line 45:

**Current**: "Use the mobile application or desktop application to access your files"

**Issue**: The word list typically recommends "app" instead of "application", but this context refers to enterprise software (Code42 for Enterprise) where "application" may be more appropriate for desktop software.

**Options**:
1. **Standard word list rule**: Replace with "app"
   - Result: "Use the mobile app or desktop app to access your files"
   - Pro: Consistent with word list, simpler language
   - Con: "Desktop app" may not accurately describe complex enterprise software

2. **Enterprise software exception**: Keep "application" for desktop, use "app" for mobile
   - Result: "Use the mobile app or desktop application to access your files"
   - Pro: More accurate for enterprise software context
   - Con: Mixed terminology

3. **Keep both as "application"**: Maintain consistency in sentence
   - Result: "Use the mobile application or desktop application to access your files"
   - Pro: Consistent within sentence, appropriate for enterprise context
   - Con: Word list recommends "app" for mobile

Which option should I use?
```

### User Choice
```
Option 2 - use "app" for mobile and "application" for desktop
```

### Skill Completion
```
✅ Fixed 12 issues:
- **Line 45**: Updated to "Use the mobile app or desktop application" (mixed terminology for context accuracy)
- **Other 11 fixes**: Standard word list replacements and formatting corrections

All fixes applied successfully!
```

---

## Example 5: Email with Phishing Pattern Warning

### User Request
```
Review this email about password updates
```

### Skill Response
```
[Performs review, detects phishing-like patterns]

## Content Governance Review: Quick Scan

**Content Type**: Broadcast Email
**Critical Issues Found**: 6 (including 3 phishing-like patterns)

⚠️ **CRITICAL: This email contains patterns commonly found in phishing attacks**

### Phishing-Like Patterns Detected

#### 1. Urgent action request (Line 8)
**Current**: "You must update your password immediately or your account will be suspended"
**Issue**: Creates false urgency and mentions negative consequences near call-to-action
**Fix**: "Update your password by Friday, June 30, to maintain access to HMS services"
**Why it matters**: Phishing emails use urgency and threats to pressure users

#### 2. Generic salutation (Line 1)
**Current**: "Dear User:"
**Issue**: Generic greeting (not personalized)
**Fix**: "Dear Members of the HMS Community:" or "Dear [First-name Last-name]:"
**Why it matters**: Phishing emails often use generic greetings

#### 3. Direct link to login page (Line 12)
**Current**: "Update your password at https://accounts.hms.harvard.edu"
**Issue**: Direct link to authentication page
**Fix**: "Visit the HMS IT website at it.hms.harvard.edu and select 'Account Management' to update your password"
**Why it matters**: Phishing emails include direct links to fake login pages

### Other Critical Issues

#### 4. Non-descriptive link text (Line 15)
**Current**: "Click here for more information"
**Fix**: "Read the password policy on the HMS IT website"

#### 5. Use of "immediately" (Line 8)
**Current**: "immediately"
**Fix**: Provide specific deadline (e.g., "by June 30")

#### 6. Missing time zone (Line 10)
**Current**: "before 5:00 PM on Friday"
**Fix**: "before 5:00 PM EDT (UTC-4) on Friday, June 30"

---

**Recommendation**: This email needs significant revision to avoid training users to respond to phishing attempts. Consider alternative communication methods for password-related instructions.

Would you like me to suggest a rewritten version that maintains security best practices?
```

---

## Example 6: Quick Structure Check

### User Request
```
Just check the structure and formatting of this KB article
```

### Skill Response
```
[Performs Targeted Review - Structure and Formatting only]

## Content Governance Review: Targeted (Structure & Formatting)

**Content Type**: Knowledge Base Article

### Structure Issues (5)

#### 1. Heading vagueness (Line 12)
**Current**: "# Introduction"
**Fix**: "# What this article covers" or remove (title should be sufficient)
**Severity**: Important - Avoid vague headings

#### 2. Paragraph length (Lines 45-56)
**Current**: 9 sentences in single paragraph
**Fix**: Split into 2-3 paragraphs (ideal 3-4 sentences each, max 6)
**Severity**: Important - Readability

#### 3. Non-parallel list (Lines 67-72)
**Current**:
- Installing the software
- You should configure the settings
- Restarting is necessary

**Fix**: Make parallel:
- Install the software
- Configure the settings
- Restart your computer

**Severity**: Important - Consistency

#### 4. Stacked headings (Lines 89-91)
**Current**: ## Prerequisites immediately followed by ### Required software
**Fix**: Add introductory sentence between headings
**Severity**: Minor - Document flow

#### 5. Numbered headings (Line 102)
**Current**: "## 3. Configuration"
**Fix**: "## Configuration" (remove numbering)
**Severity**: Minor - Heading best practices

### Formatting Issues (7)

#### 1. Title case heading (Line 23)
**Current**: "## Configure Your Settings"
**Fix**: "## Configure your settings"
**Severity**: Critical - Must use sentence case

#### 2. Missing monospace (Line 34)
**Current**: "Navigate to the Downloads folder"
**Fix**: "Navigate to the `Downloads` folder"
**Severity**: Important - File paths need monospace

#### 3-7. Additional formatting (Lines 56, 78, 92, 103, and 134)
- Curly quotes → straight quotes
- Missing Oxford commas
- Inconsistent spacing

---

All 12 issues (5 structure + 7 formatting) are auto-fixable except for:
- Paragraph splitting (Line 45-56) - Requires content judgment
- Adding intro text between stacked headings - Requires context

Apply the 10 auto-fixable formatting and structure fixes?
```

---

## Testing scenarios for skill discovery

Use these phrases to verify the skill is discovered appropriately:

### Should trigger the skill
- "Review this email draft"
- "Check this against the style guide"
- "Does this follow our content governance?"
- "Editorial review of this KB article"
- "Validate content quality"
- "Style compliance check"
- "Quick scan of this document"
- "Check for word list violations"

### Should not trigger (wrong domain)
- "Review this code for bugs" (code review, not content)
- "Check this SQL query" (technical review)
- "Analyze this data" (data analysis)

### Edge cases to monitor
- "Review this documentation" - Could be content or code docs, skill should clarify
- "Check this for errors" - Too vague, but skill could offer content review as option
