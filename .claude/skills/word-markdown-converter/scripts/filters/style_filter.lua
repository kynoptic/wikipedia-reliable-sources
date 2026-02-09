--[[
style_filter.lua - Unified Pandoc filter for Word-Markdown conversion

This unified filter consolidates functionality from:
- kbd.lua: Keyboard input handling
- custom_styles.lua: Custom character and paragraph styles
- custom_md.lua: Markdown customizations and TOC handling
- golden_fixture_styles.lua: Test fixture support

Configuration:
Set PANDOC_FILTER_MODE environment variable to control behavior:
- "golden_fixture": Simplified mode for testing (no heading demotion)
- "standard": Full conversion mode (default)
- (unrecognized values default to "standard" mode)

Usage:
  # Standard conversion
  pandoc input.md --lua-filter core/filters/style_filter.lua --reference-doc reference.docx -o output.docx

  # Golden fixture mode
  PANDOC_FILTER_MODE=golden_fixture pandoc input.md --lua-filter core/filters/style_filter.lua -o output.docx

  # DOCX to Markdown
  pandoc input.docx --lua-filter core/filters/style_filter.lua -t markdown -o output.md

This filter provides:
1. Keyboard input mapping: <kbd> tags, [text]{.kbd}, `code`{.kbd} → Input style
2. Code formatting: `inline code` → Code style, ```code blocks``` → Code block style
3. Custom style mapping: Word styles (Code, Input) ↔ Markdown semantics
4. Document structure: Title insertion, heading demotion, TOC removal
5. Test support: Golden fixture mode for simplified conversion

Limitation:
The first_header_seen state variable is reset per filter invocation. If Pandoc
processes multiple documents in a batch with persistent filter state, the
first header tracking may be incorrect. Each document conversion should use
a fresh pandoc process to ensure correct behavior.

Consolidates: kbd.lua, custom_styles.lua, custom_md.lua, golden_fixture_styles.lua
--]]

local utils = require 'pandoc.utils'

-- Configuration: detect filter mode
local filter_mode = os.getenv("PANDOC_FILTER_MODE") or "standard"
local is_golden_fixture = filter_mode == "golden_fixture"

-- Track if first header has been seen (for golden fixture mode)
local first_header_seen = false

--
-- INLINE ELEMENT HANDLERS
--

function RawInline(el)
  -- Handle <kbd> tags - remove them in markdown-to-docx, keep them in docx-to-markdown
  if el.format == "html" then
    if el.text == "<kbd>" or el.text == "</kbd>" then
      -- In standard mode, remove raw HTML tags (content will be processed as spans)
      if not is_golden_fixture then
        return {}
      end
    end
  end

  return el
end

function Span(el)
  -- Map custom Word character styles to Markdown semantics (DOCX → Markdown)
  local cs = el.attributes and el.attributes["custom-style"] or nil

  if cs == "Code" then
    -- Word Code style → Markdown inline code
    local txt = utils.stringify(el.content)
    return pandoc.Code(txt)
  elseif cs == "Input" then
    -- Word Input style → <kbd> HTML tag
    local txt = utils.stringify(el.content)
    return pandoc.RawInline('html', '<kbd>' .. txt .. '</kbd>')
  end

  -- Also detect by class list (Pandoc DOCX reader may emit styles as classes)
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
    if has_class('Input') or has_class('kbd') then
      local txt = utils.stringify(el.content)
      return pandoc.RawInline('html', '<kbd>' .. txt .. '</kbd>')
    end
  end

  return el
end

function Code(el)
  -- Handle inline code: Apply Code style for Markdown → DOCX
  -- Or convert `code`{.kbd} to Input style

  if el.classes:includes("kbd") then
    -- Keyboard input: `text`{.kbd} → Input character style
    return pandoc.Span(
      {pandoc.Str(el.text)},
      {["custom-style"] = "Input"}
    )
  else
    -- Regular inline code → Code character style
    return pandoc.Span(
      {pandoc.Str(el.text)},
      {["custom-style"] = "Code"}
    )
  end
end

--
-- BLOCK ELEMENT HANDLERS
--

function CodeBlock(el)
  -- Convert code blocks to Div with Code block paragraph style
  -- Necessary because Pandoc doesn't apply custom-style to CodeBlock elements

  -- Split code text into lines and create separate paragraphs
  local paras = {}
  for line in el.text:gmatch("([^\r\n]*)\r?\n?") do
    if line ~= "" then
      table.insert(paras, pandoc.Para({pandoc.Str(line)}))
    elseif line == "" and #paras > 0 then
      -- Empty paragraph for blank lines
      table.insert(paras, pandoc.Para({pandoc.Str("")}))
    end
  end

  if #paras == 0 then
    paras = {pandoc.Para({pandoc.Str(el.text)})}
  end

  -- Return as Div with Code block custom style
  return pandoc.Div(paras, {["custom-style"] = "Code block"})
end

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

  -- Golden fixture mode: convert first H1 to Title style
  if is_golden_fixture and not first_header_seen and el.level == 1 then
    first_header_seen = true
    return pandoc.Div(
      {pandoc.Para(el.content)},
      {["custom-style"] = "Title"}
    )
  end

  return el
end

--
-- SPECIAL INLINE SEQUENCES (for golden fixture mode)
--

function Inlines(inlines)
  -- Process inline sequences to convert <kbd>...</kbd> patterns
  -- Only needed in golden fixture mode for proper <kbd> handling

  if not is_golden_fixture then
    return inlines
  end

  local result = {}
  local i = 1

  while i <= #inlines do
    local el = inlines[i]

    -- Check for <kbd> pattern
    if el.t == 'RawInline' and el.format == 'html' and el.text == '<kbd>' then
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
        i = j + 1
      else
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

