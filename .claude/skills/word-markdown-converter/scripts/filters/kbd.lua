--[[
DEPRECATED: This filter is deprecated in favor of style_filter.lua

kbd.lua - Pandoc filter for Word-to-Markdown conversion
Maps <kbd> HTML elements to Word's "Input" character style

MIGRATION: Use style_filter.lua instead which provides:
- All kbd.lua functionality
- Additional character and paragraph style mapping
- Document structure transformations
- Configurable modes for different use cases

Old usage: pandoc input.md --lua-filter core/filters/kbd.lua --reference-doc core/utils/reference.docx -o output.docx
New usage: pandoc input.md --lua-filter core/filters/style_filter.lua --reference-doc core/utils/reference.docx -o output.docx

This file is kept temporarily for backwards compatibility but will be removed.
--]]

function RawInline(el)
  -- Handle <kbd> tags by converting them to spans with Input style
  if el.format == "html" then
    local kbd_pattern = "<kbd>(.+)</kbd>"
    local content = el.text:match(kbd_pattern)

    if content then
      -- Return a Span with the Input character style
      return pandoc.Span(
        {pandoc.Str(content)},
        {["custom-style"] = "Input"}
      )
    end
  end

  -- Return unchanged if not a kbd element
  return el
end

function Span(el)
  -- Handle spans with kbd class (alternative syntax: [text]{.kbd})
  if el.classes:includes("kbd") then
    -- Apply Input character style
    el.attributes["custom-style"] = "Input"
    return el
  end

  -- Return unchanged if not kbd class
  return el
end

-- Also handle Code elements that should be keyboard input
function Code(el)
  -- Check if the code element has kbd class or is marked as keyboard input
  if el.classes:includes("kbd") then
    -- Convert to Span with Input style instead of Code
    return pandoc.Span(
      {pandoc.Str(el.text)},
      {["custom-style"] = "Input"}
    )
  end

  -- Return unchanged for regular code
  return el
end

--[[
Additional notes:

1. This filter supports three input formats for keyboard elements:
   - <kbd>Ctrl+S</kbd> (HTML)
   - [Ctrl+S]{.kbd} (Pandoc span with kbd class)
   - `Ctrl+S`{.kbd} (Code with kbd class)

2. The "Input" style must exist in the reference.docx template

3. For testing, you can use:
   echo '[Ctrl+S]{.kbd} saves the file' | pandoc --lua-filter core/filters/kbd.lua -t docx
--]]
