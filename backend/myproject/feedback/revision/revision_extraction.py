from typing import List
from revision.revision import Revision


def extract_starts(text_list, cursor_list, time_list):
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
    for i in range(1, len(text_list)):
        if cursor_list[i] != cursor_list[i - 1] + 1:  # Check if cursor moved more than one position
            index_starts.append(i)
            if len(text_list[i]) < len(text_list[i - 1]): # si on a une suppression
                reason_starts.append("deletion")
            else:
                reason_starts.append("move") # sinon alors on a un mouvement de curseur
            if cursor_list[i] != len(text_list[i]):
                positions.append("pre-contextual")
            else:
                positions.append("contextual")
    return index_starts, reason_starts, positions


def extract_end(text_list, cursor_list, time_list, index_start, reason_start):
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
    return len(text_list) - 1 if index_end == -1 else index_end  # If no end found, return the last index

def extract_revisions(text_list, cursor_list, time_list)-> List[Revision]:
    """    Extracts all revisions in a text based on cursor movements and text states.

    Args:
        text_list (list): List of text states at each keystroke.
        cursor_list (list): List of cursor positions at each keystroke.
        time_list (list): List of timestamps corresponding to each keystroke.

    Returns:
        revisions (list): List of dictionaries containing start and end indices, reasons, and other metadata for each revision.
    """
    revisions = []
    index_starts, reason_starts, positions = extract_starts(text_list, cursor_list, time_list)

    for index_start, reason_start, position in zip(index_starts, reason_starts, positions):
        index_end = extract_end(text_list, cursor_list, time_list, index_start, reason_start)
        if index_end != -1:
            revisions.append(Revision(index_start, index_end, position, text_list[index_start], text_list[index_end])) 

    return revisions






















# définir un modèle basé sur des règles pour détecter les fins de révision
# si début = mouvement de curseur de + de 1
# fin de révision si on bouge le curseur de + de 1 -> couvre toutes les modifs internes/
# 
# si début = suppression 
# fin = après l'ajout du même nombre de caractères (ou moins) + espace
import pandas as pd
import numpy as np
import math

from sklearn.metrics import accuracy_score, recall_score, precision_score, make_scorer, f1_score

"""def define_start(prev_row, row_start):
    if abs(prev_row['cursor'] - row_start['cursor']) > 1 and row_start['characters_from_leading_edge']>1:
        return("move")
    elif row_start["isdeletion"]:
        return("deletion")
    else:
        return("not_treated")"""

def define_start(row_start):
    res = []
    if type(row_start["text_start"])!= float and row_start["cursor_start"] != len(row_start["text_start"]) and abs(row_start["cursor_start"]-row_start["cursor"])>1:
        res.append("move")
    elif type(row_start["text_end"])!= float and row_start["cursor"] != len(row_start["text_end"]) and abs(row_start["cursor_start"]-row_start["cursor"])>1:
        res.append("move")
    if row_start["isdeletion"]:
        res.append("deletion")
    if res == []:
        res.append("not_treated")
    return res
    
def find_end_move(X_data, indices):
    for i in range(1,len(indices)):
        row = X_data.loc[indices[i]]
        prev_row = X_data.loc[indices[i-1]]
        if abs(prev_row['cursor'] - row['cursor']) > 1:
            X_data.loc[indices[i-1], 'prediction'] = 1
            return X_data
    X_data.loc[indices[len(indices)-1], 'prediction'] = 1
    #print("no end found, move")
    return X_data


#fin une fois qu'on a retapé un certain nb de caractères + espace
def find_end_deletion(X_data, indices):
    typed_enough = False
    for i in range(1,len(indices)):
        row = X_data.loc[indices[i]]
        if not row['isdeletion']:
            if row['characters_produced']<=5 and row["characters_produced"]>=-5:
                typed_enough = True
            if row["isspace"] and typed_enough:
                X_data.loc[indices[i-1], 'prediction'] = 1
                return X_data
    X_data.loc[indices[len(indices)-1], 'prediction'] = 1
    #print("no end found, deletion")
    return(X_data)

def predict(X_data):
    
    #pour le moment on va laisser de côté les premières révisions de chaque texte
    prev_row = pd.Series({'episode_id': -1})
    count_reated = 0 
    count_problematic = 0
    prev_value = 0
    subset_not_treated = []
    index_covered = []
    X_data["start"] = "none"
    for index, row in X_data.iterrows():
        if row["episode_id"]!=prev_row["episode_id"] and not math.isnan(prev_row["episode_id"]):
            start = define_start(row)
            mask = X_data["episode_id"] == row["episode_id"]
            indices = X_data.index[mask]
            X_data.loc[indices, "start"] = " ".join(start)
            if "move" in start:
                X_data = find_end_move(X_data, indices)
                count_reated+=1
            elif "deletion" in start and "move" not in start:
                X_data = find_end_deletion(X_data, indices)
                count_reated+=1
                #if 1 in X_data['prediction'].value_counts():
                    #if X_data['prediction'].value_counts()[1]==prev_value:
                        #print("hey")
                    #else:
                        #prev_value = X_data['prediction'].value_counts()[1]
            
            else:
                subset_not_treated.append(row)
            #print("one done : " + str(row["episode_id"]))
        else:
            count_problematic +=1
        prev_row = row
        
    
    result = pd.DataFrame(subset_not_treated)
    result.to_csv("not_treated.csv")
    print("TREATED" + str(count_reated))
    print(X_data['prediction'].value_counts()[1])
    print(count_problematic)
    return X_data



