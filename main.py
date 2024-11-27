from scripts.config import CONFIG
from scripts.card_img import generate_all_cards_images
from scripts.pdf_deck_creator import PDFDeckCreator


if __name__ == "__main__":
    
    if CONFIG["options"]["generate images"]:
        generate_all_cards_images()
    
    if CONFIG["options"]["generate pdf"]:
        pdf = PDFDeckCreator()
        
        match CONFIG["options"]["pdf format"]:
            case "separated":
                pdf.create_separated()
            case "alternated":
                pdf.create_alternated()
            case _:
                pdf.create_default()
