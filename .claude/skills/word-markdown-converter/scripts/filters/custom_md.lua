--[[
DEPRECATED: This filter is deprecated in favor of style_filter.lua

Custom Markdown filter (AST-first)
Goal: map custom styles, drop TOC, normalize headings, structure list continuations,
and keep HTML examples/tables intact without stringy post-processing.

MIGRATION: Use style_filter.lua instead which provides:
- All custom_md.lua functionality
- Unified character style mapping
- Configurable modes for different use cases

Old usage: pandoc input.docx --lua-filter core/filters/custom_md.lua -t markdown -o output.md
New usage: pandoc input.docx --lua-filter core/filters/style_filter.lua -t markdown -o output.md

This file is kept temporarily for backwards compatibility but will be removed.
--]]

local utils = require 'pandoc.utils'

-- Inline handling for custom character styles (from Word)
function Span(el)
  local cs = el.attributes and el.attributes["custom-style"] or nil
  if cs == 'Code' then
    return pandoc.Code(utils.stringify(el.content))
  elseif cs == 'Input' or cs == 'kbd' then
    return pandoc.RawInline('html', '<kbd>' .. utils.stringify(el.content) .. '</kbd>')
  end
  return el
end

function Code(el)
  if el.classes:includes('kbd') then
    return pandoc.RawInline('html', '<kbd>' .. el.text .. '</kbd>')
  end
  return el
end

-- Drop TOC headers by style or exact text
local function is_toc_header(h)
  local cs = h.attr and h.attr.attributes and h.attr.attributes['custom-style'] or nil
  if cs == 'TOC Heading' then return true end
  local txt = utils.stringify(h.content):gsub('^%s+',''):gsub('%s+$','')
  return txt:lower() == 'table of contents'
end

function Header(el)
  if is_toc_header(el) then
    return {}
  end
  return el
end

-- Title insertion and heading demotion
local function insert_title_and_demote(doc)
  local inserted = false
  if doc.meta and doc.meta.title and utils.stringify(doc.meta.title) ~= '' then
    local h1 = pandoc.Header(1, { pandoc.Str(utils.stringify(doc.meta.title)) })
    table.insert(doc.blocks, 1, h1)
    inserted = true
  end
  local start = 1
  if #doc.blocks > 0 and doc.blocks[1].t == 'Header' then
    start = 2
  elseif inserted then
    start = 2
  end
  for i = start, #doc.blocks do
    local b = doc.blocks[i]
    if b.t == 'Header' then
      local lvl = (b.level or 1) + 1
      if lvl > 6 then lvl = 6 end
      doc.blocks[i] = pandoc.Header(lvl, b.content, b.attr)
    end
  end
end

-- Remove TOC paragraphs (internal link-only leading paragraphs or TOC styles)
local function strip_toc_paragraphs(blocks)
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
          if type(tgt) == 'table' and #tgt >= 1 then tgt = tgt[1] end
          if type(tgt) == 'string' and tgt:sub(1,1) == '#' then internal_count = internal_count + 1 end
        end
      end
      local txt = utils.stringify(b):gsub('^%s+',''):gsub('%s+$','')
      local looks_like_toc = (link_count > 0 and link_count == internal_count and #txt > 0 and #txt < 120 and not txt:find('%.' ))
      if is_toc_style or (pruning and looks_like_toc) then
        -- skip
      else
        if not looks_like_toc then pruning = false end
        table.insert(out, b)
      end
    else
      if b.t == 'Header' then pruning = false end
      table.insert(out, b)
    end
  end
  return out
end

-- Convert continuation paragraphs inside list items to a BlockQuote under the item
local function quote_list_continuations(list)
  local changed = false
  local items = list.content or list
  for i, item in ipairs(items) do
    if #item > 1 then
      local head = item[1]
      local tail = {}
      for j = 2, #item do table.insert(tail, item[j]) end
      items[i] = { head, pandoc.BlockQuote(tail) }
      changed = true
    end
  end
  if changed then
    list.content = items
    return list
  end
  return nil
end

-- Do not transform list continuation paragraphs; keep native list semantics.
function BulletList(el)
  return nil
end

function OrderedList(el)
  return nil
end

function Pandoc(doc)
  -- Strip TOC paras
  doc.blocks = strip_toc_paragraphs(doc.blocks)
  -- Insert title + demote
  insert_title_and_demote(doc)
  return doc
end

-- Flatten table cell content to a single paragraph joined with <br>
local function flatten_cell(cell)
  if not cell or not cell.contents or #cell.contents <= 1 then
    return cell
  end
  local parts = {}
  local function append_inlines(inlines)
    for _, inl in ipairs(inlines) do table.insert(parts, inl) end
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
  -- Preserve table structure; just flatten multi-block cells so pipe tables can be emitted
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