def evaluate_distance_baseline(X_data, y_truth):
    distances = []
    too_much = []
    prev_episode = -1
    depassement = 0
    true_after = 0
    #on veut aller chercher la vraie fin et aller la comparer à la fin prédite
    for index, keystroke_row in X_data.iterrows():
        if keystroke_row['episode_id']!=prev_episode and keystroke_row['prediction']==1:
            index_true_end = -1
            prev_episode = keystroke_row['episode_id']
            concerned_y = y_truth[X_data['episode_id'] == keystroke_row['episode_id']]
            for index_y, row in concerned_y.iterrows():
                if row["prediction"] == 1:
                    index_true_end = index_y
                    break
            if index_true_end!= -1:
                row_true_end = X_data.loc[index_true_end]
                distance = abs(keystroke_row['index_end']-row_true_end["index_end"])
                """if distance>10:
                    #print(keystroke_row['episode_id'])
                    #print(keystroke_row["text_start"], keystroke_row["text_end"])
                    
                    
                    if index > index_true_end:
                        depassement +=1
                        too_much.append(find_row_start(keystroke_row['episode_id'], X_data))
                        too_much.append(X_data.loc[[index]])
                        too_much.append(X_data.loc[[index+1]])
                        too_much.append(X_data.loc[[index_true_end]])
                        too_much.append(X_data.loc[[index_true_end+1]])
                    else:
                        true_after +=1
                        too_much.append(find_row_start(keystroke_row['episode_id'], X_data))
                        too_much.append(X_data.loc[[index]])
                        too_much.append(X_data.loc[[index+1]])
                        too_much.append(X_data.loc[[index_true_end]])
                        too_much.append(X_data.loc[[index_true_end+1]])
                    """
                
                distances.append(distance)
            else:
                print("WEIRD")
    print(distances)
    #result = pd.concat(too_much, ignore_index=True)
    #result.to_csv("too_much_prediction.csv")
    avg = np.mean(distances)
    std = np.std(distances, ddof=0)
    print("YES_To_PREDICT : " +str(y_truth['prediction'].value_counts()[1]))
    print("YES PREDICTED : "+ str(X_data['prediction'].value_counts()[1]))
    print((X_data['prediction'].value_counts()[1]/y_truth['prediction'].value_counts()[1]) * 100)
    count_3 = 0
    count_1 = 0
    for distance in distances:
        if distance <=3:
            count_3 +=1
        if distance <= 1:
            count_1 +=1
    print("3-off precision : " + str(count_3/len(distances)))
    print("1-off precision : " + str(count_1/len(distances)))
    
    print("ON DEPASSE LA VERITE : " + str(depassement))
    print("LA VERITE ARRIVE APRES LA PREDICTION : " + str(true_after))
    return(avg, std, np.min(distances), np.max(distances))

def find_row_start(episode_id, X_data):
    x_episode = X_data[X_data['episode_id'] == episode_id]
    return x_episode.iloc[[0]]




def go_back_to_old_conijn(X_data):
    """fonction qui permet de repasser à l'ancienne version d'annotation où on ne prend pas en compte les révisions enchâssées"""
    episode_ids = list(X_data["episode_id"].unique())
    new_data = X_data
    index_episode = 0
    print(episode_ids)
    episode_ids = sorted(episode_ids)
    for next_index in range(1,len(episode_ids)):
        episode = episode_ids[index_episode]
        next_episode = episode_ids[next_index]
        if new_data[new_data["episode_id"] == episode].iloc[0]["exercise"] == new_data[new_data["episode_id"] == next_episode].iloc[0]["exercise"] and new_data[new_data["episode_id"] == episode].iloc[0]["student"]==new_data[new_data["episode_id"] == next_episode].iloc[0]["student"]:
            #on veut choper l'index start du prochain episode et l'index end de l'episode actuel et si l'index_end est supérieur on le ramène là où il faut et on efface tout le reste
            index_end, index = get_episode_end_2(new_data,episode) # index correspond à l'index de dataframe de la vraie fin dans new_data
            index_start, index_data = get_episode_start(new_data, next_episode) #index data correspond à l'index de dataframe de début du prochain episode dans new_data 
            index_new_end = get_index_new_end(new_data, episode, index_start) #index new end correspond à l'index de dataframe dans l'episode actuel pour lequel index_end==index_start du next_episode
            #si on doit bouger la précition (i.e si l'ancienne fin se situe après le début de la prochaine révision)
            if index_start<index_end:
                new_data.loc[index, 'prediction'] = 0
                new_data.loc[index_new_end, 'prediction'] = 1
            new_data = new_data.drop(index=range(index_new_end+1, index_data)) #on efface tout ce qu'il y a entre la fin la plus proche et le prochain début
        index_episode = next_index
    #new_data.to_csv("X_data_complete_old_conijn.csv", index=False)
    return new_data

