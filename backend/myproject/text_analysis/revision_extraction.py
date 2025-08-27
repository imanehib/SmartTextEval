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
                index_starts.append(i-1)
                reason_starts.append("deletion")
                deletion = True


                if cursor_list[i] != len(text_list[i]):
                    positions.append("pre-contextual")

                else:
                    positions.append("contextual")
                
            elif len(text_list[i])>= len(text_list[i-1]) and cursor_list[i]<len(text_list[i]):
                index_starts.append(i-1)
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
        typed_enough = False
        
        for i in range(index_start + 1, len(text_list)):

            #if deletion
            if len(text_list[i]) < len(text_list[i - 1]):
                deleted_chars += len(text_list[i - 1]) - len(text_list[i])
                

            else:
                typed_chars += len(text_list[i]) - len(text_list[i - 1])

            if abs(deleted_chars - typed_chars) <= 5 :
                typed_enough = True #une fois qu"on a suffisamment tapé, même si on tape plus avant d'avoir rencontré un espace on ne veut pas bloquer la fin de révision
            if typed_enough and i < (len(text_list) - 1) and text_list[i + 1][cursor_list[i+1]-1].isspace():     
                index_end = i + 1
                return index_end
    elif reason_start == "move":
        for i in range(index_start + 2, len(text_list)):
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
    print(index_starts, reason_starts, positions)
    for index_start, reason_start, position in zip(index_starts, reason_starts, positions):
        print(text_list[index_start])
        index_end = extract_end(text_list, cursor_list, index_start, reason_start)
        print(text_list[index_end])
        if index_end != -1:
            revisions.append(Revision(index_start, index_end, position, reason_start, text_list[index_start], text_list[index_end])) 
    for revision in revisions:
        print(revision)
    return revisions


