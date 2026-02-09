--[[
md_to_word_headings.lua - Pandoc filter for Markdown to Word heading style mapping

Maps Markdown headings to Word styles according to style_map.yml:
- All # (h1) before first ## → Title style
- # (h1) after first ## → Heading 1 style
- ## (h2) → Heading 1 style (offset from Title)
- ### (h3) → Heading 2 style
- And so on...

This aligns with the HMS IT convention where document titles (all h1 before first h2)
use Title style and section headings are offset by one level.

Usage:
  pandoc input.md --lua-filter core/filters/md_to_word_headings.lua \
    --reference-doc template.docx -o output.docx
--]]

-- Track whether we've seen any h2 or below headings
local seen_h2_or_below = false

function Header(el)
  -- Get the heading level
  local level = el.level

  -- Mark when we see the first h2 or below
  if level >= 2 and not seen_h2_or_below then
    seen_h2_or_below = true
  end

  if level == 1 and not seen_h2_or_below then
    -- All h1 headings before the first h2 become Title style
    -- Convert to a Div with custom-style="Title" containing a Para
    -- Preserve heading attributes (identifier, classes, key-value pairs) for bookmarks/anchors
    local title_para = pandoc.Para(el.content)
    local div_attr = el.attr:clone()
    div_attr.attributes["custom-style"] = "Title"
    return pandoc.Div({title_para}, div_attr)
  elseif level == 1 then
    -- h1 headings after the first h2 become Heading 1
    return el
  elseif level == 2 then
    -- h2 becomes Heading 1 (demote by 1: level 2 → level 1)
    return pandoc.Header(1, el.content, el.attr)
  elseif level == 3 then
    -- h3 becomes Heading 2 (demote by 1: level 3 → level 2)
    return pandoc.Header(2, el.content, el.attr)
  elseif level == 4 then
    -- h4 becomes Heading 3 (demote by 1: level 4 → level 3)
    return pandoc.Header(3, el.content, el.attr)
  elseif level == 5 then
    -- h5 becomes Heading 4 (demote by 1: level 5 → level 4)
    return pandoc.Header(4, el.content, el.attr)
  elseif level >= 6 then
    -- h6 and beyond become Heading 5 (demote by 1: level 6 → level 5)
    return pandoc.Header(5, el.content, el.attr)
  end

  return el
end
