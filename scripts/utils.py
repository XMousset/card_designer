from pathlib import Path

from scripts.config import CONFIG


def sort_cards_path(path):
    name = Path(path).stem
    rank = name[-1:]
    color = name[:3]
    
    if rank.isdigit():
        rank = int(rank)
        if rank == 0:
            rank = 10
    else:
        match rank:
            case "J":
                rank = 11
            case "Q":
                rank = 12
            case "K":
                rank = 13
            case "A":
                rank = 14
            case _:
                raise ValueError(f"Card name as an error : {path}")
    
    return (color, rank)


def list_images_path() -> list:
        """List all images in appropriate folder.

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
