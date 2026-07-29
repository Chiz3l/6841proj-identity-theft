import os
import fitz
import docx
from PIL import Image
import pytesseract

class DocumentProcessor:
    def __init__(self):
        self.language = "eng"
        # oem is the OCR Engine Mode and 1 is the modern engine with higher accuracy
        # psm is the Page Segmenting Mode and 11 is for sparse or scattered text like that of a passport or drivers licence
        self.tesseract_config = f'--oem 1 --psm 11'

    # this is for when you have a scanned pdf of a document that needs to go through OCR
    def extract_from_pdf(self, pdf_path):
        extracted_text = []
        doc = fitz.open(pdf_path)
        
        for page in doc:
            text = page.get_text("text")
            # check if the pdf already has text in 
            if text.strip():
                extracted_text.append(text)
            # if there is no text in the pdf then scan the pdf to look for text using ocr
            else:
                # 150 is the dpi picked as the resolution is high enough for ocr but still fast
                pixel_map = page.get_pixmap(dpi=150, colorspace="GRAY", alpha=False)
                # "L" is for greyscale rendereing as it is faster
                # also converts the pixelmap that fitz generates into a image that tesseract can use for ocr
                image = Image.frombytes("L", [pixel_map.width, pixel_map.height], pixel_map.samples)
                page_text = pytesseract.image_to_string(image, lang=self.language, config=self.tesseract_config)
                extracted_text.append(page_text)

        # seperates each page by a new line and returns it as one block of text
        return "\n".join(extracted_text)

    # for when the document is in a word doc and there is no need for ocr
    def extract_from_docx(self, docx_path):
        # open the doc
        doc = docx.Document(docx_path)
        extracted_text = []

        # gets all the paragraphs from the word doc
        for paragraph in doc.paragraphs:
            # ignore empty paragraphs
            if paragraph.text.strip():
                extracted_text.append(paragraph.text)
        
        # seperates each paragraph by a new line and returns it as one block of text
        return "\n".join(extracted_text)

    # for when the document is an image that needs ocr applied (processes '.png', '.jpg', '.jpeg', '.bmp', '.tiff' formats)
    def extract_from_image(self, img_path):
        image = Image.open(img_path)
        # convert the image into grayscale to speed up processing
        if image.mode != 'L':
            image = image.convert('L')
        return pytesseract.image_to_string(image, lang=self.language, config=self.tesseract_config)

    # determines what stratagy to use (shout out comp1531) to extract the text from the file
    def process(self, file_path):
        file_extenstion = os.path.splitext(file_path)[1].lower()
        if file_extenstion == '.pdf':
            return self.extract_from_pdf(file_path)
        elif file_extenstion in ['.docx', '.doc']:
            return self.extract_from_docx(file_path)
        elif file_extenstion in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            return self.extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extenstion}")