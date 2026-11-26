import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

PURPLE_BG = "#3B185F"      
PURPLE_PANEL = "#5A248A"   
PURPLE_BUTTON = "#7B2CBF"  
PURPLE_HOVER = "#9D4EDD"   
PINK_ACCENT = "#FF69B4"    
BLACK_ACCENT = "#111111"   
TEXT_COLOR = "#FFFFFF"     
FONT_MAIN = ("Arial", 10, "bold")

# 2. MAIN WINDOW AND CANVAS SETTINGS
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 550

root = tk.Tk()
root.title("My Paint Application")
root.geometry("1080x760")
root.configure(bg=PURPLE_BG)

canvas_frame = tk.Frame(root, bg=BLACK_ACCENT, padx=4, pady=4,
                        highlightbackground=PINK_ACCENT, highlightthickness=2)
canvas_frame.pack(padx=20, pady=12)

canvas = tk.Canvas(canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                   bg="white", cursor="cross", highlightthickness=0)
canvas.pack()

image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
draw = ImageDraw.Draw(image)
canvas_image = None

# 3. DRAWING SETTINGS
current_color = "black"
brush_size = 5
tool = "brush"
fill_shapes = False
start_x = start_y = None
last_x = last_y = None
preview_shape = None
undo_stack = []

def push_undo():
    """Save a snapshot of the current image for undo."""
    undo_stack.append(image.copy())

def get_triangle_points(x1, y1, x2, y2):
    """Return vertices for a triangle bounded by (x1, y1) and (x2, y2)."""
    top_x = (x1 + x2) / 2
    return [(top_x, y1), (x1, y2), (x2, y2)]

# 4. TOOL FUNCTIONS
def choose_color():
    """Open the color chooser and update the drawing color."""
    global current_color, tool
    selected = colorchooser.askcolor(title="Choose a color")
    if selected[1] is not None:
        current_color = selected[1]
        tool = "brush"
        color_button.config(bg=current_color, fg="white" if current_color in ("black", "blue", "purple") else "black")

def set_quick_color(color):
    """Immediately set the drawing color from a quick-color button."""
    global current_color
    current_color = color
    color_button.config(bg=current_color, fg="white" if current_color in ("black", "blue", "purple") else "black")

def toggle_fill():
    """Toggle whether rectangles and ovals are filled with the current color."""
    global fill_shapes
    fill_shapes = not fill_shapes
    fill_button.config(
        text=f"Fill: {'ON' if fill_shapes else 'OFF'}",
        bg=PINK_ACCENT if fill_shapes else PURPLE_BUTTON,
        fg=BLACK_ACCENT if fill_shapes else TEXT_COLOR
    )

def set_tool(selected_tool):
    """Change the active drawing tool."""
    global tool
    tool = selected_tool

def change_brush_size(value):
    """Update the brush size using the slider."""
    global brush_size
    brush_size = int(float(value))

def undo_action():
    """Undo the most recent drawing action (freehand stroke or shape)."""
    global image, draw, preview_shape
    if undo_stack:
        image = undo_stack.pop()
        draw = ImageDraw.Draw(image)
        preview_shape = None
        refresh_canvas()

# 5. FREEHAND DRAWING
def start_drawing(event):
    """Remember the mouse position when drawing starts."""
    global last_x, last_y, start_x, start_y
    push_undo()
    last_x, last_y = event.x, event.y
    start_x, start_y = event.x, event.y

def draw_motion(event):
    """Draw while the left mouse button is held."""
    global last_x, last_y
    color = "white" if tool == "eraser" else current_color
    if tool in ("brush", "eraser"):
        
        canvas.create_line(last_x, last_y, event.x, event.y,
                           fill=color, width=brush_size,
                           capstyle=tk.ROUND, smooth=True)
        
        draw.line((last_x, last_y, event.x, event.y),
                  fill=color, width=brush_size)
        last_x, last_y = event.x, event.y
    else:
        preview_shape_drawing(event)

# 6. SHAPE DRAWING
def preview_shape_drawing(event):
    """Show a temporary shape while the mouse is dragged."""
    global preview_shape
    if preview_shape is not None:
        canvas.delete(preview_shape)
    shape_fill = current_color if fill_shapes else ""
    if tool == "line":
        preview_shape = canvas.create_line(
            start_x, start_y, event.x, event.y,
            fill=current_color, width=brush_size)
    elif tool == "rectangle":
        preview_shape = canvas.create_rectangle(
            start_x, start_y, event.x, event.y,
            outline=current_color, fill=shape_fill, width=brush_size)
    elif tool == "oval":
        preview_shape = canvas.create_oval(
            start_x, start_y, event.x, event.y,
            outline=current_color, fill=shape_fill, width=brush_size)
    elif tool == "triangle":
        pts = get_triangle_points(start_x, start_y, event.x, event.y)
        preview_shape = canvas.create_polygon(
            pts, outline=current_color, fill=shape_fill, width=brush_size)

def finish_drawing(event):
    """Store the selected shape in the Pillow image."""
    global preview_shape
    shape_fill = current_color if fill_shapes else None
    if tool == "line":
        draw.line((start_x, start_y, event.x, event.y),
                  fill=current_color, width=brush_size)
    elif tool == "rectangle":
        draw.rectangle((start_x, start_y, event.x, event.y),
                       outline=current_color, fill=shape_fill, width=brush_size)
    elif tool == "oval":
        draw.ellipse((start_x, start_y, event.x, event.y),
                     outline=current_color, fill=shape_fill, width=brush_size)
    elif tool == "triangle":
        pts = get_triangle_points(start_x, start_y, event.x, event.y)
        draw.polygon(pts, outline=current_color, fill=shape_fill, width=brush_size)
    if tool in ("line", "rectangle", "oval", "triangle"):
        preview_shape = None
        refresh_canvas()

