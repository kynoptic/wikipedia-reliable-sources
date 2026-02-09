--[[
DEPRECATED: This filter is deprecated in favor of style_filter.lua

custom_styles.lua - Enhanced Pandoc filter for custom document styling
Handles kbd > Input, inline code > Code, and code blocks > Code block

MIGRATION: Use style_filter.lua instead which provides:
- All custom_styles.lua functionality
- Additional markdown customizations
- TOC handling and title insertion
- Configurable modes for different use cases

Old usage: pandoc input.md --lua-filter core/filters/custom_styles.lua --reference-doc core/utils/reference.docx --no-highlight -o output.docx
New usage: pandoc input.md --lua-filter core/filters/style_filter.lua --reference-doc core/utils/reference.docx --no-highlight -o output.docx

This file is kept temporarily for backwards compatibility but will be removed.
--]]

-- Utilities
local utils = require 'pandoc.utils'

-- We apply demotion in the Pandoc(doc) handler after optional title insertion.

function RawInline(el)
  -- Handle <kbd> opening tags - remove them since they'll be processed differently
  if el.format == "html" and (el.text == "<kbd>" or el.text == "</kbd>") then
    -- Remove the raw HTML tags, content will be processed as normal text
    return {}
  end

  -- Return unchanged for other HTML
  return el
end

function Span(el)
  -- Map custom Word character styles to Markdown semantics when converting from DOCX
  local cs = el.attributes and el.attributes["custom-style"] or nil
  if cs == "Code" then
    local txt = utils.stringify(el.content)
    return pandoc.Code(txt)
  elseif cs == "Input" then
    local txt = utils.stringify(el.content)
    return pandoc.RawInline('html', '<kbd>' .. txt .. '</kbd>')
  end

  -- Also detect by class list (Pandoc DOCX reader may emit character styles as classes)
  if el.classes and #el.classes > 0 then
    local has_class = function(name)
      for _, c in ipairs(el.classes) do
        if string.lower(c) == string.lower(name) then return true end
      end
      return false
    end
    if has_class('Code') then
      local txt = utils.stringify(el.content)
      return pandoc.Code(txt)
    end
    if has_class('Input') then
      local txt = utils.stringify(el.content)
      return pandoc.RawInline('html', '<kbd>' .. txt .. '</kbd>')
    end
    if has_class('kbd') then
      local txt = utils.stringify(el.content)
      return pandoc.RawInline('html', '<kbd>' .. txt .. '</kbd>')
    end
  end

  -- Return unchanged if not kbd class
  return el
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

-- Demote headers when a Title is synthesized as H1
function Header(el)
  -- Drop TOC heading by style or exact text match
  local cs = el.attr and el.attr.attributes and el.attr.attributes["custom-style"] or nil
  if cs == "TOC Heading" then
    return {}
  end
  local text = utils.stringify(el.content):gsub("^%s+", ""):gsub("%s+$", "")
  if text:lower() == "table of contents" then
    return {}
  end
  -- Otherwise no-op at element level; demotion happens in Pandoc(doc)
  return el
end

-- Insert Title as H1 at the top when present in metadata (docx Title style)
function Pandoc(doc)
  local inserted_title = false
  if doc.meta and doc.meta.title and utils.stringify(doc.meta.title) ~= '' then
    local title_text = utils.stringify(doc.meta.title)
    local title_header = pandoc.Header(1, { pandoc.Str(title_text) })
    table.insert(doc.blocks, 1, title_header)
    inserted_title = true
  end

  -- Normalize paragraphs (join SoftBreak/LineBreak) and drop TOC paragraphs by style
  local normalized_blocks = {}
  local pruning_toc = true
  for _, blk in ipairs(doc.blocks) do
    if blk.t == 'Para' then
      local cs = blk.attr and blk.attr.attributes and blk.attr.attributes["custom-style"] or nil
      local is_toc_style = cs == "TOC 1" or cs == "TOC 2" or cs == "TOC 3" or cs == "TOC 4" or cs == "TOC 5" or cs == "TOC 6" or cs == "TOC Heading"

      -- Heuristic: treat leading paragraphs that are composed entirely of internal links as TOC entries
      local link_count, internal_count = 0, 0
      local function get_target(inline)
        if type(inline.target) == 'string' then return inline.target end
        if type(inline.target) == 'table' and #inline.target >= 1 then return inline.target[1] end
        return ''
      end
      for _, inline in ipairs(blk.content) do
        if inline.t == 'Link' then
          link_count = link_count + 1
          local tgt = get_target(inline)
          if type(tgt) == 'string' and tgt:sub(1,1) == '#' then
            internal_count = internal_count + 1
          end
        end
      end
      local txt = utils.stringify(blk):gsub("^%s+",""):gsub("%s+$","")
      local looks_like_toc = (link_count > 0 and link_count == internal_count and #txt > 0 and #txt < 120 and not txt:find('%.'))
        or ((txt:match('%d') ~= nil) and not txt:find('%.') and #txt > 0 and #txt < 140)

      if is_toc_style or (pruning_toc and looks_like_toc) then
        -- skip TOC paragraphs
      else
        -- stop pruning once non-TOC content appears
        if not looks_like_toc then pruning_toc = false end
        local out = {}
        for _, inline in ipairs(blk.content) do
          if inline.t == 'SoftBreak' or inline.t == 'LineBreak' then
            table.insert(out, pandoc.Space())
          else
            table.insert(out, inline)
          end
        end
        blk.content = out
        table.insert(normalized_blocks, blk)
      end
    else
      -- Any header or other block ends TOC pruning
      if blk.t == 'Header' then pruning_toc = false end
      table.insert(normalized_blocks, blk)
    end
  end
  doc.blocks = normalized_blocks

  -- Determine starting index for demotion: if the first block is a header
  -- (either inserted Title or an existing header), keep it as-is and
  -- demote all subsequent headers by one level.
  local start_idx = 1
  if #doc.blocks > 0 then
    if doc.blocks[1].t == 'Header' then
      start_idx = 2
    elseif inserted_title then
      start_idx = 2
    end
  end

  for i = start_idx, #doc.blocks do
    local blk = doc.blocks[i]
    if blk.t == 'Header' then
      local level = blk.level or 1
      local new_level = level + 1
      if new_level > 6 then new_level = 6 end
      doc.blocks[i] = pandoc.Header(new_level, blk.content, blk.attr)
    end
  end

  return doc
end

--[[
Filter order and processing:

1. RawInline: Processes <kbd>content</kbd> HTML tags
2. Span: Processes [content]{.kbd} Pandoc spans
3. Code: Processes `inline code` and `code`{.kbd}
4. CodeBlock: Processes ```code blocks```

All elements are converted to use appropriate custom character or paragraph styles.
--]]
