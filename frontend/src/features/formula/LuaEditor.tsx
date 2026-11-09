import { indentWithTab } from "@codemirror/commands"
import { indentUnit, StreamLanguage } from "@codemirror/language"
import { lua } from "@codemirror/legacy-modes/mode/lua"
import { Compartment, EditorState } from "@codemirror/state"
import { EditorView, keymap } from "@codemirror/view"
import { basicSetup } from "codemirror"
import { useEffect, useRef } from "react"

import { cn } from "@/lib/utils"

const INDENT = "  "

const editorTheme = EditorView.theme({
  "&": {
    fontSize: "13px",
    backgroundColor: "transparent",
  },
  "&.cm-focused": { outline: "none" },
  ".cm-scroller": {
    fontFamily:
      "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace",
    lineHeight: "1.6",
    minHeight: "20rem",
  },
  ".cm-content": { padding: "8px 0" },
  ".cm-gutters": {
    backgroundColor: "var(--muted)",
    color: "var(--muted-foreground)",
    borderRight: "1px solid var(--border)",
  },
  ".cm-activeLineGutter": { backgroundColor: "var(--accent)" },
  ".cm-activeLine": { backgroundColor: "color-mix(in oklab, var(--accent) 50%, transparent)" },
})

type LuaEditorProps = {
  id: string
  value: string
  labelId: string
  descriptionId?: string
  invalid?: boolean
  onChange: (value: string) => void
  onBlur?: () => void
}

export function LuaEditor({
  id,
  value,
  labelId,
  descriptionId,
  invalid = false,
  onChange,
  onBlur,
}: LuaEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const initialValueRef = useRef(value)
  const viewRef = useRef<EditorView | null>(null)
  const attributesRef = useRef(new Compartment())
  const onChangeRef = useRef(onChange)
  const onBlurRef = useRef(onBlur)

  useEffect(() => {
    onChangeRef.current = onChange
    onBlurRef.current = onBlur
  }, [onChange, onBlur])

  useEffect(() => {
    const container = containerRef.current
    if (container === null) {
      return
    }
    const view = new EditorView({
      parent: container,
      state: EditorState.create({
        doc: initialValueRef.current,
        extensions: [
          basicSetup,
          keymap.of([indentWithTab]),
          indentUnit.of(INDENT),
          EditorState.tabSize.of(INDENT.length),
          StreamLanguage.define(lua),
          editorTheme,
          attributesRef.current.of([]),
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              onChangeRef.current(update.state.doc.toString())
            }
            if (update.focusChanged && !update.view.hasFocus) {
              onBlurRef.current?.()
            }
          }),
        ],
      }),
    })
    viewRef.current = view
    return () => {
      view.destroy()
      viewRef.current = null
    }
  }, [])

  useEffect(() => {
    const view = viewRef.current
    if (view === null) {
      return
    }
    view.dispatch({
      effects: attributesRef.current.reconfigure(
        EditorView.contentAttributes.of({
          id,
          "aria-labelledby": labelId,
          "aria-invalid": invalid ? "true" : "false",
          ...(descriptionId ? { "aria-describedby": descriptionId } : {}),
        }),
      ),
    })
  }, [id, labelId, descriptionId, invalid])

  useEffect(() => {
    const view = viewRef.current
    if (view === null) {
      return
    }
    const current = view.state.doc.toString()
    if (current !== value) {
      view.dispatch({
        changes: { from: 0, to: current.length, insert: value },
      })
    }
  }, [value])

  return (
    <div
      ref={containerRef}
      className={cn(
        "overflow-hidden rounded-md border border-input shadow-xs transition-[color,box-shadow] focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/50",
        invalid &&
          "border-destructive ring-3 ring-destructive/20 focus-within:border-destructive",
      )}
    />
  )
}