"""
time_list=[1641.0, 1916.0, 4302.0, 4566.0, 4821.0, 4962.0, 6402.0, 6606.0, 6769.0, 6882.0, 6985.0, 7172.0, 7380.0, 7588.0, 7749.0, 9346.0, 10465.0, 10564.0, 10676.0, 10783.0, 11562.0, 11806.0, 11924.0, 12014.0, 12093.0, 12099.0, 12197.0, 12344.0, 12434.0, 12717.0, 12847.0, 12941.0, 13084.0, 13331.0, 13474.0, 13755.0, 13832.0, 14285.0, 14401.0, 14753.0, 14913.0, 15006.0, 15084.0, 15251.0, 15315.0, 15449.0, 15630.0, 15697.0, 15809.0, 15972.0, 16160.0, 20933.0] 
text_list_test=['J', "J'", "J'é", "J'éc", "J'écr", "J'écri", "J'écri ", "J'écri u", "J'écri un", "J'écri un ", "J'écri un t", "J'écri un te", "J'écri un tex", "J'écri un text", "J'écri un texte", "J'écris un texte", "J'écris un texte ", "J'écris un texte a", "J'écris un texte av", "J'écris un texte ave", "J'écris un texte avec", "J'écris un texte avec ", "J'écris un texte avec q", "J'écris un texte avec qu", "J'écris un texte avec que", "J'écris un texte avec quer", "J'écris un texte avec querl", "J'écris un texte avec querlq", "J'écris un texte avec querlqu", "J'écris un texte avec querlq", "J'écris un texte avec querl", "J'écris un texte avec quer", "J'écris un texte avec que", "J'écris un texte avec quel", "J'écris un texte avec quele", "J'écris un texte avec queleq", "J'écris un texte avec quelequ", "J'écris un texte avec queleq", "J'écris un texte avec quele", "J'écris un texte avec quel", "J'écris un texte avec quelq", "J'écris un texte avec quelqu", "J'écris un texte avec quelque", "J'écris un texte avec quelques", "J'écris un texte avec quelques ", "J'écris un texte avec quelques f", "J'écris un texte avec quelques fa", "J'écris un texte avec quelques fau", "J'écris un texte avec quelques faut", "J'écris un texte avec quelques faute", "J'écris un texte avec quelques fautes", "J'écris un texte avec quelques fautes."] 
cursor_list_test=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 7, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 28, 27, 26, 25, 26, 27, 28, 29, 28, 27, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]


time_list=[3427.0, 3599.0, 3726.0, 3842.0, 4039.0, 4096.0, 4304.0, 4387.0, 4627.0, 4788.0, 5022.0, 5215.0, 5376.0, 6021.0, 6331.0, 6513.0, 7423.0, 7572.0, 8517.0, 8633.0, 8867.0, 9052.0, 9219.0, 9292.0, 9443.0, 9639.0, 9823.0, 12265.0, 13983.0, 14210.0, 15928.0, 16184.0, 16414.0, 16506.0, 16652.0, 16879.0, 16972.0, 18156.0, 18834.0, 19114.0, 19319.0, 19888.0, 20008.0, 20127.0, 20275.0, 20478.0, 20714.0, 20803.0, 20900.0, 21028.0, 21092.0, 21253.0, 21314.0, 21458.0, 21549.0, 21698.0, 21874.0, 21985.0, 22495.0, 22938.0, 23164.0, 23259.0, 23389.0, 23765.0, 24322.0] 
text_list_test=['O', 'On', 'On ', 'On v', 'On va', 'On va ', 'On va m', 'On va me', 'On va met', 'On va mett', 'On va mettr', 'On va mettre', 'On va mettre ', 'On va mettre d', 'On va mettre de', 'On va mettre de ', 'On va mettre de r', 'On va mettre de re', 'On va mettre de r', 'On va mettre de ré', 'On va mettre de rév', 'On va mettre de révi', 'On va mettre de révis', 'On va mettre de révisi', 'On va mettre de révisio', 'On va mettre de révision', 'On va mettre de révisions', 'On va mettre des révisions', 'On va mettre des révisions.', 'On va mettre des révisions. ', 'On va mettre des révisions. J', "On va mettre des révisions. J'", "On va mettre des révisions. J'e", "On va mettre des révisions. J'en", "On va mettre des révisions. J'en ", "On va mettre des révisions. J'en m", "On va mettre des révisions. J'en me", "On va mettre des révisions. J'en m", "On va mettre des révisions. J'en ma", "On va mettre des révisions. J'en mai", "On va mettre des révisions. J'en mais", "On va mettre des révisions. J'en mai", "On va mettre des révisions. J'en ma", "On va mettre des révisions. J'en m", "On va mettre des révisions. J'en me", "On va mettre des révisions. J'en met", "On va mettre des révisions. J'en mets", "On va mettre des révisions. J'en mets ", "On va mettre des révisions. J'en mets d", "On va mettre des révisions. J'en mets de", "On va mettre des révisions. J'en mets de ", "On va mettre des révisions. J'en mets de t", "On va mettre des révisions. J'en mets de to", "On va mettre des révisions. J'en mets de tou", "On va mettre des révisions. J'en mets de tout", "On va mettre des révisions. J'en mets de tout ", "On va mettre des révisions. J'en mets de tout t", "On va mettre des révisions. J'en mets de tout tu", "On va mettre des révisions. J'en mets de tout t", "On va mettre des révisions. J'en mets de tout ty", "On va mettre des révisions. J'en mets de tout typ", "On va mettre des révisions. J'en mets de tout type", "On va mettre des révisions. J'en mets de tout type ", "On va mettre des révisions. J'en mets de tout type", "On va mettre des révisions. J'en mets de tout type."]
cursor_list_test=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 17, 18, 19, 20, 21, 22, 23, 24, 25, 16, 27, 28, 29, 30, 31, 32, 33, 34, 35, 34, 35, 36, 37, 36, 35, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 47, 48, 49, 50, 51, 50, 51]

extract_revisions(text_list_test, cursor_list_test)
"""