-- Pandoc Lua filter to handle <kbd> HTML tags in Markdown
-- Converts <kbd>text</kbd> to text wrapped in markers for post-processing

function RawInline(elem)
  if elem.format == 'html' then
    local text = elem.text

    -- Try to match <kbd> opening tag
    local kbd_start = text:match('^<kbd>$')
    if kbd_start then
      -- Mark this as start of keyboard input
      return pandoc.Str("⌘⌘")
    end

    -- Try to match </kbd> closing tag
    local kbd_end = text:match('^</kbd>$')
    if kbd_end then
      -- Mark this as end of keyboard input
      return pandoc.Str("⌘⌘")
    end

    -- Try to match complete <kbd>content</kbd> pattern
    local kbd_content = text:match('^<kbd>(.-)</kbd>$')
    if kbd_content then
      return pandoc.Str("⌘⌘" .. kbd_content .. "⌘⌘")
    end
  end
  return elem
end
