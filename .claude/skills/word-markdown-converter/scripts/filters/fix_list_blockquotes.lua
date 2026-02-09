--[[
Fix List Blockquotes Filter

Pandoc requires a blank line before blockquotes within list items to parse them correctly.
Without the blank line, `>` is treated as literal text. This filter detects and fixes
these cases by looking for the pattern: SoftBreak + Str ">" and converting to BlockQuote.

Also handles lists within blockquotes by parsing lines starting with "> -" into proper lists.

This makes the converter more robust for real-world markdown files.
]]

-- Check if inline element is a blockquote marker
function is_blockquote_marker(inline)
    return inline.t == "Str" and inline.text == ">"
end

-- Check if a line starts with list marker "- "
function line_starts_with_list_marker(line_inlines)
    -- Look for pattern: [Str "-", Space, ...]
    for i, inline in ipairs(line_inlines) do
        if inline.t == "Space" then
            -- Skip spaces
        elseif inline.t == "Str" and (inline.text == "-" or inline.text == "*" or inline.text == "+") then
            -- Found list marker
            return true
        else
            -- Found non-space, non-marker
            return false
        end
    end
    return false
end

-- Remove list marker from line
function remove_list_marker(line_inlines)
    local result = {}
    local found_marker = false

    for _, inline in ipairs(line_inlines) do
        if not found_marker then
            if inline.t == "Space" then
                -- Skip leading spaces
            elseif inline.t == "Str" and (inline.text == "-" or inline.text == "*" or inline.text == "+") then
                -- Found and skip marker
                found_marker = true
            else
                -- Content before marker?
                table.insert(result, inline)
            end
        else
            -- After marker, skip one space then copy rest
            if inline.t == "Space" and found_marker == true then
                found_marker = "done"  -- Mark as done after skipping space
            else
                table.insert(result, inline)
                if found_marker == true then
                    found_marker = "done"
                end
            end
        end
    end

    return result
end

-- Process Para inlines to extract blockquote lines
function extract_blockquote_lines(inlines)
    local lines = {{}}  -- Start with first line
    local current_line = 1

    for i, inline in ipairs(inlines) do
        if inline.t == "SoftBreak" or inline.t == "LineBreak" then
            -- Start new line
            current_line = current_line + 1
            lines[current_line] = {}
        else
            -- Add to current line
            table.insert(lines[current_line], inline)
        end
    end

    return lines
end

-- Check if a line starts with blockquote marker ">"
function line_starts_with_blockquote(line_inlines)
    if #line_inlines == 0 then
        return false
    end

    -- First non-space inline should be ">"
    for _, inline in ipairs(line_inlines) do
        if inline.t == "Space" then
            -- Skip leading spaces
        elseif is_blockquote_marker(inline) then
            return true
        else
            return false
        end
    end

    return false
end

-- Remove blockquote marker from line
function remove_blockquote_marker(line_inlines)
    local result = {}
    local state = "before_marker"  -- before_marker, after_marker, copying

    for _, inline in ipairs(line_inlines) do
        if state == "before_marker" then
            if is_blockquote_marker(inline) then
                state = "after_marker"  -- Found marker, skip it
            elseif inline.t == "Space" then
                -- Skip leading spaces before marker
            else
                -- Non-space, non-marker content before marker? Keep it
                table.insert(result, inline)
            end
        elseif state == "after_marker" then
            -- Skip one space after ">", then start copying
            if inline.t == "Space" then
                state = "copying"  -- Skip this space, then copy rest
            else
                -- No space after marker, just start copying
                table.insert(result, inline)
                state = "copying"
            end
        else  -- state == "copying"
            -- Copy everything after marker and space
            table.insert(result, inline)
        end
    end

    return result
end

