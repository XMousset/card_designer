from pathlib import Path

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageOps
from tqdm import tqdm

from scripts.config import CONFIG
from scripts.utils import mm_to_px, px_to_mm


class CardImg:
    """Class for managing card creation.

    Attributes
    ----------
    img_format : str
        Image extension from json file.
    back_card : Pillow.Image.Image
        Pillow image of the back.
    width : float
        Width of back image. Equal as front image.
    height : float
        Height of back image. Equal as front image.
    """
    img_format = ""
    back_card = None
    width = 0.0
    height = 0.0

    def __init__(self, rank, color) -> None:
        """Initialize card rank and color.

        Parameters
        ----------
        rank : str
            The rank of the card (e.g., 'A', 'K', 'Q').
        color : str
            The color of the card (e.g., 'hearts', 'spades').

        Raises
        ------
        ValueError
            If front and back have different size.
        """
        self.rank = rank
        self.color = color
        self.color_path = Path(CONFIG["folders"]["inputs"], color)
        if CONFIG["options"]["verify margins"]:
            front_name = CONFIG["names"]["front check"] + CardImg.img_format
        else:
            front_name = CONFIG["names"]["front"] + CardImg.img_format
        front_path = Path(CONFIG["folders"]["inputs"], front_name)
        self.front_card = Image.open(front_path)
        
        if not(self.front_card.size == CardImg.back_card.size):
            raise ValueError("front and back images must have the same size.")
    
    @classmethod
    def set_back_card(cls, img_path) -> None:
        """Set back card for the CardImg class.

        Parameters
        ----------
        img_path : str
            The path of the back image.
        """
        cls.back_card = Image.open(img_path)
        cls.width, cls.height = px_to_mm(cls.back_card.size, rounded= True)
    
    @classmethod
    def set_img_format(cls, format) -> None:
        """Set image format for the CardImg class.
        
        Parameters
        ----------
        format : str
            The image format of each inputs and outputs images
            (e.g. ".png").
        """
        cls.img_format = format
    
    def get_top_left_corner_coordinates(
        self,
        img,
        anchor_coord= [0, 0],
        anchor= [0, 0]
        ) -> npt.NDArray:
        """Get top-left corner coordinates from anchor coordinates.
        
        Calculate the top-left corner coordinates (in pixels) to place
        the image such that its anchor point (defined in percentage
        of image size) is at the specified coordinates (in pixels).
        
        Parameters
        ----------
        img : PIL.Image.Image
            Input Pillow image
        anchor_coord : list, optional
            A list representing the (x, y) coordinates (in pixels) for
            the anchor point of the image, by default [0, 0].
        anchor : list, optional
            A list representing the (x, y) coordinates (in percentage)
            of the image anchor, by default [0, 0].
            For example, [0.5, 0.5] represent the center of the image.

        Returns
        -------
        numpy.ndarray
            Array representing the (x, y) coordinates of the top-left
            corner (in pixels).

        Raises
        ------
        ValueError
            If anchor values are not between 0 and 1.
        ValueError
            If the top-left corner coordinates are negative.
        """
        if any(x < 0 or x > 1 for x in anchor):
            raise ValueError(f"Anchor values must be between 0 and 1.")
        
        top_left_coord = np.round(np.array(anchor_coord)
                                  - np.array(img.size) * np.array(anchor))
        
        if any(top_left_coord < 0):
            raise ValueError(
                "Overlay out of borders. "
                "Top left corner coordinates are negatives : "
                f"{top_left_coord}"
                )
        
        return top_left_coord

    def paste_img(self, img, top_left_coord) -> None:
        """Paste the overlay image on the card.

        Parameters
        ----------
        img : PIL.Image.Image
            The Pillow image to be pasted on the front image.
        top_left_coord : numpy.ndarray
            Array representing the (x, y) coordinates of the top-left
            corner. Units in pixels.

        Raises
        ------
        ValueError
            If the bottom-right corner coordinates of the image are
            outside of the card.
        """
        bottom_right_coord = top_left_coord + np.array(img.size)
        
        if any(bottom_right_coord > np.array(self.front_card.size)):
            raise ValueError(
                "Overlay out of boarders. "
                "Bottom right corner coordinates exceeds main image : "
                f"{bottom_right_coord}"
                )
        
        coord_int_tuple = tuple(top_left_coord.astype(int))
        self.front_card.paste(img, coord_int_tuple, mask= img)

    def paste_corners(self, img, top_left_coord) -> None:
        """Paste image symetrically on each corner of the card.

        Parameters
        ----------
        img : PIL.Image.Image
            The Pillow image to be pasted on each corners of the card.
        top_left_coord : numpy.ndarray
            Array representing the (x, y) coordinates of the top-left
            corner of the image from the top-left corner of the card.
            Units in pixels.
        """
        inverted_overlay = ImageOps.flip(ImageOps.mirror(img))
        corners_anchors = np.array([[0,0], [1,0], [0,1], [1,1]])
        need_invertion = [False, False, True, True]
        corners_pos = []
        
        for c_anch in corners_anchors:
            coord = (
                (1 - c_anch) * top_left_coord
                + c_anch * (self.front_card.size - top_left_coord)
            )
            tl_coord = self.get_top_left_corner_coordinates(img, coord, c_anch)
            corners_pos.append(tl_coord)
        
        for cond, cp in zip(need_invertion, corners_pos):
            if cond:
                self.paste_img(inverted_overlay, cp)
            else:
                self.paste_img(img, cp)

    def paste_center(self, img) -> None:
        """Paste image in the center of the card.

        Parameters
        ----------
        img : PIL.Image.Image
            The Pillow image to be paste in the middle of the card.

        Raises
        ------
        ValueError
            If the image size is greater than the card.
        """
        if any(self.front_card.size[i] < img.size[i] for i in range(2)):
            raise ValueError("Image exceeds card size.")
        
        center_coord = self.get_top_left_corner_coordinates(
            img,
            anchor_coord= np.array(self.front_card.size) / 2,
            anchor= [0.5, 0.5]
            )
        self.paste_img(img, center_coord)

    def save_image(self) -> None:
        """Save self.front_card."""
        img_name = self.color + "_" + self.rank + CardImg.img_format
        save_path = Path(
            CONFIG["folders"]["outputs"],
            CONFIG["folders"]["images"],
            img_name
            )
        self.front_card.save(save_path)


    def construct_card_image(self) -> None:
        """Paste all elements on self.front_card."""
        # center image
        center_overlay = Image.open(
            self.color_path / (self.rank + "_center" + CardImg.img_format)
        )
        self.paste_center(center_overlay)
        
        # color image in each corners
        color_overlay = Image.open(
            self.color_path / (CONFIG["names"]["symbol"] + CardImg.img_format)
        )
        color_coord = mm_to_px(
            CONFIG["dimensions"]["bleed"] + CONFIG["dimensions"]["margins"]
        )
        color_tl_coord = self.get_top_left_corner_coordinates(
            color_overlay, anchor_coord= color_coord
        )
        self.paste_corners(color_overlay, color_tl_coord)
        
        # rank image in each corners
        rank_overlay = Image.open(
            self.color_path / (self.rank + CardImg.img_format)
        )
        color_overlay_middle_coord = np.array([color_overlay.width/2, 0])
        all_dims = (
            np.array(CONFIG["dimensions"]["bleed"])
            + CONFIG["dimensions"]["margins"]
            - CONFIG["dimensions"]["space"]
        )
        rank_coord = mm_to_px(all_dims) + color_overlay_middle_coord
        rank_tl_coord = self.get_top_left_corner_coordinates(
            rank_overlay, anchor_coord= rank_coord, anchor= [0.5, 1]
        )
        self.paste_corners(rank_overlay, rank_tl_coord)


def generate_all_cards_images() -> None:
    """Loop on all cards and construct them."""
    back_name = CONFIG["names"]["back"] + CONFIG["options"]["image format"]
    back_path = Path(CONFIG["folders"]["inputs"], back_name)
    
    CardImg.set_back_card(back_path)
    CardImg.set_img_format(CONFIG["options"]["image format"])
    
    print("Images creation:")
    for r in tqdm(CONFIG["names"]["ranks"]):
        for c in CONFIG["names"]["colors"]:
            card = CardImg(r, c)
            card.construct_card_image()
            card.save_image()