--
-- TABLE HANDLING
--

local function flatten_cell(cell)
  -- Flatten multi-block table cells to single paragraph with <br>
  if not cell or not cell.contents or #cell.contents <= 1 then
    return cell
  end

  local parts = {}
  local function append_inlines(inlines)
    for _, inl in ipairs(inlines) do
      table.insert(parts, inl)
    end
  end

  for idx, blk in ipairs(cell.contents) do
    if idx > 1 then
      table.insert(parts, pandoc.LineBreak())
    end
    if blk.t == 'Para' or blk.t == 'Plain' then
      append_inlines(blk.content)
    else
      local txt = utils.stringify(blk)
      if txt and #txt > 0 then
        table.insert(parts, pandoc.Str(txt))
      end
    end
  end

  cell.contents = { pandoc.Para(parts) }
  return cell
end

function Table(tbl)
  -- Flatten multi-block cells so pipe tables can be emitted
  if tbl.head and tbl.head.rows then
    for _, row in ipairs(tbl.head.rows) do
      for _, cell in ipairs(row.cells) do
        flatten_cell(cell)
      end
    end
  end

  if tbl.bodies then
    for _, body in ipairs(tbl.bodies) do
      for _, row in ipairs(body.rows or {}) do
        for _, cell in ipairs(row.cells) do
          flatten_cell(cell)
        end
      end
    end
  end

  if tbl.foot and tbl.foot.rows then
    for _, row in ipairs(tbl.foot.rows) do
      for _, cell in ipairs(row.cells) do
        flatten_cell(cell)
      end
    end
  end

  return tbl
end

--
-- DOCUMENT-LEVEL PROCESSING
--

local function strip_toc_paragraphs(blocks)
  -- Remove TOC paragraphs (internal link-only or TOC styles)
  local out = {}
  local pruning = true

  for _, b in ipairs(blocks) do
    if b.t == 'Para' then
      local cs = b.attr and b.attr.attributes and b.attr.attributes['custom-style'] or nil
      local is_toc_style = cs and cs:match('^TOC')

      local link_count, internal_count = 0, 0
      for _, inl in ipairs(b.content) do
        if inl.t == 'Link' then
          link_count = link_count + 1
          local tgt = inl.target or ''
          if type(tgt) == 'table' and #tgt >= 1 then
            tgt = tgt[1]
          end
          if type(tgt) == 'string' and tgt:sub(1,1) == '#' then
            internal_count = internal_count + 1
          end
        end
      end

      local txt = utils.stringify(b):gsub('^%s+',''):gsub('%s+$','')
      local looks_like_toc = (link_count > 0 and link_count == internal_count and #txt > 0 and #txt < 120 and not txt:find('%.'))

      if is_toc_style or (pruning and looks_like_toc) then
        -- Skip TOC paragraphs
      else
        if not looks_like_toc then
          pruning = false
        end
        table.insert(out, b)
      end
    else
      if b.t == 'Header' then
        pruning = false
      end
      table.insert(out, b)
    end
  end

  return out
end

local function insert_title_and_demote(doc)
  -- Insert title as H1 and demote subsequent headers
  -- Skip in golden fixture mode

  if is_golden_fixture then
    return
  end

  local inserted = false
  if doc.meta and doc.meta.title and utils.stringify(doc.meta.title) ~= '' then
    local h1 = pandoc.Header(1, { pandoc.Str(utils.stringify(doc.meta.title)) })
    table.insert(doc.blocks, 1, h1)
    inserted = true
  end

  -- Determine starting index for demotion
  local start = 1
  if #doc.blocks > 0 and doc.blocks[1].t == 'Header' then
    start = 2
  elseif inserted then
    start = 2
  end

  -- Demote headers
  for i = start, #doc.blocks do
    local b = doc.blocks[i]
    if b.t == 'Header' then
      local lvl = (b.level or 1) + 1
      if lvl > 6 then lvl = 6 end
      doc.blocks[i] = pandoc.Header(lvl, b.content, b.attr)
    end
  end
end

local function normalize_paragraphs(blocks)
  -- Normalize paragraphs: join SoftBreak/LineBreak with Space
  local normalized = {}

  for _, blk in ipairs(blocks) do
    if blk.t == 'Para' then
      local out = {}
      for _, inline in ipairs(blk.content) do
        if inline.t == 'SoftBreak' or inline.t == 'LineBreak' then
          table.insert(out, pandoc.Space())
        else
          table.insert(out, inline)
        end
      end
      blk.content = out
      table.insert(normalized, blk)
    else
      table.insert(normalized, blk)
    end
  end

  return normalized
end

function Pandoc(doc)
  -- Document-level transformations

  -- Strip TOC paragraphs (unless in golden fixture mode)
  if not is_golden_fixture then
    doc.blocks = strip_toc_paragraphs(doc.blocks)
    doc.blocks = normalize_paragraphs(doc.blocks)
  end

  -- Insert title and demote headers (unless in golden fixture mode)
  insert_title_and_demote(doc)

  return doc
end

--[[
Filter processing order:
1. Inlines: <kbd>...</kbd> sequence handling (golden fixture mode)
2. RawInline: Remove raw <kbd> tags (standard mode)
3. Span: Convert custom Word styles to Markdown
4. Code: Convert inline code and kbd-marked code
5. CodeBlock: Convert to Code block paragraph style
6. Header: Drop TOC headers, handle first H1 (golden fixture)
7. Table: Flatten multi-block cells
8. Pandoc: Document-level transformations (title, demotion, TOC removal)

Configuration:
- PANDOC_FILTER_MODE=golden_fixture: Simplified mode for testing
- PANDOC_FILTER_MODE=standard: Full conversion (default)
--]]
