--[[
DEPRECATED: This filter is deprecated in favor of style_filter.lua

golden_fixture_styles.lua - Simple Pandoc filter for golden fixture testing
Handles only character styles without modifying heading structure

MIGRATION: Use style_filter.lua with PANDOC_FILTER_MODE=golden_fixture:
- All golden_fixture_styles.lua functionality
- Same simplified behavior for testing
- Unified filter management

Old usage: pandoc input.md --lua-filter core/filters/golden_fixture_styles.lua --reference-doc core/utils/reference.docx -o output.docx
New usage: PANDOC_FILTER_MODE=golden_fixture pandoc input.md --lua-filter core/filters/style_filter.lua --reference-doc core/utils/reference.docx -o output.docx

This file is kept temporarily for backwards compatibility but will be removed.
--]]

-- Utilities
local utils = require 'pandoc.utils'

-- Process inline elements to convert <kbd> tags
function Inlines(inlines)
  local result = {}
  local i = 1

  while i <= #inlines do
    local el = inlines[i]

    -- Check for <kbd> pattern
    if el.t == 'RawInline' and el.format == 'html' and el.text == '<kbd>' then
      -- Look for content and closing tag
      local content = {}
      local j = i + 1
      local found_close = false

      -- Collect content until we find </kbd>
      while j <= #inlines do
        local next_el = inlines[j]
        if next_el.t == 'RawInline' and next_el.format == 'html' and next_el.text == '</kbd>' then
          found_close = true
          break
        else
          table.insert(content, next_el)
        end
        j = j + 1
      end

      if found_close then
        -- Create Span with Input style
        local input_span = pandoc.Span(content, {["custom-style"] = "Input"})
        table.insert(result, input_span)
        i = j + 1 -- Skip past the </kbd> tag
      else
        -- No closing tag found, keep original
        table.insert(result, el)
        i = i + 1
      end
    else
      table.insert(result, el)
      i = i + 1
    end
  end

  return result
end

function Code(el)
  -- Check if the code element has kbd class or is marked as keyboard input
  if el.classes:includes("kbd") then
    -- Convert to Span with Input style instead of Code
    return pandoc.Span(
      {pandoc.Str(el.text)},
      {["custom-style"] = "Input"}
    )
  else
    -- Apply Code character style to all other inline code
    return pandoc.Span(
      {pandoc.Str(el.text)},
      {["custom-style"] = "Code"}
    )
  end
end

function CodeBlock(el)
  -- Convert CodeBlock to Div with custom-style for proper Word formatting
  -- This is necessary because Pandoc doesn't apply custom-style to CodeBlock elements

  -- Split code text into lines and create separate paragraphs for each line
  local paras = {}
  for line in el.text:gmatch("([^\r\n]*)\r?\n?") do
    if line ~= "" then
      -- Create a paragraph for each line to preserve line breaks
      table.insert(paras, pandoc.Para({pandoc.Str(line)}))
    elseif line == "" and #paras > 0 then
      -- Add empty paragraph for blank lines
      table.insert(paras, pandoc.Para({pandoc.Str("")}))
    end
  end

  -- If no content, create single paragraph
  if #paras == 0 then
    paras = {pandoc.Para({pandoc.Str(el.text)})}
  end

  -- Return as Div with Code block custom style (font styling handled by reference document)
  return pandoc.Div(paras, {["custom-style"] = "Code block"})
end

-- Track if we've seen the first header (make it Title style)
local first_header_seen = false

function Header(el)
  if not first_header_seen and el.level == 1 then
    first_header_seen = true
    -- Convert first H1 to Title style instead of Heading 1
    return pandoc.Div(
      {pandoc.Para(el.content)},
      {["custom-style"] = "Title"}
    )
  end
  return el
end

--[[
Filter processes elements in this order:
1. Header: Converts first H1 to Title style
2. Inlines: Processes <kbd> tags to Input character style
3. Code: Processes `inline code` and `code`{.kbd} to Code character style
4. CodeBlock: Processes ```code blocks``` to Code block paragraph style

All elements are converted to use appropriate custom character or paragraph styles.
--]]
