> **Human long-form docs** (AGPK-MARKET).  
> Package tarball keeps a **short** USAGE with pointers only.  
> Package: `org.excalidraw.Excalidraw.core` · `docs.read_policy=optional`.

# USAGE — org.excalidraw.Excalidraw.core

**Agent Excalidraw scene engine** (official AGPK core)

This is **not** a wrap of the React app and **not** excalidraw.com.  
It is a headless engine that speaks the public `.excalidraw` JSON used by [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw) (MIT).

| Item | Value |
|------|--------|
| package_id | `org.excalidraw.Excalidraw.core` |
| version | **1.0.0** |
| kind | `core` |
| domain | drawing / whiteboard |
| driver | `process` → `payload/bin/excalidraw_driver.py` |
| store | `$AGENTX_HOME/agpk/runtime/excalidraw` |
| deps | Python 3 stdlib only |

## Transformation

| Upstream | This package |
|----------|----------------|
| React + roughjs canvas | Scene engine + `draw.*` commands |
| Human toolbar | Agent invoke |
| Live collab | Out of core |
| Human viewing | `draw.export.svg` / `draw.export.png` → `projection.image` |

A future `*.ui` package must `depends` this core. Do not weld a GUI into core.

## Commands

See package `agent-commands.json`. Groups: `scene` · `element` · `arrange` · `style` · `export` · `library`.

High risk: `draw.scene.delete` requires `confirm=true`.

## Example

```bash
export AGPK_INVOKE_ARGS_JSON='{"name":"board"}'
sh run_cmd.sh draw.scene.new
sh run_cmd.sh draw.element.add '{"type":"rectangle","x":80,"y":60,"width":200,"height":100}'
sh run_cmd.sh draw.element.add '{"type":"text","x":100,"y":90,"text":"hello"}'
sh run_cmd.sh draw.export.svg '{}'
```

Exported `.excalidraw` files open in upstream Excalidraw.

## Out of scope

- Pixel-identical roughjs strokes
- Collaboration rooms
- Mermaid wizard
- Independent drawing-app SKU (visuals go through projection / Live View)