def get_episode_end_2(data, episode_id):
    index_end = -1
    subset = data[data['episode_id']==episode_id]
    for index, row in subset.iterrows():
        if row["prediction"] == 1:
            index_end = row["index_end"]
            return index_end, index
    return row[index_end], index

def get_episode_start(data, episode_id):
    return data[data['episode_id']==episode_id].iloc[0]["index_start"], data[data['episode_id']==episode_id].index[0]

def get_index_new_end(data, episode, index_start):
    return data[(data['episode_id']==episode) & (data['index_end']==index_start)].index[0]

#def go_back_to_old_conijn(X_data):

def baseline(X_data):
        
    for episode in X_data['episode_id'].unique():
        subset = X_data[X_data['episode_id']==episode]
        random_end = np.random.choice(subset.index)
        X_data.loc[random_end, "prediction"] = 1
    return X_data


def main():
    X_data = pd.read_csv("/home/nbl/athena-aipy/src/X_data_complete_old_conijn_clean.csv")
    #X_test = pd.read_csv('/home/nbl/athena-aipy/src/X_test_complete_old_conijn.csv')
    #y_test = pd.read_csv('/home/nbl/athena-aipy/src/y_test_complete_old_conijn.csv')
    #X_data["index_end"] = X_data["index_end"].astype(int)

    #X_data= X_data.sort_values(by=["episode_id", "index_end"]).reset_index(drop=True)
    #X_data.to_csv("X_data_complete_clean.csv", index=False)
    #X_data = X_data[~X_data["episode_id"].isin([962, 1135, 1145, 1157])]


    
    # Identify full duplicates based on "text_start" and "text_end"
   # Identify full duplicates based on "text_start" and "text_end"
    """dup_mask = X_data.duplicated(subset=["text_start", "text_end", "index_start", "index_end"], keep="first")

    # Get the (text_start, text_end, episode_id) triplets that belong to second occurrences
    rows_to_remove = X_data.loc[dup_mask, ["text_start", "text_end","index_start", "index_end", "episode_id"]]

    # Extract the rows that will be deleted
    deleted_rows = X_data.merge(rows_to_remove, on=["text_start", "text_end", "index_start", "index_end", "episode_id"], how="inner")

    # Save deleted rows to CSV
    deleted_rows.to_csv("deleted_rows.csv", index=False)
    
    # Now remove them from the original dataset
    X_data = X_data.merge(rows_to_remove, on=["text_start", "text_end", "index_start", "index_end", "episode_id"], how="left", indicator=True)
    X_data = X_data[X_data["_merge"] == "left_only"].drop(columns=["_merge"])"""
    #print(len(X_data))
    #X_data = go_back_to_old_conijn(X_data)
    #none_data = X_data.groupby(["episode_id"]).filter(lambda g: (g["prediction"] == 1).sum() == 0)
    #none_data.to_csv("data_none_old_conijn.csv", index=False)
    #X_data = X_data.groupby(["episode_id"]).filter(lambda g: (g["prediction"] == 1).sum() == 1)
    #print(len(X_data))
    #X_data = X_data.reset_index(drop=True)
    #X_data.to_csv("X_data_complete_old_conijn_clean.csv", index=False)
    #
    #X_data.groupby('episode_id')
    #print(len(X_data['episode_id'].unique()))
    #y_test = pd.read_csv('/home/nbl/athena-aipy/src/y_test_embedded_complete_clean.csv')
    #X_test = pd.read_csv('/home/nbl/athena-aipy/src/X_test_embedded_complete_clean.csv')
    print(len(X_data["episode_id"].unique()))
    #X_data = X_data[X_data["episode_id"].isin(X_test["episode_id"].unique())]
    #X_data = X_data.reset_index(drop=True)
    y_test = X_data[["prediction", "episode_id"]]
    X_data['prediction'] = 0

    X_data = predict(X_data)

    avg_move, avg_deletion, std_move, std_deletion, min_move, max_move, min_deletion, max_deletion = evaluate_distance(X_data, y_test)
    #avg, std, min, max= evaluate_distance_baseline(X_data, y_test)
    y_pred = X_data['prediction']
    y_test = y_test['prediction']
    accuracy, recall, precision, f1 = evaluate(y_test, y_pred)
    print(len(X_data))
    print(len(y_test))
    #print(len(X_test["episode_id"].unique()))
    print(f"Accuracy : {accuracy}, Recall : {recall}, Precision : {precision}, F1-Score : {f1}, Average Distance Move : {avg_move}, STD distance move : {std_move}, Min Distance : {min_move}, Max Distance : {max_move}, Average Distance Deletion : {avg_deletion}, STD distance deletion : {std_deletion}, Min Distance : {min_deletion}, Max Distance : {max_deletion}")
    #print(f"Accuracy : {accuracy}, Recall : {recall}, Precision : {precision}, F1-Score : {f1}, Average Distance : {avg}, STD distance : {std}, Min Distance : {min}, Max Distance : {max}")