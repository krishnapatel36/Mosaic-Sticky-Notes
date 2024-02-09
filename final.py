import base64
from PIL import Image, ImageFont, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import math
import os
import streamlit as st

PROGRESS_WIDTH = 20

PIN_COLORS = [
    (255, 255, 255),  # White
    (238, 117, 184),  # Pink
    (240, 177, 48),   # Orange
    (241, 237, 61),   # Yellow
    (119, 220, 126),  # Green
    (255, 165, 164)   # Peach
]

def calculate_grid_dimensions(source_width, source_height, block_size):
    rows = math.ceil(source_height / block_size)
    columns = math.ceil(source_width / block_size)
    return rows, columns

def generate_image_and_pdf(image_location, total_pins_requested, line_width=1):
    font_size = 9

    if not image_location:
        return "No image file uploaded. Please upload an image file."

    total_pins_requested = int(total_pins_requested)

    SOURCE_IMAGE = Image.open(image_location)
    SOURCE_IMAGE = SOURCE_IMAGE.convert('RGB')

    source_width, source_height = SOURCE_IMAGE.size
    demo_image = Image.new('RGB', (source_width, source_height))
    demo_pixels = demo_image.load()
    number_image = Image.new('RGB', (source_width, source_height), color=(255, 255, 255))
    number_draw = ImageDraw.Draw(number_image)
    number_font = ImageFont.load_default()

    GRID_COLOR = (128, 128, 128)

    def adjust_block_size(total_pins_requested, total_pins_available, current_block_size):
        return math.ceil(current_block_size * math.sqrt(total_pins_available / total_pins_requested))

    def add_grid_lines(image, grid_color, interval, line_width):
        draw = ImageDraw.Draw(image)
        for x in range(0, source_width, interval):
            draw.line([(x, 0), (x, source_height)], fill=grid_color, width=line_width)
        for y in range(0, source_height, interval):
            draw.line([(0, y), (source_width, y)], fill=grid_color, width=line_width)

    def average_rgb_area(x, y):
        total_r, total_g, total_b = (0, 0, 0)
        for area_y in range(y, y + block_size):
            for area_x in range(x, x + block_size):
                r, g, b = (SOURCE_IMAGE.getpixel((x, y)))
                total_r = total_r + r
                total_g = total_g + g
                total_b = total_b + b
        area = block_size * block_size
        final_rgb = (int(total_r / area), int(total_g / area), int(total_b / area))
        return final_rgb

    def fill_area(x, y, color):
        for area_y in range(y, y + block_size):
            for area_x in range(x, x + block_size):
                try:
                    if demo_pixels[area_x, area_y] != (255, 255, 255):
                        demo_pixels[area_x, area_y] = color
                except IndexError:
                    pass

    def closest_pin_color_weighted(rgb):
        r, g, b = rgb
        color_diffs = []
        for color in PIN_COLORS:
            cr, cg, cb = color
            color_diff = math.sqrt(((r - cr)*0.30)**2 + ((g - cg)*0.59)**2 + ((b - cb)*0.11)**2)
            color_diffs.append((color_diff, color))
        return min(color_diffs)[1]

    block_size = int(math.sqrt((source_width * source_height) / total_pins_requested))
    total_pin_count = 0
    all_colors = []

    for source_y in range(0, source_height, block_size):
        for source_x in range(0, source_width, block_size):
            block_rgb = average_rgb_area(source_x, source_y)
            block_pin_rgb = closest_pin_color_weighted(block_rgb)
            fill_area(source_x, source_y, block_pin_rgb)
            demo_pixels[source_x, source_y] = block_rgb
            total_pin_count = total_pin_count + 1
            all_colors.append(block_pin_rgb)
            number_draw.text((source_x + 20, source_y + 20),
                             str(PIN_COLORS.index(block_pin_rgb)),
                             font=number_font,
                             fill=(0, 0, 0))

    rows, columns = calculate_grid_dimensions(source_width, source_height, block_size)

    # Calculate the new grid dimensions
    rows = math.ceil(total_pins_requested / columns)

    all_colors.sort()

    result_text = f'{("# Total count"): <10}{"Color (rgb)": <20}\n'

    for color in PIN_COLORS:
        result_text += f'{all_colors.count(color): <10}{", ".join(map(str, color)): <20}\n'

    if line_width > 0:
        add_grid_lines(demo_image, GRID_COLOR, block_size, line_width)

    demo_image.save('output_image.png', 'PNG')

    pdf_output_path = 'Output_PDF.pdf'
    pdf_canvas = canvas.Canvas(pdf_output_path, pagesize=letter)

    boxes_per_page_horizontal = 12
    boxes_per_page_vertical = 16

    total_pages_horizontal = math.ceil(columns / boxes_per_page_horizontal)
    total_pages_vertical = math.ceil(rows / boxes_per_page_vertical)

    for page_vertical in range(total_pages_vertical):
        for page_horizontal in range(total_pages_horizontal):
            start_y = page_vertical * boxes_per_page_vertical
            start_x = page_horizontal * boxes_per_page_horizontal
            end_y = min(start_y + boxes_per_page_vertical, rows)
            end_x = min(start_x + boxes_per_page_horizontal, columns)

            pdf_canvas.showPage()

            # Add margins to the PDF by adjusting the coordinates
            left_margin = 20
            top_margin = 40
            pdf_canvas.drawInlineImage(demo_image.crop((start_x * block_size, start_y * block_size,
                                                        end_x * block_size, end_y * block_size)),
                                       left_margin, top_margin,
                                       width=letter[0] - left_margin * 2, height=letter[1] - top_margin * 2)

            # Write column and row numbers to the top margin
            pdf_canvas.setFont("Helvetica", 18)
            col_letter = chr(ord('A') + (start_x // boxes_per_page_horizontal))
            col_num = start_x % boxes_per_page_horizontal + 1
            row_num = start_y // boxes_per_page_vertical + 1
            page_label = f"{col_letter}{row_num}"
            pdf_canvas.drawString(left_margin + 14, letter[1] - top_margin + 25, page_label)

            # Write column and row numbers to the top margin
            pdf_canvas.setFont("Helvetica", 18)
            for col_num in range(start_x + 1, end_x + 1):
                col_x = left_margin + (col_num - start_x - 1) * (letter[0] - left_margin * 2) / (end_x - start_x)
                pdf_canvas.drawString(col_x + 14, letter[1] - top_margin + 5, str(col_num))

            # Write row numbers to the bottom margin
            pdf_canvas.setFont("Helvetica", 18)
            for row_num in range(start_y + 1, end_y + 1):
                row_y = top_margin - 5 - (row_num - start_y - 1) * (letter[1] - top_margin * 2) / (end_y - start_y)
                pdf_canvas.drawString(left_margin - 20, row_y + 680, str(row_num))

    pdf_canvas.save()
    return result_text, 'output_image.png', 'Output_PDF.pdf'


# Function to create a download link
def create_download_link(file_path, button_text):
    with open(file_path, "rb") as file:
        contents = file.read()
        encoded_file = base64.b64encode(contents).decode()
        href = f'<a href="data:file/txt;base64,{encoded_file}" download="{file_path}">{button_text}</a>'
    return href


# Streamlit app starts here
st.title("Image Generator")

image_location = st.file_uploader("Select Image", type=["png", "jpg", "jpeg", "gif"])

if image_location:
    total_pins_requested = st.number_input("Enter total number of sticky notes", min_value=1, value=100, step=1)

    if image_location and st.button("Generate Image and PDF"):
        result_text, preview_image_path, pdf_path = generate_image_and_pdf(image_location, total_pins_requested)

        # Display results
        st.text(result_text)

        # Display preview image
        st.image(Image.open(preview_image_path).resize((300, 300)), caption='Preview Image', use_column_width=True)

        # Create download links for PDF and output image
        pdf_download_link = create_download_link(pdf_path, "Download PDF")
        st.markdown(pdf_download_link, unsafe_allow_html=True)

        image_download_link = create_download_link('output_image.png', "Download Output Image")
        st.markdown(image_download_link, unsafe_allow_html=True)
