from pathlib import Path

from scripts.config import CONFIG


def sort_cards_path(path):
    """Key function to sort cards in ascending order.

    Parameters
    ----------
    path : str
        The full path name of a card.

    Returns
    -------
    tuple (str, int)
        Tuple (c, r) for color and rank of the card.

    Raises
    ------
    ValueError
        If the name of the card 
    """
    name = Path(path).stem
    rank_str = name[-1:]
    rank = 0
    color = name[:3]
    
    if rank_str.isdigit():
        rank = int(rank_str)
        if rank == 0:
            rank = 10
    else:
        if rank_str in ["J", "V"]:
            rank = 11
        if rank_str in ["Q", "D"]:
            rank = 12
        if rank_str in ["K", "R"]:
            rank = 13
        if rank_str == "A":
            rank = 14
    
    return (color, rank)


def list_images_path() -> list:
        """List all images in folder define by CONFIG.

        Returns
        -------
        list of Path
            List of images name.

        Raises
        ------
        ValueError
            If no image found in folder.
        """
        img_folder = Path(
            CONFIG["folders"]["outputs"], CONFIG["folders"]["images"]
        )
        path_list = []
        for p in img_folder.iterdir():
            if p.suffix.lower() == CONFIG["options"]["image format"]:
                path_list.append(img_folder / p.name)
        
        if len(path_list) == 0:
            raise ValueError(f"No image in {img_folder}")
        
        path_list.sort(key= sort_cards_path, reverse= True)
        
        return path_list


def mm_to_px(x) -> list:
    """Convert list of numbers from milimeters to rounded pixels.

    Parameters
    ----------
    x : list
        List in milimeters.

    Returns
    -------
    list of float
        List in pixels (rounded).
    """
    px_list = [
        round(mm / 25.4 * CONFIG["dimensions"]["PPP"], 0)
        for mm in x
        ]
    return px_list


def px_to_mm(x, rounded= False) -> list:
    """Convert pixels into milimeters.

    Parameters
    ----------
    x : list
        List in pixels.
    rounded : bool, optional
        Round mm results if True, by default False

    Returns
    -------
    list of float
        List in milimeters.
    """
    mm_list = [
        px * 25.4 / CONFIG["dimensions"]["PPP"]
        for px in x
        ]
    if rounded:
        mm_list = [round(mm, 0) for mm in mm_list]
    return mm_list
