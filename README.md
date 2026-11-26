# My paint application

## REQUIREMENTS COMPLETED
### ✓ Bigger brush range
So, what I did here, ma'am, was change the brush size slider. Before, the biggest brush size was only 30.

Original:


Revised:

size_slider = tk.Scale(toolbar, from_=1, to=100, orient="horizontal",
                       command=change_brush_size, length=120,
                       bg=PURPLE_PANEL, fg=TEXT_COLOR,
                       troughcolor=PURPLE_BUTTON, highlightthickness=0)
size_slider.set(5)



2. I changed from_=1 (thinnest line) to to=100 (thickest line).

When you move the slider, change_brush_size updates brush_size. Both the screen and the saved image stay 900x550, so the saved picture matches what you draw.

2. Undo Button
Before, there was no Undo button at all. I added an undo_stack list to save a copy of your drawing before you make a change.

Original code:

Python
def start_drawing(event):
    """Remember the mouse position when drawing starts."""
    global last_x, last_y, start_x, start_y
    last_x, last_y = event.x, event.y
    start_x, start_y = event.x, event.y
    
Revised code:

Python
def push_undo():
    """Save a snapshot of the current image for undo."""
    undo_stack.append(image.copy())

def undo_action():
    """Undo the most recent drawing action (freehand stroke or shape)."""
    global image, draw, preview_shape
    if undo_stack:
        image = undo_stack.pop()
        draw = ImageDraw.Draw(image)
        preview_shape = None
        refresh_canvas()

def start_drawing(event):
    """Remember the mouse position when drawing starts."""
    global last_x, last_y, start_x, start_y
    push_undo()
    last_x, last_y = event.x, event.y
    start_x, start_y = event.x, event.y
push_undo() saves a backup copy of the drawing before a stroke, shape, clear, or open action.

Clicking Undo runs undo_action(), which brings back the last saved copy on the canvas.

3. Filled Shapes (Rectangles and Ovals)
Before, rectangles and ovals only drew outlines and were always empty inside. I added a fill_shapes setting and a Fill: OFF / ON button so you can fill them with your current color.

Original code:

Python
elif tool == "rectangle":
    preview_shape = canvas.create_rectangle(
        start_x, start_y, event.x, event.y,
        outline=current_color, width=brush_size)
elif tool == "oval":
    preview_shape = canvas.create_oval(
        start_x, start_y, event.x, event.y,
        outline=current_color, width=brush_size)
Changed code:

Python
def toggle_fill():
    """Toggle whether rectangles and ovals are filled with the current color."""
    global fill_shapes
    fill_shapes = not fill_shapes
    fill_button.config(
        text=f"Fill: {'ON' if fill_shapes else 'OFF'}",
        bg=PINK_ACCENT if fill_shapes else PURPLE_BUTTON,
        fg=BLACK_ACCENT if fill_shapes else TEXT_COLOR
    )

# Inside preview_shape_drawing and finish_drawing:
shape_fill = current_color if fill_shapes else ""
Clicking the Fill button turns filling on or off.

When fill is on, the shape shows its fill color while dragging and saves filled on the final image.

4. Extra Shape Tool (Triangle)
Before, the shape tools only had Line, Rectangle, and Oval. I added a Triangle button and logic to draw and save triangles.

Original code:

Python
elif tool == "oval":
    preview_shape = canvas.create_oval(
        start_x, start_y, event.x, event.y,
        outline=current_color, width=brush_size)
Changed code:

Python
def get_triangle_points(x1, y1, x2, y2):
    """Return vertices for a triangle bounded by (x1, y1) and (x2, y2)."""
    top_x = (x1 + x2) / 2
    return [(top_x, y1), (x1, y2), (x2, y2)]

elif tool == "triangle":
    pts = get_triangle_points(start_x, start_y, event.x, event.y)
    preview_shape = canvas.create_polygon(
        pts, outline=current_color, fill=shape_fill, width=brush_size)
get_triangle_points finds the top middle point and bottom two corners from where you drag.

preview_shape_drawing shows the triangle while dragging, and finish_drawing saves it onto the image.

5. Confirm Before Clearing
Before, clicking Clear erased the whole canvas right away. I added a Yes / No confirmation box first.

Original code:

Python
def clear_canvas():
    """Replace the current drawing with a blank white image."""
    global image, draw, preview_shape
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    preview_shape = None
    refresh_canvas()
Changed code:

Python
def clear_canvas():
    """Confirm with the user, then replace the current drawing with a blank white image."""
    global image, draw, preview_shape
    confirmed = messagebox.askyesno(
        "Confirm Clear",
        "Are you sure you want to clear the canvas?",
        icon="question"
    )
    if not confirmed:
        return
    push_undo()
    image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
    draw = ImageDraw.Draw(image)
    preview_shape = None
    refresh_canvas()
If you click No, it stops and keeps your drawing.

If you click Yes, it saves an undo copy and clears the canvas to white.

6. Quick Colors (Six One-Click Colors)
Before, you had to open the color chooser window every time you wanted a color. I added six quick color buttons—Black, Red, Blue, Green, Yellow, and Purple.

Original code:

Python
color_button = make_button(toolbar, "Choose Color", choose_color)
color_button.pack(side="left", padx=4)
Changed code:

Python
def set_quick_color(color):
    """Immediately set the drawing color from a quick-color button."""
    global current_color
    current_color = color
    color_button.config(bg=current_color, fg="white" if current_color in ("black", "blue", "purple") else "black")

quick_colors = [
    ("Black", "black", "white"),
    ("Red", "red", "white"),
    ("Blue", "blue", "white"),
    ("Green", "green", "white"),
    ("Yellow", "yellow", "black"),
    ("Purple", "purple", "white"),
]
Each button in quick_colors changes current_color right away with one click and updates the color button to match.
