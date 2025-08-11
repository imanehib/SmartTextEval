from typing import List

from ..text_analysis.revision import Revision



def extract_starts(text_list, cursor_list):
    """    Extracts the starting indices of revisions in a text based on cursor movements.

    Args:
        text_list (list): List of text states at each keystroke.
        cursor_list (list): List of cursor positions at each keystroke.
        time_list (list): List of timestamps corresponding to each keystroke.

    Returns:
        index_starts (list): Indices where revisions start.
        reason_starts (list): Reasons for each revision start.
        len(index_starts) == len(reason_starts) == Number of revisions
    """
    index_starts = []
    reason_starts = []
    positions = [] # to save if contextual or pre-contextual revision
    deletion = False
    for i in range(1, len(text_list)):
        if cursor_list[i] != cursor_list[i - 1] + 1:  # Check if cursor moved more than one position and add not already deleting !! 
            
            if len(text_list[i]) < len(text_list[i - 1]) and not deletion: # si on a une suppression
                index_starts.append(i)
                reason_starts.append("deletion")
                deletion = True


                if cursor_list[i] != len(text_list[i]):
                    positions.append("pre-contextual")

                else:
                    positions.append("contextual")
                
            elif len(text_list[i])>= len(text_list[i-1]):
                index_starts.append(i)
                reason_starts.append("move") # sinon alors on a un mouvement de curseur
                deletion = False

                if cursor_list[i] != len(text_list[i]):
                    positions.append("pre-contextual")

                else:
                    positions.append("contextual")
                

        if len(text_list[i])>= len(text_list[i-1]):
            deletion = False 
            
    return index_starts, reason_starts, positions


def extract_end(text_list, cursor_list, index_start, reason_start):
    """    Extracts the ending indices of one revision in a text based on cursor movements.
    Args:
        text_list (list): List of text states at each keystroke.
        cursor_list (list): List of cursor positions at each keystroke.
        time_list (list): List of timestamps corresponding to each keystroke.
        index_start (int): Index where the revision starts.
        reason_start (str): Reason for the revision start.

    Returns:
        index_end (int): Index where the revision ends.
        
    """
    index_end = -1
    if reason_start == "deletion":
        # For deletion, we look for the end of the deletion sequence while counting the number of characters deleted
        # the end of revision is reached when whe have typed the same number of characters as we deleted +/-5 and a space
        deleted_chars = 0
        typed_chars = 0
        
        for i in range(index_start + 1, len(text_list)):

            #if deletion
            if len(text_list[i]) < len(text_list[i - 1]):
                deleted_chars += len(text_list[i - 1]) - len(text_list[i])

            else:
                typed_chars += len(text_list[i]) - len(text_list[i - 1])
            if abs(deleted_chars - typed_chars) <= 5 and (i < len(text_list) - 1 and text_list[i + 1].isspace()):
                index_end = i + 1
                return index_end
    elif reason_start == "move":
        for i in range(index_start + 1, len(text_list)):
            if abs(cursor_list[i]-cursor_list[i-1])>1:
                index_end = i-1
                return index_end
    return len(text_list) - 1 if index_end == -1 else index_end  # If no end found, return the last index

def extract_revisions(text_list, cursor_list)-> List[Revision]:
    """    Extracts all revisions in a text based on cursor movements and text states.

    Args:
        text_list (list): List of text states at each keystroke.
        cursor_list (list): List of cursor positions at each keystroke.
        time_list (list): List of timestamps corresponding to each keystroke.

    Returns:
        revisions (list): List of dictionaries containing start and end indices, reasons, and other metadata for each revision.
    """
    revisions = []
    index_starts, reason_starts, positions = extract_starts(text_list, cursor_list)

    for index_start, reason_start, position in zip(index_starts, reason_starts, positions):
        index_end = extract_end(text_list, cursor_list, index_start, reason_start)
        if index_end != -1:
            revisions.append(Revision(index_start, index_end, position, text_list[index_start], text_list[index_end])) 

    return revisions



