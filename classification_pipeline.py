import time
import json
from document_ocr import DocumentProcessor
from document_classifier import DocumentClassifier

# Initialize engines
processor = DocumentProcessor()
classifier = DocumentClassifier()
    

def run_pipeline(file_path):
    start_time = time.time()
    
    # get the text from the document 
    text = processor.process(file_path)
    ocr_time = round(time.time() - start_time, 3)
    
    # classify the document
    classification_start = time.time()
    metadata = classifier.classify(text)
    classification_time = round(time.time() - classification_start, 3)
    
    total_time = round(time.time() - start_time, 3)
    
    metadata["ocr_time_sec"] = ocr_time
    metadata["classification_time_sec"] = classification_time
    metadata["total_time_sec"] = total_time
    metadata["file_path"] = file_path
    
    return metadata

if __name__ == "__main__":
    # Test execution
    # sample_file = "sample.docx"
    # sample_file = "Passport.pdf"
    sample_file = "Sample.pdf"
    result = run_pipeline(sample_file)
    print(json.dumps(result, indent=2))