-- Build blockquote content blocks from lines
function build_blockquote_content(blockquote_lines)
    local content_blocks = {}
    local paragraph_lines = {}
    local list_items = {}
    local in_list = false

    for _, line in ipairs(blockquote_lines) do
        if line_starts_with_list_marker(line) then
            -- Flush paragraph if any
            if #paragraph_lines > 0 then
                local combined_inlines = {}
                for i, pline in ipairs(paragraph_lines) do
                    for _, inline in ipairs(pline) do
                        table.insert(combined_inlines, inline)
                    end
                    if i < #paragraph_lines then
                        table.insert(combined_inlines, pandoc.SoftBreak())
                    end
                end
                table.insert(content_blocks, pandoc.Para(combined_inlines))
                paragraph_lines = {}
            end

            -- Add list item
            in_list = true
            local item_content = remove_list_marker(line)
            table.insert(list_items, {pandoc.Plain(item_content)})
        else
            -- Regular line
            if in_list and #list_items > 0 then
                -- Flush list
                table.insert(content_blocks, pandoc.BulletList(list_items))
                list_items = {}
                in_list = false
            end

            -- Add to paragraph
            table.insert(paragraph_lines, line)
        end
    end

    -- Flush remaining content
    if #list_items > 0 then
        table.insert(content_blocks, pandoc.BulletList(list_items))
    elseif #paragraph_lines > 0 then
        local combined_inlines = {}
        for i, pline in ipairs(paragraph_lines) do
            for _, inline in ipairs(pline) do
                table.insert(combined_inlines, inline)
            end
            if i < #paragraph_lines then
                table.insert(combined_inlines, pandoc.SoftBreak())
            end
        end
        table.insert(content_blocks, pandoc.Para(combined_inlines))
    end

    return content_blocks
end

-- Process a Para or Plain block in a list item
function process_para_in_list(para)
    local block_constructor = (para.t == "Plain") and pandoc.Plain or pandoc.Para
    local lines = extract_blockquote_lines(para.content)

    -- Check if any line starts with ">"
    local has_blockquote = false
    for _, line in ipairs(lines) do
        if line_starts_with_blockquote(line) then
            has_blockquote = true
            break
        end
    end

    if not has_blockquote then
        return {para}
    end

    -- Process lines to separate blockquotes from normal content
    local result_blocks = {}
    local normal_lines = {}
    local blockquote_lines = {}

    for _, line in ipairs(lines) do
        if line_starts_with_blockquote(line) then
            -- Flush normal content if any
            if #normal_lines > 0 then
                -- Reconstruct block with line breaks
                local combined_inlines = {}
                for i, nline in ipairs(normal_lines) do
                    for _, inline in ipairs(nline) do
                        table.insert(combined_inlines, inline)
                    end
                    if i < #normal_lines then
                        table.insert(combined_inlines, pandoc.SoftBreak())
                    end
                end
                table.insert(result_blocks, block_constructor(combined_inlines))
                normal_lines = {}
            end

            -- Add to blockquote (removing the "> " marker)
            local bq_content = remove_blockquote_marker(line)
            table.insert(blockquote_lines, bq_content)
        else
            -- Flush blockquote if any
            if #blockquote_lines > 0 then
                -- Build blockquote with proper structure (paragraphs + lists)
                local bq_blocks = build_blockquote_content(blockquote_lines)
                table.insert(result_blocks, pandoc.BlockQuote(bq_blocks))
                blockquote_lines = {}
            end

            -- Add to normal content
            table.insert(normal_lines, line)
        end
    end

    -- Flush remaining content
    if #blockquote_lines > 0 then
        local bq_blocks = build_blockquote_content(blockquote_lines)
        table.insert(result_blocks, pandoc.BlockQuote(bq_blocks))
    elseif #normal_lines > 0 then
        local combined_inlines = {}
        for i, nline in ipairs(normal_lines) do
            for _, inline in ipairs(nline) do
                table.insert(combined_inlines, inline)
            end
            if i < #normal_lines then
                table.insert(combined_inlines, pandoc.SoftBreak())
            end
        end
        table.insert(result_blocks, block_constructor(combined_inlines))
    end

    return result_blocks
end

-- Process a list item
function process_list_item(item)
    local new_blocks = {}

    for _, block in ipairs(item) do
        if block.t == "Para" or block.t == "Plain" then
            local processed = process_para_in_list(block)
            for _, b in ipairs(processed) do
                table.insert(new_blocks, b)
            end
        else
            table.insert(new_blocks, block)
        end
    end

    return new_blocks
end

-- Main filter function for BulletList
function BulletList(elem)
    local new_items = {}

    for _, item in ipairs(elem.content) do
        local processed_item = process_list_item(item)
        table.insert(new_items, processed_item)
    end

    elem.content = new_items
    return elem
end

-- Main filter function for OrderedList
function OrderedList(elem)
    local new_items = {}

    for _, item in ipairs(elem.content) do
        local processed_item = process_list_item(item)
        table.insert(new_items, processed_item)
    end

    elem.content = new_items
    return elem
end