# 7. CANVAS MANAGEMENT
def refresh_canvas():
    """Display the current Pillow image on the Tkinter canvas."""
    global canvas_image
    canvas.delete("all")
    canvas_image = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor="nw", image=canvas_image)

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

# 8. OPEN AND SAVE IMAGE
def open_image():
    """Open an image and display it on the canvas."""
    global image, draw
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        try:
            push_undo()
            opened_image = Image.open(file_path).convert("RGB")
            opened_image = opened_image.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
            image = opened_image
            draw = ImageDraw.Draw(image)
            refresh_canvas()
        except Exception as error:
            messagebox.showerror("Error", f"Could not open image:\n{error}")

def save_image():
    """Save the current drawing as an image file."""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"),
                   ("JPEG Image", "*.jpg"),
                   ("Bitmap Image", "*.bmp")])
    if file_path:
        try:
            saved_img = image.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
            saved_img.save(file_path)
            messagebox.showinfo("Saved", "Your drawing has been saved!")
        except Exception as error:
            messagebox.showerror("Error", f"Could not save image:\n{error}")

# 9. TOOLBAR
def make_button(parent, text, command, bg=PURPLE_BUTTON, fg=TEXT_COLOR):
    """Create one purple-and-black button with pink highlight."""
    return tk.Button(parent, text=text, command=command,
                     bg=bg, fg=fg,
                     activebackground=PURPLE_HOVER, activeforeground=TEXT_COLOR,
                     font=FONT_MAIN, relief="flat", padx=8, pady=4,
                     highlightbackground=PINK_ACCENT, highlightthickness=1,
                     cursor="hand2")

toolbar = tk.Frame(root, bg=PURPLE_PANEL, padx=10, pady=6,
                   highlightbackground=BLACK_ACCENT, highlightthickness=2)
toolbar.pack(pady=4)

color_button = make_button(toolbar, "Choose Color", choose_color)
color_button.pack(side="left", padx=3)

make_button(toolbar, "Brush",
            lambda: set_tool("brush")).pack(side="left", padx=3)
make_button(toolbar, "Eraser",
            lambda: set_tool("eraser")).pack(side="left", padx=3)
make_button(toolbar, "Line",
            lambda: set_tool("line")).pack(side="left", padx=3)
make_button(toolbar, "Rectangle",
            lambda: set_tool("rectangle")).pack(side="left", padx=3)
make_button(toolbar, "Oval",
            lambda: set_tool("oval")).pack(side="left", padx=3)
make_button(toolbar, "Triangle",
            lambda: set_tool("triangle")).pack(side="left", padx=3)

fill_button = make_button(toolbar, "Fill: OFF", toggle_fill)
fill_button.pack(side="left", padx=3)

tk.Label(toolbar, text="Brush Size:", bg=PURPLE_PANEL,
         fg=PINK_ACCENT, font=FONT_MAIN).pack(side="left", padx=(8, 2))

size_slider = tk.Scale(toolbar, from_=1, to=100, orient="horizontal",
                       command=change_brush_size, length=120,
                       bg=PURPLE_PANEL, fg=TEXT_COLOR,
                       troughcolor=PURPLE_BUTTON, highlightthickness=0)
size_slider.set(5)
size_slider.pack(side="left", padx=3)

make_button(toolbar, "Undo", undo_action).pack(side="left", padx=3)
make_button(toolbar, "Clear", clear_canvas).pack(side="left", padx=3)
make_button(toolbar, "Open", open_image).pack(side="left", padx=3)
make_button(toolbar, "Save", save_image).pack(side="left", padx=3)

# Quick colors bar
quick_color_bar = tk.Frame(root, bg=PURPLE_PANEL, padx=10, pady=5,
                           highlightbackground=BLACK_ACCENT, highlightthickness=2)
quick_color_bar.pack(pady=4)

tk.Label(quick_color_bar, text="Quick Colors:", bg=PURPLE_PANEL,
         fg=PINK_ACCENT, font=FONT_MAIN).pack(side="left", padx=(0, 6))

quick_colors = [
    ("Black", "black", "white"),
    ("Red", "red", "white"),
    ("Blue", "blue", "white"),
    ("Green", "green", "white"),
    ("Yellow", "yellow", "black"),
    ("Purple", "purple", "white"),
]

for label, hex_color, text_fg in quick_colors:
    btn = tk.Button(
        quick_color_bar,
        text=label,
        command=lambda c=hex_color: set_quick_color(c),
        bg=hex_color,
        fg=text_fg,
        activebackground=hex_color,
        activeforeground=text_fg,
        font=FONT_MAIN,
        relief="flat",
        padx=10,
        pady=3,
        highlightbackground=PINK_ACCENT,
        highlightthickness=1,
        cursor="hand2"
    )
    btn.pack(side="left", padx=4)

# 10. CONNECT MOUSE EVENTS
canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw_motion)
canvas.bind("<ButtonRelease-1>", finish_drawing)

# 11. RUN THE APPLICATION
root.mainloop()