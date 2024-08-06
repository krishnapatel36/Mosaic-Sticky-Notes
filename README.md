
# Mosaic Art Generator Using Sticky Notes

Welcome to the Mosaic Art Generator! This Streamlit application allows you to generate mosaic art from images using sticky notes. The application converts an uploaded image into a mosaic format, calculates the required number of sticky notes, and provides both a preview image and a PDF document suitable for printing and assembly.

## Features

- **Image Upload:** Upload an image in PNG, JPG, JPEG, or GIF format.
- **Total Pins Input:** Specify the total number of sticky notes to use for the mosaic.
- **Image and PDF Generation:** Generate a mosaic image and a corresponding PDF document.
- **Preview:** View a preview of the mosaic image.
- **Download Links:** Download the generated mosaic image and PDF.

## Installation

To run this application, you'll need Python and the required libraries. Follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/your-repository.git
   cd your-repository
   ```

2. **Create a Virtual Environment (Optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Create a `requirements.txt` file with the following content:

   ```
   streamlit
   pillow
   reportlab
   ```

## Usage

1. **Run the Streamlit App:**

   ```bash
   streamlit run app.py
   ```

   Replace `app.py` with the name of your script if it's different.

2. **Upload an Image:**

   - Use the file uploader to select an image file (PNG, JPG, JPEG, GIF).

3. **Specify Total Sticky Notes:**

   - Enter the approximate number of sticky notes you want to use for the mosaic.

4. **Generate the Mosaic:**

   - Click the "Generate Image and PDF" button to create the mosaic image and PDF.

5. **View Results:**

   - The preview image and download links for both the mosaic image and the PDF will be displayed.

6. **Download Files:**

   - Use the provided download links to get the mosaic image and PDF document.

## File Details

- **Preview Image:** `output_image.png` - A preview of the generated mosaic image.
- **PDF Document:** `Output_PDF.pdf` - A PDF document containing the mosaic image with grid lines for printing and assembly.
