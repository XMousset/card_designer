from pathlib import Path

from PIL import Image
from fpdf import FPDF
from tqdm import tqdm

from scripts.utils import px_to_mm, list_images_path
from scripts.config import CONFIG


class PDFDeckCreator():
    
    back_name = CONFIG["names"]["back"] + CONFIG["options"]["image format"]
    back_path = Path(CONFIG["folders"]["inputs"], back_name)
    size = px_to_mm(Image.open(back_path).size, rounded= True)
    
    def __init__(self) -> None:
        self.img_list = list_images_path()
    
    def create(self, path_list, pdf_name) -> None:
        """Create and save the pdf with images as pages.
        
        Parameters
        ----------
        pdf_name : list of str
            List of the images path for the pdf pages.
        pdf_name : str
            Name of the created PDF.
        """
        pdf = FPDF(format=(self.size[0], self.size[1]))
        pdf.set_margins(0,0)
        pdf.set_auto_page_break(auto=False, margin=0)
        for img_path in tqdm(path_list):
                pdf.add_page()
                pdf.image(img_path, w= self.size[0], h= self.size[1])
        pdf.output(Path(CONFIG["folders"]["outputs"], pdf_name + ".pdf"))
    
    def create_default(self) -> None:
        """Create a pdf with only one back image as first page."""
        to_print = self.img_list.copy()
        to_print.insert(0, self.back_path)
        print("Default PDF creation:")
        self.create(to_print, "cards_default")
    
    def create_separated(self) -> None:
        """Create one pdf with all fronts and another with all backs images."""
        to_print = self.img_list.copy()
        print("Fronts PDF creation:")
        self.create(to_print, "cards_fronts")
        print("Backs PDF creation:")
        self.create([self.back_path]*len(to_print), "cards_backs")
    
    def create_alternated(self) -> None:
        """Create a pdf with alternation between back and front images."""
        nb_cards = len(self.img_list)
        to_print = [""] * (2 * nb_cards)
        to_print[0::2] = [self.back_path] * nb_cards
        to_print[1::2] = self.img_list
        print("Alternated PDF creation:")
        self.create(to_print, "cards_alternated")
